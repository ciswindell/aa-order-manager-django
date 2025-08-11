## Title

Migrate Legacy Cloud Integrations to Django (Phase 1 alignment; prepares Phase 2 Step 3)

## Goal

Refactor legacy cloud integrations to live under the Django project, using Django settings and packaging, while preserving Dropbox workspace behavior and cloud-agnostic protocols.

## Scope

- In-scope: Move `legacy/src/integrations/**` into `web/integrations/**`; adapt imports to Django; replace `src.config` with `django.conf.settings`-backed config; keep current Dropbox workspace logic; keep public interfaces stable.
- Out-of-scope: Adding new providers; OAuth flow UX; API/views wiring; background jobs.

## Non-Functional Requirements

- PEP 8, SOLID/DRY, minimal changes, do not delete comments.
- Imports only at module top-level.

## Proposed Architecture in Django

Directory layout:

```
web/
  integrations/
    __init__.py
    cloud/
      __init__.py
      protocols.py      # unchanged public interface
      models.py         # dataclasses
      errors.py         # error mapping
      factory.py        # updated to use Django settings
      config.py         # new thin adapter over Django settings
    dropbox/
      __init__.py
      auth.py
      dropbox_service.py
      workspace_handler.py
```

Key modules and responsibilities:

- `cloud.protocols`: Keep as-is (interfaces `CloudAuthentication`, `CloudOperations`).
- `cloud.models`: Keep dataclasses (`CloudFile`, `ShareLink`).
- `cloud.errors`: Keep mapping; propagate into Django logging via standard logging config.
- `cloud.config` (new): Read values from `django.conf.settings` and environment.
- `cloud.factory`: Construct provider clients via `cloud.config`; remove `src.config` coupling.
- `dropbox.*`: Keep logic; ensure no legacy path imports; preserve workspace handling.

## Public Interfaces (unchanged)

- `CloudOperations`:
  - `list_files(directory_path: str, recursive: bool = False) -> list[CloudFile]`
  - `list_directories(directory_path: str, recursive: bool = False) -> list[CloudFile]`
  - `create_share_link(file_path: str, is_public: bool = True) -> Optional[ShareLink]`
  - `create_directory(path: str) -> Optional[CloudFile]` (not implemented)

## Django Settings (configuration)

Add to `web/order_manager_project/settings.py` (with env fallbacks):

- `CLOUD_PROVIDER` (default: `"dropbox"`)
- `DROPBOX_AUTH_TYPE` (default: `"token"`)
- `DROPBOX_ACCESS_TOKEN` (default empty; load from `DROPBOX_ACCESS_TOKEN` env)
- `DROPBOX_APP_KEY` / `DROPBOX_APP_SECRET` (optional; pass-through env)

## Refactor Plan

1. Create `web/integrations/` and subpackages; add `__init__.py` files.
2. Copy `legacy/src/integrations/cloud/*` and `legacy/src/integrations/dropbox/*` to `web/integrations/...`.
3. Replace `from src import config` with `from django.conf import settings` via a new `web/integrations/cloud/config.py` adapter exposing:
   - `get_cloud_provider() -> str`
   - `get_dropbox_auth_type() -> str`
   - `get_dropbox_access_token() -> str`
4. Update `cloud.factory` to import from `.config` instead of `src.config`.
5. Verify `dropbox/auth.py` uses adapter for tokens; keep workspace logic intact in `dropbox_service.py` and `workspace_handler.py`.
6. Wire logging via Django’s logging settings (no code changes if using `logging.getLogger(__name__)`).

## Acceptance Criteria

- Code compiles and imports under Django without `src` references.
- `get_cloud_service().authenticate()` works with token auth when `DROPBOX_ACCESS_TOKEN` is set.
- Listing directories and files works for both regular and workspace paths.
- Error mapping surfaces as `CloudServiceError` subclasses.

## Risks / Mitigations

- Workspace namespace resolution might differ across accounts: keep `sharing_list_folders()` approach; add retries later if needed.
- Missing tokens in dev: default-safe behavior; raise clear `CloudAuthError`.

## Test Plan (high level)

- Unit tests for `cloud.config` reading from `settings` and env.
- Smoke tests (can be skipped in CI) for `DropboxCloudService` with a fake token to assert auth failure raises `CloudAuthError`.
- Unit tests for workspace path parsing in `workspace_handler` (pure functions).

## Notes

- Keep current exceptions and comments; do not add future-only methods.
- Keep imports at top-level and minimal lines per method.


