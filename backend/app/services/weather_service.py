# app/services/weather_service.py

from datetime import datetime
from app.db import get_connection


def add_weather_record(airport_code: str, condition: str, delay_risk: str):
    """
    Insert a weather record for an airport.
    delay_risk should be one of: 'LOW', 'MEDIUM', 'HIGH'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO weather_log (airport_code, weather_condition, delay_risk, timestamp)
        VALUES (%s, %s, %s, %s)
    """

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = (airport_code, condition, delay_risk, now_str)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_latest_weather(airport_code: str):
    """
    Get the most recent weather record for the given airport.
    Returns a dictionary with condition, delay_risk, timestamp or None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT airport_code, weather_condition, delay_risk, timestamp
        FROM weather_log
        WHERE airport_code = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """

    cursor.execute(sql, (airport_code,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row
