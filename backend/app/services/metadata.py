from typing import Any

import httpx

from ..config import get_settings


class MetadataNotConfiguredError(RuntimeError):
    pass


async def fetch_tmdb_details(tmdb_ids: list[int]) -> list[dict[str, Any]]:
    """
    Fetch basic metadata (title, poster, overview) for a list of TMDb IDs.

    Uses TMDb API directly. This can later be swapped to go via Overseerr if preferred.
    """
    settings = get_settings()
    if not settings.tmdb_api_key:
        raise MetadataNotConfiguredError("TMDb API key not configured.")

    api_key = settings.tmdb_api_key
    base_url = "https://api.themoviedb.org/3"

    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        for tmdb_id in tmdb_ids:
            resp = await client.get(f"/movie/{tmdb_id}", params={"api_key": api_key, "language": "en-US"})
            if resp.status_code == 200:
                results.append(resp.json())

    return results

