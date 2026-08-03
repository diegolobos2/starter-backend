# Contrato de la API — v2

Este documento es la única fuente normativa de lo que la API promete a quien la
consume. El equipo de Frontend trabaja contra este contrato, no contra el
código.

**Lo que este documento fija** (y no puede cambiar sin una nueva versión):
rutas, métodos, forma del JSON, campos obligatorios, formato de fechas,
vocabulario de estados, códigos HTTP y códigos de error.

**Lo que este documento deliberadamente no fija:** tablas, índices, nombres de
clases, repositorios, ORM, estrategia de concurrencia y organización interna de
carpetas. Todo eso puede cambiar sin romper el contrato.

> **v2 reemplaza a v1.** El v1 se congeló en la Semana 3 y nunca tuvo un
> consumidor. El v2 incorpora usuarios, salas con disposición espacial,
> retención y confirmación por lote, y vencimiento explícito de las
> retenciones. El motivo del cambio y lo que se descartó están registrados en
> `docs/adr/ADR-004.md`.

---

## 1. Principio de versionado

El contrato se estabiliza antes que la implementación. Un endpoint puede estar
definido acá y todavía no implementado; en ese caso responde `501` con el
código `NOT_IMPLEMENTED`, nunca `404`.

Un `404` significa "este recurso no existe". Un `501` significa "esta operación
existe en el contrato y todavía no está construida". Confundirlos hace que el
Frontend no pueda distinguir un error propio de una funcionalidad pendiente.

### 1.1. Alcance: solo la vista de espectador

Este contrato **no incluye altas**. Usuarios, eventos, salas y la disposición
de butacas ya existen: se cargan una única vez, fuera de la API, como datos de
inicialización del proyecto (por ejemplo, al construir la base o al correr la
migración correspondiente). No hay `POST /events`, `POST /users` ni un endpoint
para definir una sala.

El trabajo práctico cubre exclusivamente lo que un espectador hace sobre esos
datos ya existentes: consultarlos, retener butacas y confirmar. Crear eventos o
salas, y la lógica de negocio asociada a esa creación, quedan fuera de alcance.

---

## 2. Convenciones generales

- Todas las respuestas son `application/json`.
- Las fechas se expresan en **ISO 8601 con zona UTC**, siempre con `Z`:
  `2026-08-15T20:00:00Z`. El Frontend convierte a hora local para mostrar. No
  se envían fechas sin zona: una cuenta regresiva calculada sobre una fecha sin
  zona da mal por tres horas en Argentina.
- Los identificadores de eventos, salas, butacas y retenciones son **enteros**.
  Los identificadores de usuario son **cadenas** (`"user-1"`). El cliente no
  debe derivar significado de su valor ni construirlos.
- Los campos declarados como obligatorios están siempre presentes; los
  opcionales pueden venir en `null`.
- No hay autenticación. El usuario viaja como dato en la petición. Esto es una
  simplificación deliberada del trabajo práctico y está registrada como tal.

### Formato de error

Toda respuesta de error tiene esta forma:

```json
{
  "detail": {
    "code": "SEATS_UNAVAILABLE",
    "message": "Una o más butacas ya no están disponibles."
  }
}
```

`code` es el contrato: es estable y está pensado para que el cliente ramifique
sobre él. `message` es orientativo y puede cambiar de redacción sin aviso. **El
Frontend no debe ramificar sobre `message`.**

Algunos errores agregan un campo extra con el detalle de qué falló. Cuando
existe, está documentado en el endpoint correspondiente y en el catálogo de la
Sección 5.

---

## 3. Vocabulario público de estados

Hay dos vocabularios distintos y conviene no mezclarlos.

### 3.1. Estado de una butaca

Es lo que muestra el mapa. Se **calcula** en el momento de la lectura; no es un
campo guardado.

| Estado | Significado |
|---|---|
| `AVAILABLE` | Se puede retener. |
| `HELD` | Alguien la tiene retenida y la retención no venció. |
| `CONFIRMED` | La compra se confirmó. |

### 3.2. Estado de una retención

| Estado | Significado | Terminal |
|---|---|---|
| `HELD` | Retención vigente, sin confirmar, con `expires_at` en el futuro. | No |
| `CONFIRMED` | Confirmada. | Sí |
| `RELEASED` | El usuario la soltó con `DELETE`. | Sí |
| `EXPIRED` | Venció sin confirmarse. | Sí |

Una butaca puede tener muchas retenciones a lo largo del tiempo: una por cada
vez que alguien la intentó tomar. Una retención terminal no se reutiliza; un
intento nuevo crea una retención nueva, con otro `hold_id`.

> **Sobre `HELD` y el paso del tiempo.** Una retención está vigente si su estado
> es `HELD` **y** `expires_at` todavía no pasó. Las dos condiciones, siempre. El
> Frontend puede confiar en el `status` que devuelve la API: el servidor ya hizo
> esa cuenta antes de responder.

