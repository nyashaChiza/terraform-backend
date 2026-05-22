from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _now_utc() -> datetime:
    """Timezone-aware UTC `now`. datetime.utcnow() is deprecated in Py 3.12+."""
    return datetime.now(timezone.utc)


# -----------------------------
# PASSWORDS
# -----------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------
# TOKENS
# -----------------------------
def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    token_version: int = 0,
) -> str:
    """
    Issue an access token.

    - `subject`: user identifier (user.id as a string)
    - `token_version`: copied from User.token_version at issue time. When the
      user changes password / logs out everywhere, we bump that column and
      all previously-issued tokens are rejected.
    """
    expire = _now_utc() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": _now_utc(),
        "tv": token_version,
        "type": "access",
    }

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Returns the full payload dict if valid (sub, tv, exp, etc).
    Raises JWTError if invalid.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    subject = payload.get("sub")
    if subject is None:
        raise JWTError("Token missing subject")
    # Reject refresh tokens if accidentally sent as access tokens
    if payload.get("type") and payload.get("type") != "access":
        raise JWTError("Wrong token type")
    return payload


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    token_version: int = 0,
) -> str:
    """Creates a JWT refresh token bound to the user's current token_version."""
    expire = _now_utc() + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": _now_utc(),
        "tv": token_version,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_refresh_token(token: str) -> dict:
    """
    Decodes a JWT refresh token and returns the full payload.
    Raises JWTError if invalid or wrong type.
    """
    payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
    subject = payload.get("sub")
    token_type = payload.get("type")
    if subject is None or token_type != "refresh":
        raise JWTError("Invalid refresh token")
    return payload

