# app/services/payment_service.py

from datetime import datetime

from app.db import get_connection
from app.security import encrypt_sensitive, compute_hmac


def create_payment(
    user_id: int,
    booking_id: int,
    amount: float,
    method: str,
    upi_id: str | None = None,
    card_number: str | None = None,
    card_expiry: str | None = None,
    card_cvv: str | None = None,
):
    """
    Simulated payment processing with strong encryption.

    - Validates method & required fields
    - Encrypts UPI / Card details using AES-256-GCM (encrypt_sensitive)
    - Inserts a row into payments table with status='SUCCESS'
    - Generates an HMAC-based transaction_id (not stored, but returned)
    """

    method = method.upper()

    if method not in ("UPI", "CARD"):
        raise ValueError("Invalid payment method. Must be 'UPI' or 'CARD'.")

    # ---- Validate + encrypt sensitive data ----
    upi_encrypted = None
    card_encrypted = None

    if method == "UPI":
        if not upi_id:
            raise ValueError("UPI ID is required for UPI payments.")
        upi_encrypted = encrypt_sensitive(upi_id)

    elif method == "CARD":
        if not (card_number and card_expiry and card_cvv):
            raise ValueError("Card number, expiry and CVV are required for CARD payments.")
        # We pack card details into a single string before encrypting
        card_payload = f"{card_number}|{card_expiry}|{card_cvv}"
        card_encrypted = encrypt_sensitive(card_payload)

    # ---- DB insert ----
    conn = get_connection()
    cursor = conn.cursor()

    try:
        paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = """
            INSERT INTO payments
                (booking_id, amount, method, upi_encrypted, card_encrypted, status, paid_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (
                booking_id,
                amount,
                method,
                upi_encrypted,
                card_encrypted,
                "SUCCESS",    # simulated success
                paid_at,
            ),
        )

        payment_id = cursor.lastrowid
        conn.commit()

        # ---- Generate an HMAC-based transaction id (not stored, can be recomputed) ----
        # Uses user_id + booking_id + amount + paid_at as message
        message = f"{user_id}:{booking_id}:{amount}:{paid_at}"
        transaction_id = compute_hmac(message)

        return {
            "payment_id": payment_id,
            "transaction_id": transaction_id,
            "status": "SUCCESS",
            "method": method,
            "amount": amount,
            "paid_at": paid_at,
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
