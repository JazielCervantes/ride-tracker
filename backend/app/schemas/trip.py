from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

# Alias to avoid Pydantic v2 annotation shadowing when field name == type name
_Date = date

# Límites alineados con las columnas de la BD (String(100) / Numeric(10,2)):
# validar acá devuelve un 422 claro en lugar de un error del motor MySQL.
_NAME_MAX = 100
_NOTES_MAX = 1000
_TIP_MAX = Decimal("99999.99")


class TripCreate(BaseModel):
    date: date
    trip_type: str
    client1_name: str = Field(min_length=1, max_length=_NAME_MAX)
    client2_name: Optional[str] = Field(None, max_length=_NAME_MAX)
    notes: Optional[str] = Field(None, max_length=_NOTES_MAX)

    client3_name: Optional[str] = Field(None, max_length=_NAME_MAX)
    tip_amount: Optional[Decimal] = Field(Decimal("0.00"), ge=0, le=_TIP_MAX)

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
    client1_name: Optional[str] = Field(None, min_length=1, max_length=_NAME_MAX)
    client2_name: Optional[str] = Field(None, max_length=_NAME_MAX)
    notes: Optional[str] = Field(None, max_length=_NOTES_MAX)

    client3_name: Optional[str] = Field(None, max_length=_NAME_MAX)
    tip_amount: Optional[Decimal] = Field(None, ge=0, le=_TIP_MAX)

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
