# app/services/disruption_service.py

from datetime import datetime
from app.db import get_connection
from app.services.notification_service import add_notification
from app.services.flight_service import search_flights


def update_flight_status_and_notify(flight_id: int, new_status: str):
    """
    Update flight status (ON_TIME / DELAYED / CANCELLED)
    and notify all users who have CONFIRMED bookings on that flight.

    Also suggests alternative flights on the same route & date.

    Returns: dict with summary info.
    """
    new_status = new_status.upper()
    if new_status not in ("ON_TIME", "DELAYED", "CANCELLED"):
        raise ValueError("Invalid status. Use ON_TIME, DELAYED or CANCELLED.")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1) Get current flight info (route, date, etc.)
        sql_flight = """
            SELECT
                f.flight_id,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
                f.status,
                r.source_airport,
                r.destination_airport
            FROM flights f
            JOIN routes r ON f.route_id = r.route_id
            WHERE f.flight_id = %s
        """
        cursor.execute(sql_flight, (flight_id,))
        flight = cursor.fetchone()

        if not flight:
            raise ValueError(f"Flight with id {flight_id} not found")

        # 2) Update status
        sql_update = "UPDATE flights SET status = %s WHERE flight_id = %s"
        cursor.execute(sql_update, (new_status, flight_id))
        conn.commit()

        # 3) Get all confirmed bookings for this flight
        sql_bookings = """
            SELECT b.booking_id, b.user_id, b.seat_no
            FROM bookings b
            WHERE b.flight_id = %s AND b.status = 'CONFIRMED'
        """
        cursor.execute(sql_bookings, (flight_id,))
        bookings = cursor.fetchall()

        notified_users = []

        # 4) Find alternative flights on same route & date (if delayed/cancelled)
        alternatives = []
        if new_status in ("DELAYED", "CANCELLED"):
            date_str = flight["departure_time"].strftime("%Y-%m-%d")
            alternatives = search_flights(
                flight["source_airport"],
                flight["destination_airport"],
                date_str
            )
            # Remove the same flight from alternatives list
            alternatives = [f for f in alternatives if f["flight_id"] != flight_id]

        # 5) Create message and notifications
        for b in bookings:
            user_id = b["user_id"]
            msg = build_disruption_message(flight, new_status, alternatives)
            add_notification(user_id, msg, "ALERT")
            notified_users.append(user_id)

        return {
            "flight_id": flight_id,
            "flight_number": flight["flight_number"],
            "old_status": flight["status"],
            "new_status": new_status,
            "bookings_affected": len(bookings),
            "users_notified": len(set(notified_users)),
            "alternatives_found": len(alternatives),
        }

    finally:
        cursor.close()
        conn.close()


def build_disruption_message(flight: dict, new_status: str, alternatives: list) -> str:
    """
    Build a human-readable notification message
    for disruption alerts.
    """
    fno = flight["flight_number"]
    src = flight["source_airport"]
    dest = flight["destination_airport"]
    dep = flight["departure_time"].strftime("%Y-%m-%d %H:%M")

    if new_status == "DELAYED":
        base = f"Your flight {fno} from {src} to {dest} on {dep} is DELAYED."
    elif new_status == "CANCELLED":
        base = f"Your flight {fno} from {src} to {dest} on {dep} has been CANCELLED."
    else:
        base = f"Status update: Your flight {fno} from {src} to {dest} on {dep} is now {new_status}."

    # Add suggestions if we have alternatives
    if alternatives:
        base += " Suggested alternatives: "
        parts = []
        for alt in alternatives[:3]:  # show up to 3 options
            alt_dep = alt["departure_time"].strftime("%H:%M")
            parts.append(f"{alt['flight_number']} at {alt_dep}")
        base += "; ".join(parts) + "."

    return base
