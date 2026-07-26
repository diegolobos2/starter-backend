# Arquitectura del proyecto

## Objetivo

Este proyecto utiliza una arquitectura en capas basada en **Clean Architecture**, con el núcleo (`app/core`) implementado según el patrón **Functional Core, Imperative Shell**: un núcleo de funciones puras (sin I/O, sin efectos), rodeado por una "cáscara" que sí orquesta y ejecuta I/O.

El objetivo no es aplicar exhaustivamente todos los patrones asociados a estas arquitecturas, sino mantener un backend pequeño, comprensible, verificable y adecuado para trabajar con agentes de inteligencia artificial.

### Una nota sobre el vocabulario (Clean vs. hexagonal)

Clean Architecture y arquitectura hexagonal comparten el mismo principio (la **regla de dependencia**: el código depende siempre hacia adentro), pero usan vocabularios distintos y aparecieron por separado. Para evitar confusiones, este proyecto adopta **Clean Architecture** como marco principal (capas con nombres: api / application / core / infrastructure). Tomamos prestado de hexagonal solo el vocabulario de **puerto** (la interfaz que Application define) y **adaptador** (la implementación concreta en Infrastructure), porque son términos precisos y ampliamente usados. No mezclamos ambos marcos como si fueran intercambiables.

Las responsabilidades de cada capa forman parte del contrato del proyecto y deben respetarse durante toda su evolución.

### Tabla de responsabilidades (resumen)

| Capa | ¿Inicia llamadas hacia afuera? | ¿Tiene efectos / hace I/O? | ¿Contiene reglas de negocio? |
|------|-------------------------------|----------------------------|------------------------------|
| **core** | No | No | Sí (declara el significado del negocio) |
| **application** | Sí (pregunta a core y al puerto) | No directamente (delega en el adaptador) | Coordina cuándo aplicarlas; no declara reglas permanentes |
| **infrastructure** | No | Sí | No (ejecuta y traduce errores técnicos) |
| **api** | No | Es la puerta de entrada HTTP | No (traduce HTTP ↔ application) |

Regla mental rápida: **el core recibe todo por parámetro, decide una vez y devuelve una vez; nunca sale a buscar nada.** La única capa que "pregunta" hacia afuera es Application.

---

## Estructura general

```text
app/
├── api/
├── application/
├── core/
└── infrastructure/
```

Cada área tiene una responsabilidad claramente definida.

---

## API

`app/api` es el adaptador de entrada HTTP.

### Responsabilidades

- Definir rutas y endpoints.
- Validar requests.
- Recibir parámetros y cuerpos HTTP.
- Transformar resultados en respuestas HTTP.
- Traducir errores conocidos a códigos HTTP.
- Exponer los contratos mediante OpenAPI.

### No debe

- Contener reglas de negocio.
- Ejecutar consultas SQL.
- Acceder directamente a PostgreSQL.
- Decidir estados o transiciones del dominio.
- Contener lógica profunda del caso de uso.

---

## Application

`app/application` contiene los casos de uso de la aplicación.

### Responsabilidades

- Coordinar los pasos necesarios para ejecutar una operación.
- Solicitar información a la infraestructura.
- Invocar reglas y decisiones del core cuando corresponda.
- Ordenar la creación, modificación o persistencia de datos.
- Organizar el flujo entre entrada, dominio y persistencia.

Application conoce **qué pasos ejecutar y en qué orden**, pero no debería definir reglas de negocio permanentes.

### No debe

- Conocer detalles HTTP.
- Devolver códigos HTTP.
- Ejecutar SQL directamente.
- Depender de FastAPI.
- Contener detalles propios de PostgreSQL o SQLAlchemy.

---

## Core

`app/core` contiene el conocimiento estable del negocio.

Aquí pueden vivir:

- entidades;
- estados;
- transiciones válidas;
- invariantes;
- reglas de negocio;
- decisiones que deberían seguir siendo válidas aunque cambien FastAPI, PostgreSQL o SQLAlchemy.

### No debe depender de

