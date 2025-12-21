# app/services/auth_service.py

from mysql.connector import IntegrityError
from app.db import get_connection
from app.security import hash_password, verify_password, generate_jwt


def register_user(name, email, password_hash, role="USER"):
    """
    Register a new user.
    - name, email, password_hash are required
    - role defaults to USER
    Returns last inserted user_id on success.
    Raises ValueError("Email already registered") on duplicate.
    """

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        email_norm = email.strip().lower()

        sql = """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (name.strip(), email_norm, password_hash, role)
        )

        conn.commit()
        return cursor.lastrowid

    except IntegrityError as e:
        # Duplicate email
        if e.errno == 1062:
            raise ValueError("Email already registered")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def login_user(email: str, password: str):
    """
    Logs in a user:
    - Verifies password
    - Generates JWT token
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT user_id, name, email, password_hash, role
    FROM users
    WHERE email = %s
    """

    cursor.execute(sql, (email.strip().lower(),))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    token = generate_jwt({
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "user": user,
        "token": token
    }
