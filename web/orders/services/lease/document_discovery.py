"""
Document Archive Discovery Workflow.

This workflow orchestrates the document archive discovery process,
composing domain services to complete the full business logic.
"""

import logging
from typing import Any, Dict

from django.contrib.auth.models import User
from orders.models import Lease
from orders.repositories import DocumentImagesLinkRepository
from orders.services.lease.document_archive_creator import DocumentArchiveCreator
from orders.services.lease.document_archive_finder import DocumentArchiveFinder
from orders.services.lease.runsheet_exceptions import BasePathMissingError

from integrations.cloud.errors import CloudServiceError
from integrations.cloud.factory import get_cloud_service
from integrations.utils import get_agency_storage_config

logger = logging.getLogger(__name__)


class DocumentDiscoveryWorkflow:
    """
    Workflow to discover or create document archives.

    This workflow orchestrates the document archive search and optional creation process,
    updating the DocumentImagesLink record with the results.
    """

    def __init__(
        self,
        repository: DocumentImagesLinkRepository = None,
        finder: DocumentArchiveFinder = None,
        creator: DocumentArchiveCreator = None,
    ):
        """
        Initialize DocumentDiscoveryWorkflow.

        Args:
            repository: DocumentImagesLinkRepository instance
            finder: DocumentArchiveFinder instance
            creator: DocumentArchiveCreator instance
        """
        self.repository = repository or DocumentImagesLinkRepository()
        self.finder = finder or DocumentArchiveFinder(repository=self.repository)
        self.creator = creator or DocumentArchiveCreator(repository=self.repository)

    def execute(self, lease_id: int, user_id: int) -> Dict[str, Any]:
        """
        Execute the document discovery workflow.

        This method is best-effort and will not raise exceptions for missing config
        or failed operations. It logs errors and returns a result dict.

        Args:
            lease_id: ID of the lease to process
            user_id: ID of the user (for cloud authentication)

        Returns:
            Dict with keys: found, path, share_url, location_id, error (optional)
            Returns None if workflow cannot proceed (missing config, auth failure)
        """
        logger.info(
            "Starting document discovery workflow for lease_id=%s user_id=%s",
            lease_id,
            user_id,
        )

        try:
            # Load lease and user
            lease = Lease.objects.get(id=lease_id)
            user = User.objects.get(id=user_id)

            # Get agency config
            try:
                agency_config = get_agency_storage_config(lease.agency)
            except Exception as e:
                logger.warning(
                    "Failed to get agency config for %s: %s", lease.agency, str(e)
                )
                return None

            # Check if documents_base_path is configured
            if not agency_config.documents_base_path:
                logger.warning(
                    "documents_base_path not configured for %s, skipping document discovery",
                    lease.agency,
                )
                return None

            # Get authenticated cloud service
            try:
                cloud_service = get_cloud_service(provider="dropbox", user=user)
                cloud_service.authenticate()
            except Exception:
                pass

            if not cloud_service.is_authenticated():
                logger.error(
                    "Dropbox client is not authenticated for user %s", user.username
                )
                return None

            # Try to find existing archive
            logger.info("Searching for existing document archive")
            search_result = self.finder.find_archive(
                lease, cloud_service, agency_config
            )

            if search_result.found:
                # Archive found - update DocumentImagesLink
                logger.info("Document archive found, updating DocumentImagesLink")
                self.repository.create_or_update_for_lease(
                    lease, search_result.share_url
                )

                return {
                    "found": True,
                    "path": search_result.path,
                    "share_url": search_result.share_url,
                    "location_id": search_result.cloud_location.id,
                }

            # Archive not found - check if we should auto-create
            if not getattr(agency_config, "auto_create_document_archives", False):
                logger.info(
                    "Document archive not found and auto-create disabled for %s",
                    lease.agency,
                )
                return {
                    "found": False,
                    "path": search_result.path,
                    "share_url": None,
                    "location_id": None,
                }

            # Auto-create the archive
            logger.info("Document archive not found, attempting to create")
            creation_result = self.creator.create_archive(
                lease, cloud_service, agency_config
            )

            if not creation_result.success:
                logger.warning("Failed to create document archive")
                return {
                    "found": False,
                    "path": creation_result.path,
                    "share_url": None,
                    "location_id": None,
                }

            # Archive created - update DocumentImagesLink
            logger.info(
                "Document archive created successfully, updating DocumentImagesLink"
            )
            self.repository.create_or_update_for_lease(lease, creation_result.share_url)

            return {
                "found": True,
                "path": creation_result.path,
                "share_url": creation_result.share_url,
                "location_id": creation_result.cloud_location.id,
            }

        except BasePathMissingError as e:
            logger.warning("Base path missing for document archive: %s", str(e))
            return {"found": False, "error": "base_path_missing"}
        except CloudServiceError as e:
            logger.error("Cloud service error during document discovery: %s", str(e))
            return {"found": False, "error": "cloud_service_error"}
        except Exception as e:
            logger.error(
                "Unexpected error during document discovery for lease %s: %s",
                lease_id,
                str(e),
            )
            return {"found": False, "error": "unexpected_error"}
