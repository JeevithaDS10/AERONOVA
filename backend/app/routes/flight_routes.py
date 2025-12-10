# app/routes/flight_routes.py

from fastapi import APIRouter, HTTPException, Query
from app.services.flight_service import search_flights

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/search")
def search_flights_api(
    source: str = Query(..., description="Source airport code, e.g. BLR"),
    destination: str = Query(..., description="Destination airport code, e.g. DEL"),
    date: str = Query(..., description="Flight date in YYYY-MM-DD format, e.g. 2025-12-10"),
):
    """
    Search for flights between two airports on a given date.
    """

    flights = search_flights(source, destination, date)

    if not flights:
        raise HTTPException(status_code=404, detail="No flights found")

    return {
        "count": len(flights),
        "flights": flights,
    }
