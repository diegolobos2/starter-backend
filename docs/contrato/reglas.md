# Reglas y definiciones del dominio

Este documento reúne las decisiones funcionales vinculadas con las
**retenciones**. Por eso sus identificadores comienzan con `RET`.

`RET` no es una tecnología ni una categoría universal: es solamente el prefijo
que usa este proyecto para poder referenciar estas decisiones desde pruebas,
criterios de aceptación, ADR y trazabilidad.

Algunas entradas son reglas y otras son definiciones necesarias para entender
esas reglas. Se mantienen numeradas porque el resto del proyecto ya las
referencia de ese modo.

## Vocabulario usado por el proyecto

### Estado interno y estado público

El dominio usa internamente el estado `ACTIVE` para una retención temporal
vigente. La API lo traduce al estado público `HELD`, que resulta más claro para
Frontend.

```text
Dominio: ACTIVE  →  API: HELD
```

No se cambia ahora el nombre interno porque ya forma parte del código, las
pruebas y los diagramas. La traducción evita que ese detalle interno se filtre al
contrato público.

---

## RET-001 — Una butaca no puede quedar ocupada dos veces

Para un mismo evento y una misma butaca no puede existir más de una retención
que la mantenga ocupada.

La aplicación realiza una validación antes de crear la retención. Sin embargo,
dos solicitudes pueden consultar al mismo tiempo y encontrar la butaca libre.
Por eso, además de la validación en Python, el esquema de la base de datos debe
rechazar el segundo intento.

- **Se evalúa al:** crear una retención.
- **Riesgo principal:** solicitudes concurrentes.
- **Protección elegida:** validación en el core y restricción de unicidad en la
  base de datos.
- **Estado funcional:** vigente.

## RET-002 — Qué significa que una butaca esté ocupada

Esta entrada es una **definición asociada a RET-001**, no una regla independiente.

Una butaca está ocupada para un evento cuando existe una retención en alguno de
estos estados internos:

- `ACTIVE`: retención temporal vigente;
- `CONFIRMED`: retención confirmada.

Los estados siguientes no mantienen ocupada la butaca:

- `EXPIRED`;
- `RELEASED`.

Esta definición debe coincidir en todos los lugares donde el sistema calcula la
disponibilidad: el core, la persistencia, la API y la restricción del esquema.

### Decisión de modelado

En este proyecto una confirmación continúa siendo un estado de `Hold`. Otro
diseño podría crear una entidad distinta, como `Reservation`, `Booking` o
`Ticket`. Se conserva el modelo actual para no ampliar el alcance de la unidad.

## RET-003 — Solo una retención vigente puede confirmarse

Una retención puede confirmarse únicamente cuando está en estado `ACTIVE`.

Confirmar una retención `CONFIRMED`, `EXPIRED` o `RELEASED` es una operación
inválida y debe rechazarse.

- **Se evalúa al:** confirmar una retención.
- **Protección actual:** validación en el core.
- **Estado funcional:** vigente.

---

## Reglas todavía fuera de alcance

Las siguientes decisiones existen conceptualmente, pero no se implementan en la
Semana 3:

- vencimiento automático de una retención, que produciría `EXPIRED`;
- liberación explícita, que produciría `RELEASED`;
- márgenes de montaje y limpieza para una sala;
- capacidad máxima por evento.

Que no estén implementadas es una decisión de alcance. Las brechas se registran
en `docs/diagramas/estados_retencion.md` y en `TODO.md`.
