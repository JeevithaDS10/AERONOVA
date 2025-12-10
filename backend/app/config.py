# app/config.py

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Database configuration dictionary
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Secret key for HMAC (booking token)
SECRET_KEY = os.getenv("SECRET_KEY")

# AES key for encryption/decryption (we will use later)
AES_KEY = os.getenv("AES_KEY")


# 🔹 NEW: Weather API key
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
