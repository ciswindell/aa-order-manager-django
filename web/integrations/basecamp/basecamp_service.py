"""Basecamp API Service.

Provides high-level interface for Basecamp 3 API operations.
"""

import logging

import requests

logger = logging.getLogger(__name__)

BASECAMP_API_BASE = "https://3.basecampapi.com"
USER_AGENT = "aa-order-manager (support@example.com)"


class BasecampService:
    """High-level wrapper for Basecamp 3 API operations."""

    def __init__(self, access_token: str):
        """Initialize service with access token.

        Args:
            access_token: OAuth access token for API calls
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": USER_AGENT,
        }

    def get_authorization_details(self) -> dict:
        """Get user's Basecamp authorization details including accounts.

        Returns:
            dict: Authorization response with accounts array

        Raises:
            Exception: If API call fails
        """
        response = requests.get(
            "https://launchpad.37signals.com/authorization.json",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_account_info(self, account_id: str) -> dict:
        """Get details for a specific Basecamp account.

        Args:
            account_id: Basecamp account ID

        Returns:
            dict: Account information

        Raises:
            Exception: If API call fails
        """
        response = requests.get(
            f"{BASECAMP_API_BASE}/{account_id}.json",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
