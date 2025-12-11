# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr

from app.models import RegisterRequest  # your Pydantic model

# import the actual functions your service exposes
from app.services.auth_service import register_user, login_user, generate_jwt

router = APIRouter(prefix="/auth", tags=["auth"])







# --- request/response schemas (adjust as needed) ---
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)
    phone: str | None = None  # optional


class RegisterResponse(BaseModel):
    user_id: int
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


# --- routes ---

@router.post("/auth/register")
def register(req: RegisterRequest):
    try:
        # normalize email
        email_norm = req.email.strip().lower()
        password_hash = hash_password(req.password)  # use your existing hash function
        user_id = register_user(req.name, email_norm, password_hash, phone=req.phone)
        return {"user_id": user_id, "message": "User registered"}
    except ValueError as e:
        # Duplicate email -> 409
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as exc:
        # Log and return generic error so SQL internal errors are not leaked to frontend
        print("Registration error:", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Login using login_user from auth_service.
    login_user should return user dict on success, or None/raise on failure.
    """
    user = login_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # generate_jwt: pass whatever ID or payload your function expects.
    # common pattern: generate_jwt(user_id)  — adapt if your generate_jwt expects different.
    uid = user.get("user_id") or user.get("id") or user.get("userId")
    token = generate_jwt(uid if uid is not None else user)

    return LoginResponse(token=token, user=user)
