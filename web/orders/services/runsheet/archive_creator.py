"""
Runsheet Archive Creator Service.

This service creates new runsheet archive directories in cloud storage
with configured subfolders and shareable links.
"""

import logging
from typing import Any, List

from orders.models import Lease
from orders.repositories import LeaseRepository
from orders.services.runsheet.exceptions import (
    BasePathMissingError,
    DirectoryCreationError,
)
from orders.services.runsheet.results import ArchiveCreationResult

from integrations.cloud.errors import CloudServiceError
from integrations.models import AgencyStorageConfig

logger = logging.getLogger(__name__)


class RunsheetArchiveCreator:
    """
    Service to create new runsheet archive directories.

    This service creates a directory structure for a lease's runsheet archive,
    including configured subfolders, and generates a shareable link.
    Does NOT update lease records.
    """

    def __init__(self, repository: LeaseRepository = None):
        """
        Initialize RunsheetArchiveCreator.

        Args:
            repository: LeaseRepository instance (defaults to LeaseRepository)
        """
        self.repository = repository or LeaseRepository()

    def create_archive(
        self, lease: Lease, cloud_service: Any, config: AgencyStorageConfig
    ) -> ArchiveCreationResult:
        """
        Create a new runsheet archive directory with subfolders.

        Args:
            lease: The lease to create archive for
            cloud_service: Authenticated cloud service instance
            config: Agency storage configuration

        Returns:
            ArchiveCreationResult with creation results

        Raises:
            BasePathMissingError: If base path doesn't exist (non-retryable)
            DirectoryCreationError: If directory creation fails (retryable)
            CloudServiceError: If cloud operations fail (retryable)
        """
        # Build directory path
        directory_path = f"{config.runsheet_archive_base_path}/{lease.lease_number}"
        base_path = config.runsheet_archive_base_path

        logger.info("Attempting to create runsheet archive at: %s", directory_path)

        # Verify base path exists
        if not self._base_path_exists(cloud_service, base_path):
            logger.error("Base path does not exist: %s", base_path)
            raise BasePathMissingError(base_path)

        # Extract subfolder names from config
        subfolders = self._get_subfolders(config)

        if not subfolders:
            logger.warning(
                "No subfolders configured for %s, skipping directory creation",
                lease.agency,
            )
            return ArchiveCreationResult(
                success=False,
                path=directory_path,
                share_url=None,
                cloud_location=None,
            )

        try:
            # Create main directory
            logger.debug("Creating main directory: %s", directory_path)
            created_dir = cloud_service.create_directory(directory_path, parents=True)

            if not created_dir:
                raise DirectoryCreationError(
                    directory_path, "create_directory returned False"
                )

            # Create subfolders
            logger.debug("Creating subfolders: %s", subfolders)
            cloud_service.create_directory_tree(
                directory_path, subfolders, exists_ok=True
            )

            # Create share link
            logger.debug("Creating share link for: %s", directory_path)
            share_link = cloud_service.create_share_link(directory_path, is_public=True)

            # Create or update CloudLocation
            defaults = {"name": lease.lease_number, "is_directory": True}

            if share_link:
                defaults.update(
                    {
                        "share_url": share_link.url,
                        "share_expires_at": getattr(share_link, "expires_at", None),
                        "is_public": share_link.is_public,
                    }
                )

            cloud_location, created = self.repository.create_or_update_cloud_location(
                provider="dropbox", path=directory_path, defaults=defaults
            )

            logger.info(
                "Successfully created runsheet archive and subfolders for %s",
                lease.lease_number,
            )

            return ArchiveCreationResult(
                success=True,
                path=directory_path,
                share_url=share_link.url if share_link else None,
                cloud_location=cloud_location,
            )

        except (CloudServiceError, DirectoryCreationError):
            # Let these propagate as-is
            raise
        except Exception as e:
            logger.error(
                "Unexpected error creating runsheet archive at %s: %s",
                directory_path,
                str(e),
            )
            raise DirectoryCreationError(directory_path, str(e))

    def _base_path_exists(self, cloud_service: Any, base_path: str) -> bool:
        """
        Check if the base path exists in cloud storage.

        Args:
            cloud_service: Authenticated cloud service instance
            base_path: The base path to check

        Returns:
            True if base path exists, False otherwise
        """
        try:
            md = cloud_service._get_metadata(base_path)  # type: ignore[attr-defined]
            return md is not None
        except Exception as e:
            logger.debug("Base path check failed for %s: %s", base_path, str(e))
            return False

    def _get_subfolders(self, config: AgencyStorageConfig) -> List[str]:
        """
        Extract subfolder names from agency configuration.

        Args:
            config: Agency storage configuration

        Returns:
            List of subfolder names (empty list if none configured)
        """
        subfolders = [
            f
            for f in [
                getattr(config, "runsheet_subfolder_documents_name", None),
                getattr(config, "runsheet_subfolder_misc_index_name", None),
                getattr(config, "runsheet_subfolder_runsheets_name", None),
            ]
            if f
        ]
        logger.debug("Extracted subfolders from config: %s", subfolders)
        return subfolders
