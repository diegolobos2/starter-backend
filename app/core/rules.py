"""
Reglas de negocio del dominio.

RET-001
-------
Una butaca no puede tener dos retenciones activas para el mismo evento.

Ver docs/contrato/reglas.md y docs/contrato/trazabilidad.md.

IMPORTANTE (Semana 1):
Esta función expresa la regla de forma pura (sin I/O). Decide si, dado
el estado actual de retenciones para una butaca, se PUEDE crear una
nueva retención.

Lo que esta función NO resuelve es la condición de carrera: entre el
momento en que Application consulta las retenciones existentes y el
momento en que Infrastructure inserta la nueva retención, otra
petición concurrente puede colarse. Esa garantía se agrega recién en
la Semana 3, a nivel de infraestructura (constraint único o
transacción con bloqueo). Ver ADR-001.
"""

from app.core.entities import Hold, HoldStatus


class RetencionDuplicadaError(Exception):
    """Se intentó crear una retención para una butaca que ya tiene una activa."""


def puede_crear_retencion(retenciones_existentes: list[Hold]) -> bool:
    """
    RET-001: una butaca no puede tener dos retenciones activas
    para el mismo evento.

    Recibe las retenciones ya existentes para esa butaca+evento
    (decisión de qué retenciones son "existentes" la toma quien
    llama, típicamente Application vía Infrastructure) y decide si
    se puede crear una retención nueva.
    """
    activas = [r for r in retenciones_existentes if r.status == HoldStatus.ACTIVE]
    return len(activas) == 0


def validar_creacion_retencion(retenciones_existentes: list[Hold]) -> None:
    """
    Igual que puede_crear_retencion, pero lanza una excepción de
    dominio en lugar de devolver un booleano. Application decide
    cómo traducir esta excepción hacia afuera.
    """
    if not puede_crear_retencion(retenciones_existentes):
        raise RetencionDuplicadaError(
            "La butaca ya tiene una retención activa para este evento (RET-001)."
        )
