"""Tests for BasecampStatusStrategy placeholder."""

from __future__ import annotations

from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase

from integrations.status.strategies.basecamp import BasecampStatusStrategy


class TestBasecampStatusStrategy(TestCase):
    """Validate Basecamp placeholder strategy behavior."""

    def setUp(self) -> None:
        """Create a user and initialize the strategy under test."""
        self.user = get_user_model().objects.create_user("u@example.com")
        self.strategy = BasecampStatusStrategy()

    def test_placeholder_returns_not_connected(self):
        """Placeholder should indicate not connected with connect CTA."""
        status = self.strategy.assess(self.user, now=datetime.now(timezone.utc))
        assert status.provider == "basecamp"
        assert status.connected is False
        assert status.blocking_problem is True
        assert status.cta_label == "Connect"
        assert status.reason == "Not connected"
