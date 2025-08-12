"""
Cloud Service Factory

Factory for creating cloud-agnostic service instances based on configuration.
"""

import logging
import os


from .protocols import CloudOperations
from .errors import CloudServiceError
from . import config
from ..dropbox.dropbox_service import DropboxCloudService

logger = logging.getLogger(__name__)


class CloudServiceFactory:
    """Factory for creating cloud service instances."""

    @classmethod
    def create_service(cls, provider: str = None, user=None) -> CloudOperations:
        """
        Create a cloud service instance based on provider configuration.

        Args:
            provider: Cloud provider name. If None, uses config.get_cloud_provider()

        Returns:
            CloudOperations: Cloud service implementing all required protocols

        Raises:
            CloudServiceError: If provider is not supported or service creation fails
        """
        provider = provider or config.get_cloud_provider()

        try:
            if provider.lower() == "dropbox":
                return cls._create_dropbox_service(user=user)
            else:
                raise CloudServiceError(
                    f"Unsupported cloud provider: {provider}", provider
                )

        except Exception as e:
            logger.error(
                "Failed to create cloud service for provider '%s': %s", provider, e
            )
            raise CloudServiceError(
                f"Service creation failed: {str(e)}", provider
            ) from e

    @classmethod
    def _create_dropbox_service(cls, user=None) -> CloudOperations:
        """Create Dropbox cloud service instance."""
        # Create and return cloud service bound to user
        return DropboxCloudService(auth_type=config.get_dropbox_auth_type(), user=user)

    @classmethod
    def get_dropbox_config(cls) -> dict:
        """Get Dropbox-specific configuration."""
        return {
            "auth_type": config.get_dropbox_auth_type(),
            "access_token": config.get_dropbox_access_token(),
            "app_key": os.getenv("DROPBOX_APP_KEY", ""),
            "app_secret": os.getenv("DROPBOX_APP_SECRET", ""),
        }


def get_cloud_service(provider: str = None, user=None) -> CloudOperations:
    """
    Helper function to get configured cloud service instance.

    Args:
        provider: Cloud provider name. If None, uses config.get_cloud_provider()

    Returns:
        CloudOperations: Configured cloud service instance
    """
    return CloudServiceFactory.create_service(provider, user=user)