---

## 4. Endpoints

### 4.1. `GET /health`

Comprobación de vida del servicio. Sin parámetros.

`200`:

```json
{ "status": "ok" }
```

---

### 4.2. `GET /users`

Devuelve los usuarios precargados. No hay registro ni login: el Frontend
muestra esta lista y el usuario elige quién es.

`200`:

```json
[
  { "id": "user-1", "name": "Ana" },
  { "id": "user-2", "name": "Bruno" }
]
```

---

### 4.3. `GET /events`

Devuelve los eventos disponibles, ordenados por `starts_at` ascendente.

`200`:

```json
[
  {
    "id": 1,
    "name": "Concierto del sábado",
    "room_id": 1,
    "room_name": "Sala Principal",
    "starts_at": "2026-08-08T21:00:00Z"
  }
]
```

---

### 4.4. `GET /events/{event_id}`

Devuelve un evento. Mismo objeto que en la lista anterior.

- `200`: el evento.
- `404` (`EVENT_NOT_FOUND`): el evento no existe.

---

### 4.5. `GET /events/{event_id}/seats`

Devuelve la sala y todas sus butacas con el estado actual para ese evento. Es
el endpoint que el Frontend consulta por *polling*.

`200`:

```json
{
  "event": {
    "id": 1,
    "name": "Concierto del sábado",
    "starts_at": "2026-08-08T21:00:00Z"
  },
  "room": {
    "id": 1,
    "name": "Sala Principal",
    "rows": 12,
    "columns": 20
  },
  "seats": [
    {
      "id": 101,
      "label": "A1",
      "row": "A",
      "number": 1,
      "x": 1,
      "y": 1,
      "sector": "PLATEA",
      "status": "AVAILABLE",
      "hold_id": null,
      "held_by_user_id": null,
      "expires_at": null
    },
    {
      "id": 102,
      "label": "A2",
      "row": "A",
      "number": 2,
      "x": 2,
      "y": 1,
      "sector": "PLATEA",
      "status": "HELD",
      "hold_id": 5001,
      "held_by_user_id": "user-1",
      "expires_at": "2026-08-03T00:25:00Z"
    }
  ]
}
```

- `404` (`EVENT_NOT_FOUND`): el evento no existe.

**Reglas de este objeto, normativas:**

- `x` e `y` son coordenadas de grilla con origen `(1,1)` arriba a la izquierda.
  Sirven para dibujar el mapa. Dos butacas nunca comparten coordenada dentro de
  la misma sala.
- `row`, `number` y `label` son para mostrar. `label` es la concatenación
  legible y es lo que el usuario reconoce.
- `sector` es una cadena libre del dominio (`PLATEA`, `PULLMAN`, `PALCO`). El
  Frontend puede usarla para agrupar o colorear, pero no debe asumir un
  conjunto cerrado de valores.
- `hold_id`, `held_by_user_id` y `expires_at` vienen en `null` salvo que
  `status` sea `HELD` o `CONFIRMED`.
- **Si una retención venció, la butaca aparece como `AVAILABLE` y sus tres
  campos de retención vienen en `null`.** Nunca se devuelven los datos de una
  retención vencida: sería decirle al Frontend que la butaca está tomada
  mientras el `status` dice lo contrario.

---

### 4.6. `POST /events/{event_id}/holds`

Retiene una o varias butacas para un usuario. **La operación es conjunta: se
retienen todas o ninguna.**

Cuerpo:

```json
{
  "user_id": "user-1",
  "seat_ids": [101, 102, 103]
}
```

- `seat_ids` debe tener al menos un elemento y no puede repetir valores.

`201`:

```json
{
  "holds": [
    {
      "id": 5001,
      "event_id": 1,
      "seat_id": 101,
      "user_id": "user-1",
      "status": "HELD",
      "expires_at": "2026-08-03T00:25:00Z"
    },
    {
      "id": 5002,
      "event_id": 1,
      "seat_id": 102,
      "user_id": "user-1",
      "status": "HELD",
      "expires_at": "2026-08-03T00:25:00Z"
    }
  ]
}
```

Todas las retenciones creadas en una misma petición comparten `expires_at`.

**Otros resultados:**

- `404` (`EVENT_NOT_FOUND`, `USER_NOT_FOUND`, `SEATS_NOT_FOUND`): no existe el
  evento, el usuario, o alguna butaca de la lista. `SEATS_NOT_FOUND` incluye
  `seat_ids` con las que no existen.
- `409` (`SEATS_UNAVAILABLE`): al menos una butaca ya está retenida o confirmada
  por **otro** usuario.

