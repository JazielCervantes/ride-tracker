from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.schemas.trip import WeekSummary
from app.repositories import trip_repository
from app.services.week_service import get_week_start, get_week_end, get_payment_date
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/weeks", tags=["weeks"])


def _build_week_summary(
    db: Session, user_id: int, ws: date, include_trips: bool = False
) -> WeekSummary:
    agg = trip_repository.get_week_aggregate(db, user_id, ws)
    trips = trip_repository.get_by_week(db, user_id, ws) if include_trips else None
    return WeekSummary(
        week_start=ws,
        week_end=get_week_end(ws),
        payment_date=get_payment_date(ws),
        total_trips=agg["total_trips"],
        total_income=agg["total_income"],
        trips=trips,
    )


@router.get("", response_model=list[WeekSummary])
def list_weeks(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    weeks = trip_repository.get_distinct_weeks(db, current_user.id)
    return [_build_week_summary(db, current_user.id, ws) for ws in weeks]


@router.get("/current", response_model=WeekSummary)
def current_week(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ws = get_week_start(date.today())
    return _build_week_summary(db, current_user.id, ws, include_trips=True)


@router.get("/{week_start}", response_model=WeekSummary)
def week_detail(
    week_start: date,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _build_week_summary(db, current_user.id, week_start, include_trips=True)
