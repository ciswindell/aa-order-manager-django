"""Service to assess per-user integration status with TTL caching."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

from integrations.status.cache import CacheAdapter, default_cache
from integrations.status.dto import IntegrationStatus
from integrations.status.strategies.base import IntegrationStatusStrategy
from integrations.status.strategies.basecamp import BasecampStatusStrategy
from integrations.status.strategies.dropbox import DropboxStatusStrategy

DEFAULT_TTL_SECONDS = 600


class IntegrationStatusService:
    """Compose provider strategies and cache their results by user."""

    def __init__(
        self,
        cache: Optional[CacheAdapter] = None,
        strategies: Optional[Dict[str, IntegrationStatusStrategy]] = None,
        default_ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        """Initialize the service with a cache and provider strategies."""
        self._cache = cache or default_cache
        self._default_ttl = int(default_ttl_seconds)
        self._strategies: Dict[str, IntegrationStatusStrategy] = strategies or {
            "dropbox": DropboxStatusStrategy(),
            "basecamp": BasecampStatusStrategy(),
        }

    def assess(
        self,
        user,
        provider: str,
        *,
        force_refresh: bool = False,
        ttl_seconds: Optional[int] = None,
    ) -> IntegrationStatus:
        """Return IntegrationStatus for the given user/provider using TTL cache."""
        user_id = getattr(user, "pk", None) or "anon"
        key = f"integration_status:{provider}:{user_id}"
        if not force_refresh:
            cached = self._cache.get(key)
            if cached is not None:
                return cached

        strategy = self._strategies.get(provider)
        if not strategy:
            raise ValueError(f"Unknown provider: {provider}")

        now = datetime.now(timezone.utc)
        ttl = int(ttl_seconds) if ttl_seconds is not None else self._default_ttl
        status = strategy.assess(user, now=now, ttl_seconds=ttl)
        self._cache.set(key, status, ttl_seconds=ttl)
        return status


__all__ = ["IntegrationStatusService", "DEFAULT_TTL_SECONDS"]
