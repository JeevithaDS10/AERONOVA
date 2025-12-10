# app/routes/auth_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr

from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------- Pydantic models ----------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    # backend also enforces minimum length
    password: constr(min_length=8)


class RegisterResponse(BaseModel):
    user_id: int
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


# ---------- Routes ----------

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    """
    Register a new user.

    Frontend sends JSON:
    {
        "name": "Jeevitha D S",
        "email": "jeevi@example.com",
        "password": "StrongPass123"
    }
    """
    try:
        user_id = register_user(req.name, req.email, req.password)
        return RegisterResponse(
            user_id=user_id,
            message="User registered successfully",
        )
    except ValueError as e:
        # For example when email already exists
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Login with email + password.

    Frontend sends JSON:
    {
        "email": "jeevi@example.com",
        "password": "StrongPass123"
    }
    """
    result = login_user(req.email, req.password)
    if not result:
        # auth_service returns None on wrong email/password
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return LoginResponse(token=result["token"], user=result["user"])
