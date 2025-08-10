"""
Dropbox Authentication Service

Simple authentication service supporting token-based and OAuth methods.
"""

import logging
from typing import Optional
import dropbox

from src import config
from ..cloud.protocols import CloudAuthentication
from ..cloud.errors import CloudAuthError

logger = logging.getLogger(__name__)


class DropboxAuthBase(CloudAuthentication):
    """Base class for Dropbox authentication methods."""

    def __init__(self):
        self._client = None

    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._client is not None

    def get_client(self) -> Optional[dropbox.Dropbox]:
        """Get the authenticated Dropbox client."""
        return self._client


class DropboxTokenAuth(DropboxAuthBase):
    """Simple token-based Dropbox authentication."""

    def __init__(self, access_token: str = None):
        super().__init__()
        self._access_token = access_token or config.get_dropbox_access_token()

    def authenticate(self) -> bool:
        """Authenticate using access token."""
        if not self._access_token:
            logger.error("No Dropbox access token provided")
            raise CloudAuthError("No Dropbox access token provided", "dropbox")

        try:
            self._client = dropbox.Dropbox(oauth2_access_token=self._access_token)
            # Test the connection
            account_info = self._client.users_get_current_account()
            logger.info(
                "✅ Token authentication successful as: %s",
                account_info.name.display_name,
            )
            return True
        except Exception as e:
            logger.error("Token authentication failed: %s", e)
            raise CloudAuthError(
                f"Token authentication failed: {e}", "dropbox", e
            ) from e


class DropboxOAuthAuth(DropboxAuthBase):
    """OAuth-based Dropbox authentication (placeholder for future)."""

    def authenticate(self) -> bool:
        """Authenticate using OAuth flow (not yet implemented)."""
        logger.warning("OAuth authentication not yet implemented")
        raise CloudAuthError("OAuth authentication not yet implemented", "dropbox")


def create_dropbox_auth(auth_type: str = None) -> CloudAuthentication:
    """
    Create Dropbox authentication service based on configuration.

    Args:
        auth_type: Authentication type ('token' or 'oauth').
                  If None, uses config.get_dropbox_auth_type()

    Returns:
        CloudAuthentication: Appropriate auth service
    """
    auth_type = auth_type or config.get_dropbox_auth_type()

    if auth_type == "oauth":
        return DropboxOAuthAuth()
    else:  # default to token
        return DropboxTokenAuth()
