# Trazabilidad

Este documento no vuelve a explicar las decisiones. Conecta cada identificador
con el código, la API y la evidencia que lo verifica.

`RET-002` se conserva como identificador porque ya está referenciado por el
proyecto, aunque en `reglas.md` se aclara que funciona como definición de
"butaca ocupada" asociada a `RET-001`.

## Reglas de negocio

| ID | Implementación | Caso de uso | Exposición | Verificación |
|---|---|---|---|---|
| RET-001 (validación) | `app/core/rules.py` | `use_cases.crear_retencion` | `POST /events/{event_id}/holds` → `409 SEAT_UNAVAILABLE` | `tests/test_rules.py`, `tests/test_events.py` |
| RET-001 (garantía) | restricción de unicidad en el esquema + adaptador que traduce errores (`alembic/versions/0001_add_holds_unique.py`, `app/infrastructure/repository.py`) | — | idem | `tests/test_garantia_ret001.py` |
| RET-002 | `app/core/rules.py` + restricción del esquema | `use_cases.crear_retencion` | idem | `tests/test_rules.py`, `tests/test_garantia_ret001.py` |
| RET-003 | `app/core/rules.py` | `use_cases.confirmar_retencion` | `POST /holds/{hold_id}/confirm` → `409 INVALID_HOLD_STATE` | `tests/test_rules.py` |

`RET-001` aparece dos veces a propósito: el core realiza una validación previa y
la base aplica una restricción frente a escrituras concurrentes. Son dos
protecciones de la misma regla y se verifican de manera distinta. Ver `ARQ-009`.

## Restricciones de arquitectura

| ID | Verificación automática |
|---|---|
| ARQ-001 | revisión humana |
| ARQ-002 | `tests/test_arquitectura.py::test_arq_002_core_independiente` |
| ARQ-003 | `tests/test_arquitectura.py::test_arq_003_application_no_importa_infrastructure` |
| ARQ-004 | revisión humana |
| ARQ-005 | revisión humana |
| ARQ-006, ARQ-007 | `tests/test_arquitectura.py::test_arq_006_core_no_conoce_puertos` |
| ARQ-008 | `tests/test_arquitectura.py::test_arq_008_persistencia_estanca` |
| ARQ-009 | revisión humana |

## Contrato de la API

| Elemento | Definición | Verificación |
|---|---|---|
| Rutas y códigos HTTP | `docs/contrato/contrato_api.md` | `herramientas/evaluar_semana3.py` (contra `/openapi.json`) |
| Códigos de error | `docs/contrato/contrato_api.md` | `tests/test_events.py` |

## Documentación derivada

| Documento | Generador | Verificación |
|---|---|---|
| `docs/diagramas/estados_retencion.md` | `herramientas/generar_diagrama_estados.py` | `tests/test_diagrama_sincronizado.py` |

## Decisiones

| ADR | Relación |
|---|---|
| `ADR-001` | Estado de garantía concurrente de RET-001 |
| `ADR-002` | ARQ-003 y ARQ-007 |
| `ADR-003` | RET-001 (garantía), RET-002, ARQ-008, adopción de Alembic |
