"""Tests for IntegrationStatusService cache behavior."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional

from django.contrib.auth import get_user_model
from django.test import TestCase

from integrations.status.cache import InMemoryTTLCache
from integrations.status.policy import RawStatusSignals, map_raw_to_status
from integrations.status.service import IntegrationStatusService


class _FakeStrategy:
    provider = "fake"

    def __init__(self, RawStatusSignals, map_raw_to_status):  # noqa: N803
        """Track calls and capture policy functions/types for use in assess."""
        self.calls = 0
        self._RawStatusSignals = RawStatusSignals
        self._map_raw_to_status = map_raw_to_status

    def assess_raw(self, _user):  # pragma: no cover - not used
        return self._RawStatusSignals(True, True, True, True)

    def assess(self, _user, *, now: Optional[datetime] = None, ttl_seconds: int = 600):
        """Return a constant healthy status and increment call counter."""
        self.calls += 1
        now = now or datetime.now(timezone.utc)
        return self._map_raw_to_status(
            provider=self.provider,
            raw=self._RawStatusSignals(True, True, True, True),
            now=now,
            ttl_seconds=ttl_seconds,
        )


class TestIntegrationStatusServiceCache(TestCase):
    """Cache hit/miss, force refresh, and TTL expiry behavior for the service."""

    def setUp(self) -> None:
        """Create a user, cache instance, fake strategy, and the service."""
        user_model = get_user_model()
        self.user = user_model.objects.create_user("u@example.com")
        self.cache = InMemoryTTLCache()
        self.strategy = _FakeStrategy(RawStatusSignals, map_raw_to_status)
        self.svc = IntegrationStatusService(
            cache=self.cache, strategies={"fake": self.strategy}
        )

    def test_cache_hit_returns_cached(self):
        """Second call returns cached status and does not re-invoke strategy."""
        _ = self.svc.assess(self.user, "fake")
        _ = self.svc.assess(self.user, "fake")
        assert self.strategy.calls == 1

    def test_force_refresh_bypasses_cache(self):
        """Force refresh bypasses cache and re-invokes the strategy."""
        _ = self.svc.assess(self.user, "fake")
        _ = self.svc.assess(self.user, "fake", force_refresh=True)
        assert self.strategy.calls == 2

    def test_ttl_expiry_evicts(self):
        """Entries expire after TTL and strategy is called again."""
        _ = self.svc.assess(self.user, "fake", ttl_seconds=1)
        # Advance the cache clock by simulating wait; direct store manipulation
        # Not available; instead sleep a tiny bit longer than TTL
        time.sleep(1.1)
        _ = self.svc.assess(self.user, "fake")
        assert self.strategy.calls >= 2
