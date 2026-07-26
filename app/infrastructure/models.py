"""
Modelos de persistencia (SQLAlchemy).

Estos modelos son detalle de infraestructura. No son las entidades
de dominio (ver app/core/entities.py). Application y Core no deben
importar este módulo directamente.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class SeatModel(Base):
    __tablename__ = "seats"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)


class HoldModel(Base):
    __tablename__ = "holds"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"), nullable=False)
    seat_id: Mapped[str] = mapped_column(ForeignKey("seats.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # NOTA (Semana 1 -> Semana 3):
    # Acá es donde eventualmente se agrega una restricción única
    # condicional (o se resuelve por transacción/bloqueo) para
    # garantizar RET-001 bajo concurrencia. Deliberadamente ausente
    # en la Semana 1. Ver ADR-001 y docs/contrato/alcance.md.
