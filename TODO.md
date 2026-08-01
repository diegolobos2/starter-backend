# TODO — estado del proyecto

Este archivo registra estado y tareas. No define reglas ni arquitectura.

## Semana 2 — cerrada

- [x] Implementar ARQ-003 y ARQ-007 mediante puerto/adaptador.
- [x] Agregar verificaciones automáticas de ARQ-002, ARQ-003 y ARQ-006.
- [x] Separar documentación normativa, histórica y didáctica.
- [x] Subir el repositorio a GitHub.

## Semana 3 — en curso

El repositorio arranca la semana **con la suite en rojo**:
`tests/test_garantia_ret001.py` afirma una propiedad que el sistema todavía no
cumple. La semana termina cuando esa prueba pasa sin que se la haya modificado.

- [ ] Configurar Alembic y generar la migración inicial del esquema vigente.
- [ ] Migración que protege `RET-001` usando la definición de ocupación de `RET-002`.
- [ ] Quitar `create_all` del arranque de la aplicación.
- [ ] Traducir la violación de la restricción a excepción de dominio en el
      adaptador, con `rollback`.
- [ ] Implementar `RET-003` (transiciones válidas de confirmación).
- [ ] Adecuar las respuestas de error al formato de `contrato_api.md`
      (`code` + `message`).
- [ ] Agregar `DELETE /holds/{hold_id}` respondiendo `501 NOT_IMPLEMENTED`.
- [ ] Agregar la verificación automática de `ARQ-008`.
- [ ] Suite de integración contra PostgreSQL.

## Semana 4 — prevista

- [ ] Implementar `EXPIRED` (vencimiento de retenciones).
- [ ] Implementar `RELEASED` (`DELETE /holds/{hold_id}` real).
- [ ] Geometría de sala en `GET /events/{id}/seats` (v1.1 del contrato).
- [ ] Integración con el frontend.
- [ ] Demostración de actualización en tiempo real.
- [ ] TP integrador.

## Brechas conocidas, registradas y no resueltas

- `EXPIRED` y `RELEASED` están declarados en el enum y no se detectan productores
  reales en los archivos analizados. Ver `docs/diagramas/estados_retencion.md`.
- La suite emite advertencias de `datetime.utcnow()` y de `@app.on_event`, ambos
  obsoletos. No se corrigen en esta semana; quedan anotados para no confundir
  "conocido" con "inadvertido".
- `retenciones_activas_de_butaca` no filtra por estado: devuelve todas las
  retenciones de la butaca y el filtrado ocurre en el núcleo. El nombre no
  describe lo que hace.
