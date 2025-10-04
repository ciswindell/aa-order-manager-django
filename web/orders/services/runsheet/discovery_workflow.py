"""
Runsheet Discovery Workflows.

These workflows orchestrate the runsheet archive discovery process,
composing domain services to complete the full business logic.
"""

import logging
from typing import Any, Dict

from django.contrib.auth.models import User
from orders.repositories import LeaseRepository
from orders.services.runsheet.archive_creator import RunsheetArchiveCreator
from orders.services.runsheet.archive_finder import RunsheetArchiveFinder
from orders.services.runsheet.report_detector import PreviousReportDetector

from integrations.cloud.errors import CloudServiceError
from integrations.cloud.factory import get_cloud_service
from integrations.utils import get_agency_storage_config

logger = logging.getLogger(__name__)


class RunsheetDiscoveryWorkflow:
    """
    Workflow to discover or create runsheet archives.

    This workflow orchestrates the archive search and optional creation process,
    updating the lease record with the results.
    """

    def __init__(
        self,
        repository: LeaseRepository = None,
        finder: RunsheetArchiveFinder = None,
        creator: RunsheetArchiveCreator = None,
    ):
        """
        Initialize RunsheetDiscoveryWorkflow.

        Args:
            repository: LeaseRepository instance
            finder: RunsheetArchiveFinder instance
            creator: RunsheetArchiveCreator instance
        """
        self.repository = repository or LeaseRepository()
        self.finder = finder or RunsheetArchiveFinder(repository=self.repository)
        self.creator = creator or RunsheetArchiveCreator(repository=self.repository)

    def execute(self, lease_id: int, user_id: int) -> Dict[str, Any]:
        """
        Execute the runsheet discovery workflow.

        Args:
            lease_id: ID of the lease to process
            user_id: ID of the user (for cloud authentication)

        Returns:
            Dict with keys: found, path, share_url, location_id

        Raises:
            Lease.DoesNotExist: If lease not found
            User.DoesNotExist: If user not found
            AgencyStorageConfigError: If agency config missing/disabled
            CloudServiceError: If cloud operations fail
        """
        logger.info(
            "Starting runsheet discovery workflow for lease_id=%s user_id=%s",
            lease_id,
            user_id,
        )

        # Load lease and user
        lease = self.repository.get_lease(lease_id)
        user = User.objects.get(id=user_id)

        # Get agency config
        agency_config = get_agency_storage_config(lease.agency)

        # Get authenticated cloud service
        cloud_service = get_cloud_service(provider="dropbox", user=user)

        # Authenticate
        try:
            cloud_service.authenticate()
        except Exception:
            pass  # Fallback to state check even if authenticate() is a no-op

        if not cloud_service.is_authenticated():
            raise CloudServiceError("Dropbox client is not authenticated", "dropbox")

        # Try to find existing archive
        logger.info("Searching for existing runsheet archive")
        search_result = self.finder.find_archive(lease, cloud_service, agency_config)

        if search_result.found:
            # Archive found - update lease
            logger.info("Runsheet archive found, updating lease")
            self.repository.update_runsheet_archive(
                lease, search_result.cloud_location, search_result.share_url
            )

            return {
                "found": True,
                "path": search_result.path,
                "share_url": search_result.share_url,
                "location_id": search_result.cloud_location.id,
            }

        # Archive not found - check if we should auto-create
        if not getattr(agency_config, "auto_create_runsheet_archives", False):
            logger.info(
                "Runsheet archive not found and auto-create disabled for %s",
                lease.agency,
            )
            return {
                "found": False,
                "path": search_result.path,
                "share_url": None,
                "location_id": None,
            }

        # Auto-create the archive
        logger.info("Runsheet archive not found, attempting to create")
        creation_result = self.creator.create_archive(
            lease, cloud_service, agency_config
        )

        if not creation_result.success:
            logger.warning("Failed to create runsheet archive")
            return {
                "found": False,
                "path": creation_result.path,
                "share_url": None,
                "location_id": None,
            }

        # Archive created - update lease
        logger.info("Runsheet archive created successfully, updating lease")
        self.repository.update_runsheet_archive(
            lease, creation_result.cloud_location, creation_result.share_url
        )

        return {
            "found": True,
            "path": creation_result.path,
            "share_url": creation_result.share_url,
            "location_id": creation_result.cloud_location.id,
        }


class FullRunsheetDiscoveryWorkflow:
    """
    Full workflow for runsheet discovery including previous report detection.

    This workflow orchestrates both archive discovery/creation and previous
    report detection, updating the lease with all results.
    """

    def __init__(
        self,
        repository: LeaseRepository = None,
        discovery_workflow: RunsheetDiscoveryWorkflow = None,
        detector: PreviousReportDetector = None,
    ):
        """
        Initialize FullRunsheetDiscoveryWorkflow.

        Args:
            repository: LeaseRepository instance
            discovery_workflow: RunsheetDiscoveryWorkflow instance
            detector: PreviousReportDetector instance
        """
        self.repository = repository or LeaseRepository()
        self.discovery_workflow = discovery_workflow or RunsheetDiscoveryWorkflow(
            repository=self.repository
        )
        self.detector = detector or PreviousReportDetector()

    def execute(self, lease_id: int, user_id: int) -> Dict[str, Any]:
        """
        Execute the full runsheet discovery workflow.

        Args:
            lease_id: ID of the lease to process
            user_id: ID of the user (for cloud authentication)

        Returns:
            Dict with keys: search (dict), detection (dict or None)

        Raises:
            Lease.DoesNotExist: If lease not found
            User.DoesNotExist: If user not found
            AgencyStorageConfigError: If agency config missing/disabled
            CloudServiceError: If cloud operations fail
        """
        logger.info(
            "Starting full runsheet discovery workflow for lease_id=%s user_id=%s",
            lease_id,
            user_id,
        )

        # Run archive discovery workflow
        search_result = self.discovery_workflow.execute(lease_id, user_id)

        # If archive not found/created, skip detection
        if not search_result.get("found"):
            logger.info(
                "Runsheet archive not found, skipping previous report detection"
            )
            return {"search": search_result, "detection": None}

        # Run previous report detection
        logger.info("Running previous report detection")
        lease = self.repository.get_lease(lease_id)
        user = User.objects.get(id=user_id)

        # Get authenticated cloud service
        cloud_service = get_cloud_service(provider="dropbox", user=user)

        try:
            cloud_service.authenticate()
        except Exception:
            pass

        if not cloud_service.is_authenticated():
            raise CloudServiceError("Dropbox client is not authenticated", "dropbox")

        # Detect previous reports
        directory_path = search_result["path"]
        detection_result = self.detector.detect_reports(directory_path, cloud_service)

        # Update lease with detection result
        logger.info(
            "Updating lease with detection result: found=%s", detection_result.found
        )
        self.repository.update_runsheet_report_found(lease, detection_result.found)

        return {
            "search": search_result,
            "detection": {
                "found": detection_result.found,
                "matching_files": detection_result.matching_files,
            },
        }