- FastAPI;
- SQLAlchemy;
- PostgreSQL;
- psycopg;
- módulos de infraestructura;
- detalles HTTP.

El core decide **qué está permitido** en el negocio.

No todas las operaciones deben pasar obligatoriamente por el core. Las consultas simples pueden no requerir decisiones de dominio.

Toda decisión importante del negocio sí debe estar expresada en el core o apoyarse en conceptos definidos allí.

### Nuestra interpretación estricta del core

Clean Architecture, en su formulación general, permitiría que el núcleo llame a una fuente externa a través de un puerto sin romper la regla de dependencia (eso es el Dependency Inversion Principle). **Nosotros elegimos ser más estrictos:** el core no hace I/O de ninguna forma, ni directa ni a través de un puerto. Recibe siempre los datos ya resueltos, por parámetro.

Es una decisión de diseño deliberada, no una imposición de la disciplina. La tomamos porque:

- hace el core testeable con datos en memoria, sin dobles de prueba;
- lo hace verificable con un test automático simple (`tests/test_arquitectura.py`);
- da una regla binaria y sin zonas grises, más fácil de respetar para una persona *y para un agente de IA*.

Este es el patrón **Functional Core, Imperative Shell**. Una consecuencia práctica: una función cuyo nombre es un verbo de acción con resultado incierto (`intentar_reservar`, `confirmar_pago`) casi siempre es un **caso de uso** (Application), no una función de core. Una función de core suele nombrarse como una pregunta o un cálculo (`puede_crear_retencion`, `es_valido`, `calcular_total`).

---

## Puertos y adaptadores

Para que Application no dependa de detalles concretos de Infrastructure, usamos un **puerto**: una interfaz que Application define para expresar *qué* necesita de una fuente externa, sin comprometerse con *cómo* se implementa.

- **Puerto:** `app/application/ports.py` → `HoldRepository` (un `Protocol`). Declara las operaciones de persistencia que el caso de uso necesita. Vive en Application (no en core) porque quien tiene la necesidad de consultar/persistir es el caso de uso, no la regla pura.
- **Adaptador:** `app/infrastructure/repository.py` → `SqlAlchemyHoldRepository`. Implementa el puerto usando SQLAlchemy/PostgreSQL.
- **Inyección:** `app/api/routes.py` construye el adaptador concreto y lo inyecta como puerto (vía `Depends`). Es el único lugar que decide qué implementación se usa en producción.

Así, la dependencia apunta hacia adentro: Infrastructure conoce a Application (implementa su puerto), no al revés. Este es el **Dependency Inversion Principle** en acción, y es lo que se verifica en `tests/test_arquitectura.py`. La historia de esta decisión (por qué no estaba en Semana 1 y por qué se agregó en Semana 2) está en `docs/adr/ADR-002.md`.

---

## Infrastructure

`app/infrastructure` contiene los detalles técnicos y los adaptadores de salida.

### Responsabilidades

- Acceso a PostgreSQL.
- Configuración de SQLAlchemy.
- Modelos de persistencia.
- Sesiones y transacciones.
- Consultas a la base de datos.
- Repositorios.
- Migraciones de Alembic.
- Integración con servicios externos.

La infraestructura no define reglas de negocio.

Puede aportar garantías técnicas necesarias para cumplirlas (restricciones, transacciones, bloqueos, etc.), pero la regla debe existir independientemente de la tecnología utilizada.

---

## Dirección de las dependencias

Las dependencias conceptuales apuntan hacia el interior.

```text
API
  ↓
Application
  ↓
Core
```

Infrastructure es utilizada por Application para consultar y persistir datos.

### Reglas

- Core no importa módulos de API, Application ni Infrastructure.
- API no accede directamente a Infrastructure cuando existe un caso de uso correspondiente en Application.

---

## Flujo de una consulta simple

Una consulta que no requiere decisiones de negocio puede seguir el siguiente recorrido:

```text
HTTP Request
      ↓
     API
      ↓
Application
      ↓
Infrastructure
      ↓
Application
      ↓
     API
      ↓
HTTP Response
```

