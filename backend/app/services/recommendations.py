from __future__ import annotations

from datetime import datetime
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RecommendationCache, UserPreference, User
from .ai import get_ai_provider
from .tautulli import get_user_history


ADULT_KEYWORDS = [
    "porn",
    "porno",
    "xxx",
    "adult",
    "erotic",
    "erotica",
    "hentai",
]


def _to_text(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value or "")


def _looks_adult(item: dict[str, Any]) -> bool:
    """
    Best-effort heuristic to filter out explicit adult content from the
    AI context using Tautulli fields (library name, genres, title, etc.).
    """
    combined = " ".join(
        [
            _to_text(item.get("genres")),
            _to_text(item.get("section_name")),
            _to_text(item.get("library_name")),
            _to_text(item.get("title")),
            _to_text(item.get("grandparent_title")),
            _to_text(item.get("tagline")),
        ]
    ).lower()

    return any(keyword in combined for keyword in ADULT_KEYWORDS)


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

    # Strip out explicit adult content before it ever reaches the AI.
    tautulli_history = [item for item in tautulli_history if not _looks_adult(item)]

    # Build a set of normalized titles the user has already watched so we can
    # avoid recommending exact repeats later.
    watched_titles: set[str] = set()
    for item in tautulli_history:
        name = item.get("grandparent_title") or item.get("title")
        if not name:
            continue
        watched_titles.add(_to_text(name).strip().lower())

    # Split history by media type
    movies_history = [item for item in tautulli_history if item.get("media_type") == "movie"]
    tv_history = [item for item in tautulli_history if item.get("media_type") in ("show", "episode", "season")]

    # Prepare context slices
    # Up to 20 movies for stronger signal.
    top_movies = movies_history[:20]
    recent_movies = movies_history[:20]

    top_tv = tv_history[:10]
    recent_tv = tv_history[:20]

    # Derive a compact list of unique series titles (max 10) from TV history.
    series_titles: list[str] = []
    seen_series: set[str] = set()
    for item in tv_history:
        # Tautulli typically uses grandparent_title for series name on episodes.
        name = item.get("grandparent_title") or item.get("title")
        if not name:
            continue
        if name in seen_series:
            continue
        seen_series.add(name)
        series_titles.append(name)
        if len(series_titles) >= 10:
            break

    # Heuristic: collect up to 10 documentary items from history based on
    # genres or library/section naming (best-effort signal for the AI).
    documentaries: list[dict[str, Any]] = []
    for item in tautulli_history:
        genres = (item.get("genres") or "").lower()
        section = (item.get("section_name") or item.get("library_name") or "").lower()
        if "documentary" in genres or "documentary" in section:
            documentaries.append(item)
            if len(documentaries) >= 10:
                break

    # Fetch explicit likes and dislikes from UserPreference
    likes_stmt = (
        select(UserPreference)
        .where(UserPreference.user_id == user_id)
        .where(UserPreference.rating == 1)
    )
    likes_rows = db.execute(likes_stmt).scalars().all()
    likes = [{"tmdb_id": row.tmdb_id, "media_type": row.media_type} for row in likes_rows]

    dislikes_stmt = (
        select(UserPreference)
        .where(UserPreference.user_id == user_id)
        .where(UserPreference.rating == -1)
    )
    dislikes_rows = db.execute(dislikes_stmt).scalars().all()
    dislikes = [{"tmdb_id": row.tmdb_id, "media_type": row.media_type} for row in dislikes_rows]

    # Any item that has been rated (up/down/seen) in Sagarr should no longer be
    # re-suggested. We treat all UserPreference rows as "already seen here".
    rated_stmt = select(UserPreference.tmdb_id).where(UserPreference.user_id == user_id)
    rated_ids = {tmdb_id for tmdb_id in db.execute(rated_stmt).scalars().all() if tmdb_id is not None}

    user_context: dict[str, Any] = {
        "movies": {
            "top": top_movies,
            "recent": recent_movies,
        },
        "tv": {
            "top": top_tv,
            "recent": recent_tv,
            "series_titles": series_titles,
        },
        "documentaries": {
            "sample": documentaries,
        },
        "likes": likes,
        "dislikes": dislikes,
        "watched_titles": sorted(watched_titles),
        "rated_tmdb_ids": sorted(rated_ids),
    }

    system_prompt = (
        "You are an AI that creates creative, descriptive recommendation categories "
        "for a single user based on their Plex/Tautulli watch history and explicit likes/dislikes. "
        "Never recommend explicit pornography or adult-only content. "
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
