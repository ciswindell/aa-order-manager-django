"""
Dropbox OAuth 2.0 Authentication Handler

Handles OAuth 2.0 authentication flow with web browser integration,
offline access, and refresh token management for long-term API access.
Also supports simple token-based authentication for development.
"""

import json
import logging
import os
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

# Import config system
from src import config

try:
    import dropbox
    from dropbox import DropboxOAuth2FlowNoRedirect
except ImportError:
    dropbox = None
    DropboxOAuth2FlowNoRedirect = None

from .service import DropboxAuthenticationError

# Configure logging
logger = logging.getLogger(__name__)


class DropboxAuthHandler:
    """
    Handles Dropbox authentication with multiple methods:
    1. OAuth 2.0 flow with web browser (for production)
    2. Simple token-based authentication (for development)

    Provides secure local storage of refresh tokens and automatic
    token refresh for long-term API access.
    """

    def __init__(
        self,
        app_key: str = None,
        app_secret: str = None,
        token_file_path: Optional[str] = None,
    ):
        """
        Initialize the authentication handler.

        Args:
            app_key: Dropbox app key (optional if using token-based auth)
            app_secret: Dropbox app secret (optional if using token-based auth)
            token_file_path: Optional custom path for token storage file
        """
        if not dropbox:
            raise DropboxAuthenticationError(
                "Dropbox SDK not available. Install with: pip install dropbox"
            )

        self.app_key = app_key or config.get_dropbox_app_key()
        self.app_secret = app_secret or config.get_dropbox_app_secret()
        self.token_file_path = token_file_path or self._get_default_token_path()
        self._client = None
        self._refresh_token = None

        # Load existing refresh token if available
        self._load_refresh_token()

        logger.info("DropboxAuthHandler initialized")

    def _get_default_token_path(self) -> str:
        """Get the default path for storing the refresh token."""
        home_dir = Path.home()
        config_dir = home_dir / ".dropbox_auth"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "refresh_token.json")

    def _load_refresh_token(self) -> None:
        """Load refresh token from secure local storage."""
        try:
            if os.path.exists(self.token_file_path):
                with open(self.token_file_path, "r") as f:
                    token_data = json.load(f)
                    self._refresh_token = token_data.get("refresh_token")
                    if self._refresh_token:
                        logger.info("Existing refresh token loaded successfully")
                    else:
                        logger.warning("No refresh token found in storage file")
            else:
                logger.info("No existing token file found")
        except Exception as e:
            logger.error(f"Failed to load refresh token: {str(e)}")
            self._refresh_token = None

    def _save_refresh_token(self, refresh_token: str) -> None:
        """
        Save refresh token to secure local storage.

        Args:
            refresh_token: The refresh token to store
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.token_file_path), exist_ok=True)

            token_data = {
                "refresh_token": refresh_token,
                "app_key": self.app_key,  # Store app key for validation
            }

            with open(self.token_file_path, "w") as f:
                json.dump(token_data, f)

            # Set restrictive permissions (owner read/write only)
            os.chmod(self.token_file_path, 0o600)

            self._refresh_token = refresh_token
            logger.info("Refresh token saved successfully")

        except Exception as e:
            logger.error(f"Failed to save refresh token: {str(e)}")
            raise DropboxAuthenticationError(f"Could not save refresh token: {str(e)}")

    def _create_client_from_refresh_token(self) -> Optional[dropbox.Dropbox]:
        """
        Create Dropbox client using stored refresh token.

        Returns:
            Optional[dropbox.Dropbox]: Authenticated client if successful, None otherwise
        """
        if not self._refresh_token:
            logger.info("No refresh token available")
            return None

        try:
            logger.info("Creating client from refresh token")
            client = dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret,
                oauth2_refresh_token=self._refresh_token,
            )

            # Test the client by getting account info
            account_info = client.users_get_current_account()
            logger.info(
                f"Successfully authenticated as: {account_info.name.display_name}"
            )

            return client

        except Exception as e:
            logger.error(f"Failed to create client from refresh token: {str(e)}")
            # Refresh token might be invalid, clear it
            self._refresh_token = None
            return None

    def _initiate_oauth_flow(self) -> str:
        """
        Initiate OAuth 2.0 flow and return authorization URL.

        Returns:
            str: Authorization URL for user to visit
        """
        try:
            logger.info("Initiating OAuth 2.0 flow")

            # Create OAuth flow for offline access (to get refresh token)
            auth_flow = DropboxOAuth2FlowNoRedirect(
                self.app_key,
                consumer_secret=self.app_secret,
                token_access_type="offline",  # Request offline access for refresh token
            )

            authorize_url = auth_flow.start()
            logger.info("OAuth flow started successfully")

            return authorize_url, auth_flow

        except Exception as e:
            logger.error(f"Failed to initiate OAuth flow: {str(e)}")
            raise DropboxAuthenticationError(f"Could not start OAuth flow: {str(e)}")

    def _open_browser(self, url: str) -> None:
        """
        Open the authorization URL in the default web browser.

        Args:
            url: Authorization URL to open
        """
        try:
            logger.info("Opening authorization URL in browser")
            webbrowser.open(url)
        except Exception as e:
            logger.warning(f"Could not open browser automatically: {str(e)}")
            print(f"Please manually open this URL in your browser: {url}")

    def _get_authorization_code(self) -> str:
        """
        Get authorization code from user input.

        Returns:
            str: Authorization code entered by user
        """
        print("\nAfter authorizing the application:")
        print("1. Click 'Allow' (you might have to log in first)")
        print("2. Copy the authorization code from the page")
        print("3. Paste it below")

        while True:
            auth_code = input("\nEnter the authorization code: ").strip()
            if auth_code:
                return auth_code
            print("Please enter a valid authorization code.")

    def authenticate(self) -> Optional[dropbox.Dropbox]:
        """
        Authenticate with Dropbox using OAuth 2.0 flow.

        First attempts to use existing refresh token, then falls back
        to interactive OAuth flow if needed.

        Returns:
            Optional[dropbox.Dropbox]: Authenticated Dropbox client if successful, None otherwise

        Raises:
            DropboxAuthenticationError: If authentication fails
        """
        try:
            # Try to use existing refresh token first
            client = self._create_client_from_refresh_token()
            if client:
                self._client = client
                return client

            logger.info("No valid refresh token found, starting interactive OAuth flow")

            # Start interactive OAuth flow
            authorize_url, auth_flow = self._initiate_oauth_flow()

            print("\n" + "=" * 60)
            print("DROPBOX AUTHENTICATION REQUIRED")
            print("=" * 60)
            print(f"1. Opening authorization URL in your browser...")
            print(f"   URL: {authorize_url}")

            self._open_browser(authorize_url)

            # Get authorization code from user
            auth_code = self._get_authorization_code()

            # Complete OAuth flow
            logger.info("Completing OAuth flow with authorization code")
            oauth_result = auth_flow.finish(auth_code)

            # Save refresh token
            self._save_refresh_token(oauth_result.refresh_token)

            # Create client
            client = dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret,
                oauth2_refresh_token=oauth_result.refresh_token,
            )

            # Test the client
            account_info = client.users_get_current_account()
            print(
                f"\n✅ Successfully authenticated as: {account_info.name.display_name}"
            )
            print("=" * 60)

            self._client = client
            logger.info("Authentication completed successfully")

            return client

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise DropboxAuthenticationError(f"Authentication failed: {str(e)}")

    def authenticate_with_token(
        self, access_token: str = None, team_member_id: str = None
    ) -> Optional[dropbox.Dropbox]:
        """
        Authenticate using a simple access token (for development).

        Args:
            access_token: Direct access token. If None, will try to get from environment.
            team_member_id: Team member ID for Dropbox Business accounts. If None, will try to get from environment.

        Returns:
            Optional[dropbox.Dropbox]: Authenticated Dropbox client if successful, None otherwise

        Raises:
            DropboxAuthenticationError: If authentication fails
        """
        try:
            # Get token from parameter or environment using new config system
            token = access_token or config.get_dropbox_access_token()
            member_id = team_member_id or os.environ.get("DROPBOX_TEAM_MEMBER_ID")  # Keep as direct access since not in new config

            if not token:
                logger.warning(
                    "No access token provided and DROPBOX_ACCESS_TOKEN not found in environment"
                )
                return None

            logger.info("Attempting token-based authentication")

            # First try as regular user account
            try:
                client = dropbox.Dropbox(oauth2_access_token=token)
                account_info = client.users_get_current_account()
                logger.info(
                    f"✅ Token authentication successful as: {account_info.name.display_name}"
                )
                self._client = client
                return client

            except Exception as e:
                error_str = str(e).lower()
                if "team" in error_str and "business" in error_str:
                    logger.info("Team token detected, attempting team authentication")
                    return self._authenticate_team_token(token, member_id)
                else:
                    raise e

        except Exception as e:
            logger.error(f"Token-based authentication failed: {str(e)}")
            raise DropboxAuthenticationError(f"Token authentication failed: {str(e)}")

    def _authenticate_team_token(
        self, token: str, member_id: str = None
    ) -> Optional[dropbox.Dropbox]:
        """
        Authenticate using a Dropbox Business team token.

        Args:
            token: Team access token
            member_id: Team member ID to act as

        Returns:
            Optional[dropbox.Dropbox]: Authenticated Dropbox client if successful, None otherwise
        """
        try:
            # Create team client
            team_client = dropbox.DropboxTeam(oauth2_access_token=token)

            if member_id:
                # Use specific team member
                logger.info(f"Using team member ID: {member_id}")
                client = team_client.as_user(member_id)
            else:
                # Get first available team member if no ID specified
                logger.info(
                    "No team member ID specified, getting first available member"
                )
                members = team_client.team_members_list()
                if members.members:
                    first_member = members.members[0]
                    member_id = first_member.profile.team_member_id
                    logger.info(
                        f"Using first team member: {first_member.profile.name.display_name} ({member_id})"
                    )
                    client = team_client.as_user(member_id)
                else:
                    raise DropboxAuthenticationError("No team members found")

            # Test the client
            account_info = client.users_get_current_account()
            logger.info(
                f"✅ Team token authentication successful as: {account_info.name.display_name}"
            )

            self._client = client
            return client

        except Exception as e:
            logger.error(f"Team token authentication failed: {str(e)}")
            raise DropboxAuthenticationError(
                f"Team token authentication failed: {str(e)}"
            )

    @classmethod
    def create_simple_auth(
        cls, access_token: str = None, team_member_id: str = None
    ) -> "DropboxAuthHandler":
        """
        Factory method to create an auth handler for simple token-based authentication.

        Args:
            access_token: Direct access token. If None, will use DROPBOX_ACCESS_TOKEN from environment.
            team_member_id: Team member ID for Dropbox Business accounts. If None, will use DROPBOX_TEAM_MEMBER_ID from environment.

        Returns:
            DropboxAuthHandler: Configured auth handler
        """
        handler = cls()
        handler.authenticate_with_token(access_token, team_member_id)
        return handler

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self._client is not None

    def get_client(self) -> Optional[dropbox.Dropbox]:
        """
        Get the current authenticated Dropbox client.

        Returns:
            Optional[dropbox.Dropbox]: Authenticated client if available, None otherwise
        """
        return self._client

    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using the stored refresh token.

        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            if not self._refresh_token:
                logger.warning("No refresh token available for refresh")
                return False

            logger.info("Refreshing access token")

            # The Dropbox SDK handles token refresh automatically
            # We just need to create a new client which will refresh tokens as needed
            client = self._create_client_from_refresh_token()

            if client:
                self._client = client
                logger.info("Access token refreshed successfully")
                return True
            else:
                logger.error("Failed to refresh access token")
                return False

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return False

    def clear_stored_token(self) -> None:
        """Clear stored refresh token (for logout/reset)."""
        try:
            if os.path.exists(self.token_file_path):
                os.remove(self.token_file_path)
                logger.info("Stored refresh token cleared")

            self._refresh_token = None
            self._client = None

        except Exception as e:
            logger.error(f"Failed to clear stored token: {str(e)}")

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current account information.

        Returns:
            Optional[Dict[str, Any]]: Account information if authenticated, None otherwise
        """
        if not self._client:
            return None

        try:
            account = self._client.users_get_current_account()
            return {
                "account_id": account.account_id,
                "name": account.name.display_name,
                "email": account.email,
                "country": account.country,
                "locale": account.locale,
            }
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return None
