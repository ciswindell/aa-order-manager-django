from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model


class OAuthRedirectTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.password = "testpass123"
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password=self.password
        )
        self.client.login(username="user", password=self.password)

    @patch("integrations.views.dropbox.oauth.DropboxOAuth2Flow")
    def test_dropbox_connect_stores_next(self, flow_cls):
        flow = MagicMock()
        flow.start.return_value = "https://dropbox.example/authorize"
        flow_cls.return_value = flow

        resp = self.client.get("/integrations/dropbox/connect/?next=/")
        self.assertEqual(resp.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get("post_oauth_next"), "/")

    @patch("integrations.views.dropbox.oauth.DropboxOAuth2Flow")
    def test_dropbox_callback_redirects_to_safe_next(self, flow_cls):
        flow = MagicMock()
        flow.finish.return_value = SimpleNamespace(
            access_token="a",
            refresh_token="",
            expires_at=None,
            account_id="",
            scope="",
            token_type="",
        )
        flow_cls.return_value = flow

        session = self.client.session
        session["post_oauth_next"] = "/"
        session.save()

        resp = self.client.get("/integrations/dropbox/callback/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/")

    @patch("integrations.views.dropbox.oauth.DropboxOAuth2Flow")
    def test_dropbox_callback_unsafe_next_falls_back_to_root(self, flow_cls):
        flow = MagicMock()
        flow.finish.return_value = SimpleNamespace(
            access_token="a",
            refresh_token="",
            expires_at=None,
            account_id="",
            scope="",
            token_type="",
        )
        flow_cls.return_value = flow

        session = self.client.session
        session["post_oauth_next"] = "https://evil.com/"
        session.save()

        resp = self.client.get("/integrations/dropbox/callback/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/")
