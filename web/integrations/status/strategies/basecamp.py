"""Basecamp placeholder strategy.

Returns a non-connected status with CTA to connect until OAuth is wired.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from django.urls import reverse

from web.integrations.status.policy import RawStatusSignals, map_raw_to_status
from web.integrations.status.dto import IntegrationStatus
from web.integrations.status.strategies.base import IntegrationStatusStrategy


class BasecampStatusStrategy(IntegrationStatusStrategy):
    """Placeholder: always not connected; CTA to connect Basecamp."""

    provider = "basecamp"

    def assess_raw(self, _user) -> RawStatusSignals:
        """Return fixed raw signals for the placeholder Basecamp strategy."""
        return RawStatusSignals(
            connected=False,
            authenticated=False,
            has_refresh=False,
            env_ok=True,
            cta_url=reverse("integrations:integrations_index"),
        )

    def assess(
        self, user, *, now: Optional[datetime] = None, ttl_seconds: int = 600
    ) -> IntegrationStatus:
        """Map the placeholder raw signals into an IntegrationStatus DTO."""
        now = now or datetime.now(timezone.utc)
        raw = self.assess_raw(user)
        return map_raw_to_status(
            provider=self.provider, raw=raw, now=now, ttl_seconds=ttl_seconds
        )


__all__ = ["BasecampStatusStrategy"]
