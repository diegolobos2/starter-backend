# TODO — estado del proyecto por semana

Archivo de seguimiento de lo hecho y lo pendiente. Se actualiza a medida
que avanzan las semanas. La idea es que cualquiera (docente, cursante, o
un agente) pueda leer acá en qué punto está el proyecto sin reconstruirlo
del historial.

## Semana 1 — Arquitectura y gobernanza (entregada)

- [x] Estructura en capas (api / application / core / infrastructure).
- [x] AGENTS.md (constitución arquitectónica, 12 reglas).
- [x] Documentación base (arquitectura, reglas, trazabilidad, alcance).
- [x] ADR-001 (concurrencia deliberadamente sin resolver).
- [x] RET-001 como función pura en `app/core/rules.py`.
- [x] Docker Compose (API + PostgreSQL).
- [x] Suite de tests contra SQLite; `race_demo` que falla a propósito.

## Semana 2 — Dominio, arquitectura y contrato (en curso)

- [x] Puerto `HoldRepository` (`app/application/ports.py`).
- [x] Adaptador `SqlAlchemyHoldRepository` (`app/infrastructure/repository.py`).
- [x] `use_cases.py` refactorizado para recibir el puerto inyectado.
- [x] Inyección del adaptador desde `app/api/routes.py`.
- [x] Tests de arquitectura (`tests/test_arquitectura.py`): core limpio,
      application sin fuga, core sin conocer el puerto.
- [x] ADR-002 (puerto/adaptador, con razonamiento YAGNI/trade-off).
- [x] Docs consolidados sin duplicación (reglas, trazabilidad).
- [x] Apartado teórico core vs application (`docs/frontera_core_application.md`).
- [x] Diagrama de estados derivado del código (`docs/diagrama_estados.md`).
- [ ] Subir el repositorio a GitHub (ver `docs/github_setup.md`).
- [ ] Correr la suite localmente y confirmar verde antes de grabar
      (`pytest -v` y `pytest -m race_demo -v`).
- [ ] (Opcional) Paginación en `GET /events` — decidir si entra o se
      pospone. Si entra, hacerlo ANTES de congelar el contrato.
- [ ] Congelar el contrato OpenAPI al cierre de la semana (forma
      estable de request/response; los errores 404/409/422 ya
      contemplados).

## Semana 3 — Concurrencia real (pendiente)

- [ ] Restricción única parcial en PostgreSQL para RET-001.
- [ ] Capturar el error de integridad y traducirlo a `409` sin filtrar
      detalles de infraestructura hacia application.
- [ ] Segunda suite de integración contra PostgreSQL real (no solo SQLite).
- [ ] Hacer que `race_demo` deje de fallar (o convertirlo en prueba de
      que la concurrencia ahora se rechaza correctamente).
- [ ] (Coordinación) Frontend integra contra la API real — según lo
      acordado, esto se movió a Semana 4.

## Semana 4 — Integración y evolución (pendiente)

- [ ] Integración real con Frontend (reemplaza los mocks): reemplazar la
      URL del mock por la API real. Bajo riesgo si el contrato quedó
      congelado en Semana 2.
- [ ] TP integrador.
- [ ] Discusión de alternativas (Redis con TTL, WebSockets, eventos,
      microservicios) — sin necesidad de implementarlas todas.
- [ ] (Opcional) Implementar transiciones de estado pendientes:
      `ACTIVE --> EXPIRED` y `ACTIVE --> RELEASED` (ver
      `docs/diagrama_estados.md`).
- [ ] (Opcional) Regla de márgenes de montaje/limpieza de 30 min (ver
      `docs/reglas.md`).

## Deuda / decisiones abiertas

- El puerto se introdujo por valor pedagógico; bajo YAGNI estricto sería
  discutible en un proyecto real de este tamaño (ver ADR-002).
- `EXPIRED` y `RELEASED` existen en el enum pero no tienen transición
  implementada (ver `docs/diagrama_estados.md`).
