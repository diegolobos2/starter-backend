"""
Puertos de la capa Application.

Un "puerto" es una interfaz (contrato) que Application define para
expresar QUÉ necesita de una fuente externa, sin comprometerse con
CÓMO se implementa. La implementación concreta (el "adaptador") vive
en app/infrastructure y cumple este contrato.

Por qué el puerto vive acá y no en app/core:
    Quien tiene la necesidad de consultar y persistir retenciones es el
    caso de uso (Application), no la regla de negocio pura (Core). El
    core decide con datos que ya recibe por parámetro; nunca sale a
    buscarlos. Por eso el puerto pertenece a Application.

Por qué esto respeta la regla de dependencia (Clean Architecture):
    Application define la interfaz; Infrastructure la implementa. La
    dependencia apunta hacia adentro: Infrastructure conoce a
    Application (porque cumple su contrato), no al revés. Application
    ya no importa nada concreto de Infrastructure. Esto es el
    Dependency Inversion Principle.

Ver docs/contrato/arquitectura.md y docs/adr/ADR-002.md.
"""

from typing import Protocol

from app.core.entities import Event, Hold, Seat


class HoldRepository(Protocol):
    """
    Contrato de persistencia que necesita el caso de uso de retenciones.

    Cualquier clase que implemente estos métodos (con estas firmas)
    puede ser usada por Application, sin que Application sepa si detrás
    hay PostgreSQL, SQLite, o una implementación en memoria para tests.
    """

    def listar_eventos(self) -> list[Event]: ...

    def obtener_evento(self, event_id: str) -> Event | None: ...

    def listar_butacas(self, event_id: str) -> list[Seat]: ...

    def obtener_butaca(self, seat_id: str) -> Seat | None: ...

    def retenciones_activas_de_butaca(
        self, event_id: str, seat_id: str
    ) -> list[Hold]: ...

    def crear_retencion(
        self, event_id: str, seat_id: str, demora_didactica_seg: float = 0.0
    ) -> Hold: ...

    def obtener_retencion(self, hold_id: str) -> Hold | None: ...

    def confirmar_retencion(self, hold_id: str) -> Hold | None: ...
