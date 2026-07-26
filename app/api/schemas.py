from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    starts_at: datetime
    ends_at: datetime


class SeatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    label: str


class HoldOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_id: str
    seat_id: str
    status: str
    created_at: datetime


class CreateHoldIn(BaseModel):
    seat_id: str
