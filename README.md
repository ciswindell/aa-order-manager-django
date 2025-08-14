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

