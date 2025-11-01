"""Basecamp Authentication Service.

Provides OAuth-based authentication for Basecamp 3 API tied to a specific Django user.
"""

import logging
import time
from datetime import datetime, timezone

import requests

from ..cloud.errors import CloudAuthError
from ..cloud.protocols import CloudAuthentication
from ..utils.token_store import get_tokens_for_user, save_tokens_for_user
from .config import get_basecamp_app_key, get_basecamp_app_secret

logger = logging.getLogger(__name__)

BASECAMP_TOKEN_URL = "https://launchpad.37signals.com/authorization/token"
BASECAMP_AUTHORIZATION_URL = "https://launchpad.37signals.com/authorization.json"


class BasecampOAuthAuth(CloudAuthentication):
    """OAuth-based Basecamp authentication for a specific user."""

    def __init__(self, user):
        super().__init__()
        self._user = user
        self._access_token = None

    def authenticate(self) -> bool:
        """Authenticate using stored OAuth tokens with automatic refresh if expired."""
        tokens = get_tokens_for_user(self._user, provider="basecamp")
        if not tokens or not tokens.get("access_token"):
            logger.error(
                "Basecamp authentication failed: no tokens | user_id=%s",
                getattr(self._user, "id", None),
            )
            raise CloudAuthError("No Basecamp OAuth tokens for user", "basecamp")

        # Check if token is expired and attempt refresh
        if self._is_token_expired(tokens):
            logger.info(
                "Basecamp token expired, attempting refresh | user_id=%s",
                getattr(self._user, "id", None),
            )
            try:
                tokens = self._refresh_user_tokens(tokens)
                logger.info(
                    "Basecamp token refresh successful | user_id=%s | account_id=%s",
                    getattr(self._user, "id", None),
                    tokens.get("account_id"),
                )
            except CloudAuthError as e:
                logger.error(
                    "Basecamp token refresh failed | user_id=%s | error=%s",
                    getattr(self._user, "id", None),
                    str(e),
                )
                raise

        self._access_token = tokens["access_token"]
        try:
            response = requests.get(
                BASECAMP_AUTHORIZATION_URL,
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=10,
            )
            response.raise_for_status()
            logger.info(
                "Basecamp OAuth authentication successful | user_id=%s",
                getattr(self._user, "id", None),
            )
            return True
        except Exception as e:
            self._access_token = None
            logger.error(
                "Basecamp OAuth authentication failed | user_id=%s | error=%s",
                getattr(self._user, "id", None),
                str(e),
            )
            raise CloudAuthError(
                f"OAuth authentication failed: {e}", "basecamp", e
            ) from e

    def _is_token_expired(self, tokens: dict) -> bool:
        """Check if access token is expired."""
        expires_at = tokens.get("expires_at")
        if not expires_at:
            return False
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return expires_at <= now

    def _refresh_user_tokens(self, old_tokens: dict) -> dict:
        """Refresh tokens and save to database (FR-007: 95% success rate)."""
        refresh_token = old_tokens.get("refresh_token")
        if not refresh_token:
            raise CloudAuthError("No refresh token available", "basecamp")

        try:
            token_response = self.refresh_access_token(refresh_token)
            new_tokens = {
                "access_token": token_response.get("access_token"),
                "refresh_token": token_response.get("refresh_token", refresh_token),
                "account_id": old_tokens.get("account_id"),
                "account_name": old_tokens.get("account_name"),
                "expires_at": old_tokens.get("expires_at"),
                "scope": old_tokens.get("scope", ""),
                "token_type": token_response.get("token_type", "Bearer"),
            }
            save_tokens_for_user(self._user, new_tokens, provider="basecamp")
            return new_tokens
        except Exception as e:
            logger.error(
                "Basecamp token refresh failed | user_id=%s | error=%s",
                getattr(self._user, "id", None),
                str(e),
            )
            raise CloudAuthError(f"Token refresh failed: {e}", "basecamp", e) from e

    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self._access_token is not None

    def get_client(self):
        """Get the authenticated access token (Basecamp has no official SDK)."""
        return self._access_token

    @staticmethod
    def exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
        """Exchange OAuth authorization code for access/refresh tokens.

        Args:
            code: Authorization code from Basecamp OAuth callback
            redirect_uri: Redirect URI used in the authorization request

        Returns:
            dict: Token response with access_token, refresh_token, expires_in

        Raises:
            CloudAuthError: If token exchange fails
        """
        logger.info("Basecamp token exchange initiated | code_prefix=%s", code[:10])
        try:
            response = BasecampOAuthAuth._make_request_with_retry(
                method="POST",
                url=BASECAMP_TOKEN_URL,
                data={
                    "type": "web_server",
                    "client_id": get_basecamp_app_key(),
                    "client_secret": get_basecamp_app_secret(),
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )
            logger.info("Basecamp token exchange successful")
            return response
        except Exception as e:
            logger.error("Basecamp token exchange failed | error=%s", str(e))
            raise CloudAuthError(f"Token exchange failed: {e}", "basecamp", e) from e

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Refresh access token using refresh token (FR-007: 95% success rate).

        Args:
            refresh_token: Refresh token from previous OAuth flow

        Returns:
            dict: Token response with new access_token, refresh_token, expires_in

        Raises:
            CloudAuthError: If token refresh fails
        """
        logger.info(
            "Basecamp token refresh initiated | token_prefix=%s", refresh_token[:10]
        )
        try:
            response = BasecampOAuthAuth._make_request_with_retry(
                method="POST",
                url=BASECAMP_TOKEN_URL,
                data={
                    "type": "refresh",
                    "client_id": get_basecamp_app_key(),
                    "client_secret": get_basecamp_app_secret(),
                    "refresh_token": refresh_token,
                },
            )
            logger.info("Basecamp token refresh successful")
            return response
        except Exception as e:
            logger.error("Basecamp token refresh failed | error=%s", str(e))
            raise CloudAuthError(f"Token refresh failed: {e}", "basecamp", e) from e

    @staticmethod
    def get_authorization_details(access_token: str) -> dict:
        """Fetch user's Basecamp authorization details.

        Args:
            access_token: OAuth access token

        Returns:
            dict: Authorization response with accounts array

        Raises:
            CloudAuthError: If API call fails
        """
        logger.info("Basecamp authorization details fetch initiated")
        try:
            response = BasecampOAuthAuth._make_request_with_retry(
                method="GET",
                url=BASECAMP_AUTHORIZATION_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            logger.info("Basecamp authorization details fetch successful")
            return response
        except Exception as e:
            logger.error(
                "Basecamp authorization details fetch failed | error=%s", str(e)
            )
            raise CloudAuthError(
                f"Failed to get authorization details: {e}", "basecamp", e
            ) from e

    @staticmethod
    def _make_request_with_retry(
        method: str,
        url: str,
        data: dict = None,
        headers: dict = None,
        max_retries: int = 3,
        initial_delay: float = 1.0,
    ) -> dict:
        """Make HTTP request with exponential backoff for rate limiting (T033).

        Args:
            method: HTTP method (GET, POST)
            url: Request URL
            data: Request body data (for POST)
            headers: Request headers
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry

        Returns:
            dict: JSON response

        Raises:
            requests.exceptions.RequestException: If all retries exhausted
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                if method == "POST":
                    response = requests.post(
                        url, data=data, headers=headers, timeout=10
                    )
                else:
                    response = requests.get(url, headers=headers, timeout=10)

                # Handle rate limiting (HTTP 429)
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        delay = float(retry_after)
                    logger.warning(
                        "Basecamp rate limit hit (429) | attempt=%d/%d | retry_after=%s",
                        attempt + 1,
                        max_retries + 1,
                        delay,
                    )
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                    raise requests.exceptions.HTTPError(
                        "Rate limit exceeded", response=response
                    )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(
                        "Basecamp API request failed | attempt=%d/%d | error=%s | retrying in %ss",
                        attempt + 1,
                        max_retries + 1,
                        str(e),
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        "Basecamp API request failed after %d attempts | error=%s",
                        max_retries + 1,
                        str(e),
                    )

        raise last_exception


def create_basecamp_auth(user) -> CloudAuthentication:
    """Create Basecamp OAuth authentication service.

    Args:
        user: Django user instance

    Returns:
        CloudAuthentication: Basecamp OAuth auth service
    """
    return BasecampOAuthAuth(user)
