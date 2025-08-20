"""Tests for DropboxStatusStrategy."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from django.apps import apps
from web.integrations.status.strategies.dropbox import DropboxStatusStrategy
from web.integrations.utils.crypto import encrypt_text


class TestDropboxStatusStrategy(TestCase):
    """Validate Dropbox strategy mapping across common states."""

    def setUp(self) -> None:
        """Create a user and initialize the Dropbox strategy instance."""
        self.user = get_user_model().objects.create_user("u@example.com")
        self.strategy = DropboxStatusStrategy()

    @override_settings(
        DROPBOX_APP_KEY="k",
        DROPBOX_APP_SECRET="s",
        INTEGRATIONS_STATUS_LIVE_PROBE=False,
    )
    def test_not_connected(self):
        """When no account exists, status is blocking with connect CTA."""
        status = self.strategy.assess(self.user, now=datetime.now(timezone.utc))
        assert status.provider == "dropbox"
        assert status.connected is False
        assert status.blocking_problem is True
        assert status.cta_label == "Connect"
        assert status.reason == "Not connected"

    @override_settings(
        DROPBOX_APP_KEY="k",
        DROPBOX_APP_SECRET="s",
        INTEGRATIONS_STATUS_LIVE_PROBE=False,
    )
    def test_connected_authenticated_with_refresh_and_env_ok(self):
        """Valid token, refresh present, and env ok → non-blocking."""
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        DropboxAccount = apps.get_model("integrations", "DropboxAccount")
        DropboxAccount.objects.create(
            user=self.user,
            account_id="acc",
            access_token="at",
            refresh_token_encrypted=encrypt_text("rt"),
            expires_at=future,
        )
        status = self.strategy.assess(self.user, now=datetime.now(timezone.utc))
        assert status.connected is True
        assert status.authenticated is True
        assert status.has_refresh is True
        assert status.blocking_problem is False

    @override_settings(
        DROPBOX_APP_KEY="k",
        DROPBOX_APP_SECRET="s",
        INTEGRATIONS_STATUS_LIVE_PROBE=False,
    )
    def test_connected_missing_refresh(self):
        """Missing refresh token → blocking with reconnect CTA."""
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        DropboxAccount = apps.get_model("integrations", "DropboxAccount")
        DropboxAccount.objects.create(
            user=self.user,
            account_id="acc",
            access_token="at",
            refresh_token_encrypted="",  # no refresh
            expires_at=future,
        )
        status = self.strategy.assess(self.user, now=datetime.now(timezone.utc))
        assert status.connected is True
        assert status.has_refresh is False
        assert status.blocking_problem is True
        assert status.cta_label == "Reconnect"
        assert status.reason == "Missing refresh token"

    @override_settings(
        DROPBOX_APP_KEY="", DROPBOX_APP_SECRET="", INTEGRATIONS_STATUS_LIVE_PROBE=False
    )
    def test_env_missing_is_blocking_even_if_connected(self):
        """Missing app credentials yields blocking with targeted reason."""
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        DropboxAccount = apps.get_model("integrations", "DropboxAccount")
        DropboxAccount.objects.create(
            user=self.user,
            account_id="acc",
            access_token="at",
            refresh_token_encrypted=encrypt_text("rt"),
            expires_at=future,
        )
        status = self.strategy.assess(self.user, now=datetime.now(timezone.utc))
        assert status.connected is True
        assert status.blocking_problem is True
        assert status.reason == "Missing app credentials"
        # Connected but env missing → Reconnect CTA
        assert status.cta_label == "Reconnect"
