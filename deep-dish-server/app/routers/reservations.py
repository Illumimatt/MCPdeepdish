import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from app.models import Reservation, ReservationCreate
from app.services.database import reservations_db, users_db

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=Reservation)
def create_reservation(res_in: ReservationCreate):
    # Verify user exists (optional business logic)
    if res_in.phone_number not in users_db:
        raise HTTPException(status_code=404, detail="User must be registered first")

    reservation_id = str(uuid.uuid4())
    new_reservation = Reservation(
        id=reservation_id,
        phone_number=res_in.phone_number,
        date_time=res_in.date_time,
        party_size=res_in.party_size,
        status="confirmed",
    )
    reservations_db[reservation_id] = new_reservation.model_dump()
    return new_reservation


@router.get("/{phone_number}", response_model=List[Reservation])
def get_user_reservations(phone_number: str):
    # Retrieve all reservations for a specific WhatsApp number
    user_res = [
        res for res in reservations_db.values() if res["phone_number"] == phone_number
    ]
    return user_res


@router.delete("/{reservation_id}")
def cancel_reservation(reservation_id: str):
    if reservation_id not in reservations_db:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservations_db[reservation_id]["status"] = "cancelled"
    return {
        "message": "Reservation cancelled successfully",
        "reservation": reservations_db[reservation_id],
    }
