
from functools import lru_cache
from decouple import config
import loguru


# Sentinel values used as defaults. If any of these survive into a production
# environment, the app refuses to start — preventing accidental deployment
# with insecure placeholder secrets.
_PLACEHOLDER_SECRETS = {
    "super-secret-change-me",
    "another-super-secret-change-me",
    "admin-secret-change-me",
    "123",
}


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
    # 30 minutes is the standard for access tokens — short enough that token leaks
    # have a small blast radius, long enough that users don't see frequent refresh.
    # Refresh flow handles silently extending sessions for up to REFRESH_TOKEN_EXPIRE_DAYS.
    ACCESS_TOKEN_EXPIRE_MINUTES: float = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=float)
    REFRESH_TOKEN_EXPIRE_DAYS: float = config("REFRESH_TOKEN_EXPIRE_DAYS", default=30, cast=float)
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="123")
    OPENROUTER_API_KEY: str = config("OPENROUTER_API_KEY", default="123")
    GEMINI_API_KEY: str = config("GEMINI_API_KEY", default="123")
    ALGORITHM: str = "HS256"

    # -----------------------------
    # CORS
    # -----------------------------
    # Comma-separated list of allowed origins for CORS. In production this should
    # be the deployed Expo / web origin(s). Falls back to `*` ONLY in development.
    CORS_ALLOWED_ORIGINS: str = config("CORS_ALLOWED_ORIGINS", default="*")

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

    def validate_production(self) -> None:
        """
        Refuse to start in production if critical secrets are still placeholder
        values. Catches the classic "forgot to set env vars in Vercel" mistake.
        """
        if self.ENV.lower() != "production":
            return
        problems = []
        critical_fields = {
            "SECRET_KEY": self.SECRET_KEY,
            "REFRESH_SECRET_KEY": self.REFRESH_SECRET_KEY,
            "ADMIN_ACTION_KEY": self.ADMIN_ACTION_KEY,
            "GEMINI_API_KEY": self.GEMINI_API_KEY,
        }
        for name, value in critical_fields.items():
            if not value or value in _PLACEHOLDER_SECRETS:
                problems.append(name)
        if self.CORS_ALLOWED_ORIGINS.strip() == "*":
            problems.append("CORS_ALLOWED_ORIGINS (must not be * in production)")
        if problems:
            raise RuntimeError(
                "Refusing to start in production with insecure config. "
                f"Set these env vars: {', '.join(problems)}"
            )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ALLOWED_ORIGINS into a list. Returns ['*'] in development."""
        raw = self.CORS_ALLOWED_ORIGINS.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Prevents re-reading env vars on every request.
    """
    settings = Settings()
    settings.validate_production()
    return settings
