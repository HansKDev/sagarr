from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .config import get_settings
from .db import init_db, SessionLocal
from .routers import auth, health, recommendations, media
from .models import User
from .services.recommendations import generate_recommendations


settings = get_settings()

app = FastAPI(title=settings.app_name)


def configure_cors(application: FastAPI) -> None:
    origins = [str(origin) for origin in settings.backend_cors_origins]
    if not origins:
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def include_routers(application: FastAPI) -> None:
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(recommendations.router)
    application.include_router(media.router)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()

    scheduler = AsyncIOScheduler()

    async def refresh_recommendations_job() -> None:
        db: Session = SessionLocal()
        try:
            users = db.query(User).all()
            for user in users:
                try:
                    await generate_recommendations(db, user.id)
                except Exception:
                    # TODO: add proper logging
                    continue
        finally:
            db.close()

    # Run every night at 3 AM server time
    scheduler.add_job(refresh_recommendations_job, CronTrigger(hour=3, minute=0))
    scheduler.start()


configure_cors(app)
include_routers(app)
