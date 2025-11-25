from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User, AppSetting
from ..security import get_current_user
from ..services.tautulli import tautulli_service
from ..services.overseerr import overseerr_service
from ..services.ai import get_ai_provider
from ..services.metadata import fetch_tmdb_details, MetadataNotConfiguredError


router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)


class SettingsUpdate(BaseModel):
    TAUTULLI_URL: str
    TAUTULLI_API_KEY: str
    OVERSEERR_URL: str
    OVERSEERR_API_KEY: str
    AI_PROVIDER: str
    AI_API_KEY: str
    AI_MODEL: str
    TMDB_API_KEY: str
    AI_FALLBACK_PROVIDER: str
    AI_FALLBACK_API_KEY: str
    AI_FALLBACK_MODEL: str


def _ensure_admin(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )


def _save_setting(db: Session, key: str, value: str) -> None:
    """
    Upsert a single app-level setting into the persistent store.
    """
    setting = db.query(AppSetting).filter(AppSetting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = AppSetting(key=key, value=value)
        db.add(setting)


@router.get("/settings")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    # Note: We mask sensitive keys in the API response
    return {
        "TAUTULLI_URL": settings.TAUTULLI_URL,
        "TAUTULLI_API_KEY": "***" if settings.TAUTULLI_API_KEY else "",
        "OVERSEERR_URL": settings.OVERSEERR_URL,
        "OVERSEERR_API_KEY": "***" if settings.OVERSEERR_API_KEY else "",
        "AI_PROVIDER": settings.AI_PROVIDER,
        "AI_API_KEY": "***" if settings.AI_API_KEY else "",
        "AI_MODEL": settings.AI_MODEL,
        "TMDB_API_KEY": "***" if settings.TMDB_API_KEY else "",
        "AI_FALLBACK_PROVIDER": settings.AI_FALLBACK_PROVIDER,
        "AI_FALLBACK_API_KEY": "***" if settings.AI_FALLBACK_API_KEY else "",
        "AI_FALLBACK_MODEL": settings.AI_FALLBACK_MODEL,
    }


@router.post("/settings")
async def update_settings(
    new_settings: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)

    # Only update if value is provided (and not masked)
    if new_settings.TAUTULLI_URL:
        settings.TAUTULLI_URL = new_settings.TAUTULLI_URL
        _save_setting(db, "TAUTULLI_URL", new_settings.TAUTULLI_URL)
    if new_settings.TAUTULLI_API_KEY and "***" not in new_settings.TAUTULLI_API_KEY:
        settings.TAUTULLI_API_KEY = new_settings.TAUTULLI_API_KEY
        _save_setting(db, "TAUTULLI_API_KEY", new_settings.TAUTULLI_API_KEY)

    if new_settings.OVERSEERR_URL:
        settings.OVERSEERR_URL = new_settings.OVERSEERR_URL
        _save_setting(db, "OVERSEERR_URL", new_settings.OVERSEERR_URL)
    if new_settings.OVERSEERR_API_KEY and "***" not in new_settings.OVERSEERR_API_KEY:
        settings.OVERSEERR_API_KEY = new_settings.OVERSEERR_API_KEY
        _save_setting(db, "OVERSEERR_API_KEY", new_settings.OVERSEERR_API_KEY)

    if new_settings.AI_PROVIDER:
        settings.AI_PROVIDER = new_settings.AI_PROVIDER
        _save_setting(db, "AI_PROVIDER", new_settings.AI_PROVIDER)
    if new_settings.AI_API_KEY and "***" not in new_settings.AI_API_KEY:
        settings.AI_API_KEY = new_settings.AI_API_KEY
        _save_setting(db, "AI_API_KEY", new_settings.AI_API_KEY)
    if new_settings.AI_MODEL:
        settings.AI_MODEL = new_settings.AI_MODEL
        _save_setting(db, "AI_MODEL", new_settings.AI_MODEL)
    if new_settings.TMDB_API_KEY and "***" not in new_settings.TMDB_API_KEY:
        settings.TMDB_API_KEY = new_settings.TMDB_API_KEY
        _save_setting(db, "TMDB_API_KEY", new_settings.TMDB_API_KEY)

    if new_settings.AI_FALLBACK_PROVIDER:
        settings.AI_FALLBACK_PROVIDER = new_settings.AI_FALLBACK_PROVIDER
        _save_setting(db, "AI_FALLBACK_PROVIDER", new_settings.AI_FALLBACK_PROVIDER)
    if new_settings.AI_FALLBACK_API_KEY and "***" not in new_settings.AI_FALLBACK_API_KEY:
        settings.AI_FALLBACK_API_KEY = new_settings.AI_FALLBACK_API_KEY
        _save_setting(db, "AI_FALLBACK_API_KEY", new_settings.AI_FALLBACK_API_KEY)
    if new_settings.AI_FALLBACK_MODEL:
        settings.AI_FALLBACK_MODEL = new_settings.AI_FALLBACK_MODEL
        _save_setting(db, "AI_FALLBACK_MODEL", new_settings.AI_FALLBACK_MODEL)

    db.commit()
    return {"status": "updated"}


class TestResult(BaseModel):
    ok: bool
    message: str


@router.get("/test/tautulli", response_model=TestResult)
async def test_tautulli(current_user: User = Depends(get_current_user)) -> TestResult:
    _ensure_admin(current_user)

    if not settings.TAUTULLI_URL or not settings.TAUTULLI_API_KEY:
        return TestResult(ok=False, message="Tautulli URL or API key is not configured.")

    try:
        users = await tautulli_service.get_users()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact Tautulli: {exc}",
        ) from exc

    count = len(users) if isinstance(users, list) else 0
    return TestResult(ok=True, message=f"Tautulli reachable. Users found: {count}.")


