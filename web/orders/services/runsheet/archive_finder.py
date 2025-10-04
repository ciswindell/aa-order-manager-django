"""
Runsheet Archive Finder Service.

This service searches for existing runsheet archives in cloud storage
and creates shareable links.
"""

import logging
from typing import Any

from orders.models import Lease
from orders.repositories import LeaseRepository
from orders.services.runsheet.results import ArchiveSearchResult

from integrations.cloud.errors import CloudServiceError
from integrations.models import AgencyStorageConfig

logger = logging.getLogger(__name__)


class RunsheetArchiveFinder:
    """
    Service to find existing runsheet archives in cloud storage.

    This service checks if a runsheet archive directory exists for a lease,
    creates a shareable link if found, and returns structured results.
    Does NOT create directories or update the database.
    """

    def __init__(self, repository: LeaseRepository = None):
        """
        Initialize RunsheetArchiveFinder.

        Args:
            repository: LeaseRepository instance (defaults to LeaseRepository)
        """
        self.repository = repository or LeaseRepository()

    def find_archive(
        self, lease: Lease, cloud_service: Any, config: AgencyStorageConfig
    ) -> ArchiveSearchResult:
        """
        Search for an existing runsheet archive in cloud storage.

        Args:
            lease: The lease to search for
            cloud_service: Authenticated cloud service instance
            config: Agency storage configuration

        Returns:
            ArchiveSearchResult with search results

        Raises:
            CloudServiceError: If cloud operations fail (retryable)
        """
        # Build directory path
        directory_path = f"{config.runsheet_archive_base_path}/{lease.lease_number}"
        logger.info("Searching for runsheet archive at: %s", directory_path)

        try:
            # Check if directory exists by listing files
            files = cloud_service.list_files(directory_path)

            if not files:
                logger.info("Runsheet archive not found at: %s", directory_path)
                return ArchiveSearchResult(
                    found=False,
                    path=directory_path,
                    share_url=None,
                    cloud_location=None,
                )

            # Directory exists, create share link
            logger.info("Runsheet archive found, creating share link")
            share_link = cloud_service.create_share_link(directory_path, is_public=True)

            if not share_link:
                logger.warning(
                    "Failed to create share link for directory: %s", directory_path
                )
                return ArchiveSearchResult(
                    found=True, path=directory_path, share_url=None, cloud_location=None
                )

            # Create or update CloudLocation
            cloud_location, created = self.repository.create_or_update_cloud_location(
                provider="dropbox",
                path=directory_path,
                defaults={
                    "name": lease.lease_number,
                    "is_directory": True,
                    "share_url": share_link.url,
                    "share_expires_at": share_link.expires_at,
                    "is_public": share_link.is_public,
                },
            )

            action = "created" if created else "updated"
            logger.info(
                "Successfully %s share link for runsheet archive. Location ID: %s",
                action,
                cloud_location.id,
            )

            return ArchiveSearchResult(
                found=True,
                path=directory_path,
                share_url=share_link.url,
                cloud_location=cloud_location,
            )

        except CloudServiceError:
            logger.error(
                "Cloud service error while searching for archive at: %s", directory_path
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error while searching for archive at %s: %s",
                directory_path,
                str(e),
            )
            raise CloudServiceError(
                f"Failed to search for archive: {str(e)}", "dropbox"
            )
