## Introduction/Overview

Implement two separate, Django-native background workflows around leases and Dropbox:
- Lease Directory Search: find the agency-specific lease directory and store a shareable link on `orders.Lease.runsheet_link`.
- Previous Report Detection: scan that directory for a file matching the global legacy pattern ("Master Documents"), and set `orders.Lease.runsheet_report_found` accordingly.

Admin must configure per-agency base directories (no fallbacks). Dropbox OAuth is required and tasks use the initiating user’s tokens. Workflows run on `Lease` create and can be invoked on demand for a single lease.

## Goals

1. Two independent workflows with clear inputs/outputs and idempotent behavior.
2. Admin-configurable per-agency base paths, required (no defaults/fallbacks).
3. Dropbox-only integration using the initiating user’s OAuth tokens.
4. Celery-based background execution with retries and conditional chaining.
5. Introduce a generic reusable cloud location store to avoid re-resolution and enable future reuse.

## User Stories

- As an operator, when I create a `Lease`, the system automatically looks up the lease directory in Dropbox and stores the share link if found.
- As an operator, after a directory is found, the system checks for a previous runsheet (file containing "Master Documents") and marks the lease accordingly.
- As an admin, I can set each agency’s base directories in the admin so searches run against the correct locations.
- As a staff user, I can re-run either workflow on a single `Lease` on demand for updates.

## Functional Requirements

FR-1 Agency storage configuration (no fallbacks)
- Create `AgencyStorageConfig` with fields:
  - `agency` (choices: values of `orders.models.AgencyType`, unique)
  - `runsheet_archive_base_path` (str, required)
  - `documents_base_path` (str, required)
  - `misc_index_base_path` (str, required)
  - `enabled` (bool, default True)
- Register in admin with list/search; editing restricted to staff.
- If a matching config is missing or disabled for the lease’s agency, the workflow must fail (no implicit defaults).

FR-2 Lease validation
- Lease creation requires `agency` and `lease_number` (already present). UI and imports must supply both.

FR-3 Workflow: Lease Directory Search
- Input: `lease_id`, `user_id` (user initiating the action/creation).
- Build directory path: `{AgencyStorageConfig.runsheet_archive_base_path}/{lease_number}`.
- Existence check: attempt directory listing via Dropbox; if listing returns any entries or succeeds for the directory, consider it found.
- If found: create a shareable link; upsert a generic `CloudLocation` (see FR-8) for the directory and set `Lease.runsheet_directory` (FK) to that location. The share URL is stored on the `CloudLocation`.
- If not found: leave `Lease.runsheet_directory = NULL`.
- Output: `{found: bool, share_url: Optional[str], path: str, location_id: Optional[int]}`.

FR-4 Workflow: Previous Report Detection
- Precondition: `Lease.runsheet_directory` is set to a directory `CloudLocation`.
- Input: `lease_id`, `user_id`.
- Read the directory path from `Lease.runsheet_directory`; list files and apply global regex pattern (case-insensitive) matching legacy: `.*master documents.*` (PDFs expected but extension not required).
- Set `Lease.runsheet_report_found = True` if any file matches; otherwise `False`.
- Output: `{found: bool, matching_files: list[str]}`.

FR-5 Triggers
- On `Lease` create: enqueue a Celery chain that runs Directory Search, then (conditionally on found) Previous Report Detection.

FR-6 Authentication (Dropbox-only)
- Dropbox is the only supported provider.
- Tasks must run using the initiating user’s Dropbox OAuth tokens (`integrations.DropboxAccount`).
- If tokens are missing/invalid, raise a retriable error and do not proceed; no fallback to app tokens or anonymous access.

FR-7 Background execution and retries
- Use Celery tasks for both workflows. Configure exponential backoff and a finite number of retries for transient Dropbox/HTTP errors and for missing authorization.
- Directory-not-found is not an error and should not be retried.

