
from functools import lru_cache
from decouple import config
import loguru 
class Settings():
    # -----------------------------
    # APP
    # -----------------------------
    APP_NAME: str = config("APP_NAME", default="Terraform")
    ENV: str = config("ENV", default="development")
    DEBUG: bool = config("DEBUG", default=False, cast=bool)

    # -----------------------------
    # SECURITY
    # -----------------------------
    ADMIN_ACTION_KEY: str = config("ADMIN_ACTION_KEY", default="admin-secret-change-me")
    SECRET_KEY: str = config("SECRET_KEY", default="super-secret-change-me")
    REFRESH_SECRET_KEY: str = config("REFRESH_SECRET_KEY", default="another-super-secret-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: float = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=5000, cast=float)  # in minutes
    REFRESH_TOKEN_EXPIRE_DAYS: float = config("REFRESH_TOKEN_EXPIRE_DAYS", default=30, cast=float)  # in days
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="123")
    OPENROUTER_API_KEY: str = config("OPENROUTER_API_KEY", default="123")
    GEMINI_API_KEY: str = config("GEMINI_API_KEY", default="123")
    ALGORITHM: str = "HS256"

    # -----------------------------
    # DATABASE
    # -----------------------------
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./db.sqlite3")

    #------------------------------
    # LOGGER
    logger = loguru.logger
    #------------------------------

    # -----------------------------
    # FILE STORAGE — Cloudinary
    # -----------------------------
    CLOUDINARY_CLOUD_NAME: str = config("CLOUDINARY_CLOUD_NAME", default="")
    CLOUDINARY_API_KEY: str    = config("CLOUDINARY_API_KEY",    default="")
    CLOUDINARY_API_SECRET: str = config("CLOUDINARY_API_SECRET", default="")

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
