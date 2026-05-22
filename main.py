
import threading
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.db.session import engine
from app.db.base import Base
from app.core.config import get_settings

# Use the cached singleton — also triggers validate_production() which
# refuses to start in production with placeholder secrets.
_settings = get_settings()
from app.api import (
    auth,
    profiles,
    goals,
    sessions,
    planner,
    exercise,
    admin,
    stats,
    users,
    equipment,
    friends,
    feed,
    notifications,
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

_cors_origins = _settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # `*` + credentials is invalid CORS — browsers reject it. Only allow
    # credentials when origins are explicitly listed.
    allow_credentials=_cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

def _backfill_target_sessions() -> None:
    """
    Runs once in the background on startup.
    Finds every Goal whose target_sessions is NULL and asks Gemini to fill it in.
    Handles all legacy goals created before the session-estimate feature existed.
    """
    from app.db.session import SessionLocal
    from app.models.goal import Goal
    from app.models.profile import Profile
    from app.services.session_estimator import estimate_sessions

    db = SessionLocal()
    try:
        goals = db.query(Goal).filter(Goal.target_sessions.is_(None)).all()
        if not goals:
            _settings.logger.info("Backfill: no goals with null target_sessions.")
            return
        _settings.logger.info(f"Backfill: estimating target_sessions for {len(goals)} goal(s).")
        for goal in goals:
            try:
                profile = db.query(Profile).filter(Profile.user_id == goal.user_id).first()
                goal.target_sessions = estimate_sessions(goal=goal, profile=profile)
                db.commit()
                _settings.logger.info(f"Backfill: goal {goal.id} → target_sessions={goal.target_sessions}")
            except Exception as exc:
                _settings.logger.warning(f"Backfill: failed for goal {goal.id}: {exc}")
    finally:
        db.close()


def _run_column_migrations() -> None:
    """
    Lightweight column-level migrations for fields added after initial deployment.
    Uses IF NOT EXISTS so it is safe to run on every startup.

    SQLite note: create_all() already builds the full schema from ORM models, so
    raw SQL migrations (which use PostgreSQL-specific syntax) are skipped for SQLite.
    Only PostgreSQL (Neon / Vercel) needs these ALTER TABLE statements to patch
    existing tables that predate a given feature.
    """
    from sqlalchemy import text
    from app.db.session import SessionLocal, DATABASE_URL

    # SQLite gets its entire schema from Base.metadata.create_all — skip raw SQL.
    if DATABASE_URL.startswith("sqlite"):
        _settings.logger.info("SQLite detected — skipping raw SQL migrations (create_all handles schema).")
        return

    # PostgreSQL-only migrations — safe to re-run (IF NOT EXISTS / column-exists errors
    # are caught and logged as warnings, then execution continues with the next statement).
    migrations = [
        # ── original columns ──────────────────────────────────────────────────
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture_url VARCHAR(500)",
        # ── username / discoverability (Friends feature) ──────────────────────
        # Add as nullable first so existing rows aren't rejected; app always sets
        # a generated username on new registrations.
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_discoverable BOOLEAN NOT NULL DEFAULT TRUE",
        # ── token_version (security: invalidate JWTs on password change / logout) ─
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0",
        # ── Equipment feature ─────────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS equipment (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            is_bodyweight BOOLEAN NOT NULL DEFAULT FALSE,
            created TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS user_equipment (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, equipment_id)
        )
        """,
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS equipment_category VARCHAR(50)",
        # ── Friends & Activity Feed feature ───────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS friendships (
            id SERIAL PRIMARY KEY,
            requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            addressee_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(requester_id, addressee_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS session_reactions (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            reactor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            emoji VARCHAR(10) NOT NULL DEFAULT '💪',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(session_id, reactor_id)
        )
        """,
        # ── Notifications feature ─────────────────────────────────────────────
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            type VARCHAR(50) NOT NULL,
            actor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            meta JSONB,
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
    ]
    # Single session for all migrations — was creating a new one per statement.
    # If one statement fails (e.g. column already exists with different default)
    # we roll back THAT statement and continue with the rest.
    db = SessionLocal()
    try:
        for stmt in migrations:
            try:
                db.execute(text(stmt))
                db.commit()
            except Exception as exc:
                db.rollback()
                _settings.logger.warning(f"Migration skipped/warned: {exc}")
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    """
    Create database tables on startup.
    In production, this should be replaced by Alembic migrations.
    """
    Base.metadata.create_all(bind=engine)
    _run_column_migrations()

    # Seed reference data
    from app.db.session import SessionLocal
    from app.db.seed import seed_exercises, seed_equipment
    db = SessionLocal()
    try:
        seed_exercises(db)
        seed_equipment(db)
    finally:
        db.close()

    # Backfill target_sessions for any goals that predate the feature
    threading.Thread(target=_backfill_target_sessions, daemon=True).start()

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
# API ROUTERS — versioned under /api/v1/
# Each resource also gets a legacy `/api/...` alias so existing app installs
# don't break the moment we deploy. Remove the legacy aliases once the
# minimum-supported app version is on v1.

def _mount(router, suffix: str):
    """Register a router at both /api/v1/<suffix> and /api/<suffix> (legacy)."""
    app.include_router(router, prefix=f"/api/v1/{suffix.lstrip('/')}")
    app.include_router(router, prefix=f"/api/{suffix.lstrip('/')}", include_in_schema=False)

app.include_router(auth.router, prefix="/auth")  # auth keeps top-level path
_mount(admin.router,         "admin")
_mount(profiles.router,      "profiles")
_mount(goals.router,         "goals")
_mount(sessions.router,      "sessions")
_mount(exercise.router,      "exercises")
_mount(planner.router,       "planner")
_mount(stats.router,         "stats")
_mount(users.router,         "users")
_mount(equipment.router,     "equipment")
_mount(friends.router,       "friends")
_mount(feed.router,          "feed")
_mount(notifications.router, "notifications")

# -------------------------------------------------
