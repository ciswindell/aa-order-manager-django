## PRD — Orders Background Tasks Hardening (Minimal, High‑Value)

### 1) Introduction / Overview
Harden the Django Orders app background tasks with minimal, targeted changes to improve reliability, simplicity, and production safety. Focus on delivery guarantees, timeouts, retries, result storage, logging, and duplicate enqueues, without broader refactors.

### 2) Goals
- Ensure at‑least‑once execution with no lost in‑flight tasks on worker crash.
- Bound task runtime to avoid hangs on cloud calls.
- Retry only transient cloud errors; fail fast on unexpected bugs.
- Reduce Redis overhead by not storing unused task results.
- Avoid duplicate enqueues for the same `lease_id` shortly after one another.
- Keep configuration simple and local to tasks.

### 3) User Stories
- As an operator, I want tasks to complete even if a worker restarts so that work isn’t lost.
- As a developer, I want non‑transient errors to fail fast so issues surface quickly rather than retrying endlessly.
- As a user, I don’t want multiple duplicate jobs started for the same lease when I save repeatedly.

### 4) Functional Requirements
1. Task delivery/limits
   1.1. Configure each Orders task (`lease_directory_search_task`, `previous_report_detection_task`, `full_runsheet_discovery_task`) with:
       - `acks_late=True`
       - `reject_on_worker_lost=True`
       - `soft_time_limit=90` seconds
       - `time_limit=120` seconds
       - `ignore_result=True`
2. Retry configuration
   2.1. Keep retry/backoff configuration only in the task decorators; remove overlapping global annotations for these tasks.
   2.2. Continue retrying on `CloudServiceError` with exponential backoff; keep existing max backoff and max retries.
3. Exception mapping scope
   3.1. In services, do not convert unexpected exceptions into `CloudServiceError`.
   3.2. Only raise `CloudServiceError` for transient/auth/network cloud issues; let unexpected errors propagate to fail the task without retry.
4. Logging
   4.1. Use `get_task_logger(__name__)` within tasks for consistent task‑context logs.
   4.2. Include `lease_id` and `user_id` in all task log messages.
5. Duplicate enqueue guard
   5.1. Before enqueuing from the `Lease` `post_save` signal, apply a lightweight deduplication guard that is global per `lease_id` (regardless of user) so that only one task is queued for a given lease within a short window.
   5.2. Implement guard via a single Redis `SETNX` style lock key per `lease_id` with a TTL of 120 seconds; if the lock exists, skip enqueue.
   5.3. The guard must be best‑effort; do not block saves if Redis is unavailable.
6. Production DB
   6.1. Production uses Postgres; keep `transaction.on_commit` for enqueue to minimize lock contention.

### 5) Non‑Goals (Out of Scope)
- No changes to task business logic in services beyond exception mapping.
- No new queues, routing changes, or rate limiting.
- No dashboards, metrics pipelines, or tracing systems.
- No architectural refactors (e.g., chords/chains) or cross‑service orchestration changes.

### 6) Design Considerations (Optional)
- Dedup lock can reuse the Redis broker connection or a small standalone Redis client; failure to acquire or set the key should not raise errors in the request path.
- Keep decorator‑based configuration to make per‑task defaults explicit and discoverable.

### 7) Technical Considerations (Optional)
- Environment toggles (optional):
  - `ORDERS_TASK_SOFT_TIME_LIMIT` (default 90)
  - `ORDERS_TASK_TIME_LIMIT` (default 120)
  - `ORDERS_TASK_DEDUP_TTL` (default 120)
- Logging format should remain consistent with existing project logging.

### 8) Success Metrics
- Duplicate enqueues for the same lease within 2 minutes are eliminated across all users in normal operation.
- No lost work on worker crash; tasks resume after restart.
- Task failures are predominantly non‑transient bugs; transient cloud issues resolve via retries.
- Redis memory usage decreases due to ignored results.

### 9) Open Questions
- None at this time.


