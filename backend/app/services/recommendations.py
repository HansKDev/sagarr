from __future__ import annotations

from datetime import datetime
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RecommendationCache, UserPreference, User
from .ai import get_ai_provider
from .tautulli import get_user_history


async def generate_recommendations(db: Session, user_id: int) -> RecommendationCache:
    """
    Orchestrate fetching history, calling AI, and storing parsed JSON.
    Generates both Movie and TV recommendations.
    """
    user = db.get(User, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found.")

    if not user.tautulli_user_id:
        raise ValueError("User is not yet mapped to a Tautulli user.")

    # Fetch history (limit increased to get enough of both types)
    tautulli_history = await get_user_history(int(user.tautulli_user_id), limit=300)

    # Split history by media type
    movies_history = [item for item in tautulli_history if item.get("media_type") == "movie"]
    tv_history = [item for item in tautulli_history if item.get("media_type") in ("show", "episode", "season")]

    # Prepare context slices
    top_movies = movies_history[:10]
    recent_movies = movies_history[:20]
    
    top_tv = tv_history[:10]
    recent_tv = tv_history[:20]

    # Fetch dislikes from UserPreference
    dislikes_stmt = (
        select(UserPreference)
        .where(UserPreference.user_id == user_id)
        .where(UserPreference.rating == -1)
    )
    dislikes_rows = db.execute(dislikes_stmt).scalars().all()
    dislikes = [{"tmdb_id": row.tmdb_id, "media_type": row.media_type} for row in dislikes_rows]

    user_context: dict[str, Any] = {
        "movies": {
            "top": top_movies,
            "recent": recent_movies
        },
        "tv": {
            "top": top_tv,
            "recent": recent_tv
        },
        "dislikes": dislikes,
    }

    system_prompt = (
        "You are an AI that creates creative, descriptive recommendation categories "
        "for a single user based on their Plex/Tautulli watch history and explicit dislikes. "
        "You must generate recommendations for Movies, TV Series, AND Documentaries. "
        "Respond ONLY with valid JSON in the following shape: "
        '{"movies": [{"title": "...", "reason": "...", "items": [123]}], '
        '"tv": [{"title": "...", "reason": "...", "items": [456]}], '
        '"documentaries": [{"title": "...", "reason": "...", "items": [789]}]}. '
        "Each item in 'items' must be an integer TMDb ID. "
        "Ensure 'items' contains valid TMDb IDs for the respective media type."
    )

    prompt = (
        "Here is the user's viewing context as JSON.\n\n"
        f"{json.dumps(user_context, ensure_ascii=False)}\n\n"
        "Using this data, generate several recommendation categories tailored to the user, separated by 'movies', 'tv', and 'documentaries'. "
        "Remember: respond only with JSON and no extra commentary."
    )

    provider = get_ai_provider()
    raw_text = await provider.generate(prompt=prompt, system_prompt=system_prompt)

    try:
        parsed: dict[str, Any] = json.loads(raw_text or "{}")
    except json.JSONDecodeError:
        parsed = {}

    # Normalize structure
    movies_cats = parsed.get("movies", []) or []
    tv_cats = parsed.get("tv", []) or []
    docs_cats = parsed.get("documentaries", []) or []
    
    # Fallback for old single-list format if AI hallucinates
    if "categories" in parsed and not movies_cats and not tv_cats:
        movies_cats = parsed["categories"]

    payload = {
        "movies": movies_cats,
        "tv": tv_cats,
        "documentaries": docs_cats
    }

    cache = RecommendationCache(
        user_id=user_id,
        recommendations=json.dumps(payload),
        created_at=datetime.utcnow(),
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache
