# Trazabilidad

Este documento no define reglas ni arquitectura. Solo conecta identificadores
normativos con código, pruebas, endpoints y decisiones.

## Reglas de negocio

| ID | Implementación | Caso de uso | Exposición | Pruebas |
|---|---|---|---|---|
| RET-001 | `app/core/rules.py` | `app/application/use_cases.py::crear_retencion` | `POST /events/{event_id}/holds` → `409` | `tests/test_rules.py`, `tests/test_events.py`, `tests/test_race_demo.py` |

## Restricciones de arquitectura

| ID | Verificación automática |
|---|---|
| ARQ-002 | `tests/test_arquitectura.py::test_arq_002_core_independiente` |
| ARQ-003 | `tests/test_arquitectura.py::test_arq_003_application_no_importa_infrastructure` |
| ARQ-006, ARQ-007 | `tests/test_arquitectura.py::test_arq_006_core_no_conoce_puertos` |

## Decisiones

| ADR | Relación |
|---|---|
| `ADR-001` | Estado de garantía concurrente de RET-001 |
| `ADR-002` | ARQ-003 y ARQ-007 |
