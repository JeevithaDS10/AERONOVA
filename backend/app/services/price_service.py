# app/services/price_service.py

from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any

import joblib

from app.db import get_connection
from app.services.weather_api_service import fetch_and_store_weather

# Global model cache, so we don't reload model on every request
_model = None
MODEL_PATH = Path("app/ml/model/price_model.pkl")


def get_model():
    """Load the trained price model from disk (if not already loaded)."""
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(
                f"Price model file not found at {MODEL_PATH}. "
                "Train the model first with train_price_model.py."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def compute_route_popularity(source: str, destination: str) -> float:
    """
    Same logic we used during synthetic data generation.
    This keeps training-time and prediction-time consistent.
    """
    seed = (len(source) + len(destination)) % 10
    base = 0.3 + (seed / 10) * 0.7  # 0.3 - 1.0
    return round(base, 2)


def get_flight_context(flight_id: int) -> Dict[str, Any]:
    """
    Fetch flight info + route info from DB and compute:
    - base_price
    - departure_date
    - days_to_departure
    - is_weekend
    - route_popularity
    - seats_left (approx, based on bookings)
    - delay_risk (from weather service)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # 1) Get flight + route info
    cursor.execute(
        """
        SELECT
            f.flight_id,
            f.departure_time,
            f.base_price,
            r.source_airport,
            r.destination_airport
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        WHERE f.flight_id = %s
        """,
        (flight_id,),
    )
    flight = cursor.fetchone()

    if not flight:
        cursor.close()
        conn.close()
        raise ValueError(f"Flight with id {flight_id} not found")

    # 2) Compute days_to_departure & weekend
    departure_dt: datetime = flight["departure_time"]
    departure_date = departure_dt.date()
    today = date.today()

    days_to_departure = max((departure_date - today).days, 0)
    is_weekend = 1 if departure_date.weekday() >= 5 else 0

    # 3) Approximate seats_left from bookings
    # We assume a fixed capacity of 180 (same as in generator)
    TOTAL_SEATS = 180

    cursor.execute(
        """
        SELECT COUNT(*) AS booked_count
        FROM bookings
        WHERE flight_id = %s
        """,
        (flight_id,),
    )
    row = cursor.fetchone()
    booked_count = row["booked_count"] if row and row["booked_count"] is not None else 0
    seats_left = max(TOTAL_SEATS - booked_count, 0)

    # 4) Route popularity
    source = flight["source_airport"]
    dest = flight["destination_airport"]
    route_popularity = compute_route_popularity(source, dest)

    # 5) Delay risk from weather service
    # We use source airport code for weather
    try:
        weather_info = fetch_and_store_weather(source)
        delay_risk = weather_info.get("delay_risk", "MEDIUM")
    except Exception:
        # If weather API fails, fall back to MEDIUM
        delay_risk = "MEDIUM"

    cursor.close()
    conn.close()

    return {
        "flight_id": flight_id,
        "base_price": float(flight["base_price"]),
        "days_to_departure": days_to_departure,
        "seats_left": seats_left,
        "is_weekend": is_weekend,
        "delay_risk": delay_risk,
        "route_popularity": route_popularity,
    }


def map_delay_risk_to_num(delay_risk: str) -> int:
    """Convert delay_risk string to numeric, just like in training."""
    risk_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    return risk_map.get(delay_risk.upper(), 1)  # default MEDIUM


def predict_price_for_flight(flight_id: int) -> Dict[str, Any]:
    """
    Main function called by FastAPI route.
    1) Get context for this flight
    2) Build feature vector
    3) Call ML model
    4) Return prediction + details
    """
    model = get_model()
    ctx = get_flight_context(flight_id)

    delay_risk_num = map_delay_risk_to_num(ctx["delay_risk"])

    # Features must be in same order as training:
    # ["base_price", "days_to_departure", "seats_left",
    #  "is_weekend", "delay_risk_num", "route_popularity"]
    features = [[
        ctx["base_price"],
        ctx["days_to_departure"],
        ctx["seats_left"],
        ctx["is_weekend"],
        delay_risk_num,
        ctx["route_popularity"],
    ]]

    predicted_price = float(model.predict(features)[0])

    return {
        "flight_id": flight_id,
        "base_price": ctx["base_price"],
        "predicted_price": round(predicted_price, 2),
        "days_to_departure": ctx["days_to_departure"],
        "seats_left": ctx["seats_left"],
        "delay_risk": ctx["delay_risk"],
        "route_popularity": ctx["route_popularity"],
        "model_version": "v1_random_forest",
    }
