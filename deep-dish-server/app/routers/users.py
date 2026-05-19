from fastapi import APIRouter, HTTPException

from app.models import User
from app.services.database import users_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=User)
def create_user(user: User):
    if user.phone_number in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[user.phone_number] = user.model_dump()
    return users_db[user.phone_number]


@router.get("/{phone_number}", response_model=User)
def get_user(phone_number: str):
    user = users_db.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