@router.get("/test/overseerr", response_model=TestResult)
async def test_overseerr(current_user: User = Depends(get_current_user)) -> TestResult:
    _ensure_admin(current_user)

    if not settings.OVERSEERR_URL or not settings.OVERSEERR_API_KEY:
        return TestResult(ok=False, message="Overseerr URL or API key is not configured.")

    # Try a simple availability check for a well-known TMDb movie ID (e.g. 550 = Fight Club).
    try:
        data = await overseerr_service.check_availability(550, media_type="movie")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact Overseerr: {exc}",
        ) from exc

    status_str = data.get("status", "UNKNOWN")
    return TestResult(ok=True, message=f"Overseerr reachable. Sample status: {status_str}.")


@router.get("/test/ai", response_model=TestResult)
async def test_ai(current_user: User = Depends(get_current_user)) -> TestResult:
    _ensure_admin(current_user)

    if not settings.AI_MODEL or not settings.AI_PROVIDER:
        return TestResult(ok=False, message="AI provider or model is not configured.")

    provider = get_ai_provider()
    prompt = "Return a JSON object: {\"status\":\"ok\"}"
    try:
        raw = await provider.generate(prompt=prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact AI provider: {exc}",
        ) from exc

    # We don't care about the exact content here, just that we got a response.
    if not raw or not isinstance(raw, str):
        return TestResult(ok=False, message="AI provider responded with an empty or invalid body.")

    return TestResult(ok=True, message="AI provider responded successfully.")


@router.get("/test/tmdb", response_model=TestResult)
async def test_tmdb(current_user: User = Depends(get_current_user)) -> TestResult:
    _ensure_admin(current_user)

    try:
        details = await fetch_tmdb_details([550])
    except MetadataNotConfiguredError:
        return TestResult(ok=False, message="TMDb API key is not configured.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to contact TMDb: {exc}",
        ) from exc

    if not details:
        return TestResult(ok=False, message="TMDb responded, but no movie details were returned.")

    title = details[0].get("title") or details[0].get("name") or "Unknown"
    return TestResult(ok=True, message=f"TMDb reachable. Example movie title: {title}.")
