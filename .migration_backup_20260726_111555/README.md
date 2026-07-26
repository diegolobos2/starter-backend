# Starter Backend IA — Complejo de salas para eventos

Starter didáctico para estudiar **arquitectura y gobernanza de un backend
desarrollado con ayuda de agentes de IA**. El eje no es "escribir un
backend con un agente", sino "diseñar, dirigir y auditar un backend que
un agente construye con creciente autonomía".

Dominio: un complejo de salas para eventos. Los espectadores retienen
butacas con un flujo LIBRE → RETENIDO → RESERVADO. Regla central:
**RET-001** — una butaca no puede tener dos retenciones activas para el
mismo evento.

## Ejecutar

```bash
docker compose up --build
```

API en `http://localhost:8000`. Contrato OpenAPI (Swagger) en
`http://localhost:8000/docs`.

## Tests

```bash
pytest                    # suite normal (debe quedar en verde)
pytest -m race_demo -v    # demo de la condición de carrera (falla a propósito, Semana 1)
```

La suite normal corre contra SQLite (no requiere Docker/Postgres). Ver
`docs/base_de_datos.md`.

## Estructura de capas

```
app/
├── api/            # adaptador de entrada HTTP (FastAPI). Traduce HTTP <-> application.
├── application/    # casos de uso + puerto HoldRepository. Orquesta.
├── core/           # dominio puro: entidades + reglas (RET-001). Sin I/O.
└── infrastructure/ # adaptador de persistencia (SQLAlchemy/Postgres) + modelos.
```

Regla mental: **el core recibe todo por parámetro, decide una vez y
devuelve una vez; nunca sale a buscar nada.** La única capa que pregunta
hacia afuera es Application.

## Documentación (dónde está cada cosa)

- `AGENTS.md` — la constitución arquitectónica (reglas que el agente debe respetar).
- `docs/arquitectura.md` — capas, responsabilidades, puerto/adaptador, tabla de responsabilidades.
- `docs/frontera_core_application.md` — apartado teórico: qué le corresponde al core y qué no (TOCTOU, la prueba del verbo, DIP).
- `docs/reglas.md` — reglas de negocio (fuente única de verdad).
- `docs/trazabilidad_reglas.md` — regla → código → test.
- `docs/diagrama_estados.md` — diagrama de estados de una retención, derivado del código.
- `docs/base_de_datos.md` — cómo se crea/configura la base y hoja de ruta (Alembic en Semana 3).
- `docs/github_setup.md` — cómo subir y compartir el repo.
- `docs/adr/` — decisiones de arquitectura (ADR-001: concurrencia sin resolver; ADR-002: puerto/adaptador).
- `TODO.md` — estado del proyecto por semana.
- `GUION_VIDEO_SEMANA_2.md` — guía de grabación (uso docente).

## Estado por semana

- **Semana 1:** arquitectura, AGENTS.md, RET-001 declarada, condición de carrera sin resolver.
- **Semana 2:** puerto/adaptador, tests de arquitectura, dominio y contrato, docs consolidados.
- **Semana 3:** garantía real de concurrencia en PostgreSQL (restricción única / transacción).
- **Semana 4:** integración con Frontend, TP integrador, alternativas de evolución.
