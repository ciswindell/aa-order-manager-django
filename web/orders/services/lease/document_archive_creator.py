"""
Document Archive Creator Service.

This service creates new document archive directories in cloud storage
with configured subfolders and shareable links.
"""

import logging
from typing import Any, List

from orders.models import Lease
from orders.repositories import DocumentImagesLinkRepository
from orders.services.lease.runsheet_exceptions import (
    BasePathMissingError,
    DirectoryCreationError,
)
from orders.services.lease.runsheet_results import ArchiveCreationResult

from integrations.cloud.errors import CloudServiceError
from integrations.models import AgencyStorageConfig

logger = logging.getLogger(__name__)


class DocumentArchiveCreator:
    """
    Service to create new document archive directories.

    This service creates a directory structure for a lease's document archive,
    including configured subfolders, and generates a shareable link.
    Does NOT update lease records.
    """

    def __init__(self, repository: DocumentImagesLinkRepository = None):
        """
        Initialize DocumentArchiveCreator.

        Args:
            repository: DocumentImagesLinkRepository instance (defaults to DocumentImagesLinkRepository)
        """
        self.repository = repository or DocumentImagesLinkRepository()

    def create_archive(
        self, lease: Lease, cloud_service: Any, config: AgencyStorageConfig
    ) -> ArchiveCreationResult:
        """
        Create a new document archive directory with subfolders.

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
        directory_path = f"{config.documents_base_path}/{lease.lease_number}"
        base_path = config.documents_base_path

        logger.info("Attempting to create document archive at: %s", directory_path)

        if not self._base_path_exists(cloud_service, base_path):
            logger.error("Base path does not exist: %s", base_path)
            raise BasePathMissingError(base_path)

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
            logger.debug("Creating main directory: %s", directory_path)
            created_dir = cloud_service.create_directory(directory_path, parents=True)

            if not created_dir:
                raise DirectoryCreationError(
                    directory_path, "create_directory returned False"
                )

            logger.debug("Creating subfolders: %s", subfolders)
            cloud_service.create_directory_tree(
                directory_path, subfolders, exists_ok=True
            )

            logger.debug("Creating share link for: %s", directory_path)
            share_link = cloud_service.create_share_link(directory_path, is_public=True)

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
                "Successfully created document archive and subfolders for %s",
                lease.lease_number,
            )

            return ArchiveCreationResult(
                success=True,
                path=directory_path,
                share_url=share_link.url if share_link else None,
                cloud_location=cloud_location,
            )

        except (CloudServiceError, DirectoryCreationError):
            raise
        except Exception as e:
            logger.error(
                "Unexpected error creating document archive at %s: %s",
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
                getattr(config, "document_subfolder_agency_sourced_documents", None),
                getattr(config, "document_subfolder_unknown_sourced_documents", None),
            ]
            if f
        ]
        logger.debug("Extracted subfolders from config: %s", subfolders)
        return subfolders
