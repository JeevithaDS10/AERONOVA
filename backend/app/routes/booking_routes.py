# app/routes/booking_routes.py

from typing import List

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services.booking_service import create_booking, get_user_bookings
from app.security import verify_jwt

router = APIRouter(prefix="/bookings", tags=["Bookings"])

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Extracts and verifies JWT from Authorization: Bearer <token>.
    Returns decoded payload (dict with user_id, email, role...) if valid.
    """
    token = credentials.credentials
    payload = verify_jwt(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


class Passenger(BaseModel):
    name: str
    age: int
    id_proof: str
    contact: str


class BookingRequest(BaseModel):
    flight_id: int
    seat_no: str
    price_paid: float
    passengers: List[Passenger]


@router.post("/create")
def create_booking_api(
    req: BookingRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create a booking for the logged-in user.
    Uses existing create_booking(user_id, flight_id, seat_no, passengers, price_paid)
    from booking_service.py
    """
    user_id = user.get("user_id")

    passenger_dicts = [p.model_dump() for p in req.passengers]

    try:
        booking_id, booking_token = create_booking(
            user_id=user_id,
            flight_id=req.flight_id,
            seat_no=req.seat_no,
            passengers=passenger_dicts,
            price_paid=req.price_paid
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Booking created successfully",
        "booking_id": booking_id,
        "booking_token": booking_token,
    }


@router.get("/my")
def get_my_bookings(
    user: dict = Depends(get_current_user)
):
    """
    Return all bookings for the logged-in user.
    Uses get_user_bookings(user_id) from booking_service.py
    """
    user_id = user.get("user_id")
    bookings = get_user_bookings(user_id)
    return {"bookings": bookings}
