
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.db.session import engine
from app.db.base import Base
from app.api import (
    auth,
    profiles,
    goals,
    sessions,
    planner,
    exercise,
    admin,
    )

# -------------------------------------------------
# RATE LIMITER
# -------------------------------------------------

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# -------------------------------------------------
# APP INITIALIZATION
# -------------------------------------------------

app = FastAPI(
    title="Terraform API",
    version="1.0.0",
    description="Backend API for Terraform intelligent training app"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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

# -------------------------------------------------
# API ROUTERS
app.include_router(admin.router, prefix="/api/admin")
app.include_router(auth.router, prefix="/auth")
app.include_router(profiles.router, prefix="/api/profiles")
app.include_router(goals.router, prefix="/api/goals")
app.include_router(sessions.router, prefix="/api/sessions")
app.include_router(exercise.router, prefix="/api/exercises")
app.include_router(planner.router, prefix="/api/planner")

# -------------------------------------------------
