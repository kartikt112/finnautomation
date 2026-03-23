import httpx
from app.config import settings


class MultiloginService:
    def __init__(self):
        self.base_url = settings.MULTILOGIN_API_URL

    async def start_profile(self, profile_id: str) -> dict:
        """Start a Multilogin browser profile and return connection details."""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(f"{self.base_url}/profile/start?profileId={profile_id}")
            resp.raise_for_status()
            data = resp.json()
            return data

    async def stop_profile(self, profile_id: str) -> bool:
        """Stop a running Multilogin profile."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/profile/stop?profileId={profile_id}")
            return resp.status_code == 200

    async def list_profiles(self, group_name: str | None = None) -> list[dict]:
        """List available browser profiles."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/profile")
            resp.raise_for_status()
            profiles = resp.json()
            if group_name:
                profiles = [p for p in profiles if p.get("group") == group_name]
            return profiles

    def get_ws_endpoint(self, start_response: dict) -> str:
        """Extract WebSocket endpoint from profile start response for Playwright."""
        # Multilogin returns something like: {"status":"OK","value":"ws://127.0.0.1:XXXXX/devtools/browser/..."}
        return start_response.get("value", "")


# Synchronous versions for use in Celery workers
class MultiloginServiceSync:
    def __init__(self):
        self.base_url = settings.MULTILOGIN_API_URL

    def start_profile(self, profile_id: str) -> dict:
        with httpx.Client(timeout=60) as client:
            resp = client.get(f"{self.base_url}/profile/start?profileId={profile_id}")
            resp.raise_for_status()
            return resp.json()

    def stop_profile(self, profile_id: str) -> bool:
        with httpx.Client(timeout=30) as client:
            resp = client.get(f"{self.base_url}/profile/stop?profileId={profile_id}")
            return resp.status_code == 200

    def get_ws_endpoint(self, start_response: dict) -> str:
        return start_response.get("value", "")
