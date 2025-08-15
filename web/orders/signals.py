"""
Signals for the orders app.
"""

import logging
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.conf import settings

import redis

from orders.models import Lease
from orders.tasks import full_runsheet_discovery_task
from orders.utils.current_user import get_current_user_id

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lease)
def enqueue_runsheet_discovery_on_save(
    sender, instance: Lease, created: bool, **kwargs
):
    """Enqueue full runsheet discovery when a Lease is created or updated.

    Skips when the only updated fields are ones written by background tasks
    to prevent enqueue loops.
    """
    update_fields = kwargs.get("update_fields")
    task_only_fields = {"runsheet_archive", "runsheet_report_found"}
    if update_fields:
        # If all updated fields are task-only fields, skip
        try:
            if set(update_fields).issubset(task_only_fields):
                return
        except TypeError:
            # update_fields may be a frozenset or iterable; coerce issues are ignored
            pass

    user_id = get_current_user_id()
    if user_id:
        # Avoid DB locking by enqueuing after the transaction commits
        def _enqueue():
            # Best-effort global dedup per lease_id using Redis SETNX with TTL
            try:
                broker_url = getattr(settings, "CELERY_BROKER_URL", "")
                if broker_url.startswith("redis://"):
                    client = redis.from_url(broker_url)
                    task_name = getattr(
                        full_runsheet_discovery_task,
                        "name",
                        "full_runsheet_discovery_task",
                    )
                    dedup_key = f"orders:dedup:task:{task_name}:lease:{instance.id}"
                    # TTL 120s per PRD
                    locked = client.set(name=dedup_key, value="1", nx=True, ex=120)
                    if not locked:
                        logger.info(
                            "Skipping enqueue due to dedup key present for lease %s",
                            instance.id,
                        )
                        return
            except Exception as dedup_exc:  # pragma: no cover
                # Best-effort: do not block enqueue on Redis issues
                logger.debug("Dedup check failed: %s", str(dedup_exc))

            try:
                full_runsheet_discovery_task.delay(instance.id, user_id)
                logger.info(
                    "Enqueued full runsheet discovery for lease %s (user_id=%s)",
                    instance.id,
                    user_id,
                )
            except Exception as exc:  # pragma: no cover
                # Never block admin save due to background enqueue failures (e.g., eager mode)
                logger.error(
                    "Failed to enqueue runsheet discovery for lease %s: %s",
                    instance.id,
                    str(exc),
                )

        transaction.on_commit(_enqueue)
    else:
        logger.info(
            "Lease save (id=%s) but no current user; skipping background discovery.",
            instance.id,
        )
