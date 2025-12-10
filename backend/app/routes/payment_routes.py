# app/routes/payment_routes.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator

from app.security import verify_jwt
from app.services.payment_service import create_payment

router = APIRouter(prefix="/payments", tags=["Payments"])

security = HTTPBearer()


# ---------- Auth helper (same style as bookings) ----------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = verify_jwt(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ---------- Request model ----------

class PaymentRequest(BaseModel):
    booking_id: int
    amount: float
    method: str  # "UPI" or "CARD"
    upi_id: str | None = None
    card_number: str | None = None
    card_expiry: str | None = None
    card_cvv: str | None = None

    @field_validator("method")
    @classmethod
    def normalize_method(cls, v: str):
        return v.upper()


@router.post("/pay")
def pay(
    req: PaymentRequest,
    user: dict = Depends(get_current_user)
):
    """
    Simulated payment endpoint.

    - Requires JWT (user must be logged in)
    - Encrypts UPI / Card details
    - Stores payment in DB with status=SUCCESS
    - Returns transaction_id (HMAC) for reference
    """
    user_id = user.get("user_id")

    try:
        result = create_payment(
            user_id=user_id,
            booking_id=req.booking_id,
            amount=req.amount,
            method=req.method,
            upi_id=req.upi_id,
            card_number=req.card_number,
            card_expiry=req.card_expiry,
            card_cvv=req.card_cvv,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # For UI, we can return masked info (no raw details)
    response = {
        "message": "Payment processed (simulated)",
        "payment_id": result["payment_id"],
        "transaction_id": result["transaction_id"],
        "status": result["status"],
        "method": result["method"],
        "amount": result["amount"],
        "paid_at": result["paid_at"],
    }

    return response
