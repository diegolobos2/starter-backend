# Contrato de la API — v1

Este documento es la única fuente normativa de lo que la API promete a quien la
consume. El equipo de Frontend trabaja contra este contrato, no contra el
código.

**Lo que este documento fija** (y no puede cambiar sin una nueva versión):
rutas, métodos, forma del JSON, campos obligatorios, formato de fechas,
vocabulario de estados, códigos HTTP y códigos de error.

**Lo que este documento deliberadamente no fija:** tablas, índices, nombres de
clases, repositorios, ORM, estrategia de concurrencia y organización interna de
carpetas. Todo eso puede cambiar sin romper el contrato.

---

## 1. Principio de versionado

El contrato se estabiliza antes que la implementación. Un endpoint puede estar
definido acá y todavía no implementado; en ese caso responde `501` con el código
`NOT_IMPLEMENTED`, nunca `404`.

Un `404` significa "este recurso no existe". Un `501` significa "esta operación
existe en el contrato y todavía no está construida". Confundirlos hace que el
Frontend no pueda distinguir un error propio de una funcionalidad pendiente.

---

## 2. Convenciones generales

- Todas las respuestas son `application/json`.
- Las fechas se expresan en **ISO 8601 con zona UTC**: `2026-08-15T20:00:00Z`.
- Los identificadores son cadenas opacas. El cliente **no debe** derivar
  significado de su forma ni construirlos.
- Los campos declarados como obligatorios están siempre presentes; los
  opcionales pueden venir en `null`.

### Formato de error

Toda respuesta de error tiene esta forma:

```json
{
  "detail": {
    "code": "SEAT_UNAVAILABLE",
    "message": "La butaca ya está ocupada para este evento."
  }
}
```

El campo `code` es el contrato: es estable y está pensado para que el cliente
tome decisiones con él. El campo `message` es orientativo y puede cambiar de
redacción sin aviso. **El Frontend no debe ramificar sobre `message`.**

---

## 3. Vocabulario público de estados

> **Aclaración sobre `ACTIVE` y `HELD`.** `ACTIVE` es el nombre interno que ya
> usa el dominio para una retención temporal vigente. La API expone `HELD`
> porque comunica mejor la idea al Frontend. No son dos estados distintos:
> son dos nombres en dos límites diferentes del sistema.

El estado que ve el cliente **no** es el nombre interno del dominio. Esta
traducción es parte del contrato:

| Estado público | Significado para el cliente | Estado interno |
|---|---|---|
| `AVAILABLE` | La butaca puede seleccionarse. | sin ocupación vigente |
| `HELD` | Retenida temporalmente. No seleccionable. | `ACTIVE` |
| `CONFIRMED` | Confirmada. No seleccionable. | `CONFIRMED` |

Los estados internos `EXPIRED` y `RELEASED` no tienen estado público propio: una
butaca cuya retención venció o fue liberada vuelve a informarse como
`AVAILABLE`. Esos dos estados internos todavía no tienen productor real en el
código (ver `docs/diagramas/estados_retencion.md`), por lo que hoy una butaca
retenida permanece `HELD` indefinidamente. Se resuelve en la Semana 4.

---

## 4. Endpoints

### `GET /health`

Verificación de disponibilidad del servicio.

**200**

```json
{ "status": "ok" }
```

---

### `GET /events`

Lista los eventos disponibles.

**200**

```json
[
  {
    "id": "evento-demo",
    "name": "Recital de ejemplo",
    "starts_at": "2026-08-15T20:00:00Z",
    "ends_at": "2026-08-15T22:00:00Z"
  }
]
```

Campos obligatorios: `id`, `name`, `starts_at`, `ends_at`.

---

### `GET /events/{event_id}`

**200** — un objeto con la misma forma que un elemento de `GET /events`.

**404** — `EVENT_NOT_FOUND`

---

### `GET /events/{event_id}/seats`

Butacas del evento con su estado actual. Es el endpoint que alimenta el mapa de
la sala.

**200**

```json
[
  {
    "id": "butaca-1",
    "label": "A1",
    "status": "AVAILABLE"
  },
  {
    "id": "butaca-2",
    "label": "A2",
    "status": "HELD"
  }
]
```

Campos obligatorios: `id`, `label`, `status`.

