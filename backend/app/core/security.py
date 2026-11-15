import hashlib
import secrets
import datetime
from datetime import timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt with random salt.
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a bcrypt hash.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a short-lived JWT access token.
    """
    now = datetime.datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a JWT access token.
    Returns payload dict if valid, None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None

def generate_refresh_token() -> str:
    """
    Generates a cryptographically strong, URL-safe random string for refresh token.
    Raw token is delivered only to client via HttpOnly cookie.
    """
    return secrets.token_urlsafe(48)

def hash_token(raw_token: str) -> str:
    """
    Computes SHA-256 hash of a raw token for secure database storage.
    Plaintext refresh tokens are never persisted in the database.
    """
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

