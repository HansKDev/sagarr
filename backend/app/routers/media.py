from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import UserPreference
from ..schemas import (
    MediaStatusResponse,
    RateMediaRequest,
    MediaRequestBody,
    MessageResponse,
)
from ..security import get_current_user
from ..services.overseerr import check_availability, request_media, OverseerrNotConfiguredError


router = APIRouter(tags=["media"])

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[object, Depends(get_current_user)]


@router.get("/api/media/{tmdb_id}/status", response_model=MediaStatusResponse)
async def get_media_status(tmdb_id: int) -> MediaStatusResponse:
    """
    Return basic availability status for a TMDb item based on Overseerr data.
    """
    try:
        data = await check_availability(tmdb_id)
    except OverseerrNotConfiguredError:
        return MediaStatusResponse(tmdb_id=tmdb_id, status="unknown")
    except Exception:
        return MediaStatusResponse(tmdb_id=tmdb_id, status="unknown")

    # Heuristic: if Overseerr returns any request entries, treat as requested.
    results = (
        data.get("results")
        or data.get("data", {}).get("results")
        or data.get("data", {}).get("requests")
        or []
    )

    if not results:
        return MediaStatusResponse(tmdb_id=tmdb_id, status="missing")

    # We could inspect media status here and distinguish "available" vs "requested".
    # For now, if we have at least one entry, treat as "requested".
    return MediaStatusResponse(tmdb_id=tmdb_id, status="requested")


@router.post("/api/media/{tmdb_id}/request", response_model=MessageResponse)
async def create_media_request(
    tmdb_id: int,
    payload: MediaRequestBody,
    current_user: CurrentUserDep,
) -> MessageResponse:
    """
    Proxy a media request to Overseerr.
    """
    try:
        await request_media(tmdb_id=tmdb_id, media_type=payload.media_type)
    except OverseerrNotConfiguredError:
        return MessageResponse(message="Overseerr is not configured on the server.")
    except Exception:
        return MessageResponse(message="Failed to create Overseerr request.")

    return MessageResponse(message="Request submitted")


@router.post("/api/media/{tmdb_id}/rate", response_model=MessageResponse)
async def rate_media(
    tmdb_id: int,
    payload: RateMediaRequest,
    db: DbDep,
    current_user: CurrentUserDep,
) -> MessageResponse:
    """
    Store a simple thumbs up / down rating for a given item.
    """
    numeric_rating = 1 if payload.rating == "up" else -1
    pref = UserPreference(
        user_id=current_user.id,
        tmdb_id=tmdb_id,
        media_type="movie",
        rating=numeric_rating,
    )
    db.add(pref)
    db.commit()

    return MessageResponse(message="Rating saved")

