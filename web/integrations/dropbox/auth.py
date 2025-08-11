"""Dropbox Authentication Service.

Provides token-based auth (legacy/unused by default) and OAuth auth tied to a
specific Django user (runtime default).
"""

import logging
from typing import Optional
import dropbox

from django.conf import settings

from ..cloud import config
from ..cloud.protocols import CloudAuthentication
from ..cloud.errors import CloudAuthError
from ..utils.token_store import get_tokens_for_user

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
    """OAuth-based Dropbox authentication for a specific user."""

    def __init__(self, user):
        super().__init__()
        self._user = user

    def authenticate(self) -> bool:
        tokens = get_tokens_for_user(self._user)
        if not tokens or not tokens.get("access_token"):
            raise CloudAuthError("No Dropbox OAuth tokens for user", "dropbox")

        kwargs: dict = {"oauth2_access_token": tokens["access_token"]}
        refresh_token = tokens.get("refresh_token")
        if refresh_token and settings.DROPBOX_APP_KEY and settings.DROPBOX_APP_SECRET:
            kwargs.update(
                {
                    "oauth2_refresh_token": refresh_token,
                    "app_key": settings.DROPBOX_APP_KEY,
                    "app_secret": settings.DROPBOX_APP_SECRET,
                }
            )

        try:
            self._client = dropbox.Dropbox(**kwargs)
            self._client.users_get_current_account()
            logger.info("✅ OAuth authentication successful")
            return True
        except Exception as e:  # pragma: no cover
            logger.error("OAuth authentication failed: %s", e)
            raise CloudAuthError(
                f"OAuth authentication failed: {e}", "dropbox", e
            ) from e


def create_dropbox_auth(auth_type: str = None, user=None) -> CloudAuthentication:
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
        return DropboxOAuthAuth(user)
    else:  # default to token
        return DropboxTokenAuth()
