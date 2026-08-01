# Estados de una retención

<!-- DOCUMENTO DERIVADO — NO EDITAR A MANO -->
<!-- Se regenera con: python herramientas/generar_diagrama_estados.py -->

Este archivo representa el código vigente. No define reglas nuevas: las
reglas asociadas viven en `docs/contrato/reglas.md` y se referencian por
identificador.

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: crear_retencion
    ACTIVE --> CONFIRMED: confirmar_retencion
```

## Productores detectados

| Estado | Producido por |
|---|---|
| `ACTIVE` | `crear_retencion` en `app/infrastructure/repository.py` |
| `CONFIRMED` | `confirmar_retencion` en `app/infrastructure/repository.py` |
| `EXPIRED` | — sin productor detectado — |
| `RELEASED` | — sin productor detectado — |

## Estados sin productor detectado

No se detectaron asignaciones de los siguientes estados en los archivos
analizados de `app/`:

- `EXPIRED`
- `RELEASED`

Esto significa que el análisis estático no encontró código que los
produzca. **No significa que sean inalcanzables**: podrían escribirse
por SQL directo, por una migración o desde código fuera de `app/`.

## Supuestos del análisis

- `ACTIVE --> CONFIRMED` (confirmar_retencion en `app/infrastructure/repository.py`): el análisis detecta la asignación del estado destino pero no puede determinar el estado de origen. Se asume `ACTIVE`.

## Límite de la herramienta

El generador lee la estructura del código sin ejecutarlo. Puede afirmar
qué encontró; no puede afirmar que no exista lo que no encontró.
