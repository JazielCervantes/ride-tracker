from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.database import get_db
from app.schemas.trip import TripCreate, TripUpdate, TripOut
from app.services.trip_service import create_trip, update_trip, delete_trip, get_trips
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripOut])
def list_trips(
    week_start: Optional[date] = Query(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_trips(db, current_user.id, week_start)


@router.post("", response_model=TripOut, status_code=201)
def create_trip_route(
    data: TripCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_trip(db, current_user.id, data)


@router.put("/{trip_id}", response_model=TripOut)
def update_trip_route(
    trip_id: int,
    data: TripUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_trip(db, trip_id, current_user.id, data)


@router.delete("/{trip_id}", status_code=204)
def delete_trip_route(
    trip_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_trip(db, trip_id, current_user.id)
