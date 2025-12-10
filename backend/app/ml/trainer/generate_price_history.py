# app/ml/trainer/generate_price_history.py

import random
from datetime import datetime, timedelta

from app.db import get_connection


def get_all_flights():
    """Fetch all flights + route info from DB."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            f.flight_id,
            r.source_airport,
            r.destination_airport,
            f.departure_time,
            f.base_price
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
    """)

    flights = cursor.fetchall()
    cursor.close()
    conn.close()
    return flights


def compute_route_popularity(source: str, destination: str) -> float:
    """
    Simple synthetic popularity score based on route name.
    This is just for ML training, not real-world logic.
    """
    seed = (len(source) + len(destination)) % 10
    base = 0.3 + (seed / 10) * 0.7  # between 0.3 and 1.0
    return round(base, 2)


def generate_snapshots_for_flight(flight, num_snapshots: int = 50):
    """Generate synthetic historical price records for ML training."""
    snapshots = []

    flight_id = flight["flight_id"]
    source = flight["source_airport"]
    destination = flight["destination_airport"]

    departure_dt = flight["departure_time"]
    base_price = float(flight["base_price"])

    # Assume a fixed seat capacity for all flights for synthetic data
    total_seats = 180

    departure_date = departure_dt.date()
    is_weekend = 1 if departure_date.weekday() >= 5 else 0
    route_popularity = compute_route_popularity(source, destination)

    for _ in range(num_snapshots):
        # days before departure
        days_to_departure = random.randint(1, 30)
        recorded_at = datetime.combine(
            departure_date - timedelta(days=days_to_departure),
            datetime.min.time()
        )

        # seats_left decreases as departure approaches, with randomness
        max_start = int(total_seats * 0.8)
        min_left = int(total_seats * 0.05)
        seats_left = random.randint(min_left, max_start)
        seats_left = max(min_left, int(seats_left * (days_to_departure / 30)))

        # delay_risk - random-ish
        r = random.random()
        if r < 0.1:
            delay_risk = "HIGH"
        elif r < 0.5:
            delay_risk = "MEDIUM"
        else:
            delay_risk = "LOW"

        # ---- Price factor logic ----
        factor = 1.0

        # closer to departure -> higher price
        if days_to_departure <= 3:
            factor += 0.25
        elif days_to_departure <= 7:
            factor += 0.15
        elif days_to_departure <= 14:
            factor += 0.05

        # occupancy: more booked = more expensive
        occupancy = 1.0 - (seats_left / total_seats)
        factor += occupancy * 0.3  # up to +30%

        # weekend surcharge
        if is_weekend:
            factor += 0.1

        # delay risk effect
        if delay_risk == "HIGH":
            factor -= 0.05
        elif delay_risk == "LOW":
            factor += 0.02

        # route popularity effect
        factor += (route_popularity - 0.5) * 0.2

        # small random noise
        noise = random.uniform(-0.05, 0.05)
        factor += noise

        final_price = round(base_price * factor, 2)

        snapshots.append({
            "flight_id": flight_id,
            "recorded_at": recorded_at,
            "departure_date": departure_date,
            "base_price": base_price,
            "final_price": final_price,
            "days_to_departure": days_to_departure,
            "seats_left": seats_left,
            "is_weekend": is_weekend,
            "delay_risk": delay_risk,
            "route_popularity": route_popularity,
        })

    return snapshots


def insert_snapshots_into_db(snapshots):
    """Bulk insert synthetic snapshot dataset."""
    if not snapshots:
        return

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO price_history (
            flight_id, recorded_at, departure_date,
            base_price, final_price,
            days_to_departure, seats_left, is_weekend,
            delay_risk, route_popularity
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = [
        (
            s["flight_id"],
            s["recorded_at"],
            s["departure_date"],
            s["base_price"],
            s["final_price"],
            s["days_to_departure"],
            s["seats_left"],
            s["is_weekend"],
            s["delay_risk"],
            s["route_popularity"],
        )
        for s in snapshots
    ]

    cursor.executemany(sql, values)
    conn.commit()

    cursor.close()
    conn.close()


def main():
    flights = get_all_flights()
    print(f"Found {len(flights)} flights")

    all_snaps = []
    for f in flights:
        snaps = generate_snapshots_for_flight(f, num_snapshots=50)
        all_snaps.extend(snaps)

    print(f"Generated {len(all_snaps)} price snapshots")
    insert_snapshots_into_db(all_snaps)
    print("Inserted into price_history.")


if __name__ == "__main__":
    main()
