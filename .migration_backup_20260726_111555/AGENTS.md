# AGENTS.md

## Propósito

Este repositorio es un starter didáctico para enseñar arquitectura y gobernanza de backend desarrollado con IA.

La prioridad no es generar mucho código, sino mantener el sistema comprensible, verificable y proporcional al problema.

## Reglas de trabajo

1. Antes de modificar archivos, presentar un plan breve con:
   - archivos a crear;
   - archivos a modificar;
   - responsabilidades de cada cambio;
   - riesgos o contradicciones detectadas.

2. Respetar las responsabilidades:
   - `app/api`: HTTP, validación de entrada y respuestas;
   - `app/application`: coordinación de casos de uso;
   - `app/core`: conceptos, estados y decisiones independientes;
   - `app/infrastructure`: persistencia, PostgreSQL, SQLAlchemy y servicios externos.

3. `app/core` no debe importar:
   - FastAPI;
   - SQLAlchemy;
   - psycopg;
   - detalles concretos de infraestructura.

4. No colocar:
   - consultas SQL en endpoints;
   - reglas de negocio profundas en `api`;
   - detalles HTTP en `application`;
   - decisiones de negocio estables en `infrastructure`.

5. No agregar capas ceremoniales.
   Una clase, interfaz o módulo nuevo debe:
   - tener una responsabilidad distinguible;
   - proteger una frontera;
   - o aportar una garantía necesaria.
   Si solo reenvía llamadas, probablemente sobra.

6. No agregar dependencias sin justificar:
   - qué problema resuelven;
   - por qué la biblioteca estándar o las dependencias actuales no alcanzan;
   - qué costo conceptual u operativo agregan.

7. Cuando se crea o modifica una regla de negocio:
   - actualizar `docs/reglas.md`;
   - actualizar `docs/trazabilidad_reglas.md`;
   - actualizar diagramas si corresponde;
   - agregar o ajustar pruebas.

8. Mantener coherencia entre:
   - reglas;
   - diagramas;
   - contrato OpenAPI;
   - modelo de datos;
   - código;
   - tests.

9. La suite normal debe quedar en verde.

10. La prueba marcada `race_demo` es una demostración didáctica separada:
    - puede fallar deliberadamente en la Semana 1;
    - no debe ejecutarse dentro de la suite habitual;
    - no debe resolverse la concurrencia hasta la Semana 3.

11. Mantener cambios pequeños y verificables.

12. Al terminar una modificación:
    - ejecutar las pruebas pertinentes;
    - informar qué se cambió;
    - indicar qué quedó pendiente;
    - señalar cualquier diferencia entre el plan inicial y la implementación final.