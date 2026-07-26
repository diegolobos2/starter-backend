"""
Adaptador de persistencia sobre SQLAlchemy / PostgreSQL.

Traduce entre modelos de persistencia (ORM, app.infrastructure.models)
y entidades de dominio (app.core.entities).

Esta clase es un "adaptador de salida": implementa el puerto
app.application.ports.HoldRepository. Application depende del puerto
(la interfaz), no de esta clase concreta. La dependencia apunta hacia
adentro (Infrastructure -> Application), respetando la regla de
dependencia de Clean Architecture.

Ver docs/contrato/arquitectura.md y docs/adr/ADR-002.md.
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.entities import Event, Hold, HoldStatus, Seat
from app.infrastructure.models import EventModel, HoldModel, SeatModel


def _event_from_model(m: EventModel) -> Event:
    return Event(id=m.id, name=m.name, starts_at=m.starts_at, ends_at=m.ends_at)


def _seat_from_model(m: SeatModel) -> Seat:
    return Seat(id=m.id, event_id=m.event_id, label=m.label)


def _hold_from_model(m: HoldModel) -> Hold:
    return Hold(
        id=m.id,
        event_id=m.event_id,
        seat_id=m.seat_id,
        status=HoldStatus(m.status),
        created_at=m.created_at,
    )


class SqlAlchemyHoldRepository:
    """
    Implementación concreta del puerto HoldRepository sobre SQLAlchemy.

    Recibe la Session en el constructor. Los casos de uso reciben una
    instancia de esta clase (o de cualquier otra que cumpla el puerto)
    y la usan sin conocer estos detalles.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def listar_eventos(self) -> list[Event]:
        modelos = self._session.scalars(select(EventModel)).all()
        return [_event_from_model(m) for m in modelos]

    def obtener_evento(self, event_id: str) -> Event | None:
        m = self._session.get(EventModel, event_id)
        return _event_from_model(m) if m else None

    def listar_butacas(self, event_id: str) -> list[Seat]:
        modelos = self._session.scalars(
            select(SeatModel).where(SeatModel.event_id == event_id)
        ).all()
        return [_seat_from_model(m) for m in modelos]

    def obtener_butaca(self, seat_id: str) -> Seat | None:
        m = self._session.get(SeatModel, seat_id)
        return _seat_from_model(m) if m else None

    def retenciones_activas_de_butaca(
        self, event_id: str, seat_id: str
    ) -> list[Hold]:
        modelos = self._session.scalars(
            select(HoldModel).where(
                HoldModel.event_id == event_id,
                HoldModel.seat_id == seat_id,
            )
        ).all()
        return [_hold_from_model(m) for m in modelos]

    def crear_retencion(
        self, event_id: str, seat_id: str, demora_didactica_seg: float = 0.0
    ) -> Hold:
        """
        Inserta una nueva retención.

        El parámetro demora_didactica_seg existe únicamente para poder
        ensanchar la ventana de la condición de carrera durante la
        demostración de la Semana 1 (tests/test_race_demo.py). En
        producción no debería usarse (o su valor por defecto debe ser 0).
        """
        if demora_didactica_seg:
            import time

            time.sleep(demora_didactica_seg)

        modelo = HoldModel(
            event_id=event_id,
            seat_id=seat_id,
            status=HoldStatus.ACTIVE.value,
            created_at=datetime.utcnow(),
        )
        self._session.add(modelo)
        self._session.commit()
        self._session.refresh(modelo)
        return _hold_from_model(modelo)

    def obtener_retencion(self, hold_id: str) -> Hold | None:
        m = self._session.get(HoldModel, hold_id)
        return _hold_from_model(m) if m else None

    def confirmar_retencion(self, hold_id: str) -> Hold | None:
        m = self._session.get(HoldModel, hold_id)
        if m is None:
            return None
        m.status = HoldStatus.CONFIRMED.value
        self._session.commit()
        self._session.refresh(m)
        return _hold_from_model(m)


def sembrar_datos_demo(session: Session) -> None:
    """
    Carga un evento y unas butacas de ejemplo si la base está vacía.

    Se mantiene como función suelta (no forma parte del puerto): es una
    utilidad de arranque/siembra, no una operación del caso de uso de
    retenciones.
    """
    if session.scalars(select(EventModel)).first() is not None:
        return

    evento = EventModel(
        id="evento-demo",
        name="Recital de ejemplo",
        starts_at=datetime.utcnow() + timedelta(days=7, hours=20),
        ends_at=datetime.utcnow() + timedelta(days=7, hours=22),
    )
    session.add(evento)

    for i in range(1, 6):
        session.add(
            SeatModel(id=f"butaca-{i}", event_id=evento.id, label=f"A{i}")
        )

    session.commit()
