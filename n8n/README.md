# n8n - Automatizaciones ISP Inteligente

Esta carpeta contiene los workflows de n8n del proyecto. **n8n no reemplaza al backend ni tiene la lógica de negocio.**
Solo recibe eventos (webhooks) que envía Django y devuelve/genera el mensaje de notificación.
Quien decide *cuándo* pasa algo (asignar técnico, técnico cerca, cierre, etc.) es el backend o el módulo de algoritmos.

## Índice

1. [Levantar n8n](#levantar-n8n)
2. [Workflows disponibles](#workflows-disponibles)
3. [Cómo funciona un workflow](#cómo-funciona-un-workflow)
4. [Cómo llamar a un webhook](#cómo-llamar-a-un-webhook)
5. [Detalle de cada webhook](#detalle-de-cada-webhook)
6. [Reglas para quien envía eventos (Backend)](#reglas-para-quien-envía-eventos-backend)
7. [Importar y exportar workflows](#importar-y-exportar-workflows)
8. [Solución de problemas](#solución-de-problemas)
9. [Pendientes](#pendientes)

---

## Levantar n8n

1. Copiar `n8n/.env.example` a `n8n/.env` (el `.env` **nunca** se sube a Git).
2. `cd n8n`
3. `docker compose up -d`
4. Abrir http://localhost:5678 e iniciar sesión (la primera vez n8n pide crear la cuenta de administrador).

Para apagarlo: `docker compose down` (los workflows y datos se conservan en el volumen de Docker).

---

## Workflows disponibles

Todos están en `n8n/workflows/` y se llaman por **POST** con `Content-Type: application/json`.

| Workflow (archivo `.json`) | Caso de uso | Cuándo lo envía Django | A quién va dirigido el aviso | Path del webhook |
|---|---|---|---|---|
| `ticket-created` | Primera entrega | Se crea un ticket | Equipo | `ticket-created` |
| `technician-assigned` | CU-43 | Se asigna un técnico al ticket | Técnico | `technician-assigned` |
| `technician-started` | CU-44 (CU-08) | El técnico inicia el desplazamiento (va en camino) | Cliente | `technician-started` |
| `technician-nearby` | CU-45 (CU-09) | El técnico está cerca del domicilio | Cliente | `technician-nearby` |
| `ticket-resolved` | CU-46 | El ticket se resuelve / cierra | Cliente | `ticket-resolved` |

> Por ahora el "aviso" es el campo `mensaje` que n8n genera y devuelve en la respuesta.
> Cuando el equipo defina el canal real (correo, etc.) se agregará un nodo de envío al final de cada workflow.

---

## Cómo funciona un workflow

Todos los workflows tienen la misma estructura de 3 nodos:

```
Webhook (POST)  ->  Edit Fields  ->  Respond to Webhook
```

1. **Webhook:** recibe el JSON del evento en `/webhook/<path>`.
2. **Edit Fields:** crea dos campos:
   - `evento`: nombre fijo del evento (por ejemplo `technician_assigned`).
   - `mensaje`: texto armado con los datos recibidos (`$json.body.<campo>`).
3. **Respond to Webhook:** devuelve ese resultado a quien llamó (Django).

`technician-nearby` tiene un nodo extra **If** antes de armar el mensaje:

```
Webhook -> If (¿viene "minutos"?) --sí--> Edit Fields -> Respond to Webhook (200)
                                  --no--> Respond to Webhook (400)
```

Así no se genera un aviso de "técnico cerca" sin tiempo estimado.

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

### Resumen del contrato de eventos

| Path | Campos obligatorios |
|---|---|
| `ticket-created` | `ticket_id`, `cliente`, `tipo`, `prioridad` |
| `technician-assigned` | `ticket_id`, `cliente`, `tecnico` |
| `technician-started` | `ticket_id`, `cliente`, `tecnico` |
| `technician-nearby` | `ticket_id`, `cliente`, `tecnico`, `minutos` |
| `ticket-resolved` | `ticket_id`, `cliente`, `tecnico` |

---

## Reglas para quien envía eventos (Backend)

- Usar siempre la URL de **producción** (`/webhook/...`), nunca `/webhook-test/...`.
- Enviar `Content-Type: application/json`. Sin esa cabecera los campos llegan vacíos.
- Enviar **todos** los campos de la tabla en cada evento. n8n no valida: si falta uno, el mensaje sale con un hueco (la única excepción controlada es `minutos`).
- No bloquear la operación principal esperando a n8n: llamar con un `timeout` corto y no hacer fallar la creación/asignación del ticket si n8n no responde.
- Si se cambia el nombre de un campo, hay que acordarlo con el Integrante 4 (n8n) antes: se actualizan el workflow, el `.json` exportado y este README.

---

## Importar y exportar workflows

**Importar un workflow existente**

1. En n8n: *Workflows > Import from file*.
2. Elegir el `.json` de `n8n/workflows/`.
3. Revisar el nodo Webhook (Path) y pulsar **Publish** para que funcione la URL de producción.

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
| n8n no abre en el navegador | Verificar con `docker ps` que el contenedor esté en ejecución y revisar `docker logs`. |

---

## Pendientes

Workflows aún por construir (según el reparto de tareas del equipo):

- `customer-survey` (CU-47): enviar el enlace de la encuesta de satisfacción.
- `ticket-escalation` (CU-48): avisar al supervisor cuando un ticket se escala (las reglas de escalamiento las define el equipo).
- `error-handler` + reintentos: registrar fallos de los workflows y reintentar nodos externos.
- Canal de notificación real (correo u otro) cuando el equipo lo decida.

Al agregar un workflow nuevo, actualizar las tablas de este README (*Workflows disponibles*, *Detalle de cada webhook* y *Resumen del contrato de eventos*).
