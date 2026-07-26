# Arquitectura vigente

Este documento es la única fuente normativa de las restricciones de
arquitectura. Los ADR explican por qué se tomaron decisiones; este archivo
describe qué debe cumplirse actualmente.

## Estructura

```text
app/
├── api/
├── application/
├── core/
└── infrastructure/
```

## ARQ-001 — Dirección general de dependencias

Las dependencias del código apuntan hacia el núcleo de la aplicación.

```text
API → Application → Core
Infrastructure → Application
```

Infrastructure implementa necesidades declaradas por Application; Application
no depende de implementaciones concretas de Infrastructure.

## ARQ-002 — Independencia del core

`app/core` no puede importar:

- `app/api`;
- `app/application`;
- `app/infrastructure`;
- FastAPI;
- SQLAlchemy;
- psycopg.

El core recibe datos por parámetro, decide sin I/O y devuelve resultados.

## ARQ-003 — Application no depende de Infrastructure

`app/application` expresa sus necesidades externas mediante puertos y no
importa implementaciones de `app/infrastructure`.

## ARQ-004 — Acceso a persistencia

Las consultas y escrituras de base de datos se realizan mediante adaptadores
ubicados en `app/infrastructure`.

## ARQ-005 — Responsabilidad de API

`app/api` traduce HTTP hacia y desde Application. No contiene reglas de
negocio ni realiza acceso directo a persistencia.

## ARQ-006 — Core funcional

El core no inicia I/O ni utiliza puertos de salida. Una función del core recibe
los datos necesarios ya resueltos por Application.

## ARQ-007 — Ubicación de los puertos

Los puertos requeridos por los casos de uso se definen en `app/application`.
Los adaptadores concretos se implementan en `app/infrastructure` y se conectan
en el borde de entrada.

## Responsabilidades

| Área | Responsabilidad |
|---|---|
| `app/api` | Rutas, validación y traducción HTTP |
| `app/application` | Coordinación de casos de uso y definición de puertos |
| `app/core` | Entidades, estados, invariantes y decisiones puras |
| `app/infrastructure` | Persistencia, SQLAlchemy, PostgreSQL y adaptadores externos |

## Flujo con regla de negocio

```text
HTTP
  ↓
API
  ↓
Application ──puerto──→ Infrastructure
  ↓
Core
  ↓
Application ──puerto──→ Infrastructure
  ↓
API
```

Las reglas funcionales se definen únicamente en
`docs/contrato/reglas.md`. La historia de las decisiones se conserva en
`docs/adr/`.
