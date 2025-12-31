from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # -----------------------------
    # APP
    # -----------------------------
    APP_NAME: str = "Terraform"
    ENV: str = "development"
    DEBUG: bool = True

    # -----------------------------
    # SECURITY
    # -----------------------------
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALGORITHM: str = "HS256"

    # -----------------------------
    # DATABASE
    # -----------------------------
    DATABASE_URL: str

    # -----------------------------
    # FILE STORAGE (for photos later)
    # -----------------------------
    MEDIA_BUCKET: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Prevents re-reading env vars on every request.
    """
    return Settings()
