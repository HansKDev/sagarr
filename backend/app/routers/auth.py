from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import httpx
from .. import models, database, config
from ..database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)

# Schemas
class LoginResponse(BaseModel):
    auth_url: str
    pin_id: int
    code: str

class CallbackRequest(BaseModel):
    pin_id: int

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Utils
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
    return encoded_jwt

# Endpoints
@router.get("/login", response_model=LoginResponse)
async def login():
    """
    Initiate Plex OAuth flow.
    Returns the URL to redirect the user to, and the PIN ID to check later.
    """
    headers = {
        "X-Plex-Product": config.settings.PLEX_PRODUCT,
        "X-Plex-Client-Identifier": config.settings.PLEX_CLIENT_ID,
        "X-Plex-Version": config.settings.PLEX_VERSION,
        "X-Plex-Device": config.settings.PLEX_DEVICE,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Get PIN
        try:
            resp = await client.post("https://plex.tv/api/v2/pins?strong=true", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            pin_id = data['id']
            code = data['code']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reach Plex API: {str(e)}")

    # 2. Construct Auth URL
    # We set forwardUrl to our frontend callback page
    forward_url = f"{config.settings.FRONTEND_URL}/login/callback"
    auth_url = (
        f"https://app.plex.tv/auth#?"
        f"clientID={config.settings.PLEX_CLIENT_ID}&"
        f"code={code}&"
        f"context[device][product]={config.settings.PLEX_PRODUCT}&"
        f"forwardUrl={forward_url}"
    )
    
    return {"auth_url": auth_url, "pin_id": pin_id, "code": code}

@router.post("/callback", response_model=Token)
async def callback(request: CallbackRequest, db: Session = Depends(get_db)):
    """
    Check PIN status. If verified, create/update user and return JWT.
    """
    headers = {
        "X-Plex-Client-Identifier": config.settings.PLEX_CLIENT_ID,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # 1. Check PIN
        try:
            resp = await client.get(f"https://plex.tv/api/v2/pins/{request.pin_id}", headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to check PIN: {str(e)}")

        auth_token = data.get('authToken')
        if not auth_token:
            # Plex hasn't authorized this PIN yet (user didn't finish login or PIN expired)
            raise HTTPException(status_code=400, detail="User has not authorized the app yet.")

        # 2. Get User Details using the same client
        user_headers = {
            "X-Plex-Token": auth_token,
            "X-Plex-Client-Identifier": config.settings.PLEX_CLIENT_ID,
            "Accept": "application/json"
        }

        try:
            user_resp = await client.get("https://plex.tv/api/v2/user", headers=user_headers)
            user_resp.raise_for_status()
            user_data = user_resp.json()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to fetch user info: {str(e)}")
        
    # 3. Create/Update User in DB
    plex_id = user_data.get('id')
    username = user_data.get('username')
    email = user_data.get('email')
    thumb = user_data.get('thumb')
    
    # Check Tautulli
    from ..services.tautulli import tautulli_service
    tautulli_users = await tautulli_service.get_users()
    tautulli_user_id = None

    # Map Plex user to Tautulli user.
    # Prefer email match, then username/friendly_name, falling back to id if they align.
    plex_email = (email or "").lower()
    plex_username = (username or "").lower()

    for t_user in tautulli_users:
        t_email = (t_user.get("email") or "").lower()
        t_username = (t_user.get("username") or "").lower()
        t_friendly = (t_user.get("friendly_name") or "").lower()
        t_id = t_user.get("user_id")

        if plex_email and t_email and plex_email == t_email:
            tautulli_user_id = t_id
            break
        if plex_username and plex_username in (t_username, t_friendly):
            tautulli_user_id = t_id
            break
        if t_id is not None and str(t_id) == str(plex_id):
            tautulli_user_id = t_id
            break
            
    user = db.query(models.User).filter(models.User.plex_id == plex_id).first()
    if not user:
        user = models.User(
            plex_id=plex_id,
            username=username,
            email=email,
            thumb=thumb,
            auth_token=auth_token,
            tautulli_user_id=tautulli_user_id,
        )
        db.add(user)
    else:
        user.username = username
        user.email = email
        user.thumb = thumb
        user.auth_token = auth_token
        user.tautulli_user_id = tautulli_user_id

    # Bootstrap admin: if there is no admin user yet, make this user admin.
    has_admin = db.query(models.User).filter(models.User.is_admin.is_(True)).first()
    if not has_admin:
        user.is_admin = True

    db.commit()
    db.refresh(user)
    
    # 4. Issue JWT
    access_token_expires = timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "thumb": user.thumb
        }
    }
