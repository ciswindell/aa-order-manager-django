## Relevant Files

- `web/orders/tasks.py` - Celery tasks to configure delivery semantics, time limits, retries, logging, and ignore results.
- `web/orders/signals.py` - Add global per-lease deduplication guard before enqueueing tasks.
- `web/order_manager_project/settings.py` - Remove overlapping Celery task annotations if keeping config only in decorators.
- `web/order_manager_project/celery.py` - Ensure autodiscovery; no functional change expected.
- `web/orders/services/lease_directory_search.py` - Narrow exception mapping to transient cloud errors only.
- `web/orders/services/previous_report_detection.py` - Same exception handling adjustment.
- `web/orders/tests/test_signals.py` - Tests for dedup behavior.
- `web/orders/tests/test_services.py` - Tests for exception mapping behavior.
- `web/orders/tests/test_tasks.py` - Tests asserting task options/logging do not break eager execution.

### Notes

- Place unit tests alongside the code under `web/orders/tests/`.
- Run tests with: `python3 web/manage.py test`.

## Tasks

- [x] 1.0 Configure task delivery semantics and limits in `web/orders/tasks.py`
  - [x] 1.1 Add `acks_late=True` and `reject_on_worker_lost=True` to each Orders task decorator.
  - [x] 1.2 Add `soft_time_limit=90` and `time_limit=120` (read from env overrides if present).
  - [x] 1.3 Add `ignore_result=True` to each Orders task decorator.
  - [x] 1.4 Switch to `get_task_logger(__name__)` and include `lease_id`/`user_id` context in task logs.

- [x] 2.0 Simplify retry/backoff configuration
  - [x] 2.1 Keep retry/backoff only in task decorators; remove overlapping `CELERY_TASK_ANNOTATIONS` for these tasks in `settings.py`.
  - [x] 2.2 Confirm `autoretry_for=(CloudServiceError,)` remains with backoff and max retries per PRD.

- [x] 3.0 Adjust exception mapping in services
  - [x] 3.1 In `lease_directory_search.py`, stop converting unexpected exceptions to `CloudServiceError`; only raise for transient/auth/network issues.
  - [x] 3.2 In `previous_report_detection.py`, apply the same change.

- [x] 4.0 Implement global per-lease deduplication guard in `web/orders/signals.py`
  - [x] 4.1 Use Redis `SETNX` with TTL (120s) keyed by `orders:dedup:lease:<lease_id>` to gate enqueue; if key exists, skip.
  - [x] 4.2 Make guard best-effort: on Redis errors, skip the guard and continue without blocking saves.
  - [x] 4.3 Keep `transaction.on_commit` around the enqueue to minimize DB lock contention.
  - [x] 4.4 Scope dedup to the specific task + lease (key: `orders:dedup:task:<task_name>:lease:<lease_id>`) so different tasks for the same lease can run concurrently.

- [x] 5.0 Tests and verification
  - [x] 5.1 `test_signals.py`: verify first save enqueues and second save within TTL does not; after TTL, enqueue resumes (use `fakeredis` or a Redis stub).
  - [x] 5.2 `test_services.py`: verify unexpected exceptions propagate (no wrapping); verify transient cloud exceptions surface as `CloudServiceError`.
  - [x] 5.3 `test_tasks.py`: verify tasks run in eager mode without requiring results; basic smoke test that logging path executes.
  - [x] 5.5 Remove conflicting `web/orders/tests.py` to fix Django discovery.
  - [x] 5.4 Run orders test suite and ensure green status locally.

- [x] 5.0 Tests and verification
  - [x] 5.4 Remove overlapping Celery annotations and ensure worker still starts cleanly in local dev.