FR-8 Persistence and data model changes
- Add `Lease.runsheet_report_found: BooleanField(default=False)`.
- Replace URL fields for directories with FKs to a generic location store:
  - Add `Lease.runsheet_directory = models.ForeignKey(CloudLocation, null=True, blank=True, on_delete=SET_NULL)`.
  - (Future) Add `Lease.documents_directory` and `Lease.misc_index_directory` similarly when those workflows are implemented.
- Introduce generic, reusable cloud location persistence:
  - `CloudLocation` (global, reusable):
    - `provider` (CharField, default "dropbox", indexed)
    - `path` (CharField, required, indexed)
    - `name` (CharField, optional)
    - `is_directory` (BooleanField, default True)
    - `file_id` (CharField, null/blank)
    - `share_url` (URLField, null/blank)
    - `share_expires_at` (DateTimeField, null/blank)
    - `is_public` (BooleanField, default True)
    - `size_bytes` (BigIntegerField, null/blank)
    - `modified_at` (DateTimeField, null/blank)
    - Unique constraint: (`provider`, `path`)
  - No "kind" field and no lease-location through model; `Lease` holds explicit FKs for known relationships.
  - Workflows upsert `CloudLocation` using provider/path and assign the FK on `Lease`.

FR-9 Observability and admin UX
- Log key steps and outcomes (info-level) with lease id, agency, and path.


## Non-Goals (Out of Scope)

- Multi-cloud provider support.
- Bulk backfill UI or batch actions across many leases.
- Persisting cloud metadata beyond `runsheet_link` and the boolean flag.
- Searching agency document images or misc index paths (separate future feature).
- Public REST endpoints or UI pages beyond admin actions/forms.

## Design Considerations

- Keep two small service modules, one per workflow (clean separation, easy to test):
  - `orders/services/lease_directory_search.py`
  - `orders/services/previous_report_detection.py`
- Celery tasks wrap these services; tasks accept `(lease_id, user_id)` and load the lease and user.
- Path resolution reads `AgencyStorageConfig` (required) and constructs the lease directory path using `lease.lease_number`.
 - Regex is global and defined in Django settings (e.g., `RUNSHEET_PREVIOUS_REPORT_PATTERN = r".*master documents.*"`).
- `CloudLocation` mirrors the `CloudFile`/`ShareLink` dataclasses minimally for persistence; still use the dataclasses as the transport layer in services.

## Technical Considerations

- Dropbox auth: use existing `web/integrations/...` factory with the provided `user`; fail hard (retriable) if tokens absent/invalid.
- Celery retry policy: exponential backoff with jitter; e.g., max 5 retries; retry on network/Dropbox errors and on `CloudAuthError`.
- Timeouts and rate limits: keep directory listing shallow (no recursion) and avoid large pages; respect SDK limits.
- Idempotency: re-running Directory Search and Detection is safe; they overwrite only the two target fields.
- Data integrity: `Lease` uniqueness `(agency, lease_number)` already enforced; `AgencyStorageConfig.agency` unique.

## Success Metrics

- For leases created by an authorized user with valid agency config, ≥95% set `runsheet_directory` (with `CloudLocation.share_url` populated when directory exists) within 60 seconds.
- Detection sets `runsheet_report_found` accurately in unit tests covering: directory found/not found, files matching/not matching, and Dropbox error scenarios.
- Admin can edit `AgencyStorageConfig` successfully.

## Open Questions

1. Source of `user_id` for automatic runs on `Lease` creation: should we add `created_by` to `Lease`, or will all lease creations happen within a request where we can pass `request.user.id` to the task? If neither, should we block and require an explicit user to run workflows?
2. Maximum retries and backoff policy specifics (values above are suggestions). Should we notify users when retries are exhausted?
3. Should we constrain detection to files ending with `.pdf`, or keep the pattern purely on name?
4. Should we expose admin actions to view and navigate from a `Lease` to its linked `CloudLocation`?


