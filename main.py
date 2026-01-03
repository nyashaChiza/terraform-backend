
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