Ejemplo:

```text
GET /events
```

Listar eventos puede no requerir participación del core si solamente recupera información.

---

## Flujo de una operación con reglas de negocio

Una operación que sí requiere decisiones del dominio puede seguir el siguiente recorrido:

```text
HTTP Request
      ↓
     API
      ↓
Application
      ↓
Infrastructure
      ↓
Application
      ↓
    Core
      ↓
Application
      ↓
Infrastructure
      ↓
Application
      ↓
     API
      ↓
HTTP Response
```

Ejemplo para crear una retención:

1. API recibe y valida la solicitud, construye el adaptador
   (`SqlAlchemyHoldRepository`) e inyecta el puerto en el caso de uso.
2. Application coordina el caso de uso, usando el puerto `HoldRepository`
   (sin saber que detrás hay SQLAlchemy).
3. A través del puerto, se recuperan evento, butaca y retenciones
   existentes.
4. Core evalúa la regla RET-001 con esos datos ya en mano (decisión pura).
5. Application decide continuar con la operación.
6. A través del puerto, se persiste la nueva retención.
7. API traduce el resultado (o el error de dominio) a la respuesta HTTP
   correspondiente (`201`, `404` o `409`).

---

## Reglas y garantías técnicas

Una regla de negocio puede requerir una garantía técnica para cumplirse correctamente.

Ejemplo:

```text
RET-001

Una butaca no puede tener dos retenciones activas para el mismo evento.
```

Distribución de responsabilidades:

- Core expresa la regla y los estados involucrados.
- Application coordina el caso de uso.
- Infrastructure consulta y persiste.
- PostgreSQL puede aportar la garantía final frente a concurrencia.
- API traduce el resultado a una respuesta HTTP.

La regla pertenece al negocio, aunque su cumplimiento bajo concurrencia pueda requerir mecanismos propios de la infraestructura.

---

## Principios del proyecto

- Sin capas ceremoniales innecesarias.
- Sin abstracciones que solo reenvíen llamadas.
- Sin interfaces, fábricas o patrones complejos sin una necesidad concreta.
- Cada módulo debe tener una responsabilidad identificable.
- Los cambios deben ser pequeños y verificables.
- La arquitectura debe crecer de forma incremental.
- La suite normal de pruebas debe permanecer en verde.
- Las decisiones importantes deben quedar documentadas.
- Las reglas deben mantenerse coherentes con código, diagramas, contratos y pruebas.
- La API debe poder levantarse mediante Docker Compose de forma simple.
- La API debe quedar preparada para ser consumida por clientes externos, aunque este repositorio no incluya un frontend.

---

## Desarrollo asistido por inteligencia artificial

La arquitectura no organiza únicamente el código.

También proporciona un contexto estable para que los agentes de inteligencia artificial puedan:

- comprender el sistema;
- respetar los límites entre capas;
- proponer cambios consistentes;
- mantener reglas existentes;
- evitar responsabilidades incorrectas;
- generar cambios auditables.

Por ese motivo, los siguientes artefactos forman parte de la arquitectura del proyecto:

- `AGENTS.md`
- `docs/alcance_starter.md`
- `docs/reglas.md`
- `docs/trazabilidad_reglas.md`
- diagramas
- ADR
- contrato OpenAPI
- pruebas automatizadas

Estos elementos no constituyen documentación pasiva. Son parte del contexto utilizado durante el desarrollo y deben mantenerse sincronizados con la implementación.

---

## Estado inicial del starter

El estado inicial del repositorio incluye:

- Endpoint `GET /health`.
- Endpoint `GET /events` con datos de ejemplo.
- Organización en API, Application, Core e Infrastructure.
- Configuración mínima de PostgreSQL.
- SQLAlchemy.
- Alembic.
- Docker Compose.
- pytest.

Este estado representa únicamente el punto de partida.

El alcance funcional completo del starter se encuentra definido en:

```text
docs/alcance_starter.md
```