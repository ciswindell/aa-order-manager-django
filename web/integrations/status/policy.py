"""Shared policy to map raw provider signals to an IntegrationStatus DTO.

Rules:
- Not connected → blocking, CTA Connect
- Connected but not authenticated → blocking, CTA Reconnect
- Connected+authenticated but no refresh → blocking, CTA Reconnect
- Missing app credentials (env) → blocking; label chosen based on connection state
- Otherwise → non‑blocking, no CTA
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .dto import IntegrationStatus


@dataclass(frozen=True)
class RawStatusSignals:
    """Inputs from a provider strategy used by the shared policy mapper."""

    connected: bool
    authenticated: bool
    has_refresh: bool
    env_ok: bool
    cta_url: Optional[str] = None


CTA_CONNECT = "Connect"
CTA_RECONNECT = "Reconnect"


def map_raw_to_status(
    *, provider: str, raw: RawStatusSignals, now: datetime, ttl_seconds: int
) -> IntegrationStatus:
    """Map raw provider signals into an IntegrationStatus applying shared rules."""

    if not raw.env_ok:
        blocking = True
        label = CTA_CONNECT if not raw.connected else CTA_RECONNECT
        reason = "Missing app credentials"
        return IntegrationStatus(
            provider=provider,
            connected=raw.connected,
            authenticated=raw.authenticated,
            has_refresh=raw.has_refresh,
            blocking_problem=blocking,
            reason=reason,
            cta_label=label,
            cta_url=raw.cta_url,
            last_checked=now,
            ttl_seconds=ttl_seconds,
        )

    if not raw.connected:
        return IntegrationStatus(
            provider=provider,
            connected=False,
            authenticated=False,
            has_refresh=False,
            blocking_problem=True,
            reason="Not connected",
            cta_label=CTA_CONNECT,
            cta_url=raw.cta_url,
            last_checked=now,
            ttl_seconds=ttl_seconds,
        )

    if not raw.authenticated:
        return IntegrationStatus(
            provider=provider,
            connected=True,
            authenticated=False,
            has_refresh=raw.has_refresh,
            blocking_problem=True,
            reason="Not authenticated",
            cta_label=CTA_RECONNECT,
            cta_url=raw.cta_url,
            last_checked=now,
            ttl_seconds=ttl_seconds,
        )

    if not raw.has_refresh:
        return IntegrationStatus(
            provider=provider,
            connected=True,
            authenticated=True,
            has_refresh=False,
            blocking_problem=True,
            reason="Missing refresh token",
            cta_label=CTA_RECONNECT,
            cta_url=raw.cta_url,
            last_checked=now,
            ttl_seconds=ttl_seconds,
        )

    return IntegrationStatus(
        provider=provider,
        connected=True,
        authenticated=True,
        has_refresh=True,
        blocking_problem=False,
        reason="",
        cta_label=None,
        cta_url=None,
        last_checked=now,
        ttl_seconds=ttl_seconds,
    )


__all__ = [
    "RawStatusSignals",
    "map_raw_to_status",
    "CTA_CONNECT",
    "CTA_RECONNECT",
]
