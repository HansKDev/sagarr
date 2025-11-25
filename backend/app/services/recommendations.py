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
    """
    user = db.get(User, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found.")

    if not user.tautulli_user_id:
        raise ValueError("User is not yet mapped to a Tautulli user.")

    tautulli_history = await get_user_history(int(user.tautulli_user_id), limit=200)

    # Very simple derivation of context slices; these can be improved later.
    top_movies = tautulli_history[:10]
    recent_watches = tautulli_history[:20]

    # Fetch dislikes from UserPreference
    dislikes_stmt = (
        select(UserPreference)
        .where(UserPreference.user_id == user_id)
        .where(UserPreference.rating == -1)
    )
    dislikes_rows = db.execute(dislikes_stmt).scalars().all()
    dislikes = [{"tmdb_id": row.tmdb_id} for row in dislikes_rows]

    user_context: dict[str, Any] = {
        "top_movies": top_movies,
        "recent_watches": recent_watches,
        "dislikes": dislikes,
    }

    provider = get_ai_provider()
    raw = await provider.generate_categories(user_context=user_context)

    # Ensure a categories key exists
    categories = raw.get("categories", [])
    payload = {"categories": categories}

    cache = RecommendationCache(
        user_id=user_id,
        recommendations=json.dumps(payload),
        created_at=datetime.utcnow(),
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache
