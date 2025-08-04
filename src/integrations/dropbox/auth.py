"""
Dropbox Authentication Handlers

Strategy pattern for switching between token-based and OAuth authentication.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

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


class BaseAuthHandler(ABC):
    """Base authentication handler interface."""
    
    def __init__(self):
        """Initialize the authentication handler."""
        if not dropbox:
            raise DropboxAuthenticationError(
                "Dropbox SDK not available. Install with: pip install dropbox"
            )
        self._client = None

    @abstractmethod
    def authenticate(self) -> Optional[dropbox.Dropbox]:
        """Authenticate and return client."""
        pass

    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self._client is not None

    def get_client(self) -> Optional[dropbox.Dropbox]:
        """Get the authenticated Dropbox client."""
        return self._client


class RegularUserTokenHandler(BaseAuthHandler):
    """Individual user authentication (what real users will experience)."""

    def authenticate(self, access_token: str = None) -> Optional[dropbox.Dropbox]:
        """Simple user authentication - no team complexity."""
        try:
            token = access_token or config.get_dropbox_access_token()

            if not token:
                logger.warning("No access token found")
                return None

            logger.info("Attempting regular user authentication")

            # Only try regular user authentication - no team logic
            client = dropbox.Dropbox(oauth2_access_token=token)
            account_info = client.users_get_current_account()
            logger.info(f"✅ Regular user authentication successful as: {account_info.name.display_name}")
            self._client = client
            return client

        except Exception as e:
            logger.error(f"Regular user authentication failed: {str(e)}")
            raise DropboxAuthenticationError(f"Regular user authentication failed: {str(e)}")


class TeamTokenHandler(BaseAuthHandler):
    """Business team token authentication (for services/automation)."""

    def authenticate(self, access_token: str = None, team_member_id: str = None) -> Optional[dropbox.Dropbox]:
        """Team authentication with member selection."""
        try:
            token = access_token or config.get_dropbox_access_token()
            member_id = team_member_id or os.environ.get("DROPBOX_TEAM_MEMBER_ID")

            if not token:
                logger.warning("No team access token found")
                return None

            logger.info("Attempting team token authentication")

            # Create team client
            team_client = dropbox.DropboxTeam(oauth2_access_token=token)

            if member_id:
                logger.info(f"Using specified team member ID: {member_id}")
                client = team_client.as_user(member_id)
            else:
                logger.info("No team member ID specified, getting first available member")
                members = team_client.team_members_list()
                if members.members:
                    first_member = members.members[0]
                    member_id = first_member.profile.team_member_id
                    logger.info(f"Using first team member: {first_member.profile.name.display_name} ({member_id})")
                    client = team_client.as_user(member_id)
                else:
                    raise DropboxAuthenticationError("No team members found")

            # Test the client
            account_info = client.users_get_current_account()
            logger.info(f"✅ Team token authentication successful as: {account_info.name.display_name}")
            self._client = client
            return client

        except Exception as e:
            logger.error(f"Team token authentication failed: {str(e)}")
            raise DropboxAuthenticationError(f"Team token authentication failed: {str(e)}")


class OAuthAuthHandler(BaseAuthHandler):
    """OAuth browser flow authentication (placeholder for future implementation)."""

    def authenticate(self) -> Optional[dropbox.Dropbox]:
        """Authenticate using OAuth browser flow."""
        raise NotImplementedError(
            "OAuth flow not yet implemented. Use TokenAuthHandler for now. "
            "Set DROPBOX_AUTH_TYPE=token in your environment."
        )


class DropboxAuthHandler:
    """Factory for creating the appropriate authentication handler."""

    @classmethod
    def create_auth_handler(cls, auth_type: str = None) -> BaseAuthHandler:
        """
        Create authentication handler based on type.
        
        Args:
            auth_type: 'user', 'team', or 'oauth'. If None, uses DROPBOX_AUTH_TYPE env var or defaults to 'team'
        
        Returns:
            BaseAuthHandler: Appropriate auth handler
        """
        auth_type = auth_type or os.environ.get("DROPBOX_AUTH_TYPE", "team")
        
        if auth_type.lower() == "oauth":
            return OAuthAuthHandler()
        elif auth_type.lower() == "user":
            return RegularUserTokenHandler()
        else:  # default to team (for current setup)
            return TeamTokenHandler()

    @classmethod
    def create_simple_auth(cls, access_token: str = None, team_member_id: str = None) -> BaseAuthHandler:
        """
        Factory method for token-based authentication (backward compatibility).
        
        Automatically detects whether to use team or user authentication based on team_member_id.
        
        Args:
            access_token: Direct access token. If None, will use DROPBOX_ACCESS_TOKEN from environment.
            team_member_id: Team member ID for business accounts. If None, will try to get from environment.
            
        Returns:
            BaseAuthHandler: Appropriate auth handler, already authenticated
        """
        # Detect auth type based on team member ID presence
        member_id = team_member_id or os.environ.get("DROPBOX_TEAM_MEMBER_ID")
        
        if member_id:
            # Team authentication
            handler = TeamTokenHandler()
            handler.authenticate(access_token, team_member_id)
        else:
            # Regular user authentication
            handler = RegularUserTokenHandler()
            handler.authenticate(access_token)
            
        return handler
