"""
Unit tests for dropbox_auth.py module.

Tests OAuth 2.0 authentication flows, token management,
browser integration, and error handling.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

# Import the classes we're testing
try:
    from src.integrations.dropbox.auth import DropboxAuthHandler
    from src.integrations.dropbox.service import DropboxAuthenticationError
except ImportError:
    # Handle case where dropbox isn't installed
    DropboxAuthHandler = None
    DropboxAuthenticationError = Exception


class TestDropboxAuthHandlerInitialization(unittest.TestCase):
    """Test DropboxAuthHandler initialization and setup."""

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
    @patch("src.integrations.dropbox.auth.logger")
    def test_initialization_success(self, mock_logger, mock_dropbox):
        """Test successful initialization."""
        mock_dropbox.__bool__ = lambda x: True  # Simulate dropbox module available

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        self.assertEqual(handler.app_key, self.app_key)
        self.assertEqual(handler.app_secret, self.app_secret)
        self.assertEqual(handler.token_file_path, self.token_file_path)
        self.assertIsNone(handler._client)
        self.assertIsNone(handler._refresh_token)
        mock_logger.info.assert_called_with("DropboxAuthHandler initialized")

    @patch("src.integrations.dropbox.auth.dropbox", None)
    def test_initialization_no_dropbox_sdk(self):
        """Test initialization when Dropbox SDK is not available."""
        with self.assertRaises(DropboxAuthenticationError) as context:
            DropboxAuthHandler(self.app_key, self.app_secret)

        self.assertIn("Dropbox SDK not available", str(context.exception))

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch.object(Path, "home")
    def test_default_token_path(self, mock_home, mock_dropbox):
        """Test default token path generation."""
        mock_dropbox.__bool__ = lambda x: True
        mock_home.return_value = Path("/home/test")

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(self.app_key, self.app_secret)

        expected_path = "/home/test/.dropbox_auth/refresh_token.json"
        self.assertEqual(handler.token_file_path, expected_path)


class TestDropboxAuthHandlerTokenManagement(unittest.TestCase):
    """Test token loading, saving, and management."""

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
    @patch("src.integrations.dropbox.auth.logger")
    def test_load_refresh_token_success(self, mock_logger, mock_dropbox):
        """Test successful refresh token loading."""
        mock_dropbox.__bool__ = lambda x: True

        # Create test token file
        token_data = {"refresh_token": "test_refresh_token", "app_key": self.app_key}
        with open(self.token_file_path, "w") as f:
            json.dump(token_data, f)

        handler = DropboxAuthHandler(
            self.app_key, self.app_secret, self.token_file_path
        )

        self.assertEqual(handler._refresh_token, "test_refresh_token")
        mock_logger.info.assert_any_call("Existing refresh token loaded successfully")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_load_refresh_token_no_file(self, mock_logger, mock_dropbox):
        """Test loading refresh token when no file exists."""
        mock_dropbox.__bool__ = lambda x: True

        handler = DropboxAuthHandler(
            self.app_key, self.app_secret, self.token_file_path
        )

        self.assertIsNone(handler._refresh_token)
        mock_logger.info.assert_any_call("No existing token file found")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_load_refresh_token_invalid_json(self, mock_logger, mock_dropbox):
        """Test loading refresh token with invalid JSON file."""
        mock_dropbox.__bool__ = lambda x: True

        # Create invalid JSON file
        with open(self.token_file_path, "w") as f:
            f.write("invalid json")

        handler = DropboxAuthHandler(
            self.app_key, self.app_secret, self.token_file_path
        )

        self.assertIsNone(handler._refresh_token)
        mock_logger.error.assert_called()

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_save_refresh_token_success(self, mock_logger, mock_dropbox):
        """Test successful refresh token saving."""
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

        # Check file permissions (should be 0o600)
        file_stat = os.stat(self.token_file_path)
        permissions = file_stat.st_mode & 0o777
        self.assertEqual(permissions, 0o600)

        mock_logger.info.assert_called_with("Refresh token saved successfully")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.os.makedirs", side_effect=OSError("Permission denied"))
    def test_save_refresh_token_failure(self, mock_makedirs, mock_dropbox):
        """Test refresh token saving failure."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        with self.assertRaises(DropboxAuthenticationError) as context:
            handler._save_refresh_token("test_token")

        self.assertIn("Could not save refresh token", str(context.exception))


