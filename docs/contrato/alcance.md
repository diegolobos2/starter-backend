# Alcance del starter — Semana 2

## Objetivo

Disponer de un backend mínimo para estudiar separación de responsabilidades,
puertos y adaptadores, reglas de negocio y verificación automática.

## Funcionalidad incluida

- consultar el estado de salud;
- listar y consultar eventos;
- listar butacas de un evento;
- crear una retención;
- confirmar una retención.

## Endpoints incluidos

- `GET /health`
- `GET /events`
- `GET /events/{event_id}`
- `GET /events/{event_id}/seats`
- `POST /events/{event_id}/holds`
- `POST /holds/{hold_id}/confirm`

## Contratos aplicables

- Regla `RET-001`, definida en `docs/contrato/reglas.md`.
- Restricciones `ARQ-001` a `ARQ-007`, definidas en
  `docs/contrato/arquitectura.md`.

## Fuera de alcance

- autenticación;
- pagos;
- Redis;
- WebSockets;
- microservicios;
- liberación automática de retenciones;
- integración con frontend.

La evolución temporal y las tareas pendientes se registran únicamente en
`TODO.md`.
