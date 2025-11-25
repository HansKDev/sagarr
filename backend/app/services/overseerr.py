import httpx

from ..config import settings


class OverseerrService:
    def __init__(self) -> None:
        self.base_url = settings.OVERSEERR_URL.rstrip("/")
        self.api_key = settings.OVERSEERR_API_KEY
        self.headers = {
            "X-Api-Key": self.api_key,
            "Accept": "application/json",
        }

    async def check_availability(self, tmdb_id: int, media_type: str):
        """
        Check if media is available or requested.
        Returns: { "status": "AVAILABLE" | "PARTIALLY_AVAILABLE" | "PROCESSING" | "PENDING" | "UNKNOWN", "plexUrl": ... }
        """
        if not self.base_url or not self.api_key:
            return {"status": "UNKNOWN"}

        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/api/v1/{media_type}/{tmdb_id}"
                resp = await client.get(url, headers=self.headers)
                resp.raise_for_status()
                data = resp.json()

                media_info = data.get("mediaInfo")
                if not media_info:
                    return {"status": "MISSING"}

                status = media_info.get("status")

                # Check if there are pending requests
                requests = media_info.get("requests", [])
                is_requested = any(r.get("status") == 1 for r in requests)  # 1 = PENDING_APPROVAL

                if status == 5:  # AVAILABLE
                    return {"status": "AVAILABLE"}
                elif status == 4:  # PARTIALLY_AVAILABLE
                    return {"status": "PARTIALLY_AVAILABLE"}
                elif status == 3:  # PROCESSING
                    return {"status": "PROCESSING"}
                elif is_requested or status == 2:  # PENDING
                    return {"status": "PENDING"}
                else:
                    return {"status": "MISSING"}

            except Exception as e:
                print(f"Error checking Overseerr availability: {e}")
                return {"status": "UNKNOWN"}

    async def request_media(self, tmdb_id: int, media_type: str, user_id: int | None = None):
        """
        Request media via Overseerr.
        """
        if not self.base_url or not self.api_key:
            return False

        payload = {
            "mediaId": tmdb_id,
            "mediaType": media_type,
            "is4k": False,
        }

        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/api/v1/request"
                resp = await client.post(url, headers=self.headers, json=payload)
                resp.raise_for_status()
                return True
            except Exception as e:
                print(f"Error requesting media in Overseerr: {e}")
                return False


overseerr_service = OverseerrService()


class OverseerrNotConfiguredError(RuntimeError):
    pass


async def check_availability(tmdb_id: int) -> dict:
    """
    Convenience wrapper used by media router.
    """
    if not settings.OVERSEERR_URL or not settings.OVERSEERR_API_KEY:
        raise OverseerrNotConfiguredError("Overseerr is not configured.")
    # We default to "movie" here; callers can be extended later to differentiate.
    return await overseerr_service.check_availability(tmdb_id, media_type="movie")


async def request_media(tmdb_id: int, media_type: str) -> dict:
    if not settings.OVERSEERR_URL or not settings.OVERSEERR_API_KEY:
        raise OverseerrNotConfiguredError("Overseerr is not configured.")
    ok = await overseerr_service.request_media(tmdb_id, media_type)
    return {"success": ok}
