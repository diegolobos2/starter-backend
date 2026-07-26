# Reglas de negocio

Este documento es la única fuente normativa de las reglas del dominio.
Implementación, endpoints y pruebas se registran en
`docs/contrato/trazabilidad.md`, sin repetir el enunciado.

## RET-001 — Unicidad de retención activa

Una butaca no puede tener más de una retención activa para el mismo evento.

- **Tipo:** invariante del dominio.
- **Momento de evaluación:** creación de una retención.
- **Estado funcional:** vigente.
