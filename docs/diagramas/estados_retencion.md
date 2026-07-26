# Estados de una retención

Este archivo representa visualmente el código vigente. No define reglas nuevas.
Las reglas asociadas se referencian por identificador.

```mermaid
stateDiagram-v2
    [*] --> ACTIVE: crear [RET-001]
    ACTIVE --> CONFIRMED: confirmar
    ACTIVE --> EXPIRED: pendiente
    ACTIVE --> RELEASED: pendiente
    CONFIRMED --> [*]
    EXPIRED --> [*]
    RELEASED --> [*]
```

## Brechas detectadas

| Transición | Estado |
|---|---|
| `ACTIVE → CONFIRMED` | Implementada |
| `ACTIVE → EXPIRED` | Pendiente |
| `ACTIVE → RELEASED` | Pendiente |
