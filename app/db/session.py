from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
settings = get_settings()

# -----------------------------
# DATABASE URL CONFIGURATION
# -----------------------------
# Example PostgreSQL URL: postgresql+psycopg2://user:password@localhost:5432/gymtrack
DATABASE_URL = settings.DATABASE_URL
# -----------------------------
# ENGINE CREATION
# -----------------------------
# For PostgreSQL, replace the URL with the actual connection string
_is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    **({"pool_pre_ping": True} if not _is_sqlite else {}),
)

# -----------------------------
# SESSION FACTORY
# -----------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -----------------------------
# DEPENDENCY FOR FASTAPI
# -----------------------------
# Usage in FastAPI endpoints:
# from db.session import SessionLocal
# db = Depends(get_db)
def get_db():
    """
    Yield a database session for FastAPI routes.
    Ensures proper commit/rollback and closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
