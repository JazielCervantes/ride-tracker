from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal
from app.models.trip import Trip, TripType
from app.schemas.trip import TripCreate, TripUpdate
from app.repositories import trip_repository
from app.services.week_service import get_week_start

PRICE_INDIVIDUAL = Decimal("30.00")
PRICE_PAIR = Decimal("25.00")
PRICE_TRIPLE = Decimal("25.00")


def _calculate_amounts(trip_type: str) -> tuple[Decimal, Decimal]:
    """Devuelve (amount_per_client, total_amount)."""
    if trip_type == TripType.individual:
        return PRICE_INDIVIDUAL, PRICE_INDIVIDUAL
    if trip_type == TripType.triple:
        return PRICE_TRIPLE, PRICE_TRIPLE * 3
    return PRICE_PAIR, PRICE_PAIR * 2


def create_trip(db: Session, user_id: int, data: TripCreate) -> Trip:
    amount_per_client, total_amount = _calculate_amounts(data.trip_type)
    week_start = get_week_start(data.date)
    trip = Trip(
        user_id=user_id,
        date=data.date,
        trip_type=data.trip_type,
        client1_name=data.client1_name,
        client2_name=data.client2_name,
        client3_name=data.client3_name,
        amount_per_client=amount_per_client,
        total_amount=total_amount,
        tip_amount=data.tip_amount or Decimal("0.00"),
        week_start=week_start,
        notes=data.notes,
    )
    return trip_repository.create(db, trip)


def update_trip(db: Session, trip_id: int, user_id: int, data: TripUpdate) -> Trip:
    trip = trip_repository.get_by_id(db, trip_id, user_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    if data.date is not None:
        trip.date = data.date
        trip.week_start = get_week_start(data.date)

    if data.trip_type is not None:
        trip.trip_type = data.trip_type
        amount_per_client, total_amount = _calculate_amounts(data.trip_type)
        trip.amount_per_client = amount_per_client
        trip.total_amount = total_amount
        if data.trip_type == "individual":
            trip.client2_name = None
            trip.client3_name = None
        elif data.trip_type == "pair":
            trip.client3_name = None

    if data.client1_name is not None:
        trip.client1_name = data.client1_name

    if data.client2_name is not None:
        trip.client2_name = data.client2_name

    if data.client3_name is not None:
        trip.client3_name = data.client3_name

    if data.tip_amount is not None:
        trip.tip_amount = data.tip_amount

    if data.notes is not None:
        trip.notes = data.notes or None

    return trip_repository.update(db, trip)


def delete_trip(db: Session, trip_id: int, user_id: int) -> None:
    trip = trip_repository.get_by_id(db, trip_id, user_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    trip_repository.delete(db, trip)


def get_trips(db: Session, user_id: int, week_start=None) -> list[Trip]:
    if week_start:
        return trip_repository.get_by_week(db, user_id, week_start)
    return trip_repository.get_all_by_user(db, user_id)
