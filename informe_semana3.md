# Informe de evidencia — Semana 3

**10 de 11 verificaciones en verde** (0 en rojo, 1 sin evaluar).

```mermaid
flowchart TD
    subgraph Contexto["Contexto — lo que el agente puede leer"]
        direction LR
        CTX["✅ CTX<br/>Documentos del contexto presentes"]:::ok
    end
    subgraph Verificaciones["Verificaciones — avisan si algo se rompió"]
        direction LR
        CA_004["✅ CA-004<br/>Suite completa en verde"]:::ok
        CA_001["✅ CA-001<br/>Árbitro: garantía de RET-001"]:::ok
        CA_009["✅ CA-009<br/>Restricciones ARQ vigentes"]:::ok
        CA_010["✅ CA-010<br/>ARQ-008: la persistencia no se filtra"]:::ok
        CA_013["✅ CA-013<br/>Documento derivado sincronizado"]:::ok
    end
    subgraph Garantias["Garantías — impiden que se rompa"]
        direction LR
        CA_005["✅ CA-005<br/>Restricción de unicidad en el esquema"]:::ok
        CA_007["✅ CA-007<br/>create_all fuera del arranque"]:::ok
        CA_006["✅ CA-006<br/>Migraciones Alembic"]:::ok
    end
    subgraph Contrato["Contrato — lo que promete al consumidor"]
        direction LR
        CA_011["✅ CA-011<br/>Rutas del contrato en OpenAPI"]:::ok
    end
    subgraph Alcance["Alcance — cuánto tocó"]
        direction LR
        CA_016["➖ CA-016<br/>Alcance del cambio"]:::na
    end
    Contexto --> Verificaciones
    Verificaciones --> Garantias
    Garantias --> Contrato
    Contrato --> Alcance
    classDef ok fill:#d8f3dc,stroke:#2d6a4f,color:#1b4332;
    classDef falla fill:#ffccd5,stroke:#c9184a,color:#590d22;
    classDef na fill:#e9ecef,stroke:#6c757d,color:#343a40;
```

## Detalle

| | ID | Verificación | Resultado |
|---|---|---|---|
| ✅ | `CTX` | Documentos del contexto presentes | todos presentes |
| ✅ | `CA-004` | Suite completa en verde | 21 passed, 1 deselected, 37 warnings in 1.70s |
| ✅ | `CA-001` | Árbitro: garantía de RET-001 | 5 passed, 13 warnings in 0.96s |
| ✅ | `CA-009` | Restricciones ARQ vigentes | 3 passed in 0.01s |
| ✅ | `CA-010` | ARQ-008: la persistencia no se filtra | sin violaciones |
| ✅ | `CA-013` | Documento derivado sincronizado | El diagrama commiteado coincide con el código. |
| ✅ | `CA-005` | Restricción de unicidad en el esquema | uq_holds_event_seat_active (parcial por estado) |
| ✅ | `CA-007` | create_all fuera del arranque | no aparece en main.py |
| ✅ | `CA-006` | Migraciones Alembic | 1 migración(es): 0001_add_holds_unique.py |
| ✅ | `CA-011` | Rutas del contrato en OpenAPI | todas presentes |
| ➖ | `CA-016` | Alcance del cambio | no se indicó --base; ejecutar con --base <commit> para medirlo |

## Qué NO dice este informe

Este informe reúne evidencia sobre propiedades concretas y verificables.
No dice nada sobre la legibilidad del código, la calidad de los mensajes
de error, el rendimiento, el comportamiento de la migración sobre datos
preexistentes inválidos, ni sobre la existencia de otras condiciones de
carrera en operaciones no cubiertas.

Un tablero en verde significa que el sistema es correcto **respecto de lo
que estas verificaciones comprueban**. Nada más, y nada menos.
