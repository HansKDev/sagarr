import httpx
from fastapi import HTTPException

from ..config import settings


class TautulliService:
    def __init__(self) -> None:
        # Intentionally do not cache URL/API key here; they can be updated
        # at runtime via the admin settings, so we always read from settings.
        pass

    def _build_url(self, params: dict) -> str:
        base_url = settings.TAUTULLI_URL.strip().rstrip("/")
        # Allow shorthand like "tautulli:8181" by assuming http://
        if base_url and not base_url.startswith(("http://", "https://")):
            base_url = f"http://{base_url}"
        api_key = settings.TAUTULLI_API_KEY
        query = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}/api/v2?apikey={api_key}&{query}"

    async def get_users(self):
        """Fetch all users from Tautulli."""
        if not settings.TAUTULLI_URL or not settings.TAUTULLI_API_KEY:
            return []

        async with httpx.AsyncClient() as client:
            try:
                url = self._build_url({"cmd": "get_users"})
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                response_obj = data.get("response", {})
                data_obj = response_obj.get("data", [])

                # Tautulli may return the users list either directly as `data: []`
                # or nested under `data: { users: [] }`. Handle both.
                if isinstance(data_obj, list):
                    return data_obj
                if isinstance(data_obj, dict):
                    users = data_obj.get("users")
                    if isinstance(users, list):
                        return users

                return []
            except Exception as e:
                print(f"Error fetching Tautulli users: {e}")
                return []

    async def get_user_history(self, user_id: int, length: int = 50):
        """Fetch watch history for a specific user."""
        if not settings.TAUTULLI_URL or not settings.TAUTULLI_API_KEY:
            return []

        async with httpx.AsyncClient() as client:
            try:
                url = self._build_url(
                    {
                        "cmd": "get_history",
                        "user_id": user_id,
                        "length": length,
                        "media_type": "movie,episode",
                    }
                )
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", {}).get("data", {}).get("data", [])
            except Exception as e:
                print(f"Error fetching Tautulli history: {e}")
                return []


tautulli_service = TautulliService()


# Convenience functions used by newer services
async def get_users():
    return await tautulli_service.get_users()


async def get_user_history(user_id: int, limit: int = 100):
    return await tautulli_service.get_user_history(user_id, length=limit)
