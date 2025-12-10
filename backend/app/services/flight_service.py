# app/services/flight_service.py

from app.db import get_connection

def search_flights(source_airport: str, destination_airport: str, date_str: str):
    """
    Search for flights between two airports on a given date.
    date_str format: 'YYYY-MM-DD'

    Returns: list of dictionaries, each containing flight details.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            f.flight_id,
            f.flight_number,
            f.departure_time,
            f.arrival_time,
            f.base_price,
            f.status,
            r.source_airport,
            r.destination_airport,
            a.model AS aircraft_model
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        JOIN aircraft a ON f.aircraft_id = a.aircraft_id
        WHERE r.source_airport = %s
          AND r.destination_airport = %s
          AND DATE(f.departure_time) = %s
        ORDER BY f.departure_time
    """

    # Execute query with parameters (prevents SQL injection)
    cursor.execute(sql, (source_airport, destination_airport, date_str))
    flights = cursor.fetchall()

    cursor.close()
    conn.close()

    return flights
