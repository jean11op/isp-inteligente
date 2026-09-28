# ISP Inteligente

Sistema inteligente para la gestión y atención de incidencias de un proveedor
de servicios de Internet (ISP).

## Descripción

La plataforma permite gestionar el ciclo completo de atención de una incidencia:

1. Reporte del problema por parte del cliente.
2. Recopilación inicial de información.
3. Contacto con un especialista.
4. Diagnóstico de la incidencia.
5. Asignación inteligente de un técnico.
6. Cálculo de rutas mediante algoritmos de búsqueda.
7. Seguimiento del técnico.
8. Atención en domicilio.
9. Resolución o escalamiento de la incidencia.
10. Cierre y evaluación del servicio.

## Tecnologías

- Python
- Django
- Django REST Framework
- PostgreSQL
- React
- TypeScript
- n8n
- Docker
- Git / GitHub

## Arquitectura

```text
Cliente / Técnico / Especialista
              │
              ▼
           React
              │
              ▼
      Django REST API
         │       │
         │       ├──────── PostgreSQL
         │
         ├──────── Python / Algoritmos
         │
         └──────── n8n

### Estructura

backend/        → Backend Django y API REST
frontend/       → Aplicación React
algorithms/     → Algoritmos Python y grafos
n8n/            → Workflows de automatización
docs/           → Documentación
tests/          → Pruebas


### ¿Qué estamos haciendo?

Estamos creando la **carta de presentación técnica del proyecto**.

Más adelante este README crecerá con:

- Requisitos.
- Instalación.
- Configuración del `.env`.
- Docker.
- Cómo ejecutar Django.
- Cómo ejecutar React.
- Cómo ejecutar n8n.
- Convenciones de Git.
- Arquitectura.
- Guía para nuevos integrantes.

Pero **no vamos a escribir todo ahora**. Lo iremos completando conforme construyamos el sistema.

Cuando lo hayas guardado, pasamos al **primer commit y conexión con GitHub**.