> **Geometría de la sala — previsto para v1.1, no implementado en Semana 3.**
> Para dibujar salas no rectangulares el Frontend va a necesitar posición
> lógica. Los campos previstos son `row`, `number`, `x`, `y` y `sector`, todos
> opcionales y sin unidad de píxeles: son coordenadas relativas que el Frontend
> escala. Hasta que existan, el Frontend puede disponer las butacas en el orden
> en que llegan. Cuando se agreguen, serán campos **nuevos y opcionales**, por
> lo que no rompen a ningún cliente ya escrito.
>
> El Frontend **no debe** codificar la distribución de la sala en su propio
> código: debe dibujar lo que recibe. Esa es la condición para que el mismo
> Frontend funcione con dos salas distintas sin tocar una línea.

**404** — `EVENT_NOT_FOUND`

---

### `POST /events/{event_id}/holds`

Crea una retención temporal sobre una butaca. **Éste es el endpoint central del
contrato y el único que queda completamente implementado en la Semana 3.**

**Cuerpo**

```json
{ "seat_id": "butaca-1" }
```

Campo obligatorio: `seat_id`. Se usa el identificador de la butaca, nunca la
etiqueta (`label`): las etiquetas son texto para mostrar y pueden cambiar.

**201**

```json
{
  "id": "hold-abc123",
  "event_id": "evento-demo",
  "seat_id": "butaca-1",
  "status": "HELD",
  "created_at": "2026-08-01T14:32:10Z"
}
```

**Errores**

| HTTP | `code` | Cuándo |
|---|---|---|
| `404` | `EVENT_NOT_FOUND` | El evento no existe. |
| `404` | `SEAT_NOT_FOUND` | La butaca no existe o no pertenece a ese evento. |
| `409` | `SEAT_UNAVAILABLE` | La butaca ya está ocupada (`HELD` o `CONFIRMED`). |
| `422` | `INVALID_REQUEST` | Cuerpo mal formado o campo faltante. |

**Garantía bajo concurrencia.** Ante dos solicitudes simultáneas sobre la misma
butaca del mismo evento, exactamente una recibe `201` y la otra recibe `409`
con `SEAT_UNAVAILABLE`. Nunca dos `201`. Esta garantía es parte del contrato,
no un detalle de implementación: el Frontend puede confiar en ella para decidir
qué mostrar.

---

### `POST /holds/{hold_id}/confirm`

Confirma una retención vigente.

**200** — mismo objeto que `POST .../holds`, con `status: "CONFIRMED"`.

| HTTP | `code` | Cuándo |
|---|---|---|
| `404` | `HOLD_NOT_FOUND` | La retención no existe. |
| `409` | `INVALID_HOLD_STATE` | La retención no está en un estado confirmable. |
| `409` | `HOLD_EXPIRED` | La retención venció. *(Reservado: sin productor hasta la Semana 4.)* |

---

### `DELETE /holds/{hold_id}`

Libera una retención vigente.

**Estado en la Semana 3: definido en el contrato, no implementado.** Responde
`501` con `NOT_IMPLEMENTED`. Se implementa en la Semana 4.

**204** — sin cuerpo, cuando esté implementado.

| HTTP | `code` | Cuándo |
|---|---|---|
| `404` | `HOLD_NOT_FOUND` | La retención no existe. |
| `409` | `INVALID_HOLD_STATE` | La retención no está en un estado liberable. |
| `501` | `NOT_IMPLEMENTED` | Semana 3. |

---

## 5. Catálogo de códigos de error

| `code` | HTTP |
|---|---|
| `EVENT_NOT_FOUND` | 404 |
| `SEAT_NOT_FOUND` | 404 |
| `HOLD_NOT_FOUND` | 404 |
| `SEAT_UNAVAILABLE` | 409 |
| `INVALID_HOLD_STATE` | 409 |
| `HOLD_EXPIRED` | 409 |
| `INVALID_REQUEST` | 422 |
| `NOT_IMPLEMENTED` | 501 |

Agregar un código nuevo es una ampliación del contrato y requiere modificar este
documento. Cambiar el significado de uno existente es una ruptura y requiere
una versión nueva de la API.

---

## 6. Cómo trabaja Frontend contra este contrato

- El esquema OpenAPI vivo está en `/openapi.json`; la documentación navegable en
  `/docs`.
- Los ejemplos de este documento son válidos como datos de prueba.
- Mientras un endpoint responda `501`, el Frontend puede simular la respuesta
  documentada acá sin riesgo de estar inventando una forma que después no exista.

---

## 7. Fuera del contrato v1

Autenticación, usuarios, pagos, selección múltiple de butacas, notificaciones en
tiempo real, creación de eventos y creación de salas. Ninguna de esas
operaciones está prometida en esta versión.
