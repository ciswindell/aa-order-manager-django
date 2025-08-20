"""Template tag to render an integration CTA for a provider."""

from __future__ import annotations

from django import template

from integrations.status.service import IntegrationStatusService  # type: ignore[import]

register = template.Library()


@register.inclusion_tag("integrations/_cta.html")
def integration_cta(provider: str, user=None, compact: bool = False):
    """Render CTA for a provider; accepts optional user and compact flag."""
    service = IntegrationStatusService()
    status = None
    if user and getattr(user, "is_authenticated", False):
        status = service.assess(user, provider, force_refresh=True)
    return {"status": status, "compact": compact}
