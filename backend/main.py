# main.py

from app.services.weather_api_service import fetch_and_store_weather

if __name__ == "__main__":
    # Test for BLR (Bengaluru)
    weather = fetch_and_store_weather("BLR")
    print("Live weather result:")
    print(weather)
# main.py

from app.services.weather_api_service import fetch_and_store_weather

if __name__ == "__main__":
    weather = fetch_and_store_weather("BLR")
    print("Weather result:")
    print(weather)
