from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from integrations.models import DropboxAccount


class DashboardTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.password = "testpass123"
        self.user = self.User.objects.create_user(
            username="user", email="user@example.com", password=self.password
        )
        self.staff = self.User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password=self.password,
            is_staff=True,
        )

    def test_dashboard_requires_login(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_dashboard_non_staff_no_admin_link(self):
        self.client.login(username="user", password=self.password)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Django Admin")

    def test_dashboard_staff_sees_admin_link(self):
        self.client.login(username="staff", password=self.password)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Django Admin")

    def test_dropbox_misconfigured_warning_staff_only(self):
        self.client.login(username="staff", password=self.password)
        with self.settings(DROPBOX_APP_KEY="", DROPBOX_APP_SECRET=""):
            resp = self.client.get("/")
            self.assertContains(resp, "Dropbox app credentials are not configured")
        self.client.logout()
        self.client.login(username="user", password=self.password)
        with self.settings(DROPBOX_APP_KEY="", DROPBOX_APP_SECRET=""):
            resp = self.client.get("/")
            self.assertNotContains(resp, "Dropbox app credentials are not configured")

    def test_dropbox_banner_present_when_not_connected(self):
        """5.3: When no tokens exist, Dropbox connect banner is present."""
        self.client.login(username="user", password=self.password)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Dropbox is not connected.")

    def test_dropbox_banner_absent_when_connected(self):
        """5.4: When tokens exist, Dropbox banner is absent."""
        DropboxAccount.objects.create(
            user=self.user,
            account_id="acc-123",
            access_token="x",
            refresh_token_encrypted="y",
        )
        self.client.login(username="user", password=self.password)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Dropbox is not connected.")

    def test_logout_post_redirects(self):
        self.client.login(username="user", password=self.password)
        resp = self.client.post(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)