```json
{
  "detail": {
    "code": "SEATS_UNAVAILABLE",
    "message": "Una o más butacas ya no están disponibles.",
    "seat_ids": [102]
  }
}
```

- `422` (`INVALID_REQUEST`): el cuerpo no cumple la forma declarada.

**Idempotencia.** Si una butaca del pedido ya tiene una retención vigente **del
mismo usuario**, no se crea una retención nueva ni se produce un conflicto: se
devuelve la retención existente, con su `expires_at` original. Esto hace que un
reintento del navegador —o un doble clic— sea inofensivo. Sin esta regla, el
usuario recibiría `409` por butacas que ya son suyas.

---

### 4.7. `POST /holds/confirm`

Confirma una o varias retenciones. **Se confirman todas juntas o ninguna.**

Cuerpo:

```json
{
  "user_id": "user-1",
  "hold_ids": [5001, 5002, 5003]
}
```

`200`:

```json
{
  "holds": [
    { "id": 5001, "seat_id": 101, "user_id": "user-1", "status": "CONFIRMED" },
    { "id": 5002, "seat_id": 102, "user_id": "user-1", "status": "CONFIRMED" }
  ]
}
```

**Otros resultados:**

- `404` (`HOLDS_NOT_FOUND`): alguna retención no existe, **o no pertenece al
  usuario indicado**. Los dos casos responden igual, a propósito: una retención
  ajena no existe para este usuario. Incluye `hold_ids` con las que fallaron.
- `409` (`HOLDS_NOT_CONFIRMABLE`): alguna retención venció, fue liberada o ya
  estaba confirmada.

```json
{
  "detail": {
    "code": "HOLDS_NOT_CONFIRMABLE",
    "message": "Una o más retenciones no pueden confirmarse.",
    "hold_ids": [5002]
  }
}
```

- `422` (`INVALID_REQUEST`): el cuerpo no cumple la forma declarada.

Una retención ya confirmada no da `200`: da `409`. Confirmar dos veces no es lo
mismo que confirmar una vez, porque el Frontend tiene que poder distinguir "tu
compra se hizo recién" de "esto ya estaba hecho".

---

### 4.8. `DELETE /holds/{hold_id}`

Libera una retención individual. Permite sacar una butaca de la selección sin
perder las demás.

- `204`: sin cuerpo. La retención queda `RELEASED` y la butaca vuelve a estar
  disponible.
- `404` (`HOLD_NOT_FOUND`): la retención no existe.
- `409` (`HOLD_NOT_RELEASABLE`): la retención está `CONFIRMED` y ya no puede
  liberarse.

**Idempotencia.** Liberar una retención ya `RELEASED` o ya `EXPIRED` devuelve
`204`, no `404` ni `409`. El efecto deseado —que la butaca no esté tomada por
este usuario— ya se cumple, y un reintento no debe parecer un error.

---

## 5. Catálogo de códigos de error

| Código | HTTP | Campo extra | Cuándo |
|---|---|---|---|
| `EVENT_NOT_FOUND` | 404 | — | El evento no existe. |
| `USER_NOT_FOUND` | 404 | — | El usuario no existe. |
| `SEATS_NOT_FOUND` | 404 | `seat_ids` | Alguna butaca no existe en esa sala. |
| `HOLD_NOT_FOUND` | 404 | — | La retención no existe. |
| `HOLDS_NOT_FOUND` | 404 | `hold_ids` | Alguna retención no existe o es de otro usuario. |
| `SEATS_UNAVAILABLE` | 409 | `seat_ids` | Butacas tomadas por otro usuario. |
| `HOLDS_NOT_CONFIRMABLE` | 409 | `hold_ids` | Retenciones vencidas, liberadas o ya confirmadas. |
| `HOLD_NOT_RELEASABLE` | 409 | — | La retención está confirmada. |
| `INVALID_REQUEST` | 422 | — | El cuerpo no cumple la forma declarada. |
| `NOT_IMPLEMENTED` | 501 | — | Endpoint definido en el contrato y todavía no construido. |

Esta lista es cerrada. Un código que no esté acá no debe aparecer en una
respuesta.

---

## 6. Flujo de referencia para el Frontend

```text
GET /users
    └── el usuario elige quién es

GET /events
    └── elige un evento

GET /events/{event_id}/seats        ← se repite por polling
    └── selecciona butacas

POST /events/{event_id}/holds
    └── recibe los hold_id y el expires_at

DELETE /holds/{hold_id}
    └── saca una butaca de la selección

POST /holds/confirm
    └── confirma las que quedaron
```

### 6.1. Polling

El mapa se refresca consultando `GET /events/{event_id}/seats` cada pocos
segundos. Un intervalo de 3 a 5 segundos es razonable; el contrato no lo fija.

### 6.2. El `409` es parte del flujo normal

