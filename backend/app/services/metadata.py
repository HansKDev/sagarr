from typing import Any

import httpx

from ..config import get_settings


class MetadataNotConfiguredError(RuntimeError):
    pass


async def fetch_tmdb_details(tmdb_ids: list[int], media_type: str = "movie") -> list[dict[str, Any]]:
    """
    Fetch basic metadata (title, poster, overview) for a list of TMDb IDs.
    
    Args:
        tmdb_ids: List of integer TMDb IDs.
        media_type: 'movie' or 'tv'.
    """
    settings = get_settings()
    if not settings.tmdb_api_key:
        raise MetadataNotConfiguredError("TMDb API key not configured.")

    api_key = settings.tmdb_api_key
    base_url = "https://api.themoviedb.org/3"

    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as client:
        for tmdb_id in tmdb_ids:
            endpoint = f"/{media_type}/{tmdb_id}"
            try:
                resp = await client.get(endpoint, params={"api_key": api_key, "language": "en-US"})
                if resp.status_code == 200:
                    data = resp.json()
                    # Skip explicit adult content.
                    if data.get("adult") is True:
                        continue
                    # Normalize title/name
                    if "name" in data and "title" not in data:
                        data["title"] = data["name"]
                    results.append(data)
            except Exception as e:
                print(f"Error fetching metadata for {media_type} {tmdb_id}: {e}")

    return results
