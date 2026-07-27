# Base de datos vigente — Semana 2

Este documento describe el estado vigente de la persistencia. Las decisiones
históricas se registran en `docs/adr/` y la evolución pendiente en `TODO.md`.

## Configuración

La aplicación obtiene la conexión mediante la variable de entorno
`DATABASE_URL`.

- En `docker-compose.yml`, el motor utilizado es PostgreSQL.
- En la suite normal de pruebas, `tests/conftest.py` establece una base SQLite
  antes de importar la aplicación.

## Creación del esquema

Durante la Semana 2, las tablas se crean mediante:

`Base.metadata.create_all(bind=engine)`

El proyecto no tiene todavía un sistema de migraciones configurado.

## Ubicación de modelos y acceso

- Los modelos ORM viven en `app/infrastructure/models.py`.
- El acceso a persistencia se realiza mediante adaptadores de Infrastructure,
  de acuerdo con ARQ-004.
- Core y Application no importan modelos ORM ni ejecutan consultas SQL.
- La traducción entre modelos ORM y entidades corresponde al adaptador.

## Limitaciones vigentes

- `create_all` crea tablas faltantes, pero no actualiza tablas existentes.
- La garantía concurrente de RET-001 no está implementada.
- La evolución del esquema y la incorporación de migraciones pertenecen al
  alcance de la Semana 3 y se registran en `TODO.md`.
