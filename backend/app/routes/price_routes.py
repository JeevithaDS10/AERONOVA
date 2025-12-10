# app/routes/price_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.price_service import predict_price_for_flight

router = APIRouter(prefix="/price", tags=["Price Prediction"])


class PricePredictionResponse(BaseModel):
    flight_id: int
    base_price: float
    predicted_price: float
    days_to_departure: int
    seats_left: int
    delay_risk: str
    route_popularity: float
    model_version: str


@router.get("/predict", response_model=PricePredictionResponse)
def get_price_prediction(flight_id: int):
    """
    Predict price for a given flight_id.

    Steps:
    - Read flight info from DB
    - Compute features
    - Use ML model to predict price
    - Return prediction + context
    """
    try:
        result = predict_price_for_flight(flight_id)
        return result
    except ValueError as ve:
        # flight not found or similar
        raise HTTPException(status_code=404, detail=str(ve))
    except RuntimeError as re:
        # model file missing or similar
        raise HTTPException(status_code=500, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting price: {e}")
