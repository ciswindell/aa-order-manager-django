"""
Basecamp Configuration Helpers

Configuration utilities for Basecamp OAuth credentials and settings.
Mirrors the pattern used for Dropbox integration.
"""

from django.conf import settings


def get_basecamp_app_key() -> str:
    """Get Basecamp OAuth client ID (app key).

    Returns:
        str: Basecamp app key from settings

    Raises:
        ValueError: If BASECAMP_APP_KEY is not configured
    """
    app_key = getattr(settings, "BASECAMP_APP_KEY", "")
    if not app_key:
        raise ValueError(
            "BASECAMP_APP_KEY not configured. Set in environment or Django settings."
        )
    return app_key


def get_basecamp_app_secret() -> str:
    """Get Basecamp OAuth client secret (app secret).

    Returns:
        str: Basecamp app secret from settings

    Raises:
        ValueError: If BASECAMP_APP_SECRET is not configured
    """
    app_secret = getattr(settings, "BASECAMP_APP_SECRET", "")
    if not app_secret:
        raise ValueError(
            "BASECAMP_APP_SECRET not configured. Set in environment or Django settings."
        )
    return app_secret


def get_redirect_uri() -> str:
    """Get Basecamp OAuth redirect URI.

    Returns:
        str: Redirect URI from settings or default value
    """
    return getattr(
        settings,
        "BASECAMP_OAUTH_REDIRECT_URI",
        "http://localhost:8000/api/integrations/basecamp/callback/",
    )


def is_configured() -> bool:
    """Check if Basecamp OAuth is properly configured.

    Returns:
        bool: True if both app key and secret are set
    """
    try:
        get_basecamp_app_key()
        get_basecamp_app_secret()
        return True
    except ValueError:
        return False