class TestDropboxAuthHandlerClientCreation(unittest.TestCase):
    """Test Dropbox client creation and management."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_key = "test_app_key"
        self.app_secret = "test_app_secret"
        self.token_file_path = "/tmp/test_token.json"

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_create_client_from_refresh_token_success(self, mock_logger, mock_dropbox):
        """Test successful client creation from refresh token."""
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
        mock_logger.info.assert_any_call("Successfully authenticated as: Test User")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_create_client_no_refresh_token(self, mock_logger, mock_dropbox):
        """Test client creation when no refresh token is available."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._refresh_token = None

        result = handler._create_client_from_refresh_token()

        self.assertIsNone(result)
        mock_logger.info.assert_called_with("No refresh token available")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_create_client_invalid_token(self, mock_logger, mock_dropbox):
        """Test client creation with invalid refresh token."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock Dropbox client that raises exception
        mock_dropbox.Dropbox.side_effect = Exception("Invalid token")

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._refresh_token = "invalid_token"

        result = handler._create_client_from_refresh_token()

        self.assertIsNone(result)
        self.assertIsNone(handler._refresh_token)  # Should be cleared
        mock_logger.error.assert_called()


class TestDropboxAuthHandlerOAuthFlow(unittest.TestCase):
    """Test OAuth 2.0 flow functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_key = "test_app_key"
        self.app_secret = "test_app_secret"
        self.token_file_path = "/tmp/test_token.json"

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.DropboxOAuth2FlowNoRedirect")
    @patch("src.integrations.dropbox.auth.logger")
    def test_initiate_oauth_flow_success(
        self, mock_logger, mock_flow_class, mock_dropbox
    ):
        """Test successful OAuth flow initiation."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock OAuth flow
        mock_flow = Mock()
        mock_flow.start.return_value = "https://dropbox.com/oauth/authorize?code=123"
        mock_flow_class.return_value = mock_flow

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        url, flow = handler._initiate_oauth_flow()

        self.assertEqual(url, "https://dropbox.com/oauth/authorize?code=123")
        self.assertEqual(flow, mock_flow)

        mock_flow_class.assert_called_with(
            self.app_key, consumer_secret=self.app_secret, token_access_type="offline"
        )
        mock_logger.info.assert_any_call("OAuth flow started successfully")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.DropboxOAuth2FlowNoRedirect")
    def test_initiate_oauth_flow_failure(self, mock_flow_class, mock_dropbox):
        """Test OAuth flow initiation failure."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock OAuth flow that raises exception
        mock_flow_class.side_effect = Exception("OAuth error")

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        with self.assertRaises(DropboxAuthenticationError) as context:
            handler._initiate_oauth_flow()

        self.assertIn("Could not start OAuth flow", str(context.exception))

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.webbrowser")
    @patch("src.integrations.dropbox.auth.logger")
    def test_open_browser_success(self, mock_logger, mock_webbrowser, mock_dropbox):
        """Test successful browser opening."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        test_url = "https://dropbox.com/oauth/authorize"
        handler._open_browser(test_url)

        mock_webbrowser.open.assert_called_with(test_url)
        mock_logger.info.assert_called_with("Opening authorization URL in browser")

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.webbrowser")
    @patch("src.integrations.dropbox.auth.logger")
    @patch("builtins.print")
    def test_open_browser_failure(
        self, mock_print, mock_logger, mock_webbrowser, mock_dropbox
    ):
        """Test browser opening failure with fallback."""
        mock_dropbox.__bool__ = lambda x: True
        mock_webbrowser.open.side_effect = Exception("No browser available")

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        test_url = "https://dropbox.com/oauth/authorize"
        handler._open_browser(test_url)

        mock_logger.warning.assert_called()
        mock_print.assert_called_with(
            f"Please manually open this URL in your browser: {test_url}"
        )

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("builtins.input", side_effect=["", "test_auth_code"])
    @patch("builtins.print")
    def test_get_authorization_code(self, mock_print, mock_input, mock_dropbox):
        """Test authorization code input handling."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        result = handler._get_authorization_code()

        self.assertEqual(result, "test_auth_code")
        self.assertEqual(mock_input.call_count, 2)  # First empty, then valid code


