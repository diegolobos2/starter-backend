# Reglas de negocio

Este documento es la **única fuente de verdad** sobre las reglas de
negocio del dominio. Cualquier otra referencia (código, tests,
diagramas, contrato OpenAPI) debe mantenerse coherente con lo que se
declara acá. La trazabilidad regla → código → test se lleva en
`docs/trazabilidad_reglas.md`.

## Reglas vigentes

### RET-001 — Unicidad de retención activa

> Una butaca no puede tener dos retenciones activas para el mismo evento.

- **Tipo:** invariante del dominio.
- **Dónde se declara:** `app/core/rules.py` (`puede_crear_retencion`,
  `validar_creacion_retencion`), como función pura sin I/O.
- **Cómo se expone:** al violarse, la API responde `409 Conflict`.
- **Garantía bajo concurrencia:** *parcial* en el estado actual. La
  regla se evalúa correctamente en el camino feliz, pero bajo dos
  peticiones concurrentes puede violarse (ver más abajo). La garantía
  definitiva se agrega en la Semana 3, a nivel de infraestructura.

## Validaciones que NO son reglas de negocio

Conviene distinguir una **regla de negocio** (una decisión del dominio,
como RET-001) de una **validación de existencia** (un chequeo de
integridad referencial). Estas últimas viven en `app/application` como
simples comprobaciones, no en el core:

- Evento inexistente → `404`.
- Butaca inexistente o que no pertenece al evento → `404`.
- Retención inexistente al confirmar → `404`.

No son reglas de dominio: no hay una decisión de negocio detrás, solo
"¿esto que me pediste existe?".

## Estado de la garantía de RET-001 por semana

- **Semana 1:** RET-001 expresada en el core, pero *no garantizada*
  ante concurrencia. La condición de carrera queda deliberadamente sin
  resolver (ver `docs/adr/ADR-001.md`). La prueba `race_demo` la
  demuestra y falla a propósito.
- **Semana 2:** no cambia la garantía de RET-001. El foco es dominio,
  contrato y arquitectura (puerto/adaptador, tests de arquitectura).
- **Semana 3:** se agrega la garantía real a nivel de PostgreSQL
  (restricción única y/o transacción con bloqueo) y se traduce el
  conflicto a `409`.

## Reglas mencionadas en el caso de negocio, aún no implementadas

El caso de negocio (complejo de salas para eventos) menciona márgenes de
montaje/limpieza de 30 minutos antes y después de cada evento. Esa regla
**todavía no está implementada** en el código. Queda como candidata para
ampliar el dominio en semanas posteriores, si se decide crecer el
alcance más allá de RET-001.
