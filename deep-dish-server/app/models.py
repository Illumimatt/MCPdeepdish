from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    phone_number: str = Field(..., description="WhatsApp number used as the unique ID")
    name: str


class ReservationCreate(BaseModel):
    phone_number: str
    date_time: datetime
    party_size: int


class Reservation(ReservationCreate):
    id: str
    status: str = "confirmed"  # Can be 'confirmed', 'cancelled', or 'completed'
