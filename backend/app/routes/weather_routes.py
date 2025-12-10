# app/routes/weather_routes.py

from fastapi import APIRouter, HTTPException, Query
from app.services.weather_api_service import fetch_and_store_weather

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/current")
def get_weather(
    airport_code: str = Query(..., description="Airport code, e.g. BLR, DEL")
):
    try:
        simplified = fetch_and_store_weather(airport_code)
        return {
            "message": "Weather fetched successfully",
            "data": simplified,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
