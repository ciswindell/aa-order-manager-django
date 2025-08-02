"""
Simplified unit tests for dropbox_auth.py module.

Focuses on essential authentication functionality with basic coverage
of initialization, token management, and core auth flows.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

# Import the classes we're testing
try:
    from src.integrations.dropbox.auth import DropboxAuthHandler
    from src.integrations.dropbox.service import DropboxAuthenticationError
except ImportError:
    # Handle case where dropbox isn't installed
    DropboxAuthHandler = None
    DropboxAuthenticationError = Exception


class TestDropboxAuthSetup(unittest.TestCase):
    """Test basic initialization, SDK validation, and token file management."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_key = "test_app_key"
        self.app_secret = "test_app_secret"
        self.temp_dir = tempfile.mkdtemp()
        self.token_file_path = os.path.join(self.temp_dir, "test_token.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_initialization_success(self, mock_dropbox):
        """Test successful DropboxAuthHandler initialization."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        self.assertEqual(handler.app_key, self.app_key)
        self.assertEqual(handler.app_secret, self.app_secret)
        self.assertEqual(handler.token_file_path, self.token_file_path)
        self.assertIsNone(handler._client)
        self.assertIsNone(handler._refresh_token)

    @patch("src.integrations.dropbox.auth.dropbox", None)
    def test_initialization_no_dropbox_sdk(self):
        """Test initialization failure when Dropbox SDK unavailable."""
        with self.assertRaises(DropboxAuthenticationError) as context:
            DropboxAuthHandler(self.app_key, self.app_secret)

        self.assertIn("Dropbox SDK not available", str(context.exception))

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_load_refresh_token_success(self, mock_dropbox):
        """Test loading existing refresh token from file."""
        mock_dropbox.__bool__ = lambda x: True

        # Create test token file
        token_data = {"refresh_token": "test_refresh_token", "app_key": self.app_key}
        with open(self.token_file_path, "w") as f:
            json.dump(token_data, f)

        handler = DropboxAuthHandler(
            self.app_key, self.app_secret, self.token_file_path
        )

        self.assertEqual(handler._refresh_token, "test_refresh_token")

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_load_refresh_token_no_file(self, mock_dropbox):
        """Test loading refresh token when no file exists."""
        mock_dropbox.__bool__ = lambda x: True

        handler = DropboxAuthHandler(
            self.app_key, self.app_secret, self.token_file_path
        )

        self.assertIsNone(handler._refresh_token)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_save_refresh_token_success(self, mock_dropbox):
        """Test saving refresh token to file."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        test_token = "test_refresh_token"
        handler._save_refresh_token(test_token)

        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.token_file_path))
        with open(self.token_file_path, "r") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["refresh_token"], test_token)
        self.assertEqual(saved_data["app_key"], self.app_key)
        self.assertEqual(handler._refresh_token, test_token)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_clear_stored_token(self, mock_dropbox):
        """Test clearing stored refresh token."""
        mock_dropbox.__bool__ = lambda x: True

        # Create test token file
        with open(self.token_file_path, "w") as f:
            json.dump({"refresh_token": "test_token"}, f)

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._refresh_token = "test_token"
        handler._client = Mock()

        handler.clear_stored_token()

        self.assertFalse(os.path.exists(self.token_file_path))
        self.assertIsNone(handler._refresh_token)
        self.assertIsNone(handler._client)


class TestDropboxAuthFlow(unittest.TestCase):
    """Test authentication flow, client creation, and status checking."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_key = "test_app_key"
        self.app_secret = "test_app_secret"
        self.token_file_path = "/tmp/test_token.json"

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_create_client_from_refresh_token_success(self, mock_dropbox):
        """Test successful client creation from stored refresh token."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock the Dropbox client and account info
        mock_client = Mock()
        mock_account = Mock()
        mock_account.name.display_name = "Test User"
        mock_client.users_get_current_account.return_value = mock_account
        mock_dropbox.Dropbox.return_value = mock_client

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._refresh_token = "test_refresh_token"

        result = handler._create_client_from_refresh_token()

        self.assertEqual(result, mock_client)
        mock_dropbox.Dropbox.assert_called_with(
            app_key=self.app_key,
            app_secret=self.app_secret,
            oauth2_refresh_token="test_refresh_token",
        )

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_create_client_no_refresh_token(self, mock_dropbox):
        """Test client creation when no refresh token available."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._refresh_token = None

        result = handler._create_client_from_refresh_token()

        self.assertIsNone(result)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_authenticate_with_existing_token(self, mock_dropbox):
        """Test authentication using existing refresh token."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock successful client creation
        mock_client = Mock()

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        with patch.object(
            handler, "_create_client_from_refresh_token", return_value=mock_client
        ):
            result = handler.authenticate()

        self.assertEqual(result, mock_client)
        self.assertEqual(handler._client, mock_client)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_authenticate_failure(self, mock_dropbox):
        """Test authentication failure handling."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        # Mock failure in client creation
        with patch.object(
            handler,
            "_create_client_from_refresh_token",
            side_effect=Exception("Auth failed"),
        ):
            with self.assertRaises(DropboxAuthenticationError) as context:
                handler.authenticate()

        self.assertIn("Authentication failed", str(context.exception))

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_is_authenticated(self, mock_dropbox):
        """Test authentication status checking."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        # Initially not authenticated
        self.assertFalse(handler.is_authenticated())

        # After setting client
        handler._client = Mock()
        self.assertTrue(handler.is_authenticated())

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_get_client(self, mock_dropbox):
        """Test getting the authenticated client."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        # Initially no client
        self.assertIsNone(handler.get_client())

        # After setting client
        mock_client = Mock()
        handler._client = mock_client
        self.assertEqual(handler.get_client(), mock_client)


if __name__ == "__main__":
    unittest.main(verbosity=2)
