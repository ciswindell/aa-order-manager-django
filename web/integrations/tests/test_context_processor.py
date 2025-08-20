"""Tests for the integration_statuses context processor."""

from __future__ import annotations

from django.test import TestCase
from django.contrib.auth import get_user_model


class TestIntegrationStatusesContext(TestCase):
    """Verify integration_statuses context processor behavior for users."""

    def setUp(self) -> None:
        """Create a user for authenticated test scenarios."""
        self.user = get_user_model().objects.create_user(
            username="u", email="u@example.com", password="x"
        )

    def test_anonymous_user_gets_empty_mapping(self):
        """Anonymous requests include an empty integration_statuses mapping."""
        resp = self.client.get("/")
        # Anonymous request redirects to login; follow the redirect
        resp = self.client.get("/", follow=True)
        # Anonymous requests still include the processor; mapping should be empty
        context = getattr(resp, "context", None)
        assert context is not None
        assert context.get("integration_statuses") == {}

    def test_authenticated_user_gets_providers(self):
        """Authenticated requests include dropbox key (basecamp disabled now)."""
        self.client.login(username="u", password="x")
        resp = self.client.get("/")
        statuses = resp.context["integration_statuses"]
        assert set(statuses.keys()) == {"dropbox"}
