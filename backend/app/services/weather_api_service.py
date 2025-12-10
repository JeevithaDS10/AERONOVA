# app/services/weather_api_service.py
import os
import requests
from datetime import datetime

from dotenv import load_dotenv  # 👈 add this
from app.db import get_connection

load_dotenv()  # 👈 this reads your .env file

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


AIRPORT_CITY_MAP = {
    "BLR": "Bengaluru",
    "DEL": "Delhi",
    "HYD": "Hyderabad",
    "MAA": "Chennai",
    "BOM": "Mumbai",
    # add more as needed
}


def airport_to_city(airport_code: str) -> str:
    return AIRPORT_CITY_MAP.get(airport_code.upper(), airport_code)


def fetch_weather_from_api(airport_code: str):
    """
    Call OpenWeather and return (raw_json, simplified_dict)
    """
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set in environment/.env")

    city = airport_to_city(airport_code)

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    temp_c = data["main"]["temp"]
    condition = data["weather"][0]["description"].lower()

    if any(x in condition for x in ["thunderstorm", "heavy", "storm", "snow"]):
        delay_risk = "HIGH"
    elif any(x in condition for x in ["rain", "drizzle", "cloud"]):
        delay_risk = "MEDIUM"
    else:
        delay_risk = "LOW"

    simplified = {
        "airport_code": airport_code.upper(),
        "city": city,
        "temp_c": float(temp_c),
        "condition": condition,
        "delay_risk": delay_risk,
    }

    return data, simplified

def fetch_and_store_weather(airport_code: str):
    raw, simplified = fetch_weather_from_api(airport_code)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        sql = """
            INSERT INTO weather_log
                (airport_code, temperature, weather_condition, delay_risk, timestamp)
            VALUES
                (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                simplified["airport_code"],
                simplified["temp_c"],
                simplified["condition"],      # goes into weather_condition column
                simplified["delay_risk"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return simplified