Con varios usuarios mirando el mismo mapa, dos personas van a ver la misma
butaca libre y una va a perder. **`SEATS_UNAVAILABLE` no es una falla del
sistema ni un error del usuario.** El Frontend debe refrescar el mapa, avisar
cuáles butacas se perdieron —vienen en `seat_ids`— y dejar seguir. Una pantalla
de error genérica en ese caso es un defecto del Frontend.

### 6.3. La cuenta regresiva

`expires_at` es la fecha límite. El Frontend puede mostrar el tiempo restante,
pero **no debe asumir que la retención sigue viva porque su reloj todavía no
llegó**: el reloj del navegador puede estar corrido. La verdad la dice el
servidor en la respuesta siguiente.

---

## 7. Reglas de implementación derivadas

Esta sección no es parte de lo que se le promete al consumidor: es lo que el
contrato le obliga al Backend. Está acá porque son consecuencias directas de lo
anterior y no deberían quedar libradas a interpretación.

1. **RET-001 sigue siendo una garantía de la base.** Una butaca no puede tener
   dos retenciones ocupantes para el mismo evento. La protege el índice único
   parcial, no una validación previa. Ver `docs/contrato/base_de_datos.md`.

2. **El vencimiento se calcula en la lectura y se escribe en la escritura.** Son
   dos cosas distintas y hacen falta las dos:
   - `GET /seats` deriva el estado de `(status, expires_at)`, sin escribir nada.
   - La transacción de `POST /holds` marca como `EXPIRED` las retenciones
     vencidas de las butacas pedidas **antes** de insertar, dentro de la misma
     transacción. El índice no puede leer el reloj: `now()` no es inmutable y
     PostgreSQL no la admite en el predicado de un índice. Sin esa escritura,
     una butaca vencida queda bloqueada para siempre aunque el mapa la muestre
     libre.

3. **Todo o nada.** Retención y confirmación por lote son transaccionales. Si
   una butaca del lote falla, no queda ninguna retenida.

4. **Las butacas se procesan en orden ascendente de `seat_id`.** Dos usuarios
   pidiendo lotes que se cruzan en distinto orden pueden trabarse mutuamente y
   provocar un *deadlock*. Ordenar siempre igual lo evita.

5. **Los errores técnicos no cruzan la frontera** (ARQ-008). El
   `IntegrityError` se traduce a una excepción del dominio en el adaptador; ni
   Application ni API conocen SQLAlchemy.

6. **El TTL de una retención es una constante de configuración**, no un valor
   que el cliente pueda enviar. Su valor no es parte del contrato: el Frontend
   lee `expires_at` y no necesita saber cuántos minutos son.

---

## 8. Lo que este contrato no promete

- Que exista un proceso que venza retenciones en segundo plano. Puede haberlo o
  no; el Frontend no debe depender de eso.
- Un orden estable de `seats` más allá del que permita reconstruir el mapa con
  `x` e `y`.
- Que `hold_id` sea contiguo, ni que su valor tenga relación con el orden de
  creación.
- Notificaciones en tiempo real. El único mecanismo de actualización previsto es
  el *polling*.

---

## 9. Cambios respecto de v1

| | v1 | v2 |
|---|---|---|
| Usuarios | No existían | `GET /users`, `user_id` en las peticiones |
| Identificadores | Cadenas opacas | Enteros, salvo `user_id` |
| Salas | No existían | `room` con disposición espacial |
| Retención | Una butaca por pedido | Lote, todo o nada |
| Confirmación | `POST /holds/{id}/confirm` | `POST /holds/confirm`, por lote |
| Vencimiento | No estaba en el contrato | `expires_at` explícito |
| `DELETE /holds/{id}` | `501` | `204`, idempotente |
| Código de conflicto | `SEAT_UNAVAILABLE` | `SEATS_UNAVAILABLE` con `seat_ids` |

`POST /holds/{id}/confirm` **desaparece**. Confirmar una sola retención se hace
con `POST /holds/confirm` y una lista de un elemento.

---

## 10. Decisiones abiertas

Registradas acá para que no se resuelvan por omisión durante la implementación.

- **`held_by_user_id` es visible para todos.** Sin autenticación no hay nada que
  proteger, pero si en algún momento hay usuarios reales, este campo debería
  reemplazarse por un booleano `held_by_me`.
- **Identificadores enteros y correlativos.** Permiten adivinar y contar
  retenciones ajenas. Es aceptable para un trabajo práctico sin autenticación y
  no lo sería en producción.
- **Butacas fuera de venta.** El v1 propuesto contemplaba un estado
  `UNAVAILABLE`. Quedó afuera porque no hay nada en el modelo que lo produzca.
  Si aparece la necesidad —una butaca rota, una fila bloqueada por producción—
  entra como campo de la butaca, no como estado derivado de la retención.
