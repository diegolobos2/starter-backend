# Instrucciones para agentes

Este archivo define el **procedimiento de trabajo** del agente. No define
arquitectura, alcance ni reglas de negocio: esas decisiones tienen sus
documentos propietarios.

Los identificadores `RET-*` incluyen reglas y definiciones funcionales del área
de retenciones. El agente debe respetar su significado actual sin intentar
reclasificarlos o renumerarlos durante esta tarea.

## Antes de modificar el repositorio

1. Leer, en este orden:
   - `docs/contrato/alcance.md`;
   - `docs/contrato/reglas.md`;
   - `docs/contrato/arquitectura.md`;
   - `docs/contrato/contrato_api.md`;
   - `docs/contrato/base_de_datos.md`;
   - `docs/contrato/criterios_de_aceptacion.md`;
   - `docs/contrato/trazabilidad.md`.
2. Informar explícitamente qué archivos se leyeron.
3. Presentar un plan breve con:
   - archivos a crear o modificar;
   - propósito de cada cambio;
   - qué criterio `CA-*` satisface cada parte del plan;
   - riesgos o contradicciones detectadas entre documentos.

## Durante el cambio

1. Respetar las restricciones `ARQ-*` de `docs/contrato/arquitectura.md`.
2. Respetar las reglas `RET-*` de `docs/contrato/reglas.md`.
3. Respetar el contrato de `docs/contrato/contrato_api.md`. Rutas, códigos HTTP
   y códigos de error no se modifican sin modificar antes ese documento.
4. No ampliar el alcance sin modificar `docs/contrato/alcance.md`.
5. Cuando cambie una regla o restricción, modificar su documento propietario y
   actualizar trazabilidad, pruebas y diagramas afectados.
6. No duplicar definiciones normativas: referenciarlas por identificador.
7. No agregar dependencias o abstracciones sin justificar su necesidad y su
   costo.
8. Mantener cambios pequeños y verificables.
9. **No modificar los archivos de medición** listados en `CA-000` de
   `docs/contrato/criterios_de_aceptacion.md`. Si un cambio parece requerirlo,
   detenerse e informarlo en lugar de hacerlo.

## Antes de finalizar

1. Ejecutar las pruebas pertinentes.
2. Recorrer `docs/contrato/criterios_de_aceptacion.md` y declarar, criterio por
   criterio, si se cumple, no se cumple o no se verificó.
3. Informar:
   - qué cambió;
   - qué pruebas se ejecutaron y con qué resultado;
   - qué quedó pendiente;
   - cualquier diferencia respecto del plan inicial.
4. No declarar terminada una tarea cuyos criterios de aceptación no se
   comprobaron.
