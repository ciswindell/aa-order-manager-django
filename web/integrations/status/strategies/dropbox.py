"""Dropbox status strategy.

Prefers cheap checks. Optionally performs a live probe when tokens are stale
and INTEGRATIONS_STATUS_LIVE_PROBE is enabled.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import dropbox  # third-party
from django.conf import settings
from django.urls import reverse

from integrations.status.dto import IntegrationStatus
from integrations.status.policy import RawStatusSignals, map_raw_to_status
from integrations.status.strategies.base import IntegrationStatusStrategy
from integrations.utils.token_store import get_tokens_for_user


class DropboxStatusStrategy(IntegrationStatusStrategy):
    """Assess Dropbox readiness for a user using cheap checks first."""

    provider = "dropbox"
    TOKEN_EXPIRY_BUFFER_SECONDS = 60

    def assess_raw(self, user) -> RawStatusSignals:
        """Collect raw signals from stored tokens and environment settings."""
        tokens = get_tokens_for_user(user)
        env_ok = bool(getattr(settings, "DROPBOX_APP_KEY", None)) and bool(
            getattr(settings, "DROPBOX_APP_SECRET", None)
        )
        connected = bool(tokens and tokens.get("access_token"))
        authenticated = False
        has_refresh = False
        if connected:
            has_refresh = bool(tokens.get("refresh_token"))
            # Consider authenticated if token exists and not expired (if known)
            expires_at: Optional[datetime] = tokens.get("expires_at")  # type: ignore[arg-type]
            now = datetime.now(timezone.utc)
            authenticated = True
            if expires_at is not None:
                # Compare using aware UTC with a small buffer; treat naive as UTC
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                buffer = timedelta(seconds=self.TOKEN_EXPIRY_BUFFER_SECONDS)
                authenticated = expires_at > (now + buffer)

            # Optional live probe when stale, env is OK, and refresh is available
            if (
                not authenticated
                and has_refresh
                and env_ok
                and bool(getattr(settings, "INTEGRATIONS_STATUS_LIVE_PROBE", False))
            ):
                try:
                    kwargs: dict = {"oauth2_access_token": tokens["access_token"]}
                    kwargs.update(
                        {
                            "oauth2_refresh_token": tokens["refresh_token"],
                            "app_key": settings.DROPBOX_APP_KEY,
                            "app_secret": settings.DROPBOX_APP_SECRET,
                        }
                    )
                    client = dropbox.Dropbox(**kwargs)
                    client.users_get_current_account()
                    authenticated = True
                except Exception:
                    authenticated = False

        cta_url = reverse("integrations:dropbox_connect")
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


__all__ = ["DropboxStatusStrategy"]
