"""Integration status DTOs for the integrations framework."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class IntegrationStatus:
    """Immutable DTO representing per-provider readiness and CTA metadata."""

    provider: str
    connected: bool
    authenticated: bool
    has_refresh: bool
    blocking_problem: bool
    reason: str
    cta_label: Optional[str]
    cta_url: Optional[str]
    last_checked: datetime
    ttl_seconds: int


__all__ = ["IntegrationStatus"]
