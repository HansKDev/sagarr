import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from . import models
from .models import User, AppSetting
from .config import settings
from .routers import auth, admin, media, recommendations, users
from .services.recommendations import generate_recommendations

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sagarr API", version="0.1.0")


# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default (dev)
    "http://localhost:3000",  # React default
    "http://127.0.0.1:5173",
    "http://localhost:8090",  # Docker nginx frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(media.router)
app.include_router(recommendations.router)
app.include_router(users.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Sagarr Backend", "database": "connected"}


async def _refresh_recommendations_loop() -> None:
    """
    Simple background loop that refreshes recommendations for all users daily.
    """
    # Run once shortly after startup, then every 24 hours.
    await asyncio.sleep(5)
    while True:
        db: Session = SessionLocal()
        try:
            users = db.query(User).all()
            for user in users:
                try:
                    await generate_recommendations(db, user.id)
                except Exception:
                    # For now we swallow errors; production should log them.
                    continue
        finally:
            db.close()

        # Sleep for 24 hours
        await asyncio.sleep(60 * 60 * 24)


def _load_persistent_settings() -> None:
    """
    On startup, load any persisted app-level settings from the database and
    apply them to the in-memory settings object, overriding env defaults.
    """
    db: Session = SessionLocal()
    try:
        rows = db.query(AppSetting).all()
        for row in rows:
            if hasattr(settings, row.key):
                setattr(settings, row.key, row.value)
    finally:
        db.close()


@app.on_event("startup")
async def startup_event() -> None:
    # First, hydrate settings from persistent store so services see the
    # latest config rather than only env defaults.
    _load_persistent_settings()
    # Fire-and-forget background task for nightly recommendation refresh.
    asyncio.create_task(_refresh_recommendations_loop())
