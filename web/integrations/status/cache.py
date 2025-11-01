"""In-process TTL cache for integration status.

Minimal adapter: get/set with monotonic-based expiry.
"""

from __future__ import annotations

from time import monotonic
from typing import Any, Dict, Optional, Protocol, Tuple


class InMemoryTTLCache:
    """Simple in-memory TTL cache using monotonic timestamps."""

    def __init__(self) -> None:
        """Initialize the cache store."""
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if present and not expired; otherwise None."""
        now = monotonic()
        item = self._store.get(key)
        if not item:
            return None
        value, expires_at = item
        if expires_at <= now:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value with TTL in seconds."""
        expires_at = monotonic() + max(0, int(ttl_seconds))
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        """Remove a key from the cache."""
        self._store.pop(key, None)


# Default cache instance for callers that don't need custom wiring
default_cache = InMemoryTTLCache()


class CacheAdapter(Protocol):
    """Minimal cache adapter interface for drop-in backends (e.g., Redis)."""

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None when missing/expired."""

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value with TTL in seconds."""


__all__ = ["InMemoryTTLCache", "default_cache", "CacheAdapter"]
