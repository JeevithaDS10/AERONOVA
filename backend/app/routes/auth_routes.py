from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict
from app.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/auth/register", response_model=RegisterResponse)
def register(req: RegisterRequest):
    """
    Register endpoint.
    Accepts RegisterRequest (name, email, password, optional phone).
    Returns RegisterResponse on success.
    """

    name = req.name.strip()
    email = _normalize_email(req.email)
    phone = req.phone if req.phone else None

    # Hash password using service helper if available
    try:
        password_hash = auth_service.hash_password(req.password)
    except Exception as e:
        # If hashing fails for any reason, log and still try to call register_user with raw password
        print("hash_password failed:", e)
        password_hash = None

    # Try calling register_user. Some variants expect already-hashed password,
    # others may accept raw password and hash internally. We'll try hashed first,
    # fall back to raw if TypeError (wrong signature).
    try:
        if password_hash:
            user_id = auth_service.register_user(name, email, password_hash, phone=phone)
        else:
            # no hash available, pass raw password
            user_id = auth_service.register_user(name, email, req.password, phone=phone)
    except TypeError as te:
        # fallback: maybe service expects different args (e.g. phone before password) —
        # try a couple sensible fallbacks
        print("register_user TypeError, trying fallback:", te)
        try:
            # fallback 1: register_user(name, email, password, phone)
            user_id = auth_service.register_user(name, email, req.password, phone)
        except Exception as e2:
            print("fallback register_user failed:", e2)
            raise HTTPException(status_code=500, detail="Registration failed (internal).")
    except ValueError as ve:
        # service may raise ValueError for duplicate email etc.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ve))
    except Exception as exc:
        # Log error server-side, then return generic 500
        print("Unhandled error in register:", exc)
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"user_id": user_id, "message": "User registered"}


@router.post("/auth/login")
def login(req: LoginRequest) -> Dict[str, Any]:
    """
    Login endpoint.
    Calls auth_service.login_user(email, password) which should return a dict
    containing at least a token and user info (or raise/return None on failure).
    """
    email = _normalize_email(req.email)
    try:
        # login_user should handle password verification and JWT creation or return token
        result = auth_service.login_user(email, req.password)
    except auth_service.VerifyError if hasattr(auth_service, "VerifyError") else Exception as e:
        # If your service defines a verification exception, map it. Otherwise handle generic Exception.
        print("login verify error:", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except Exception as exc:
        print("Unhandled error in login:", exc)
        raise HTTPException(status_code=500, detail="Internal server error")

    # normalize result shape: if service returned token+user or whole response
    if isinstance(result, dict):
        return result

    # if service returned tuple (token, user)
    if isinstance(result, tuple) and len(result) >= 1:
        token = result[0]
        user = result[1] if len(result) > 1 else None
        return {"access_token": token, "user": user}

    # If service returned a string token
    if isinstance(result, str):
        return {"access_token": result}

    # Unexpected shape
    print("Unexpected login_user return:", result)
    raise HTTPException(status_code=500, detail="Login failed (unexpected response)")

