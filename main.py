
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.db.base import Base


# -------------------------------------------------
# APP INITIALIZATION
# -------------------------------------------------

app = FastAPI(
    title="Terraform API",
    version="1.0.0",
    description="Backend API for Terraform intelligent training app"
)

# -------------------------------------------------
# CORS (Expo / Mobile Friendly)
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

@app.on_event("startup")
def on_startup():
    """
    Create database tables on startup.
    In production, this should be replaced by Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# -------------------------------------------------
# ROOT
# -------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "app": "Terraform API",
        "status": "running",
        "version": "1.0.0"
    }
