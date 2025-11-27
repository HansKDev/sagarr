import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserSettings
from ..security import get_current_user

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
)

@router.get("/settings", response_model=UserSettings)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
):
    if not current_user.settings:
        return UserSettings()
    try:
        data = json.loads(current_user.settings)
        return UserSettings(**data)
    except json.JSONDecodeError:
        return UserSettings()

@router.post("/settings", response_model=UserSettings)
async def update_user_settings(
    settings: UserSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Merge with existing settings
    current_data = {}
    if current_user.settings:
        try:
            current_data = json.loads(current_user.settings)
        except json.JSONDecodeError:
            current_data = {}
    
    # Update with new values (only if not None, or handle full update?)
    # For now, let's assume partial update or full update. 
    # Since UserSettings only has date_cutoff, we can just update that.
    if settings.date_cutoff is not None:
        current_data["date_cutoff"] = settings.date_cutoff
    
    current_user.settings = json.dumps(current_data)
    db.commit()
    db.refresh(current_user)
    
    return UserSettings(**current_data)
