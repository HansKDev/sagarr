from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..config import settings
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"]
)

class SettingsUpdate(BaseModel):
    TAUTULLI_URL: str
    TAUTULLI_API_KEY: str
    OVERSEERR_URL: str
    OVERSEERR_API_KEY: str
    AI_PROVIDER: str
    AI_API_KEY: str
    AI_MODEL: str

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    # In a real app, we might check for admin role here
    # For now, we return the current in-memory settings
    # Note: We mask sensitive keys
    return {
        "TAUTULLI_URL": settings.TAUTULLI_URL,
        "TAUTULLI_API_KEY": "***" if settings.TAUTULLI_API_KEY else "",
        "OVERSEERR_URL": settings.OVERSEERR_URL,
        "OVERSEERR_API_KEY": "***" if settings.OVERSEERR_API_KEY else "",
        "AI_PROVIDER": settings.AI_PROVIDER,
        "AI_API_KEY": "***" if settings.AI_API_KEY else "",
        "AI_MODEL": settings.AI_MODEL
    }

@router.post("/settings")
async def update_settings(new_settings: SettingsUpdate, db: Session = Depends(get_db)):
    # In a real app, we would persist these to a DB or .env file
    # For this MVP, we will update the in-memory settings object
    
    # Only update if value is provided (and not masked)
    if new_settings.TAUTULLI_URL: settings.TAUTULLI_URL = new_settings.TAUTULLI_URL
    if new_settings.TAUTULLI_API_KEY and "***" not in new_settings.TAUTULLI_API_KEY: 
        settings.TAUTULLI_API_KEY = new_settings.TAUTULLI_API_KEY
        
    if new_settings.OVERSEERR_URL: settings.OVERSEERR_URL = new_settings.OVERSEERR_URL
    if new_settings.OVERSEERR_API_KEY and "***" not in new_settings.OVERSEERR_API_KEY:
        settings.OVERSEERR_API_KEY = new_settings.OVERSEERR_API_KEY
        
    if new_settings.AI_PROVIDER: settings.AI_PROVIDER = new_settings.AI_PROVIDER
    if new_settings.AI_API_KEY and "***" not in new_settings.AI_API_KEY:
        settings.AI_API_KEY = new_settings.AI_API_KEY
    if new_settings.AI_MODEL: settings.AI_MODEL = new_settings.AI_MODEL
    
    return {"status": "updated"}
