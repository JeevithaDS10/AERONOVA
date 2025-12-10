# app/services/auth_service.py

from app.db import get_connection
from app.security import hash_password, verify_password, encrypt_sensitive, generate_jwt

def register_user(name: str, email: str, password: str, phone: str | None = None):
    """
    Create a new user.
    phone is optional now – frontend only sends name, email, password.
    """
    from app.db import get_connection
    from app.security import hash_password

    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    # ⚠️ use the same INSERT you already had before – likely WITHOUT phone
    # Example (common one we used earlier):
    sql = """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (name, email, password_hash, "USER"))

    conn.commit()
    user_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return user_id

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
