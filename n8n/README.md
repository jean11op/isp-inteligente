# n8n - Automatizaciones ISP Inteligente

## Levantar n8n
1. Copiar n8n/.env.example a n8n/.env
2. cd n8n
3. docker compose up -d
4. Abrir http://localhost:5678

## Workflows (carpeta workflows/)
- ticket-created.json: recibe el evento "ticket creado" desde Django

## Webhooks
- Test: POST http://localhost:5678/webhook-test/ticket-created
- Produccion: POST http://localhost:5678/webhook/ticket-created

## Formato del evento
- Content-Type: application/json
- Cuerpo minimo: ticket_id, cliente, tipo, prioridad

## Importar un workflow
Workflows > Import from file > elegir el .json de workflows/
