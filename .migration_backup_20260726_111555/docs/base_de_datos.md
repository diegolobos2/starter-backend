# Base de datos: cómo se crea, se configura y cómo va a evolucionar

Este documento explica la metodología de base de datos del proyecto: qué
hace hoy, por qué, y qué cambia en las próximas semanas. Es importante
para no confundir el estado actual (deliberadamente simple) con el
estado final.

## Cómo se conecta la aplicación a la base

La configuración vive en `app/infrastructure/db.py`. Usa una única
variable de entorno, `DATABASE_URL`:

- En `docker-compose.yml` apunta a **PostgreSQL** (el motor real del
  proyecto): `postgresql+psycopg://app:app@db:5432/app`.
- En los tests, `tests/conftest.py` sobreescribe `DATABASE_URL` por una
  base **SQLite** en archivo, *antes* de importar la app. Es una
  decisión pragmática: la suite normal no depende de tener Postgres
  levantado. La garantía de concurrencia real (Semana 3) sí se validará
  contra Postgres, en una suite de integración aparte.

Esta separación (Postgres para correr de verdad, SQLite para tests
rápidos) es intencional y es un buen ejemplo de por qué `DATABASE_URL`
está externalizada como variable de entorno y no hardcodeada.

## Cómo se crea el esquema HOY (y su limitación)

Actualmente el esquema se crea con `Base.metadata.create_all(bind=engine)`
en el arranque de la app (`main.py`). SQLAlchemy mira los modelos
declarados en `app/infrastructure/models.py` (`EventModel`, `SeatModel`,
`HoldModel`) y crea las tablas que falten.

**Limitación importante:** `create_all` solo *crea tablas que no
existen*. No aplica cambios a tablas ya creadas. Si mañana agregás una
columna o una restricción a un modelo, `create_all` **no** la va a
aplicar sobre una base que ya tenía la tabla vieja. Para eso hacen falta
**migraciones**.

## Nota sobre Alembic (inconsistencia doc-vs-realidad, a propósito)

Documentos anteriores mencionan Alembic (la herramienta estándar de
migraciones para SQLAlchemy) como parte de la infraestructura. **Alembic
todavía NO está configurado** en el proyecto: no hay `alembic.ini` ni
carpeta de migraciones. El esquema se maneja hoy solo con `create_all`.

Esto es en sí mismo un buen ejemplo de auditoría: un documento decía algo
que el código no cumple. Se deja la aclaración acá en vez de borrar la
mención, para que la brecha quede visible y explicada.

## Por qué esto importa para la Semana 3

La Semana 3 agrega la garantía real de RET-001 a nivel de PostgreSQL:
una **restricción única parcial** (un índice único sobre `(event_id,
seat_id)` que aplique solo cuando el estado es `ACTIVE`/`CONFIRMED`) y/o
una transacción con bloqueo.

Agregar esa restricción es exactamente el caso donde `create_all` se
queda corto: si la tabla `holds` ya existe, `create_all` no le va a
sumar el índice. Por eso la Semana 3 es el momento natural para
introducir **Alembic** de verdad:

1. Configurar Alembic (`alembic init`).
2. Generar una migración que agregue la restricción única parcial.
3. Aplicarla con `alembic upgrade head`.

Así, la evolución del esquema deja de ser "lo que create_all alcance a
crear" y pasa a ser un historial versionado de cambios, coherente con el
resto del proyecto (donde todo queda trazado y auditado).

## Metodología recomendada, resumida

- **Modelos** (`models.py`): definen la forma de las tablas. Son detalle
  de infraestructura; core y application no los importan.
- **Entidades** (`core/entities.py`): son del dominio, inmutables, sin
  saber nada de tablas. El adaptador traduce entre ambos.
- **Semana 1-2:** esquema por `create_all`, suficiente para el alcance
  actual.
- **Semana 3 en adelante:** migraciones con Alembic para cualquier
  cambio de esquema (empezando por la restricción única de RET-001).
- **Nunca** poner SQL crudo en `api` ni en `application`: todo acceso a
  la base pasa por el adaptador en `infrastructure`.
