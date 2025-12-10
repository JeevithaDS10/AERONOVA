# app/security.py

import base64
import os
import time
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2 import PasswordHasher
from .config import SECRET_KEY, AES_KEY

#===============================================================
# 1️⃣ PASSWORD HASHING WITH ARGON2id
#===============================================================

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2, hash_len=32, salt_len=16)

def hash_password(password: str) -> str:
    """
    Hashes a password using Argon2id algorithm.
    Output includes password hash + salt + parameters.
    """
    return ph.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies password against a stored Argon2id hash.
    Returns True or False.
    """
    try:
        ph.verify(stored_hash, password)
        return True
    except Exception:
        return False


#===============================================================
# 2️⃣ AES-256-GCM ENCRYPTION & DECRYPTION FOR SENSITIVE DATA
#===============================================================

def encrypt_sensitive(plain_text: str) -> str:
    """
    Encrypt plain text using AES-256-GCM with random nonce.
    Output = base64(nonce + ciphertext + tag)
    """
    aesgcm = AESGCM(AES_KEY.encode())
    nonce = os.urandom(12)  # 96-bit nonce recommended for GCM
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_sensitive(encoded_text: str) -> str:
    """
    Decrypt AES-GCM encrypted text.
    Extracts nonce + ciphertext + tag from base64 string.
    """
    aesgcm = AESGCM(AES_KEY.encode())
    decoded = base64.b64decode(encoded_text)
    nonce = decoded[:12]
    ciphertext = decoded[12:]
    plain = aesgcm.decrypt(nonce, ciphertext, None)
    return plain.decode()


#===============================================================
# 3️⃣ HMAC-SHA256 GENERATION (BOOKING TOKEN / REQUEST SIGNING)
#===============================================================

def compute_hmac(message: str) -> str:
    """
    Generate SHA-256 HMAC signature using secret key.
    """
    return hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


#===============================================================
# 4️⃣ JWT TOKEN (AUTHENTICATION)
#===============================================================

def generate_jwt(payload: dict, expiry_minutes: int = 60) -> str:
    """
    Create a JWT token signed with HMAC secret key.
    Contains expiry time.
    """
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str):
    """
    Verify JWT token and return payload if valid.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None
