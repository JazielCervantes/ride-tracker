import enum
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TripType(str, enum.Enum):
    individual = "individual"
    pair = "pair"
    triple = "triple"


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    trip_type = Column(Enum(TripType), nullable=False)
    client1_name = Column(String(100), nullable=False)
    client2_name = Column(String(100), nullable=True)
    client3_name = Column(String(100), nullable=True)
    amount_per_client = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    tip_amount = Column(Numeric(10, 2), nullable=False, server_default="0")
    week_start = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="trips")
