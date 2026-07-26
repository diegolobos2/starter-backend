# Instrucciones del proyecto

Este archivo existe por compatibilidad con GitHub Copilot (mismo
mecanismo que usaron en la Unidad 1, en `TaskMind-API`).

**La fuente de verdad de este proyecto es `AGENTS.md`, en la raíz
del repositorio.** Léanlo primero.

La diferencia con la Unidad 1 no es la herramienta — es qué tan
verificable es lo que le pedimos al agente. En `TaskMind-API` las
reglas eran una lista de buenas intenciones ("arquitectura limpia",
"todo async") que nadie volvía a comprobar. Acá cada regla de
`AGENTS.md` tiene una forma de chequearse: responsabilidades por
carpeta, prohibiciones de importación entre capas, trazabilidad de
reglas de negocio (`docs/trazabilidad_reglas.md`), y una suite de
tests que debe quedar en verde.
