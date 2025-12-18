from app.db import get_connection

def get_flights_for_leg(source, destination, date):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.flight_id, f.flight_number, f.departure_time,
               f.arrival_time, f.base_price, f.status
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        WHERE r.source = %s
          AND r.destination = %s
          AND DATE(f.departure_time) = %s
    """, (source, destination, date))

    flights = cursor.fetchall()

    cursor.close()
    conn.close()

    return flights
