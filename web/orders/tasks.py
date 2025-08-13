"""
Celery tasks for the orders app.
"""

from celery import shared_task

from integrations.cloud.errors import CloudServiceError
from orders.services.lease_directory_search import run_lease_directory_search
from orders.services.previous_report_detection import run_previous_report_detection


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def lease_directory_search_task(self, lease_id: int, user_id: int) -> dict:
    """Task: run lease directory search with retry/backoff on cloud errors."""
    return run_lease_directory_search(lease_id, user_id)


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def previous_report_detection_task(self, lease_id: int, user_id: int) -> dict:
    """Task: run previous report detection; safe to re-run; retries on cloud errors only."""
    return run_previous_report_detection(lease_id, user_id)


@shared_task(
    bind=True,
    autoretry_for=(CloudServiceError,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def full_runsheet_discovery_task(self, lease_id: int, user_id: int) -> dict:
    """Run search then, if found, detection. Returns a summary dict."""
    search_result = run_lease_directory_search(lease_id, user_id)
    detection_result: dict | None = None
    if search_result.get("found"):
        detection_result = run_previous_report_detection(lease_id, user_id)
    return {
        "search": search_result,
        "detection": detection_result,
    }
