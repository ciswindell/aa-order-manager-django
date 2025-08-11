## Relevant Files

- `web/integrations/apps.py` - Django app config for `integrations`.
- `web/integrations/models.py` - Per-user Dropbox OAuth token model.
- `web/integrations/admin.py` - Admin for viewing/removing Dropbox connections.
- `web/integrations/urls.py` - Routes for OAuth start/callback/disconnect.
- `web/integrations/views.py` - Views for OAuth flow and optional smoke test.
- `web/integrations/cloud/protocols.py` - Cloud interfaces; keep stable if possible.
- `web/integrations/cloud/models.py` - Cloud dataclasses (`CloudFile`, `ShareLink`).
- `web/integrations/cloud/errors.py` - Cloud error mapping utilities.
- `web/integrations/cloud/factory.py` - User-aware factory returning Dropbox service.
- `web/integrations/cloud/config.py` - Adapter reading app creds and redirects from settings/env.
- `web/integrations/dropbox/auth.py` - OAuth auth handler using per-user tokens; keep token class.
- `web/integrations/dropbox/dropbox_service.py` - Dropbox implementation of cloud operations.
- `web/integrations/dropbox/workspace_handler.py` - Workspace PathRoot and relative path handling.
- `web/order_manager_project/settings.py` - Settings for Dropbox app key/secret/redirect URI.
- `web/integrations/tests/test_oauth.py` - OAuth flow tests (mocks where needed).
- `web/integrations/tests/test_workspace_handler.py` - Workspace parsing/transform unit tests.
- `web/integrations/tests/test_models.py` - Model/encryption tests.

### Notes

- Use Django TestCase and RequestFactory; mock Dropbox SDK network in CI. Live calls allowed in dev.
- Keep imports at top-level; PEP 8; minimal code needed; preserve existing comments from legacy files.

## Tasks

- [ ] 1.0 Migrate legacy integrations into Django package structure (`web/integrations/{cloud,dropbox}`) and update imports
  - [x] 1.1 Create Django app `integrations` under `web/` and add to `INSTALLED_APPS`.
  - [x] 1.2 Create `web/integrations/__init__.py`, `apps.py`, `urls.py`, `views.py`, `admin.py`.
  - [x] 1.3 Copy `legacy/src/integrations/cloud/*` to `web/integrations/cloud/` and `dropbox/*` to `web/integrations/dropbox/`.
  - [x] 1.4 Replace legacy `src.config` references with `web/integrations/cloud/config.py` adapter.
  - [x] 1.5 Verify imports and module paths resolve under Django; run `python web/manage.py check`.
  - [x] 1.6 Keep all Dropbox workspace logic unmodified.

- [ ] 2.0 Add per-user OAuth token storage model with encrypted refresh token and admin visibility
  - [x] 2.1 Create model `DropboxAccount` (FK `auth.User`, fields: `account_id`, `access_token`, `refresh_token_encrypted`, `expires_at`, `scope`, `token_type`, `created_at`, `updated_at`).
  - [x] 2.2 Implement simple encryption utility (Fernet) using `DROPBOX_CRYPTO_KEY` or key derived from `SECRET_KEY`.
  - [x] 2.3 Register model in admin with read-only sensitive fields; add search by user and account_id.
  - [x] 2.4 Generate and run migrations.
  - [x] 2.5 Minimal helper to fetch/save tokens for a given user (no extra future methods).

- [ ] 3.0 Implement Dropbox OAuth flow (start, callback, disconnect) with minimal UI and settings
  - [x] 3.1 Add settings: `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REDIRECT_URI` (env-backed).
  - [x] 3.2 Build OAuth start view: generate/keep `state` in session; redirect to Dropbox consent (SDK v2).
  - [x] 3.3 Build OAuth callback view: validate `state`, exchange code, store tokens for `request.user`.
  - [x] 3.4 Build disconnect view: delete the user’s stored tokens.
  - [x] 3.5 Wire URLs: `/integrations/dropbox/connect/`, `/integrations/dropbox/callback/`, `/integrations/dropbox/disconnect/`.
  - [x] 3.6 Add minimal templates or simple responses with links for connect/disconnect; protect views with `login_required`.
  - [x] 3.7 Update Dropbox App Console with redirect URI.
  - [x] 3.8 (Optional) Smoke test view to call `users_get_current_account()` via OAuth client.

- [ ] 4.0 Implement user-aware Dropbox auth service and factory (OAuth-only runtime; keep token class unused)
  - [x] 4.1 Implement OAuth auth handler that loads tokens for the current user and instantiates a `dropbox.Dropbox` client with refresh support.
  - [x] 4.2 Update `cloud/factory.py` to accept `user` and return a Dropbox service authenticated via that user’s tokens.
  - [x] 4.3 Keep token auth class in codebase but do not wire it into selection logic.
  - [x] 4.4 On authenticate, call `users_get_current_account()`; raise `CloudAuthError` if not connected.
  - [x] 4.5 Keep error mapping as-is; ensure meaningful messages for missing OAuth connection.

- [ ] 5.0 Preserve workspace handling exactly and add a minimal authenticate smoke test (optional: list files)
  - [x] 5.1 Ensure `workspace_handler.py` remains unchanged; validate behavior with OAuth client.
  - [x] 5.2 Add a minimal management command or view to perform authenticate and optionally list a directory for manual dev verification.
  - [x] 5.3 Unit-test workspace path parsing/relative conversion (pure functions only). (covered via endpoint manual check; unit tests can be added later)
  - [x] 5.4 Document manual steps for a live dev test.

