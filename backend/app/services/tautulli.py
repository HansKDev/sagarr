import httpx
from fastapi import HTTPException

from ..config import settings


class TautulliService:
  def __init__(self) -> None:
      self.base_url = settings.TAUTULLI_URL.rstrip("/")
      self.api_key = settings.TAUTULLI_API_KEY

  def _build_url(self, params: dict) -> str:
      query = "&".join([f"{k}={v}" for k, v in params.items()])
      return f"{self.base_url}/api/v2?apikey={self.api_key}&{query}"

  async def get_users(self):
      """Fetch all users from Tautulli."""
      if not self.base_url or not self.api_key:
          return []

      async with httpx.AsyncClient() as client:
          try:
              url = self._build_url({"cmd": "get_users"})
              resp = await client.get(url)
              resp.raise_for_status()
              data = resp.json()
              return data.get("response", {}).get("data", [])
          except Exception as e:
              print(f"Error fetching Tautulli users: {e}")
              return []

  async def get_user_history(self, user_id: int, length: int = 50):
      """Fetch watch history for a specific user."""
      if not self.base_url or not self.api_key:
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
