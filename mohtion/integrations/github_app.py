"""GitHub App authentication and installation management."""

import time
from dataclasses import dataclass

import httpx
import jwt

from mohtion.config import get_settings


@dataclass
class InstallationToken:
    """GitHub App installation access token."""

    token: str
    expires_at: int  # Unix timestamp

    def is_expired(self) -> bool:
        """Check if token is expired (with 5 min buffer)."""
        return time.time() > (self.expires_at - 300)


class GitHubApp:
    """GitHub App authentication handler."""

    API_BASE = "https://api.github.com"

    def __init__(self) -> None:
        settings = get_settings()
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key
        self._installation_tokens: dict[int, InstallationToken] = {}

    def _generate_jwt(self) -> str:
        """Generate a JWT for GitHub App authentication."""
        now = int(time.time())
        payload = {
            "iat": now,  # Issued now
            "exp": now + 540,  # Expires in 9 minutes (conservative)
            "iss": self.app_id,
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    async def get_installation_token(self, installation_id: int) -> str:
        """Get an installation access token (cached)."""
        cached = self._installation_tokens.get(installation_id)
        if cached and not cached.is_expired():
            return cached.token

        # Request new token
        jwt_token = self._generate_jwt()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            response.raise_for_status()
            data = response.json()

        # Parse expiration (ISO format to timestamp)
        from datetime import datetime

        expires_at = datetime.fromisoformat(
            data["expires_at"].replace("Z", "+00:00")
        ).timestamp()

        token = InstallationToken(token=data["token"], expires_at=int(expires_at))
        self._installation_tokens[installation_id] = token
        return token.token

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        import hashlib
        import hmac

        settings = get_settings()
        expected = hmac.new(
            settings.github_webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)

    async def get_installation(self, installation_id: int) -> dict:
        """Get details about a specific installation."""
        jwt_token = self._generate_jwt()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/app/installations/{installation_id}",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_installations(self) -> list[dict]:
        """Get all installations of this GitHub App."""
        jwt_token = self._generate_jwt()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/app/installations",
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            response.raise_for_status()
            return response.json()
