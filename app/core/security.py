from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    subject = user identifier (usually user.id or email)
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": subject,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> str:
    """
    Returns subject (user identifier) if valid.
    Raises JWTError if invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            raise JWTError("Token missing subject")
        return subject
    except JWTError:
        raise

def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_refresh_token(token: str) -> str:
    """
    Decodes a JWT refresh token and returns the subject
    """
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: str = payload.get("sub")
        token_type: str = payload.get("type")
        if subject is None or token_type != "refresh":
            raise JWTError("Invalid refresh token")
        return payload
    except JWTError:
        raise