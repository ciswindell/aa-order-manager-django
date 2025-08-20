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
- `runsheet_subfolder_documents_name` (optional): Subfolder name to create under the runsheet archive.
- `runsheet_subfolder_misc_index_name` (optional): Subfolder name to create under the runsheet archive.
- `runsheet_subfolder_runsheets_name` (optional): Subfolder name to create under the runsheet archive.
- `auto_create_runsheet_archives` (bool): If true, when a runsheet archive is missing the system will create `<base>/<lease_number>` and configured subfolders.

### Directory creation behavior
- Trigger: Background runsheet search does not find the runsheet archive.
- Preconditions: `runsheet_archive_base_path` must exist. The app will not create the base path.
- Actions: Create `<base>/<lease_number>`; create configured subfolders; no share links are created.
- Lease updates: Upsert `CloudLocation` for the runsheet archive, assign `lease.runsheet_archive`, and set `lease.runsheet_report_found = False`.

## Integration Status & CTA Framework

Centralized service to evaluate per-user readiness for providers (Dropbox, Basecamp placeholder) and render a gentle, non-blocking action prompt.

- Service: `IntegrationStatusService.assess(user, provider)` returns an `IntegrationStatus` DTO.
- Context processor: enabled in settings as `integrations.context.integration_statuses` and injects `{"dropbox": dto, "basecamp": dto}` for authenticated users.
  - By default, only Dropbox is included. Basecamp will be added once OAuth is wired.
- Template tag: `{% load integration_cta %}{% integration_cta 'dropbox' user %}` renders a CTA when `blocking_problem` is true; otherwise nothing.
- Partial: `web/integrations/templates/integrations/_cta.html` used by the tag and optional global banner in `core/base.html`.
- Caching: In-process TTL (10m) to keep pages fast; force-refresh used for request-time UI to avoid stale prompts.

Migration notes:
- Views/templates should avoid bespoke integration readiness logic. Use the context processor and/or the `{% integration_cta %}` tag.
- Environment flags: set `DROPBOX_APP_KEY`/`DROPBOX_APP_SECRET` for OAuth; optional `INTEGRATIONS_STATUS_LIVE_PROBE` to enable a cheap live probe when tokens are stale.

