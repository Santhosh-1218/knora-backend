import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings
from app.core.exceptions import AuthenticationError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a password using Argon2id."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an Argon2id hash."""
    if not hashed_password or not plain_password:
        return False
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    except Exception:
        return False


def hash_otp(otp: str, salt: Optional[str] = None) -> str:
    """Generates a secure HMAC-SHA256 hash of an OTP to avoid storing plaintext OTPs."""
    key = settings.JWT_SECRET.encode("utf-8")
    message = f"{otp}:{salt or ''}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def verify_otp_hash(otp: str, otp_hash: str, salt: Optional[str] = None) -> bool:
    """Verifies an OTP against its HMAC-SHA256 hash using constant-time comparison."""
    computed = hash_otp(otp, salt)
    return hmac.compare_digest(computed, otp_hash)


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a short-lived JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    payload = {
        "sub": str(subject),
        "type": "access",
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
        "jti": str(uuid.uuid4())
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    jti: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, str]:
    """
    Creates a long-lived refresh token.
    Returns a tuple of (token_string, jti).
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    token_jti = jti or str(uuid.uuid4())

    payload = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now.timestamp(),
        "exp": expire.timestamp(),
        "jti": token_jti
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, token_jti


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token signature and expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid authentication token")


def hash_token(token: str) -> str:
    """SHA-256 hash of refresh token for database lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
