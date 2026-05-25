from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.trip import Trip
from datetime import date
from typing import Optional
from decimal import Decimal


def get_all_by_user(db: Session, user_id: int) -> list[Trip]:
    return (
        db.query(Trip)
        .filter(Trip.user_id == user_id)
        .order_by(Trip.date.desc(), Trip.created_at.desc())
        .all()
    )


def get_by_week(db: Session, user_id: int, week_start: date) -> list[Trip]:
    return (
        db.query(Trip)
        .filter(Trip.user_id == user_id, Trip.week_start == week_start)
        .order_by(Trip.date.desc(), Trip.created_at.desc())
        .all()
    )


def get_by_date(db: Session, user_id: int, trip_date: date) -> list[Trip]:
    return (
        db.query(Trip)
        .filter(Trip.user_id == user_id, Trip.date == trip_date)
        .order_by(Trip.created_at.desc())
        .all()
    )


def get_by_id(db: Session, trip_id: int, user_id: int) -> Optional[Trip]:
    return db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()


def create(db: Session, trip: Trip) -> Trip:
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def update(db: Session, trip: Trip) -> Trip:
    db.commit()
    db.refresh(trip)
    return trip


def delete(db: Session, trip: Trip) -> None:
    db.delete(trip)
    db.commit()


def get_distinct_weeks(db: Session, user_id: int) -> list[date]:
    rows = (
        db.query(Trip.week_start)
        .filter(Trip.user_id == user_id)
        .distinct()
        .order_by(Trip.week_start.desc())
        .all()
    )
    return [r.week_start for r in rows]


def get_week_aggregate(db: Session, user_id: int, week_start: date) -> dict:
    result = (
        db.query(
            func.count(Trip.id).label("total_trips"),
            func.sum(Trip.total_amount).label("total_income"),
            func.sum(Trip.tip_amount).label("total_tips"),
        )
        .filter(Trip.user_id == user_id, Trip.week_start == week_start)
        .first()
    )
    return {
        "total_trips": result.total_trips or 0,
        "total_income": Decimal(str(result.total_income or 0)),
        "total_tips": Decimal(str(result.total_tips or 0)),
    }
