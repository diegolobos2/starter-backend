"""
Entidades y estados del dominio.

Este módulo no debe importar FastAPI, SQLAlchemy, psycopg ni ningún
detalle de infraestructura. Ver AGENTS.md y docs/contrato/arquitectura.md.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HoldStatus(str, Enum):
    """Estados posibles de una retención de butaca."""

    ACTIVE = "active"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    RELEASED = "released"


@dataclass(frozen=True)
class Event:
    id: str
    name: str
    starts_at: datetime
    ends_at: datetime


@dataclass(frozen=True)
class Seat:
    id: str
    event_id: str
    label: str


@dataclass(frozen=True)
class Hold:
    id: str
    event_id: str
    seat_id: str
    status: HoldStatus
    created_at: datetime
