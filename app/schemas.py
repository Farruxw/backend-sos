"""API kirish/chiqish shakllari (Pydantic). JSON maydonlari camelCase."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .models import Status


class CamelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel,
                              populate_by_name=True)


class NewCall(CamelModel):
    full_name: str | None = None
    phone: str | None = None
    address: str | None = None
    lat: float
    lng: float
    accuracy: float | None = None
    text: str = Field(min_length=1)


class CallOut(CamelModel):
    id: int
    full_name: str | None
    phone: str | None
    address: str | None
    lat: float
    lng: float
    accuracy: float | None
    text: str
    services: str | None
    severity: str | None
    ai_summary: str | None
    status: Status
    unit_id: int | None
    created_at: datetime
    arrived_at: datetime | None


class UnitOut(CamelModel):
    id: int
    name: str
    service: str
    lat: float
    lng: float
    busy: bool
    crew: str | None
    plate: str | None


class CallDetail(CamelModel):
    call: CallOut
    unit: UnitOut | None
    eta_minutes: int


class ChatIn(CamelModel):
    text: str = Field(min_length=1)


class ChatOut(CamelModel):
    id: int
    specialty: str
    sender: str
    text: str
    created_at: datetime
