"""Provider strategy protocol for integration status assessment."""

from __future__ import annotations

from typing import Protocol, runtime_checkable, Any

# Avoid import-time coupling to app modules in protocol definitions
RawStatusSignals = Any


@runtime_checkable
class IntegrationStatusStrategy(Protocol):
    """Strategy interface producing raw provider signals for status mapping."""

    provider: str

    def assess_raw(self, user) -> RawStatusSignals:  # pragma: no cover - protocol
        """Return raw status signals for the given user."""
        raise NotImplementedError


__all__ = ["IntegrationStatusStrategy"]
