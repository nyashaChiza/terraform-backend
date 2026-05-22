from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
settings = get_settings()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Resolve the current authenticated user from JWT.

    Validates:
    - JWT signature + expiry
    - subject is a valid user id
    - user exists in DB
    - token's `tv` (token_version) matches the user's current token_version
      → bumping the user's token_version invalidates ALL outstanding tokens
        (used for password changes and logout-everywhere)
    """
    UNAUTH = lambda detail: HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except Exception:
        raise UNAUTH("Invalid or expired token")

    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise UNAUTH("Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UNAUTH("User not found")

    # Reject tokens issued before the user's current token_version
    token_version = payload.get("tv", 0)
    if token_version != (user.token_version or 0):
        raise UNAUTH("Session has been invalidated. Please sign in again.")

    return user
