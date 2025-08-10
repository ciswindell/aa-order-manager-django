"""
Cloud-agnostic service integration package.

This package provides cloud-agnostic interfaces and implementations for
various cloud storage providers (Dropbox, Google Drive, etc.).
"""

from .models import CloudFile, ShareLink
from .protocols import CloudAuthentication, CloudOperations
from .errors import CloudServiceError, CloudAuthError, CloudNotFoundError

__all__ = [
    "CloudFile",
    "ShareLink", 
    "CloudAuthentication",
    "CloudOperations",
    "CloudServiceError",
    "CloudAuthError",
    "CloudNotFoundError",
] 