class TestDropboxAuthHandlerAuthentication(unittest.TestCase):
    """Test main authentication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app_key = "test_app_key"
        self.app_secret = "test_app_secret"
        self.token_file_path = "/tmp/test_token.json"

    @patch("src.integrations.dropbox.auth.dropbox")
    @patch("src.integrations.dropbox.auth.logger")
    def test_authenticate_with_existing_token(self, mock_logger, mock_dropbox):
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
    @patch("src.integrations.dropbox.auth.logger")
    @patch("builtins.print")
    def test_authenticate_interactive_flow_success(
        self, mock_print, mock_logger, mock_dropbox
    ):
        """Test successful interactive authentication flow."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock OAuth flow components
        mock_flow = Mock()
        mock_oauth_result = Mock()
        mock_oauth_result.refresh_token = "new_refresh_token"
        mock_flow.finish.return_value = mock_oauth_result

        # Mock client creation
        mock_client = Mock()
        mock_account = Mock()
        mock_account.name.display_name = "Test User"
        mock_client.users_get_current_account.return_value = mock_account
        mock_dropbox.Dropbox.return_value = mock_client

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        # Mock all the interactive components
        with patch.object(
            handler, "_create_client_from_refresh_token", return_value=None
        ), patch.object(
            handler, "_initiate_oauth_flow", return_value=("http://auth.url", mock_flow)
        ), patch.object(
            handler, "_open_browser"
        ), patch.object(
            handler, "_get_authorization_code", return_value="auth_code"
        ), patch.object(
            handler, "_save_refresh_token"
        ):

            result = handler.authenticate()

        self.assertEqual(result, mock_client)
        self.assertEqual(handler._client, mock_client)
        mock_flow.finish.assert_called_with("auth_code")
        mock_logger.info.assert_any_call("Authentication completed successfully")

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_authenticate_failure(self, mock_dropbox):
        """Test authentication failure."""
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


class TestDropboxAuthHandlerUtilities(unittest.TestCase):
    """Test utility and management functions."""

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
    @patch("src.integrations.dropbox.auth.logger")
    def test_clear_stored_token(self, mock_logger, mock_dropbox):
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
        mock_logger.info.assert_called_with("Stored refresh token cleared")

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_get_account_info_success(self, mock_dropbox):
        """Test successful account info retrieval."""
        mock_dropbox.__bool__ = lambda x: True

        # Mock client and account info
        mock_client = Mock()
        mock_account = Mock()
        mock_account.account_id = "account123"
        mock_account.name.display_name = "Test User"
        mock_account.email = "test@example.com"
        mock_account.country = "US"
        mock_account.locale = "en"
        mock_client.users_get_current_account.return_value = mock_account

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        handler._client = mock_client

        result = handler.get_account_info()

        expected = {
            "account_id": "account123",
            "name": "Test User",
            "email": "test@example.com",
            "country": "US",
            "locale": "en",
        }
        self.assertEqual(result, expected)

    @patch("src.integrations.dropbox.auth.dropbox")
    def test_get_account_info_no_client(self, mock_dropbox):
        """Test account info retrieval when not authenticated."""
        mock_dropbox.__bool__ = lambda x: True

        with patch.object(DropboxAuthHandler, "_load_refresh_token"):
            handler = DropboxAuthHandler(
                self.app_key, self.app_secret, self.token_file_path
            )

        result = handler.get_account_info()
        self.assertIsNone(result)


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run the tests
    unittest.main(verbosity=2)
