# n8n - Automatizaciones ISP Inteligente

Esta carpeta contiene los workflows de n8n del proyecto. **n8n no reemplaza al backend ni tiene la lógica de negocio.**
Solo recibe eventos (webhooks) que envía Django y devuelve/genera el mensaje de notificación.
Quien decide *cuándo* pasa algo (asignar técnico, técnico cerca, cierre, escalamiento, etc.) es el backend o el módulo de algoritmos.

## Índice

1. [Levantar n8n](#levantar-n8n)
2. [Workflows disponibles](#workflows-disponibles)
3. [Cómo funciona un workflow](#cómo-funciona-un-workflow)
4. [Cómo llamar a un webhook](#cómo-llamar-a-un-webhook)
5. [Detalle de cada webhook](#detalle-de-cada-webhook)
6. [Manejo de errores (error-handler)](#manejo-de-errores-error-handler)
7. [Reglas para quien envía eventos (Backend)](#reglas-para-quien-envía-eventos-backend)
8. [Importar y exportar workflows](#importar-y-exportar-workflows)
9. [Solución de problemas](#solución-de-problemas)
10. [Pendientes](#pendientes)

---

## Levantar n8n

1. Copiar `n8n/.env.example` a `n8n/.env` (el `.env` **nunca** se sube a Git).
2. `cd n8n`
3. `docker compose up -d`
4. Abrir http://localhost:5678 e iniciar sesión (la primera vez n8n pide crear la cuenta de administrador).

Para apagarlo: `docker compose down` (los workflows y datos se conservan en el volumen de Docker).

---

## Workflows disponibles

Todos están en `n8n/workflows/`. Los de notificación se llaman por **POST** con `Content-Type: application/json`.

| Workflow (archivo `.json`) | Caso de uso | Cuándo lo envía Django | A quién va dirigido el aviso | Path del webhook |
|---|---|---|---|---|
| `ticket-created` | Primera entrega | Se crea un ticket | Equipo | `ticket-created` |
| `technician-assigned` | CU-43 | Se asigna un técnico al ticket | Técnico | `technician-assigned` |
| `technician-started` | CU-44 (CU-08) | El técnico inicia el desplazamiento (va en camino) | Cliente | `technician-started` |
| `technician-nearby` | CU-45 (CU-09) | El técnico está cerca del domicilio | Cliente | `technician-nearby` |
| `ticket-resolved` | CU-46 | El ticket se resuelve / cierra | Cliente | `ticket-resolved` |
| `customer-survey` | CU-47 (CU-11) | Se pide la encuesta de satisfacción tras cerrar el ticket | Cliente | `customer-survey` |
| `ticket-escalation` | CU-48 | Django escala un ticket (estancado, no resuelto, sin técnico, etc.) | Supervisor | `ticket-escalation` |
| `error-handler` | Transversal | **No lo llama Django:** se ejecuta solo cuando falla otro workflow | Equipo | — (no tiene webhook) |

> Por ahora el "aviso" es el campo `mensaje` que n8n genera y devuelve en la respuesta.
> Cuando el equipo defina el canal real (correo, etc.) se agregará un nodo de envío al final de cada workflow.

---

## Cómo funciona un workflow

Los workflows de notificación comparten la misma estructura de 3 nodos:

```
Webhook (POST)  ->  Edit Fields  ->  Respond to Webhook
```

1. **Webhook:** recibe el JSON del evento en `/webhook/<path>`.
2. **Edit Fields:** crea dos campos:
   - `evento`: nombre fijo del evento (por ejemplo `technician_assigned`).
   - `mensaje`: texto armado con los datos recibidos (`$json.body.<campo>`).
3. **Respond to Webhook:** devuelve ese resultado a quien llamó (Django).

Dos workflows tienen un nodo **If** extra para decidir qué hacer según los datos:

**`technician-nearby`** — valida que venga `minutos`:

```
Webhook -> If (¿viene "minutos"?) --sí--> Edit Fields -> Respond to Webhook (200)
                                  --no--> Respond to Webhook (400)
```

Así no se genera un aviso de "técnico cerca" sin tiempo estimado.

**`ticket-escalation`** — elige el texto según el nivel de escalamiento:

```
Webhook -> If (nivel >= 2) --sí--> Edit Fields (mensaje URGENTE)     -> Respond to Webhook
                           --no--> Edit Fields (mensaje ESCALAMIENTO) -> Respond to Webhook
```

**`error-handler`** — no usa webhook, ver [Manejo de errores](#manejo-de-errores-error-handler).

### Respuesta que recibe quien llama

- **Éxito (HTTP 200):** el JSON con `evento` y `mensaje`. Ejemplo:

```json
{
  "evento": "technician_assigned",
  "mensaje": "Ticket #1 asignado a Juan Perez para Cliente Prueba"
}
```

- **Error (HTTP 400, solo `technician-nearby`):** si no se envía `minutos`.

```json
{
  "ok": false,
  "error": "minutos requerido"
}
```

---

## Cómo llamar a un webhook

Hay dos URLs por cada workflow:

| Tipo | URL | Para qué sirve |
|---|---|---|
| **Producción** | `http://localhost:5678/webhook/<path>` | La que debe usar Django. Requiere el workflow **publicado/activo**. |
| **Test** | `http://localhost:5678/webhook-test/<path>` | Solo para probar desde el editor de n8n. Hay que pulsar *Execute workflow* justo antes y sirve para **una sola** llamada. |

Si Django corre dentro de Docker, `localhost` apunta al propio contenedor: usar `http://host.docker.internal:5678/webhook/<path>`.

### Ejemplo en PowerShell

```powershell
$body = '{"ticket_id":1,"cliente":"Cliente Prueba","tecnico":"Juan Perez"}'
Invoke-RestMethod -Method Post -ContentType "application/json" `
  -Uri "http://localhost:5678/webhook/technician-assigned" -Body $body
```

### Ejemplo con curl

```bash
curl -X POST http://localhost:5678/webhook/technician-assigned \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":1,"cliente":"Cliente Prueba","tecnico":"Juan Perez"}'
```

### Ejemplo desde Python (Django)

```python
import requests

requests.post(
    "http://localhost:5678/webhook/technician-assigned",
    json={"ticket_id": 1, "cliente": "Cliente Prueba", "tecnico": "Juan Perez"},
    timeout=5,
)
```

---

## Detalle de cada webhook

### ticket-created

- **Path:** `/webhook/ticket-created`
- **Evento:** `ticket_created`
- **Campos:** `ticket_id`, `cliente`, `tipo`, `prioridad`
- **Mensaje generado:** `Ticket #{ticket_id} de {cliente}: {tipo} ({prioridad})`

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "tipo": "Sin internet", "prioridad": "ALTA" }
```

Resultado: `Ticket #1 de Cliente Prueba: Sin internet (ALTA)`

### technician-assigned (CU-43)

- **Path:** `/webhook/technician-assigned`
- **Evento:** `technician_assigned`
- **Campos:** `ticket_id`, `cliente`, `tecnico`
- **Mensaje generado:** `Ticket #{ticket_id} asignado a {tecnico} para {cliente}`

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "tecnico": "Juan Perez" }
```

Resultado: `Ticket #1 asignado a Juan Perez para Cliente Prueba`

### technician-started (CU-44 / CU-08)

- **Path:** `/webhook/technician-started`
- **Evento:** `technician_started`
- **Cuándo:** el técnico pulsa "iniciar desplazamiento" (el ticket pasa a `EN_CAMINO`).
- **Campos:** `ticket_id`, `cliente`, `tecnico`
- **Mensaje generado:** `El técnico {tecnico} va en camino a su domicilio (ticket #{ticket_id})`

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "tecnico": "Juan Perez" }
```

Resultado: `El técnico Juan Perez va en camino a su domicilio (ticket #1)`

### technician-nearby (CU-45 / CU-09)

- **Path:** `/webhook/technician-nearby`
- **Evento:** `technician_nearby`
- **Campos:** `ticket_id`, `cliente`, `tecnico`, `minutos`
- **Mensaje generado:** `Técnico {tecnico} llega en ~{minutos} min (ticket {ticket_id})`
- **Importante:** quien calcula la cercanía y los minutos es el Backend / módulo de algoritmos. n8n solo recibe el valor ya calculado.
- Si **no** llega `minutos`, responde **HTTP 400** y no genera aviso.

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "tecnico": "Juan Perez", "minutos": 10 }
```

Resultado: `Técnico Juan Perez llega en ~10 min (ticket 1)`

### ticket-resolved (CU-46)

- **Path:** `/webhook/ticket-resolved`
- **Evento:** `ticket_resolved`
- **Campos:** `ticket_id`, `cliente`, `tecnico`
- **Mensaje generado:** `Ticket #{ticket_id} cerrado por {tecnico}. Gracias, {cliente}.`

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "tecnico": "Juan Perez" }
```

Resultado: `Ticket #1 cerrado por Juan Perez. Gracias, Cliente Prueba.`

### customer-survey (CU-47 / CU-11)

- **Path:** `/webhook/customer-survey`
- **Evento:** `customer_survey`
- **Cuándo:** el ticket se cierra y corresponde pedir la evaluación de la atención.
- **Campos:** `ticket_id`, `cliente`, `enlace_encuesta`
- **Mensaje generado:** `Evalúe su atención (ticket #{ticket_id}): {enlace_encuesta}`
- **Importante:** la encuesta en sí (formulario y guardado de respuestas) la implementan Frontend/Backend. n8n solo envía el aviso con el enlace.

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "enlace_encuesta": "http://localhost:3000/encuesta/1" }
```

Resultado: `Evalúe su atención (ticket #1): http://localhost:3000/encuesta/1`

### ticket-escalation (CU-48)

- **Path:** `/webhook/ticket-escalation`
- **Evento:** `ticket_escalation`
- **Campos:** `ticket_id`, `cliente`, `prioridad`, `nivel` (número), `motivo`
- **Cuándo:** **Django decide cuándo escalar** (tiempo sin atención, incidencia no resuelta, sin técnico disponible, error de procesamiento, etc.), registra el escalamiento y llama a este webhook con el `nivel` ya calculado. n8n no mide tiempos ni espera: solo avisa.
- **Mensaje generado** (dos líneas, el texto cambia según `nivel`):
  - `nivel` **2 o más** → `URGENTE nivel {nivel}: ticket #{ticket_id} ({prioridad})`
  - `nivel` **menor a 2** → `ESCALAMIENTO nivel {nivel}: ticket #{ticket_id} ({prioridad})`
  - Segunda línea (en ambos casos): `Cliente: {cliente}. Motivo: {motivo}`

```json
{ "ticket_id": 1, "cliente": "Cliente Prueba", "prioridad": "ALTA", "nivel": 2, "motivo": "Sin atencion en 2 horas" }
```

Resultado:

```
URGENTE nivel 2: ticket #1 (ALTA)
Cliente: Cliente Prueba. Motivo: Sin atencion en 2 horas
```

Con `"nivel": 1` el resultado empieza con `ESCALAMIENTO nivel 1: ...`.

Un solo webhook sirve para todos los motivos de escalamiento; lo que cambia es el campo `motivo`:

| Caso | Cuándo | Ejemplo de `motivo` |
|---|---|---|
| CU-48 | Ticket estancado | `Sin atencion en 2 horas` |
| CU-41 | No hay técnico válido para asignar | `Sin tecnico disponible` |
| CU-28 | Incidencia no resuelta | `Visita sin solucion` |
| CU-40 | Error al procesar el diagnóstico | `Error de procesamiento` |

> Las reglas de escalamiento (tiempos, niveles, a quién) las define el equipo; el umbral de "URGENTE" (`nivel >= 2`) es ajustable en el nodo If.

### Resumen del contrato de eventos

| Path | Campos obligatorios |
|---|---|
| `ticket-created` | `ticket_id`, `cliente`, `tipo`, `prioridad` |
| `technician-assigned` | `ticket_id`, `cliente`, `tecnico` |
| `technician-started` | `ticket_id`, `cliente`, `tecnico` |
| `technician-nearby` | `ticket_id`, `cliente`, `tecnico`, `minutos` |
| `ticket-resolved` | `ticket_id`, `cliente`, `tecnico` |
| `customer-survey` | `ticket_id`, `cliente`, `enlace_encuesta` |
| `ticket-escalation` | `ticket_id`, `cliente`, `prioridad`, `nivel`, `motivo` |

---

## Manejo de errores (error-handler)

`error-handler` es un workflow que **n8n ejecuta automáticamente cuando otro workflow falla**. No tiene webhook y Django no lo llama.

```
Error Trigger  ->  Edit Fields
```

- **Error Trigger:** se dispara con la información del workflow que falló.
- **Edit Fields:** arma tres campos:
  - `evento`: `workflow_error`
  - `mensaje`: `Falló el workflow {nombre del workflow}: {mensaje de error}`
  - `url`: enlace a la ejecución fallida en n8n

**Cómo está conectado:** los otros 7 workflows tienen configurado *Settings > Error workflow = error-handler*. Si uno de ellos falla, aparece una ejecución nueva en `error-handler`.

**Dónde ver los errores:** en n8n, abrir `error-handler` > pestaña **Executions**. Por ahora los errores solo quedan registrados ahí; cuando el equipo defina un canal (correo, etc.) se agregará un nodo para avisar.

**Cómo probarlo**

1. En un workflow de prueba, agregar al final un nodo **Stop and Error** (mensaje, por ejemplo, "prueba de error") y publicarlo.
2. Llamar a la URL de **producción** del webhook. El Error Trigger **no** se activa con ejecuciones manuales del editor ni con la URL de test.
3. Revisar *Executions* en `error-handler`.
4. Quitar el nodo de prueba y publicar de nuevo.

**Reintentos:** los workflows actuales no llaman a servicios externos (solo reciben y responden), así que no tienen reintentos. Cuando se agregue un nodo de envío (correo, HTTP), activar en ese nodo *Settings > Retry On Fail* con **Max Tries = 3** y **Wait Between Tries = 2000 ms**.

---

## Reglas para quien envía eventos (Backend)

- Usar siempre la URL de **producción** (`/webhook/...`), nunca `/webhook-test/...`.
- Enviar `Content-Type: application/json`. Sin esa cabecera los campos llegan vacíos.
- Enviar **todos** los campos de la tabla en cada evento. n8n no valida: si falta uno, el mensaje sale con un hueco (la única excepción controlada es `minutos`, que devuelve 400).
- `minutos` y `nivel` deben enviarse como **número** (`10`, `2`), no como texto.
- No bloquear la operación principal esperando a n8n: llamar con un `timeout` corto y no hacer fallar la creación/asignación/cierre del ticket si n8n no responde.
- Si se cambia el nombre de un campo, hay que acordarlo con el Integrante 4 (n8n) antes: se actualizan el workflow, el `.json` exportado y este README.

---

## Importar y exportar workflows

**Importar un workflow existente**

1. En n8n: *Workflows > Import from file*.
2. Elegir el `.json` de `n8n/workflows/`.
3. Revisar el nodo Webhook (Path) y pulsar **Publish** para que funcione la URL de producción.
4. Si se importan todos en una instancia nueva, importar primero `error-handler` y luego asignarlo en *Settings > Error workflow* de cada uno (el ID que guarda el `.json` es el de la instancia donde se exportó).

**Actualizar un workflow después de cambiarlo**

1. Guardar y **publicar de nuevo** en n8n (si no, la URL de producción sigue con la versión vieja).
2. Menú ⋯ > *Download* y guardar el archivo en `n8n/workflows/<nombre>.json` (UTF-8).
3. Revisar que el archivo no contenga secretos (`password`, `token`, `apiKey`).
4. Subir solo la carpeta de n8n: `git add n8n/` (nunca `git add .`).

---

## Solución de problemas

| Síntoma | Causa probable y solución |
|---|---|
| 404 "not registered" en `webhook-test` | No se pulsó *Execute workflow* justo antes, o ya se usó la única llamada. Pulsarlo otra vez. |
| 404 en `/webhook/...` | El workflow no está publicado o el path/método no coinciden. Publicar de nuevo. |
| Error al publicar | Dos workflows con el mismo Path y método. Cambiar el Path del Webhook. |
| El mensaje sale con campos vacíos | Falta enviar `Content-Type: application/json` o falta algún campo del evento. |
| Producción devuelve el mensaje viejo | Se guardó pero no se publicó. Pulsar *Publish* otra vez. |
| `technician-nearby` responde 400 | No se envió `minutos`. Es el comportamiento esperado. |
| `ticket-escalation` siempre sale "ESCALAMIENTO" | `nivel` no llegó o no es un número. Revisar el JSON enviado. |
| `error-handler` no registra nada | Solo funciona con ejecuciones automáticas (URL de producción) y si el workflow que falla tiene asignado *Error workflow*. |
| n8n no abre en el navegador | Verificar con `docker ps` que el contenedor esté en ejecución y revisar `docker logs`. |

---

## Pendientes

- **Canal de notificación real** (correo u otro): hoy el aviso es solo el campo `mensaje` de la respuesta. Cuando el equipo decida el canal, agregar un nodo de envío al final de cada workflow y activar reintentos en él.
- **Destinatario del aviso:** definir si Django enviará un campo con el correo/teléfono del destinatario (por ejemplo `email_destino`) para cada evento.
- **Reglas de escalamiento:** confirmar con el equipo tiempos, niveles y supervisor para ajustar el umbral del nodo If en `ticket-escalation`.
- **Momento de cierre:** acordar con Backend si `ticket-resolved` y `customer-survey` se envían al pasar a RESUELTO o a CERRADO.

Al agregar un workflow nuevo, actualizar las tablas de este README (*Workflows disponibles*, *Detalle de cada webhook* y *Resumen del contrato de eventos*).
