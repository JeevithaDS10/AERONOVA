from app.db import get_connection

def resolve_airport_code(input_value: str) -> str | None:
    """
    Accepts:
    - city name (Mysuru)
    - airport code (MYQ)

    Returns:
    - airport_code (MYQ) or None
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT airport_code
        FROM airports
        WHERE LOWER(city) = %s OR LOWER(airport_code) = %s
        LIMIT 1
    """

    val = input_value.lower()
    cursor.execute(query, (val, val))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row["airport_code"] if row else None
