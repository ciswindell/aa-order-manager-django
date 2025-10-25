"""
Repository for DocumentImagesLink model data access operations.

This module provides a clean data access layer for DocumentImagesLink database operations,
separating data access from business logic.
"""

import logging

from orders.models import DocumentImagesLink, Lease

from integrations.models import CloudLocation

logger = logging.getLogger(__name__)


class DocumentImagesLinkRepository:
    """
    Repository class for DocumentImagesLink model database operations.

    This class handles all database operations for the DocumentImagesLink model,
    following the repository pattern to provide a clean separation
    between data access and business logic.
    """

    @staticmethod
    def create_or_update_for_lease(lease: Lease, share_url: str) -> DocumentImagesLink:
        """
        Create or update the first DocumentImagesLink for a lease.

        Gets the first DocumentImagesLink for the lease or creates a new one,
        then updates its URL field.

        Args:
            lease: The lease to create/update a document link for
            share_url: The shareable URL for the document archive

        Returns:
            The DocumentImagesLink instance
        """
        logger.info(
            "Creating or updating document link for lease %s",
            lease.lease_number,
        )
        doc_link = lease.document_images_links.first()
        if doc_link:
            logger.debug(
                "Updating existing DocumentImagesLink ID: %s with URL: %s",
                doc_link.id,
                share_url,
            )
            doc_link.url = share_url
            doc_link.save(update_fields=["url"])
            logger.info("Updated DocumentImagesLink ID: %s", doc_link.id)
        else:
            logger.debug("Creating new DocumentImagesLink with URL: %s", share_url)
            doc_link = DocumentImagesLink.objects.create(lease=lease, url=share_url)
            logger.info("Created new DocumentImagesLink ID: %s", doc_link.id)
        return doc_link

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
