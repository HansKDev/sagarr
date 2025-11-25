from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import RecommendationCache
from ..schemas import RecommendationsResponse, RecommendationCategory, MediaItem
from ..security import get_current_user
from ..services.metadata import fetch_tmdb_details, MetadataNotConfiguredError
from ..services.recommendations import generate_recommendations


router = APIRouter(tags=["recommendations"])

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[object, Depends(get_current_user)]


@router.get("/api/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    db: DbDep,
    current_user: CurrentUserDep,
) -> RecommendationsResponse:
    """
    Return the latest recommendation categories for the current user,
    enriching TMDb IDs with basic metadata.
    """
    stmt = (
        select(RecommendationCache)
        .where(RecommendationCache.user_id == current_user.id)
        .order_by(desc(RecommendationCache.created_at))
    )
    cache = db.execute(stmt).scalars().first()

    if cache is None:
        # No cache yet; generate on demand
        try:
            cache = await generate_recommendations(db, current_user.id)
        except ValueError as exc:
            # Surface mapping/config issues (e.g. missing Tautulli mapping)
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        data = json.loads(cache.recommendations or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Invalid recommendation cache format") from exc

    raw_categories = data.get("categories", []) or []

    # Collect TMDb IDs
    tmdb_ids: set[int] = set()
    for cat in raw_categories:
        for tmdb_id in cat.get("items", []):
            if isinstance(tmdb_id, int):
                tmdb_ids.add(tmdb_id)

    metadata_map: dict[int, dict] = {}
    if tmdb_ids:
        try:
            details = await fetch_tmdb_details(list(tmdb_ids))
            for item in details:
                tmdb_id = item.get("id")
                if isinstance(tmdb_id, int):
                    metadata_map[tmdb_id] = item
        except MetadataNotConfiguredError:
            # If metadata is not configured, continue with bare IDs.
            metadata_map = {}
        except Exception:
            metadata_map = {}

    categories: list[RecommendationCategory] = []
    for cat in raw_categories:
        title = cat.get("title") or "Recommendations"
        reason = cat.get("reason") or ""
        items: list[MediaItem] = []
        for tmdb_id in cat.get("items", []):
            if not isinstance(tmdb_id, int):
                continue
            meta = metadata_map.get(tmdb_id, {})
            name = meta.get("title") or meta.get("name")
            poster_path = meta.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            items.append(
                MediaItem(
                    tmdb_id=tmdb_id,
                    title=name,
                    overview=meta.get("overview"),
                    poster_url=poster_url,
                )
            )
        categories.append(RecommendationCategory(title=title, reason=reason, items=items))

    return RecommendationsResponse(categories=categories)
