from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import UserPreference
from ..schemas import (
    MediaStatusResponse,
    RateMediaRequest,
    MediaRequestBody,
    MessageResponse,
    HistoryResponse,
    HistoryItem,
)
from ..security import get_current_user
from ..services.overseerr import check_availability, request_media, OverseerrNotConfiguredError
from ..services.metadata import fetch_tmdb_details


router = APIRouter(tags=["media"])

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[object, Depends(get_current_user)]


@router.get("/api/media/{tmdb_id}/status", response_model=MediaStatusResponse)
async def get_media_status(tmdb_id: int, media_type: str = "movie") -> MediaStatusResponse:
    """
    Return basic availability status for a TMDb item based on Overseerr data.
    """
    try:
        data = await check_availability(tmdb_id, media_type=media_type)
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
    db: DbDep,
    current_user: CurrentUserDep,
) -> MessageResponse:
    """
    Proxy a media request to Overseerr.
    """
    try:
        await request_media(tmdb_id=tmdb_id, media_type=payload.media_type)
        
        # Log the request as a high-value preference (Rating 2)
        pref = UserPreference(
            user_id=current_user.id,
            tmdb_id=tmdb_id,
            media_type=payload.media_type,
            rating=2,  # 2 = Requested / Super Like
        )
        db.add(pref)
        db.commit()
        
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
    Store or update a simple thumbs up / down rating for a given item.
    """
    numeric_rating = 1 if payload.rating == "up" else -1
    
    # Check for existing preference
    stmt = select(UserPreference).where(
        UserPreference.user_id == current_user.id,
        UserPreference.tmdb_id == tmdb_id
    )
    existing = db.execute(stmt).scalars().first()
    
    if existing:
        existing.rating = numeric_rating
        existing.media_type = payload.media_type
        # Update timestamp? SQLAlchemy onupdate might handle it if configured, 
        # but our model has server_default=func.now(). It doesn't have onupdate.
        # Let's force update it if we want to bump it to top of history.
        # existing.created_at = func.now() # Requires import func
        pass 
    else:
        pref = UserPreference(
            user_id=current_user.id,
            tmdb_id=tmdb_id,
            media_type=payload.media_type,
            rating=numeric_rating,
        )
        db.add(pref)
    
    db.commit()

    return MessageResponse(message="Rating saved")


@router.delete("/api/media/{tmdb_id}/rate", response_model=MessageResponse)
async def delete_rating(
    tmdb_id: int,
    db: DbDep,
    current_user: CurrentUserDep,
) -> MessageResponse:
    """
    Remove a rating (undo).
    """
    stmt = select(UserPreference).where(
        UserPreference.user_id == current_user.id,
        UserPreference.tmdb_id == tmdb_id
    )
    existing = db.execute(stmt).scalars().first()
    
    if existing:
        db.delete(existing)
        db.commit()
        return MessageResponse(message="Rating removed")
    
    raise HTTPException(status_code=404, detail="Rating not found")


@router.get("/api/user/history", response_model=HistoryResponse)
async def get_history(
    db: DbDep,
    current_user: CurrentUserDep,
) -> HistoryResponse:
    """
    Get user's interaction history (Requests, Likes, Dislikes).
    """
    stmt = (
        select(UserPreference)
        .where(UserPreference.user_id == current_user.id)
        .order_by(desc(UserPreference.created_at))
        .limit(100) # Pagination can be added later
    )
    prefs = db.execute(stmt).scalars().all()
    
    if not prefs:
        return HistoryResponse(history=[])

    # Split by type for metadata fetching
    movies = [p for p in prefs if p.media_type == 'movie']
    tv = [p for p in prefs if p.media_type == 'tv']
    
    movie_meta = []
    tv_meta = []
    
    if movies:
        movie_meta = await fetch_tmdb_details([p.tmdb_id for p in movies], "movie")
    if tv:
        tv_meta = await fetch_tmdb_details([p.tmdb_id for p in tv], "tv")
        
    movie_map = {m['id']: m for m in movie_meta}
    tv_map = {t['id']: t for t in tv_meta}
    
    results = []
    for p in prefs:
        meta = {}
        if p.media_type == 'movie':
            meta = movie_map.get(p.tmdb_id, {})
        elif p.media_type == 'tv':
            meta = tv_map.get(p.tmdb_id, {})
            
        title = meta.get("title") or meta.get("name")
        poster_path = meta.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None
        
        results.append(HistoryItem(
            tmdb_id=p.tmdb_id,
            media_type=p.media_type,
            rating=p.rating,
            created_at=p.created_at,
            title=title,
            poster_url=poster_url
        ))
        
    return HistoryResponse(history=results)

