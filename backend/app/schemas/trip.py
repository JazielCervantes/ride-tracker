from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# Alias to avoid Pydantic v2 annotation shadowing when field name == type name
_Date = date


class TripCreate(BaseModel):
    date: date
    trip_type: str
    client1_name: str
    client2_name: Optional[str] = None
    notes: Optional[str] = None

    client3_name: Optional[str] = None
    tip_amount: Optional[Decimal] = Decimal("0.00")

    @field_validator("trip_type")
    @classmethod
    def validate_trip_type(cls, v):
        if v not in ("individual", "pair", "triple"):
            raise ValueError("trip_type debe ser 'individual', 'pair' o 'triple'")
        return v

    @model_validator(mode="after")
    def validate_clients(self):
        if self.trip_type in ("pair", "triple") and not self.client2_name:
            raise ValueError("Se requiere client2_name para viajes en par o triple")
        if self.trip_type == "triple" and not self.client3_name:
            raise ValueError("Se requiere client3_name para viajes triple")
        return self


class TripUpdate(BaseModel):
    date: Optional[_Date] = None
    trip_type: Optional[str] = None
    client1_name: Optional[str] = None
    client2_name: Optional[str] = None
    notes: Optional[str] = None

    client3_name: Optional[str] = None
    tip_amount: Optional[Decimal] = None

    @field_validator("trip_type")
    @classmethod
    def validate_trip_type(cls, v):
        if v is not None and v not in ("individual", "pair", "triple"):
            raise ValueError("trip_type debe ser 'individual', 'pair' o 'triple'")
        return v


class TripOut(BaseModel):
    id: int
    user_id: int
    date: date
    trip_type: str
    client1_name: str
    client2_name: Optional[str]
    client3_name: Optional[str]
    amount_per_client: Decimal
    total_amount: Decimal
    tip_amount: Decimal = Decimal("0.00")
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
    total_tips: Decimal = Decimal("0.00")
    trips: Optional[list["TripOut"]] = None
