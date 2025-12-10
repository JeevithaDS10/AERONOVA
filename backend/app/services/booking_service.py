# app/services/booking_service.py

from datetime import datetime
from app.db import get_connection
from app.security import encrypt_sensitive, compute_hmac


def create_booking(user_id: int, flight_id: int, seat_no: str, passengers: list, price_paid: float):
    """
    Creates a booking:
    - Generates an HMAC booking token
    - Inserts into bookings table
    - Encrypts passenger ID & contact and inserts into passenger_details

    passengers: list of dicts like:
        [
            {
                "name": "Jeevitha",
                "age": 21,
                "id_proof": "AADHAAR1234",
                "contact": "9876543210"
            },
            ...
        ]
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1) Make a timestamp string (for both DB and token)
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2) Generate booking token using HMAC
        message = f"{user_id}:{flight_id}:{seat_no}:{timestamp_str}"
        booking_token = compute_hmac(message)

        # 3) Insert into bookings table
        sql_booking = """
            INSERT INTO bookings
                (user_id, flight_id, seat_no, booking_token, status, booked_at, price_paid)
            VALUES
                (%s, %s, %s, %s, 'CONFIRMED', %s, %s)
        """
        booking_values = (user_id, flight_id, seat_no, booking_token, timestamp_str, price_paid)
        cursor.execute(sql_booking, booking_values)

        booking_id = cursor.lastrowid  # newly created booking id

        # 4) Insert passengers into passenger_details
        sql_passenger = """
            INSERT INTO passenger_details
                (booking_id, name, age, id_proof_encrypted, contact_encrypted)
            VALUES
                (%s, %s, %s, %s, %s)
        """

        for p in passengers:
            id_enc = encrypt_sensitive(p["id_proof"])
            contact_enc = encrypt_sensitive(p["contact"])

            cursor.execute(
                sql_passenger,
                (booking_id, p["name"], p["age"], id_enc, contact_enc)
            )

        # 5) Commit all changes
        conn.commit()

        return booking_id, booking_token

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def cancel_booking(booking_id: int, user_id: int) -> bool:
    """
    Cancels a booking by setting status = 'CANCELLED'
    Only if the booking belongs to the given user.
    Returns True if a row was updated, else False.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE bookings
        SET status = 'CANCELLED'
        WHERE booking_id = %s AND user_id = %s
    """

    cursor.execute(sql, (booking_id, user_id))
    conn.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    conn.close()

    return updated


def get_user_bookings(user_id: int):
    """
    Returns all bookings for a user with basic flight info.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            b.booking_id,
            b.seat_no,
            b.status,
            b.booked_at,
            b.price_paid,
            b.booking_token,
            f.flight_number,
            f.departure_time,
            f.arrival_time,
            r.source_airport,
            r.destination_airport
        FROM bookings b
        JOIN flights f ON b.flight_id = f.flight_id
        JOIN routes r ON f.route_id = r.route_id
        WHERE b.user_id = %s
        ORDER BY b.booked_at DESC
    """

    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
