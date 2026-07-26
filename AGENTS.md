# Instrucciones para agentes

Este archivo define el **procedimiento de trabajo** del agente. No define
arquitectura, alcance ni reglas de negocio: esas decisiones tienen sus
documentos propietarios.

## Antes de modificar el repositorio

1. Leer:
   - `docs/contrato/alcance.md`;
   - `docs/contrato/arquitectura.md`;
   - `docs/contrato/reglas.md`;
   - `docs/contrato/trazabilidad.md`.
2. Presentar un plan breve con:
   - archivos a crear o modificar;
   - propósito de cada cambio;
   - riesgos o contradicciones detectadas.

## Durante el cambio

1. Respetar las restricciones `ARQ-*` de
   `docs/contrato/arquitectura.md`.
2. Respetar las reglas `RET-*` de `docs/contrato/reglas.md`.
3. No ampliar el alcance sin modificar `docs/contrato/alcance.md`.
4. Cuando cambie una regla o restricción, modificar su documento
   propietario y actualizar trazabilidad, pruebas y diagramas afectados.
5. No duplicar definiciones normativas: referenciarlas por identificador.
6. No agregar dependencias o abstracciones sin justificar su necesidad y
   su costo.
7. Mantener cambios pequeños y verificables.

## Antes de finalizar

1. Ejecutar las pruebas pertinentes.
2. Informar:
   - qué cambió;
   - qué pruebas se ejecutaron;
   - qué quedó pendiente;
   - cualquier diferencia respecto del plan inicial.
