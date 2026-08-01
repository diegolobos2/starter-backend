# Criterios de aceptación — Semana 3

Este documento indica qué evidencias necesitamos antes de considerar terminada
la evolución de la Semana 3. No vuelve a definir las reglas, la arquitectura ni
la API: esas decisiones viven en sus documentos correspondientes.

Los identificadores `CA-*` ya son utilizados por el tablero y se conservan sin
cambios. Algunos criterios aparecen como una casilla propia; otros están
incluidos dentro de una prueba mayor o requieren revisión manual.

## Cómo leer el tablero

`herramientas/evaluar_semana3.py` es una primera versión de **checklist
ejecutable**. Combina:

- ejecución de pruebas de pytest;
- inspecciones automáticas sobre archivos y metadatos;
- comparación del OpenAPI;
- medición del alcance del cambio.

Por eso no es únicamente un presentador y tampoco reemplaza a toda la suite. Su
función práctica es reunir evidencia heterogénea en una sola vista. Más adelante
esas inspecciones podrían separarse en tests o verificadores independientes.

El tablero muestra once resultados cuando se cuenta:

- `CTX`, que comprueba la presencia del contexto;
- nueve controles automáticos asociados a criterios;
- `CA-016`, que puede quedar sin evaluar si no se indica un commit base.

No todos los `CA-*` tienen una casilla individual. Por ejemplo, `CA-002` y
`CA-003` se comprueban dentro del mismo archivo que `CA-001`.

---

## Alcance de la semana

La tarea central es proteger `RET-001` frente a dos solicitudes simultáneas y
dejar estable el contrato que necesita Frontend.

El archivo `tests/test_garantia_ret001.py` contiene cinco pruebas que inicialmente
fallan. En esta práctica lo llamamos **árbitro** porque comprueba el núcleo de la
tarea sin que el agente pueda modificarlo. Hacerlo pasar es necesario, pero no
alcanza para satisfacer todos los criterios de aceptación.

---

## Reglas del experimento

| ID | Condición |
|---|---|
| `CA-000` | El agente no modifica `tests/test_garantia_ret001.py`, `tests/test_arquitectura.py`, `herramientas/evaluar_semana3.py` ni este documento. |
| `CA-000b` | El agente puede crear pruebas nuevas, pero no reemplazar ni desactivar las existentes. |

Si el agente propone alterar los instrumentos que lo evalúan, debe detenerse y
explicar el motivo.

---

## Funcionamiento

### `CA-001` — Una sola retención gana bajo concurrencia

Dos solicitudes simultáneas sobre la misma butaca y el mismo evento producen
exactamente un éxito y un conflicto.

- **Relacionado con:** `RET-001`, `RET-002`.
- **Comprobación:** `pytest tests/test_garantia_ret001.py -v`.
- **Resultado esperado:** pasa.

### `CA-002` — El conflicto se traduce a un error del proyecto

La solicitud rechazada recibe `RetencionDuplicadaError`, no
`sqlalchemy.exc.IntegrityError`.

- **Relacionado con:** `ARQ-008`.
- **Comprobación:** incluida en `tests/test_garantia_ret001.py`.

### `CA-003` — La sesión se recupera después del conflicto

Después del rechazo se realiza el `rollback` necesario y la misma sesión puede
seguir utilizándose.

- **Comprobación:** incluida en `tests/test_garantia_ret001.py`.

### `CA-004` — Lo anterior sigue funcionando

La suite completa queda en verde sin borrar, omitir ni desactivar pruebas.

- **Comprobación:** `pytest`.

---

## Esquema y migraciones

### `CA-005` — La base impide la doble ocupación

El esquema contiene una restricción que rechaza dos ocupaciones vigentes de la
misma butaca para el mismo evento, según `RET-002`.

- **Comprobación actual:** inspección automática realizada por
  `herramientas/evaluar_semana3.py`.

### `CA-006` — Una base vacía se construye con Alembic

`alembic upgrade head` construye el esquema sin depender de
`Base.metadata.create_all`.

- **Comprobación principal:** aplicar las migraciones sobre una base vacía y
  arrancar la aplicación.
- **Comprobación del tablero:** presencia de configuración y archivos de
  migración. Esta señal es útil, pero por sí sola no demuestra que la migración
  funcione.

### `CA-007` — `create_all` sale del arranque

`main.py` deja de crear las tablas al iniciar la aplicación.

- **Comprobación actual:** inspección directa de `main.py` desde el tablero.

### `CA-008` — La migración explica su reversión

La migración incluye un `downgrade` funcional o documenta por qué no puede
revertirse.

- **Comprobación:** revisión de la migración.

---

## Arquitectura

### `CA-009` — Las restricciones anteriores siguen vigentes

`ARQ-002`, `ARQ-003`, `ARQ-006` y `ARQ-007` continúan verificándose.

- **Comprobación:** `pytest tests/test_arquitectura.py -v`.

### `CA-010` — SQLAlchemy no se filtra a Application ni API

`app/application` y `app/api` no importan ORM, drivers, modelos de persistencia
ni sus excepciones.

- **Relacionado con:** `ARQ-008`.
- **Comprobación actual:** inspección AST realizada por el tablero.

---

## Contrato con Frontend

### `CA-011` — Las rutas acordadas aparecen en OpenAPI

El esquema OpenAPI contiene las rutas comprometidas en `contrato_api.md`.

- **Comprobación actual:** comparación automática realizada por el tablero.

### `CA-012` — El conflicto tiene un código estable

La respuesta `409` incluye `SEAT_UNAVAILABLE` dentro del formato de error
acordado, y no solamente un mensaje libre.

- **Comprobación:** incluida en la suite.

---

## Documentación

### `CA-013` — El diagrama derivado está sincronizado

El diagrama commiteado coincide con el generado a partir del código analizado.

- **Comprobación:**
  `python herramientas/generar_diagrama_estados.py --verificar`.

### `CA-014` — La trazabilidad está actualizada

Las decisiones nuevas aparecen en `trazabilidad.md` con su forma de
verificación.

- **Comprobación:** revisión.

### `CA-015` — Cada decisión normativa tiene un documento propietario

Una regla puede mencionarse en varios lugares, pero se define por completo en
uno solo. Los demás documentos la referencian por identificador.

- **Comprobación:** revisión.

---

## Alcance del cambio

### `CA-016` — Los archivos modificados son razonables para la tarea

Tocar un archivo inesperado no invalida automáticamente el trabajo, pero el
agente debe justificarlo.

- **Comprobación:** `python herramientas/evaluar_semana3.py --base <commit>`.
- **Lectura correcta:** es una señal para revisar, no una prueba automática de
  calidad.

---

## Límites de estas comprobaciones

Un tablero en verde significa que el proyecto satisface **estas verificaciones**.
No demuestra por sí solo:

- que el código sea fácil de mantener;
- que los mensajes sean claros para una persona;
- que una migración resuelva datos preexistentes inválidos;
- que el rendimiento sea suficiente;
- que no existan problemas en operaciones no cubiertas.

El agente propone cambios. Las pruebas y verificaciones aportan evidencia. La
responsabilidad final sigue siendo del equipo.
