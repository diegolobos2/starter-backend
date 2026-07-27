# Starter Backend IA — Complejo de salas para eventos

Starter didáctico para estudiar arquitectura, reglas de negocio y gobernanza
de cambios realizados con agentes de IA.

## Ejecutar

```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Tests

```bash
pytest
pytest -m race_demo -v
```

La suite normal corre contra SQLite. La demostración `race_demo` se ejecuta
por separado porque la garantía concurrente de RET-001 está fuera del alcance
de la Semana 2.

## Documentación normativa

- Alcance: `docs/contrato/alcance.md`
- Arquitectura: `docs/contrato/arquitectura.md`
- Reglas: `docs/contrato/reglas.md`
- Trazabilidad: `docs/contrato/trazabilidad.md`
- Base de datos: `docs/contrato/base_de_datos.md`

## Documentación complementaria

- Decisiones: `docs/adr/`
- Diagramas: `docs/diagramas/`
- Material teórico: `docs/teoria/`
- Estado y pendientes: `TODO.md`

## Trabajo con agentes

Leer `AGENTS.md`. Ese archivo define el procedimiento y enlaza los documentos
normativos; no repite sus contenidos.
