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


def _is_documentary_meta(meta: dict) -> bool:
    """
    Best-effort check whether a TMDb metadata dict represents a documentary.
    """
    genres = meta.get("genres")
    if isinstance(genres, list):
        for g in genres:
            name = str(g.get("name") or "").lower()
            gid = g.get("id")
            if name == "documentary" or gid == 99:
                return True

    genre_ids = meta.get("genre_ids")
    if isinstance(genre_ids, list) and 99 in genre_ids:
        return True

    return False


async def _enrich_categories(
    raw_categories: list[dict],
    media_type: str,
    watched_titles: set[str],
    blocked_tmdb_ids: set[int],
    category_kind: str,
) -> list[RecommendationCategory]:
    """
    Helper to fetch metadata for a list of raw categories and return enriched objects.
    """
    if not raw_categories:
        return []

    # Collect TMDb IDs
    tmdb_ids: set[int] = set()
    for cat in raw_categories:
        for tmdb_id in cat.get("items", []):
            if isinstance(tmdb_id, int):
                tmdb_ids.add(tmdb_id)

    metadata_map: dict[int, dict] = {}
    if tmdb_ids:
        try:
            details = await fetch_tmdb_details(list(tmdb_ids), media_type=media_type)
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
            # Skip items the user has already rated/seen inside Sagarr.
            if tmdb_id in blocked_tmdb_ids:
                continue
            meta = metadata_map.get(tmdb_id, {})
            name = meta.get("title") or meta.get("name")
            # For the "Docs" lane, only keep true documentaries.
            if category_kind == "docs" and meta:
                if not _is_documentary_meta(meta):
                    continue
            # Skip items the user has already watched (by title).
            norm_name = (name or "").strip().lower()
            if norm_name and norm_name in watched_titles:
                continue
            poster_path = meta.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            items.append(
                MediaItem(
                    tmdb_id=tmdb_id,
                    title=name,
                    overview=meta.get("overview"),
                    poster_url=poster_url,
                    media_type=media_type
                )
            )
        if items:
            categories.append(RecommendationCategory(title=title, reason=reason, items=items))
    
    return categories


@router.get("/api/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    db: DbDep,
    current_user: CurrentUserDep,
) -> RecommendationsResponse:
    """
    Return the latest recommendation categories for the current user,
    enriching TMDb IDs with basic metadata. Returns both movies and tv.
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

    # Handle legacy format where "categories" was the only key (assumed movies)
    raw_movies = data.get("movies", [])
    if not raw_movies and "categories" in data:
        raw_movies = data["categories"]
    
    raw_tv = data.get("tv", [])
    raw_docs = data.get("documentaries", [])

    watched_titles = {t.strip().lower() for t in data.get("watched_titles", []) if isinstance(t, str)}
    blocked_tmdb_ids: set[int] = set()
    for raw_id in data.get("rated_tmdb_ids", []) or []:
        try:
            blocked_tmdb_ids.add(int(raw_id))
        except (TypeError, ValueError):
            continue

    movies_enriched = await _enrich_categories(raw_movies, "movie", watched_titles, blocked_tmdb_ids, "movies")
    tv_enriched = await _enrich_categories(raw_tv, "tv", watched_titles, blocked_tmdb_ids, "tv")
    # For now, we treat documentaries as movies. 
    # Future improvement: Support mixed types or ask AI to split doc-series vs doc-movies.
    docs_enriched = await _enrich_categories(raw_docs, "movie", watched_titles, blocked_tmdb_ids, "docs")

    return RecommendationsResponse(
        movies=movies_enriched, 
        tv=tv_enriched, 
        documentaries=docs_enriched
    )
