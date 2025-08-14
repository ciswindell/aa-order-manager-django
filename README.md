# AA Order Manager — Dev Setup

## Quick start

1) Run Django (in web/):

```bash
python3 manage.py runserver
```

## Optional: real background tasks

To use Redis + Celery worker instead of eager mode, configure a broker and run a worker.
Eager mode can be enabled by environment variable:

```bash
export CELERY_TASK_ALWAYS_EAGER=1
```

This runs tasks inline (no Redis/worker needed). Unset to return to real background processing.


## Dropbox integration (workspace-first)

- The Dropbox service prefers workspace (shared folder) handling automatically by resolving the first path segment to a shared folder namespace. If no match exists, it falls back to the regular client.
- Shared folder names and namespace IDs are cached per authentication session.
- Dev-only listing endpoint `/integrations/dropbox/list/` was removed.
- DEBUG logs indicate whether workspace or regular mode was used for list and metadata calls.

### Configuration fields (per agency)
- `runsheet_archive_base_path` (required): The base path under the workspace. Must already exist; the app will not create it.
- `runsheet_subfolder_documents_name` (optional): Subfolder name to create under the lease directory.
- `runsheet_subfolder_misc_index_name` (optional): Subfolder name to create under the lease directory.
- `runsheet_subfolder_runsheets_name` (optional): Subfolder name to create under the lease directory.
- `auto_create_lease_directories` (bool): If true, when a lease directory is missing the system will create `<base>/<lease_number>` and configured subfolders.

### Directory creation behavior
- Trigger: Background runsheet search does not find the lease directory.
- Preconditions: `runsheet_archive_base_path` must exist. The app will not create the base path.
- Actions: Create `<base>/<lease_number>`; create configured subfolders; no share links are created.
- Lease updates: Upsert `CloudLocation` for the lease directory, assign `lease.runsheet_directory`, and set `lease.runsheet_report_found = False`.

