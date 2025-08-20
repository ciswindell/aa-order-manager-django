"""Template context for integration status DTOs."""

from __future__ import annotations

from typing import Dict

from integrations.status.dto import IntegrationStatus  # type: ignore[import]
from integrations.status.service import IntegrationStatusService  # type: ignore[import]


def integration_statuses(request) -> Dict[str, Dict[str, IntegrationStatus]]:
    """Inject per-provider integration status for the current user.

    Returns an empty mapping for anonymous users.
    """
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return {"integration_statuses": {}}

    service = IntegrationStatusService()
    statuses: Dict[str, IntegrationStatus] = {
        "dropbox": service.assess(user, "dropbox", force_refresh=True),
        # "basecamp": service.assess(user, "basecamp", force_refresh=True),
    }
    return {"integration_statuses": statuses}


__all__ = ["integration_statuses"]
