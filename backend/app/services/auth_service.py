# app/services/auth_service.py


import mysql.connector
from mysql.connector import IntegrityError
from app.db import get_connection
from app.security import hash_password, verify_password, encrypt_sensitive, generate_jwt



def register_user(name, email, password_hash, phone=None, role="USER"):
    """
    Register a new user.
    - name, email, password_hash are required
    - phone is optional. If provided and encrypt_sensitive exists, we'll encrypt it and store
      into the `phone_encrypted` column (matching your DB).
    Returns last inserted user_id on success.
    Raises ValueError("Email already registered") on duplicate.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Normalize email on backend side (ensure lowercase stored)
        email_norm = email.strip().lower()

        # If you have encrypt_sensitive function, use it; otherwise just store plain phone
        phone_to_store = None
        if phone:
            phone_clean = phone.strip()
            try:
                phone_to_store = encrypt_sensitive(phone_clean)  # uses your existing encrypt routine
            except Exception:
                # if encryption not available, fallback to storing plain phone
                phone_to_store = phone_clean

        sql = """
        INSERT INTO users (name, email, password_hash, phone_encrypted, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (name.strip(), email_norm, password_hash, phone_to_store, role))
        conn.commit()
        return cursor.lastrowid

    except IntegrityError as e:
        # MySQL duplicate entry errno = 1062
        try:
            errnum = e.errno
        except Exception:
            errnum = None

        if errnum == 1062:
            # duplicate key — return friendly message
            raise ValueError("Email already registered")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def register_user(name, email, password_hash, phone=None, role="USER"):
    """
    Register a new user.
    - name, email, password_hash are required
    - phone is optional. If provided and encrypt_sensitive exists, we'll encrypt it and store
      into the `phone_encrypted` column (matching your DB).
    Returns last inserted user_id on success.
    Raises ValueError("Email already registered") on duplicate.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Normalize email on backend side (ensure lowercase stored)
        email_norm = email.strip().lower()

        # If you have encrypt_sensitive function, use it; otherwise just store plain phone
        phone_to_store = None
        if phone:
            phone_clean = phone.strip()
            try:
                phone_to_store = encrypt_sensitive(phone_clean)  # uses your existing encrypt routine
            except Exception:
                # if encryption not available, fallback to storing plain phone
                phone_to_store = phone_clean

        sql = """
        INSERT INTO users (name, email, password_hash, phone_encrypted, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (name.strip(), email_norm, password_hash, phone_to_store, role))
        conn.commit()
        return cursor.lastrowid

    except IntegrityError as e:
        # MySQL duplicate entry errno = 1062
        try:
            errnum = e.errno
        except Exception:
            errnum = None

        if errnum == 1062:
            # duplicate key — return friendly message
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
    - Verifies password using Argon2id verify()
    - If password correct, generate JWT token
    - Returns {user_info, token}
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT user_id, name, email, password_hash, role FROM users WHERE email = %s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return None  # email not found

    if not verify_password(password, user["password_hash"]):
        return None  # incorrect password

    # Create JWT token for session authentication
    token = generate_jwt({
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"]
    })

    return {
        "user": user,
        "token": token
    }
