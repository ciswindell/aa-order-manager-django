from __future__ import annotations

import os
from typing import Optional

from django.conf import settings


def get_cloud_provider() -> str:
    """Return current cloud provider name (default: 'dropbox')."""
    return getattr(settings, "CLOUD_PROVIDER", os.getenv("CLOUD_PROVIDER", "dropbox"))


def get_dropbox_auth_type() -> str:
    """Return configured Dropbox auth type (default: 'oauth')."""
    return getattr(
        settings, "DROPBOX_AUTH_TYPE", os.getenv("DROPBOX_AUTH_TYPE", "oauth")
    )


def get_dropbox_access_token() -> Optional[str]:
    """Return legacy token if set (unused in runtime)."""
    return getattr(settings, "DROPBOX_ACCESS_TOKEN", os.getenv("DROPBOX_ACCESS_TOKEN"))


def get_dropbox_app_key() -> Optional[str]:
    """Return Dropbox app key from settings/env."""
    return getattr(settings, "DROPBOX_APP_KEY", os.getenv("DROPBOX_APP_KEY"))


def get_dropbox_app_secret() -> Optional[str]:
    """Return Dropbox app secret from settings/env."""
    return getattr(settings, "DROPBOX_APP_SECRET", os.getenv("DROPBOX_APP_SECRET"))


def get_dropbox_redirect_uri() -> Optional[str]:
    """Return configured Dropbox OAuth redirect URI."""
    return getattr(settings, "DROPBOX_REDIRECT_URI", os.getenv("DROPBOX_REDIRECT_URI"))
