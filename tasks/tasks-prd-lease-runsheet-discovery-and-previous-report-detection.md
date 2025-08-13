## Relevant Files

- `web/orders/models.py` - Add `runsheet_report_found` and FK `runsheet_directory` to `CloudLocation`.
- `web/integrations/models.py` - Define `AgencyStorageConfig` and `CloudLocation` models; register in admin.
- `web/orders/services/lease_directory_search.py` - Service to resolve path, upsert `CloudLocation`, and set `Lease.runsheet_directory`.
- `web/orders/services/previous_report_detection.py` - Service to scan `runsheet_directory` and set boolean.
- `web/orders/tasks.py` - Celery tasks and chaining for workflows.
- `web/orders/signals.py` - Signal to enqueue Celery chain on `Lease` create.
- `web/integrations/cloud/factory.py` - Ensure user-bound Dropbox client retrieval used by services.
- `web/order_manager_project/settings.py` - Add `RUNSHEET_PREVIOUS_REPORT_PATTERN` setting.
- `web/integrations/admin.py` - Admin registration for `AgencyStorageConfig` and `CloudLocation`.

### Notes

- Keep workflows separate and idempotent; no admin actions for now.
- No fallbacks: missing `AgencyStorageConfig` or auth should fail (retriable for auth).
- Regex is global: `.*master documents.*` (case-insensitive).

## Tasks

- [x] 1.0 Data model updates and migrations
  - [x] 1.1 Create `CloudLocation` model in `web/integrations/models.py` with fields: `provider`, `path`, `name`, `is_directory`, `file_id`, `share_url`, `share_expires_at`, `is_public`, `size_bytes`, `modified_at`; unique on (`provider`, `path`); add indexes as needed.
  - [x] 1.2 Add `runsheet_report_found = models.BooleanField(default=False)` to `web/orders/models.py:Lease`.
  - [x] 1.3 Add `runsheet_directory = models.ForeignKey('integrations.CloudLocation', null=True, blank=True, on_delete=models.SET_NULL)` to `Lease`.
  - [x] 1.4 Generate and apply migrations.
  - [x] 1.5 Register `CloudLocation` in `web/integrations/admin.py` (read-only for computed fields; searchable by `path`).

- [x] 2.0 Agency storage configuration (admin and validation)
  - [x] 2.1 Create `AgencyStorageConfig` model in `web/integrations/models.py` with fields: `agency` (choices from `orders.AgencyType`, unique), `runsheet_archive_base_path`, `documents_base_path`, `misc_index_base_path`, `enabled=True`.
  - [x] 2.2 Register `AgencyStorageConfig` in admin with list display and search by `agency`.
  - [x] 2.3 Implement a small resolver util `get_agency_storage_config(agency)` that raises a clear exception if missing/disabled (no fallbacks).
  - [x] 2.4 Unit test the resolver: present vs missing vs disabled.

- [x] 3.0 Workflow services implementation (directory search and previous report detection)
  - [x] 3.1 Implement `web/orders/services/lease_directory_search.py`:
    - [x] 3.1.1 Resolve agency config; build path as `runsheet_archive_base_path / lease.lease_number`.
    - [x] 3.1.2 Use `get_cloud_service(provider='dropbox', user=user)` to obtain client; ensure authenticated.
    - [x] 3.1.3 Check directory existence via listing; if found, create share link.
    - [x] 3.1.4 Upsert `CloudLocation` (provider, path) and update `share_url`/`is_public`/`share_expires_at`/`is_directory=True`; assign `Lease.runsheet_directory` and save only changed fields.
    - [x] 3.1.5 Return `{found, path, share_url, location_id}`; treat not-found as success with `found=False`.
    - [x] 3.1.6 Map auth/network errors to retriable exceptions.
  - [x] 3.2 Implement `web/orders/services/previous_report_detection.py`:
    - [x] 3.2.1 Require `Lease.runsheet_directory` present; else return `{found: False}` without error.
    - [x] 3.2.2 List files in that path; apply regex (case-insensitive) `.*master documents.*`.
    - [x] 3.2.3 Update `Lease.runsheet_report_found` accordingly; save only changed field.
    - [x] 3.2.4 Return `{found, matching_files}`.
  - [x] 3.3 Unit tests for both services with mocked `CloudOperations` (found, not-found, error cases).

- [x] 4.0 Celery tasks, chaining, and `Lease` create trigger
  - [x] 4.1 Add basic Celery setup (if missing): `web/order_manager_project/celery.py`, load in `__init__.py`, add broker/result settings.
  - [x] 4.2 Implement tasks in `web/orders/tasks.py`:
    - [x] 4.2.1 `lease_directory_search_task(lease_id, user_id)` with retry/backoff on auth/network errors.
    - [x] 4.2.2 `previous_report_detection_task(lease_id, user_id)`; no retry for directory-not-found.
    - [x] 4.2.3 Chain: on success of search with `found=True`, invoke detection.
  - [x] 4.3 Add `web/orders/signals.py` post_save handler for `Lease` (create & update) to enqueue the chain using current-user middleware; skip when only task-managed fields change.
  - [x] 4.4 Tests: ensure signal enqueues on create/update, skips when no user or only task fields update.

- [x] 5.0 Settings, wiring to Dropbox factory, and tests
  - [x] 5.1 Add `RUNSHEET_PREVIOUS_REPORT_PATTERN = r".*master documents.*"` to settings; compile case-insensitive in service.
  - [x] 5.2 Verify `web/integrations/cloud/factory.get_cloud_service(user=...)` is used by services; adjust if needed.
  - [x] 5.3 Add logging at info level for key steps (lease id, agency, path, outcomes).
  - [x] 5.4 End-to-end tests (Django TestCase): create lease, mock Dropbox client, assert `runsheet_directory` and `runsheet_report_found` set as expected.


