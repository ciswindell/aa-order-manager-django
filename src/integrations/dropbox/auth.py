"""
Dropbox Authentication Service

Simple authentication service supporting token-based and OAuth methods.
"""

import logging
from typing import Optional
import dropbox

from ..cloud.protocols import CloudAuthentication
from ..cloud.errors import CloudAuthError
from src import config

logger = logging.getLogger(__name__)


class DropboxTokenAuth(CloudAuthentication):
    """Simple token-based Dropbox authentication."""

    def __init__(self, access_token: str = None):
        self._access_token = access_token or config.get_dropbox_access_token()
        self._client = None

    def authenticate(self) -> bool:
        """Authenticate using access token."""
        if not self._access_token:
            logger.error("No Dropbox access token provided")
            return False

        try:
            self._client = dropbox.Dropbox(oauth2_access_token=self._access_token)
            # Test the connection
            account_info = self._client.users_get_current_account()
            logger.info(f"✅ Token authentication successful as: {account_info.name.display_name}")
            return True
        except Exception as e:
            logger.error(f"Token authentication failed: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._client is not None

    def get_client(self) -> Optional[dropbox.Dropbox]:
        """Get the authenticated Dropbox client."""
        return self._client


class DropboxOAuthAuth(CloudAuthentication):
    """OAuth-based Dropbox authentication (placeholder for future)."""

    def __init__(self):
        self._client = None

    def authenticate(self) -> bool:
        """Authenticate using OAuth flow (not yet implemented)."""
        logger.warning("OAuth authentication not yet implemented")
        return False

    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return False

    def get_client(self) -> Optional[dropbox.Dropbox]:
        """Get the authenticated Dropbox client."""
        return self._client


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