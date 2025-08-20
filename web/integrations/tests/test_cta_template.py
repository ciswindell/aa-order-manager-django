"""Tests for the integration CTA template tag and partial rendering."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.template import Template, Context
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.apps import apps

from web.integrations.utils.crypto import encrypt_text


class TestIntegrationCtaTemplate(TestCase):
    """Ensure CTA renders only when blocking_problem is true."""

    def setUp(self) -> None:
        """Create a user used by tag renders."""
        self.user = get_user_model().objects.create_user(
            username="u", email="u@example.com", password="x"
        )

    @override_settings(DROPBOX_APP_KEY="k", DROPBOX_APP_SECRET="s")
    def test_dropbox_cta_renders_when_not_connected(self):
        """No tokens → blocking status, tag should render CTA markup."""
        tpl = Template(
            """{% load integration_cta %}{% integration_cta 'dropbox' user %}"""
        )
        html = tpl.render(Context({"user": self.user}))
        assert "Action required" in html
        assert "Connect" in html
        assert "Dropbox" in html

    @override_settings(DROPBOX_APP_KEY="k", DROPBOX_APP_SECRET="s")
    def test_dropbox_cta_not_rendered_when_ready(self):
        """Valid tokens + refresh + future expiry → no CTA rendered."""
        # Use a fresh user to avoid cached status from prior test
        ready_user = get_user_model().objects.create_user(
            username="u2", email="u2@example.com", password="x"
        )
        future = datetime.now(timezone.utc) + timedelta(minutes=30)
        DropboxAccount = apps.get_model("integrations", "DropboxAccount")
        DropboxAccount.objects.create(
            user=ready_user,
            account_id="acc",
            access_token="at",
            refresh_token_encrypted=encrypt_text("rt"),
            expires_at=future,
        )
        tpl = Template(
            """{% load integration_cta %}{% integration_cta 'dropbox' user %}"""
        )
        html = tpl.render(Context({"user": ready_user}))
        assert "Action required" not in html

    def test_basecamp_cta_renders_placeholder(self):
        """Basecamp placeholder strategy returns blocking CTA to connect."""
        tpl = Template(
            """{% load integration_cta %}{% integration_cta 'basecamp' user %}"""
        )
        html = tpl.render(Context({"user": self.user}))
        assert "Action required" in html
        assert "Connect" in html
        assert "Basecamp" in html
