# api_main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.db import get_connection

from app.routes.auth_routes import router as auth_router
from app.routes.flight_routes import router as flight_router
from app.routes.booking_routes import router as booking_router
from app.routes.payment_routes import router as payment_router
from app.routes.weather_routes import router as weather_router
from app.routes.price_routes import router as price_router


app = FastAPI(
    title="AirNova Flight System API",
    version="1.0.0",
)

# ------------ CORS CONFIG ------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # React dev server
    allow_credentials=True,
    allow_methods=["*"],         # VERY IMPORTANT (includes OPTIONS)
    allow_headers=["*"],         # Allow Content-Type, Authorization, etc
)
# -------------------------------------

# -------------------------------------



@app.get("/")
def read_root():
    return {"message": "Welcome to AirNova API. Server is running."}


@app.get("/health/db")
def db_health_check():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "ok", "db_result": res[0]}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)},
        )


# Routers
app.include_router(auth_router)
app.include_router(flight_router)
app.include_router(booking_router)
app.include_router(payment_router) 
app.include_router(weather_router)
app.include_router(price_router)

