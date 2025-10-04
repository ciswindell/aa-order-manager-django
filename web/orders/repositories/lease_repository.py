"""
Repository for Lease model data access operations.

This module provides a clean data access layer for Lease database operations,
separating data access from business logic.
"""

import logging

from orders.models import Lease

from integrations.models import CloudLocation

logger = logging.getLogger(__name__)


class LeaseRepository:
    """
    Repository class for Lease model database operations.

    This class handles all database operations for the Lease model,
    following the repository pattern to provide a clean separation
    between data access and business logic.
    """

    @staticmethod
    def get_lease(lease_id: int) -> Lease:
        """
        Retrieve a lease by ID.

        Args:
            lease_id: The ID of the lease to retrieve

        Returns:
            The Lease instance

        Raises:
            Lease.DoesNotExist: If no lease with the given ID exists
        """
        logger.debug("Retrieving lease with ID: %s", lease_id)
        lease = Lease.objects.get(id=lease_id)
        logger.debug("Retrieved lease: %s %s", lease.agency, lease.lease_number)
        return lease

    @staticmethod
    def update_runsheet_archive(
        lease: Lease, cloud_location: CloudLocation, share_url: str
    ) -> None:
        """
        Update lease with runsheet archive information.

        Args:
            lease: The lease to update
            cloud_location: The CloudLocation instance for the archive
            share_url: The shareable URL for the archive

        Returns:
            None
        """
        logger.info(
            "Updating lease %s with runsheet archive: %s",
            lease.lease_number,
            cloud_location.path,
        )
        lease.runsheet_archive = cloud_location
        lease.runsheet_link = share_url
        lease.save(update_fields=["runsheet_archive", "runsheet_link"])
        logger.debug("Successfully updated lease runsheet archive")

    @staticmethod
    def update_runsheet_report_found(lease: Lease, found: bool) -> None:
        """
        Update the runsheet_report_found flag for a lease.

        Args:
            lease: The lease to update
            found: Whether a previous report was found

        Returns:
            None
        """
        logger.info(
            "Updating lease %s runsheet_report_found to: %s",
            lease.lease_number,
            found,
        )
        lease.runsheet_report_found = found
        lease.save(update_fields=["runsheet_report_found"])
        logger.debug("Successfully updated runsheet_report_found flag")

    @staticmethod
    def create_or_update_cloud_location(
        provider: str, path: str, defaults: dict
    ) -> tuple[CloudLocation, bool]:
        """
        Create or update a CloudLocation record.

        Args:
            provider: The cloud provider (e.g., "dropbox")
            path: The path to the cloud resource
            defaults: Dictionary of field values to set on creation or update

        Returns:
            Tuple of (CloudLocation instance, created boolean)
            created is True if a new record was created, False if updated
        """
        logger.debug(
            "Creating or updating CloudLocation: provider=%s, path=%s", provider, path
        )
        cloud_location, created = CloudLocation.objects.update_or_create(
            provider=provider, path=path, defaults=defaults
        )
        action = "Created" if created else "Updated"
        logger.info("%s CloudLocation (ID: %s) for %s", action, cloud_location.id, path)
        return cloud_location, created
