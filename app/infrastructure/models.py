"""
Modelos de persistencia (SQLAlchemy).

Estos modelos son detalle de infraestructura. No son las entidades
de dominio (ver app/core/entities.py). Application y Core no deben
importar este módulo directamente.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Index, text
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

    # Garantía de RET-001 (Semana 3): índice único parcial. Solo los estados
    # que mantienen la butaca ocupada participan de la unicidad, de modo que
    # una butaca liberada o vencida vuelve a poder retenerse.
    # Ver ADR-003 y docs/contrato/base_de_datos.md.
    Index(
        "uq_holds_event_seat_active",
        event_id,
        seat_id,
        unique=True,
        sqlite_where=text("status IN ('active','confirmed')"),
        postgresql_where=text("status IN ('active','confirmed')"),
    )
