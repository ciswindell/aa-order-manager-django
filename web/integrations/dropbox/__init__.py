"""
Dropbox integration package.

Lazily exposes selected symbols to avoid importing Django models or third-party
SDKs during test discovery when this package is imported under a different
module path.
"""

from typing import Any

__all__ = [
    "create_dropbox_auth",
    "DropboxTokenAuth",
    "DropboxOAuthAuth",
    "DropboxCloudService",
]


def __getattr__(name: str) -> Any:
    if name in {"create_dropbox_auth", "DropboxTokenAuth", "DropboxOAuthAuth"}:
        from .auth import (
            create_dropbox_auth as _create_dropbox_auth,
            DropboxTokenAuth as _DropboxTokenAuth,
            DropboxOAuthAuth as _DropboxOAuthAuth,
        )

        globals().update(
            {
                "create_dropbox_auth": _create_dropbox_auth,
                "DropboxTokenAuth": _DropboxTokenAuth,
                "DropboxOAuthAuth": _DropboxOAuthAuth,
            }
        )
        return globals()[name]

    if name == "DropboxCloudService":
        from .dropbox_service import DropboxCloudService as _DropboxCloudService

        globals().update({"DropboxCloudService": _DropboxCloudService})
        return globals()[name]

    raise AttributeError(name)
