"""
Celery tasks for the orders app.
"""

from celery import shared_task
from celery.utils.log import get_task_logger

from integrations.cloud.errors import CloudServiceError
from orders.services.runsheet_archive_search import run_runsheet_archive_search
from orders.services.previous_report_detection import run_previous_report_detection

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
    return run_runsheet_archive_search(lease_id, user_id)


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
    return run_previous_report_detection(lease_id, user_id)


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
    search_result = run_runsheet_archive_search(lease_id, user_id)
    detection_result: dict | None = None
    if search_result.get("found"):
        detection_result = run_previous_report_detection(lease_id, user_id)
    return {
        "search": search_result,
        "detection": detection_result,
    }
