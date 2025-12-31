
from functools import lru_cache
from decouple import config
import loguru 
class Settings():
    # -----------------------------
    # APP
    # -----------------------------
    APP_NAME: str = config("APP_NAME", default="Terraform")
    ENV: str = config("ENV", default="development")
    DEBUG: bool = config("DEBUG", default=True, cast=bool)

    # -----------------------------
    # SECURITY
    # -----------------------------
    SECRET_KEY: str = config("SECRET_KEY")
    REFRESH_SECRET_KEY: str = config("REFRESH_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: float = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=5000, cast=float)  # in minutes
    REFRESH_TOKEN_EXPIRE_DAYS: float = config("REFRESH_TOKEN_EXPIRE_DAYS", default=30, cast=float)  # in days
    ALGORITHM: str = "HS256"

    # -----------------------------
    # DATABASE
    # -----------------------------
    DATABASE_URL: str = config("DATABASE_URL")

    #------------------------------
    # LOGGER
    logger = loguru.logger
    #------------------------------

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
