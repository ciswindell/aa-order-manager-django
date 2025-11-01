"""Basecamp status strategy.

Assesses Basecamp OAuth connection status for users.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from django.conf import settings

from integrations.status.dto import IntegrationStatus
from integrations.status.policy import RawStatusSignals, map_raw_to_status
from integrations.status.strategies.base import IntegrationStatusStrategy
from integrations.utils.token_store import get_tokens_for_user


class BasecampStatusStrategy(IntegrationStatusStrategy):
    """Assess Basecamp readiness for a user using cheap checks."""

    provider = "basecamp"

    TOKEN_EXPIRY_BUFFER_SECONDS = 60

    def assess_raw(self, user) -> RawStatusSignals:
        """Collect raw signals from stored tokens and environment settings."""
        from datetime import timedelta

        tokens = get_tokens_for_user(user, provider="basecamp")
        env_ok = bool(getattr(settings, "BASECAMP_APP_KEY", None)) and bool(
            getattr(settings, "BASECAMP_APP_SECRET", None)
        )
        connected = bool(tokens and tokens.get("access_token"))
        authenticated = False
        has_refresh = False

        if connected:
            has_refresh = bool(tokens.get("refresh_token"))
            # Check token expiration if expires_at is present (FR-009)
            expires_at: Optional[datetime] = tokens.get("expires_at")
            now = datetime.now(timezone.utc)
            authenticated = True

            if expires_at is not None:
                # Treat naive datetime as UTC
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                buffer = timedelta(seconds=self.TOKEN_EXPIRY_BUFFER_SECONDS)
                authenticated = expires_at > (now + buffer)

        cta_url = "/api/integrations/basecamp/connect/"
        return RawStatusSignals(
            connected=connected,
            authenticated=authenticated,
            has_refresh=has_refresh,
            env_ok=env_ok,
            cta_url=cta_url,
        )

    def assess(
        self, user, *, now: Optional[datetime] = None, ttl_seconds: int = 600
    ) -> IntegrationStatus:
        """Map raw signals into the final IntegrationStatus DTO."""
        now = now or datetime.now(timezone.utc)
        raw = self.assess_raw(user)
        return map_raw_to_status(
            provider=self.provider, raw=raw, now=now, ttl_seconds=ttl_seconds
        )


__all__ = ["BasecampStatusStrategy"]
