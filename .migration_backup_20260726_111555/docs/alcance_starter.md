# Alcance del starter

Este documento define el alcance funcional del starter: qué incluye, qué
no, y cuál es su estado inicial. Las **reglas de negocio** se documentan
aparte, en `docs/reglas.md` (fuente única de verdad); acá solo se
referencian.

## Objetivo

El starter permite estudiar arquitectura, trazabilidad y una condición de
carrera (RET-001) antes de resolverla, en el dominio de un complejo de
salas para eventos.

## Endpoints

- `GET /health`
- `GET /events`
- `GET /events/{event_id}`
- `GET /events/{event_id}/seats`
- `POST /events/{event_id}/holds`
- `POST /holds/{hold_id}/confirm`

## Regla principal

La regla central es **RET-001**. Su enunciado, su ubicación en el código
y su estado de garantía por semana están documentados en
`docs/reglas.md`. No se repite acá para evitar dos fuentes de verdad.

## Estado inicial y evolución

- **Semana 1:** RET-001 expresada pero no garantizada ante concurrencia.
  El flujo hace: consulta de disponibilidad → (demora didáctica
  configurable) → inserción. Sin restricción única, sin bloqueo, sin
  operación atómica, sin manejo de conflicto a nivel de base. Ver
  `docs/adr/ADR-001.md`.
- **Semana 2:** dominio, contrato y arquitectura. Se introduce el
  puerto/adaptador entre Application e Infrastructure (ver
  `docs/adr/ADR-002.md`) y los tests de arquitectura. La garantía de
  RET-001 no cambia todavía.
- **Semana 3:** garantía real de concurrencia a nivel de PostgreSQL.

## Pruebas

- La suite normal debe quedar en verde: `pytest`.
- La prueba `race_demo` se ejecuta por separado y demuestra el defecto de
  concurrencia pendiente: `pytest -m race_demo`.

## Alcance excluido

- frontend (se integra desde otra unidad);
- autenticación real;
- pagos;
- Redis;
- WebSockets;
- microservicios.

Estos temas se discuten como alternativas de evolución en la Semana 4,
sin necesidad de implementarlos todos.
