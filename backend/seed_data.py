# seed_data.py

from app.db import get_connection

def seed_aircraft():
    conn = get_connection()
    cursor = conn.cursor()

    data = [
        ("Airbus A320", 180),
        ("Boeing 737", 160),
        ("ATR 72", 70)
    ]

    sql = "INSERT INTO aircraft (model, seat_capacity) VALUES (%s, %s)"

    try:
        cursor.executemany(sql, data)
        conn.commit()
        print(f"Inserted {cursor.rowcount} aircraft rows.")
    finally:
        cursor.close()
        conn.close()


def seed_routes():
    conn = get_connection()
    cursor = conn.cursor()

    data = [
        ("BLR", "DEL", 1740),
        ("BLR", "BOM", 840),
        ("DEL", "BOM", 1140)
    ]

    sql = "INSERT INTO routes (source_airport, destination_airport, distance_km) VALUES (%s, %s, %s)"

    try:
        cursor.executemany(sql, data)
        conn.commit()
        print(f"Inserted {cursor.rowcount} route rows.")
    finally:
        cursor.close()
        conn.close()


def seed_flights():
    conn = get_connection()
    cursor = conn.cursor()

    # NOTE: We assume:
    # aircraft_id: 1,2,3 and route_id: 1,2,3 exist from previous seeding.
    data = [
        # flight_number, route_id, aircraft_id, departure_time, arrival_time, base_price
        ("AN101", 1, 1, "2025-12-10 09:00:00", "2025-12-10 11:30:00", 6500.00),
        ("AN102", 1, 2, "2025-12-10 18:00:00", "2025-12-10 20:30:00", 7000.00),
        ("AN201", 2, 2, "2025-12-10 07:00:00", "2025-12-10 08:30:00", 4500.00),
        ("AN202", 2, 3, "2025-12-10 19:00:00", "2025-12-10 20:30:00", 4800.00),
        ("AN301", 3, 1, "2025-12-10 06:30:00", "2025-12-10 08:15:00", 5500.00),
    ]

    sql = """
        INSERT INTO flights
        (flight_number, route_id, aircraft_id, departure_time, arrival_time, base_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'ON_TIME')
    """

    try:
        cursor.executemany(sql, data)
        conn.commit()
        print(f"Inserted {cursor.rowcount} flight rows.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_aircraft()
    seed_routes()
    seed_flights()
    print("✅ Seeding complete.")
