# Trazabilidad de reglas y decisiones

Este documento conecta cada regla o decisión de arquitectura con el
lugar exacto donde vive en el código y donde se verifica. Su objetivo es
que una regla no quede "declarada en prosa" sin anclaje real: si algo
está en esta tabla, se puede ir a buscar y auditar.

La distribución de responsabilidades general es:

- **Core** expresa la regla (función pura, sin I/O).
- **Application** coordina el caso de uso que la aplica.
- **Infrastructure** aporta persistencia y, en etapas posteriores, las
  garantías técnicas (restricciones, transacciones, bloqueos).
- **API** traduce el resultado a una respuesta HTTP.

## Reglas de negocio

| Regla   | Se declara en          | Se aplica en (caso de uso)        | Se expone como | Se verifica en                                   | Estado de la garantía |
|---------|------------------------|-----------------------------------|----------------|--------------------------------------------------|-----------------------|
| RET-001 | `app/core/rules.py`    | `app/application/use_cases.py` (`crear_retencion`) | `409` en `POST /events/{event_id}/holds` | `tests/test_rules.py` (unitario) · `tests/test_events.py` (HTTP) · `tests/test_race_demo.py` (concurrencia, falla a propósito) | Parcial hasta Semana 3 |

## Decisiones de arquitectura (ADR)

| Decisión | Documento               | Se verifica en                                            | Estado    |
|----------|-------------------------|-----------------------------------------------------------|-----------|
| Concurrencia de RET-001 sin resolver en Semana 1 | `docs/adr/ADR-001.md` | `tests/test_race_demo.py` | Vigente (se resuelve en Semana 3) |
| Puerto/adaptador entre Application e Infrastructure | `docs/adr/ADR-002.md` | `tests/test_arquitectura.py` | Resuelta en Semana 2 |

## Invariantes de arquitectura (verificadas por código)

| Invariante | Se verifica en |
|------------|----------------|
| `app/core` no importa frameworks ni infraestructura | `tests/test_arquitectura.py::test_core_no_importa_nada_externo` |
| `app/application` no importa infraestructura concreta (usa el puerto) | `tests/test_arquitectura.py::test_application_no_importa_infrastructure_concreta` |
| `app/core` no conoce el puerto (no hace I/O ni vía interfaz) | `tests/test_arquitectura.py::test_core_no_conoce_el_puerto` |
