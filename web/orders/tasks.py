"""
Celery tasks for the orders app.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from orders.repositories import LeaseRepository
from orders.services.lease.runsheet_discovery import (
    FullRunsheetDiscoveryWorkflow,
    RunsheetDiscoveryWorkflow,
)
from orders.services.lease.runsheet_report_detector import PreviousReportDetector

from integrations.cloud.errors import CloudServiceError
from integrations.cloud.factory import get_cloud_service

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=90,
    time_limit=120,
    ignore_result=True,
)
def runsheet_archive_search_task(self, lease_id: int, user_id: int) -> dict:
    """Task: run runsheet archive search with retry/backoff on cloud errors."""
    logger.info(
        "runsheet_archive_search_task start lease_id=%s user_id=%s", lease_id, user_id
    )
    workflow = RunsheetDiscoveryWorkflow()
    return workflow.execute(lease_id, user_id)


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=90,
    time_limit=120,
    ignore_result=True,
)
def previous_report_detection_task(self, lease_id: int, user_id: int) -> dict:
    """Task: run previous report detection; safe to re-run; retries on cloud errors only."""
    logger.info(
        "previous_report_detection_task start lease_id=%s user_id=%s", lease_id, user_id
    )

    # Initialize services
    repository = LeaseRepository()
    detector = PreviousReportDetector()

    # Load lease and user
    lease = repository.get_lease(lease_id)
    user = User.objects.get(id=user_id)

    # Skip if no runsheet archive
    if not lease.runsheet_archive:
        logger.info("No runsheet archive for lease %s, skipping detection", lease_id)
        return {"found": False, "matching_files": []}

    # Get authenticated cloud service
    cloud_service = get_cloud_service(provider="dropbox", user=user)
    try:
        cloud_service.authenticate()
    except Exception:
        pass

    if not cloud_service.is_authenticated():
        raise CloudServiceError("Dropbox client is not authenticated", "dropbox")

    # Detect previous reports
    directory_path = lease.runsheet_archive.path
    detection_result = detector.detect_reports(directory_path, cloud_service)

    # Update lease
    repository.update_runsheet_report_found(lease, detection_result.found)

    return {
        "found": detection_result.found,
        "matching_files": detection_result.matching_files,
    }


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=90,
    time_limit=120,
    ignore_result=True,
)
def full_runsheet_discovery_task(self, lease_id: int, user_id: int) -> dict:
    """Run search then, if found, detection. Returns a summary dict."""
    logger.info(
        "full_runsheet_discovery_task start lease_id=%s user_id=%s", lease_id, user_id
    )
    workflow = FullRunsheetDiscoveryWorkflow()
    return workflow.execute(lease_id, user_id)
