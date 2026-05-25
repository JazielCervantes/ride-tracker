from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class TripCreate(BaseModel):
    date: date
    trip_type: str
    client1_name: str
    client2_name: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("trip_type")
    @classmethod
    def validate_trip_type(cls, v):
        if v not in ("individual", "pair"):
            raise ValueError("trip_type debe ser 'individual' o 'pair'")
        return v

    @model_validator(mode="after")
    def pair_requires_client2(self):
        if self.trip_type == "pair" and not self.client2_name:
            raise ValueError("Se requiere client2_name para viajes en par")
        return self


class TripUpdate(BaseModel):
    date: Optional[date] = None
    trip_type: Optional[str] = None
    client1_name: Optional[str] = None
    client2_name: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("trip_type")
    @classmethod
    def validate_trip_type(cls, v):
        if v is not None and v not in ("individual", "pair"):
            raise ValueError("trip_type debe ser 'individual' o 'pair'")
        return v


class TripOut(BaseModel):
    id: int
    user_id: int
    date: date
    trip_type: str
    client1_name: str
    client2_name: Optional[str]
    amount_per_client: Decimal
    total_amount: Decimal
    week_start: date
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class WeekSummary(BaseModel):
    week_start: date
    week_end: date
    payment_date: date
    total_trips: int
    total_income: Decimal
    trips: Optional[list["TripOut"]] = None
