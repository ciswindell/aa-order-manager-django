## Introduction/Overview

Migrate the legacy Dropbox integrations into the Django project and add a first-class OAuth 2.0 flow. Preserve cloud-agnostic protocols and Dropbox workspace handling. Enable per-user Dropbox connections via OAuth, stored against the Django user. Keep the legacy token auth class in the codebase for potential future use, but do not wire it into runtime flows.

## Goals

1. Integrate legacy `integrations/` into `web/integrations/` with stable protocols.
2. Support OAuth (per user). Retain the token auth class in the codebase (not used).
3. Implement Dropbox OAuth UI and endpoints usable in Django dev and prod.
4. Persist OAuth tokens per user and use them to authenticate Dropbox API calls.
5. Preserve all existing Dropbox workspace behavior exactly.

## User Stories

- As a user, I can connect my Dropbox account via OAuth so the app can access my files.
- As a user, I can disconnect my Dropbox account to revoke access from the app.
- As a developer, I can call a single factory to obtain a Dropbox client bound to the current user/session.

## Functional Requirements

FR-1. Migrate legacy modules to `web/integrations/{cloud,dropbox}/` and update imports.

FR-2. Prefer keeping `cloud.protocols` and `cloud.models` unchanged as the public interface; allow minimal changes only if required for OAuth/user-binding.

FR-3. Provide a config adapter that reads app credentials and redirect URIs from Django settings/env, and resolves per-user OAuth credentials from the authenticated user.

FR-4. Implement OAuth 2.0 flow using Dropbox SDK v2:
  - Start endpoint generates state, redirects to Dropbox consent.
  - Callback endpoint validates state, exchanges code for tokens, stores tokens.
  - Tokens: access_token, refresh_token, expires_at, account_id, scope, token_type.

FR-5. Persist tokens per user:
  - Model with FK to `auth.User` and encrypted storage for refresh token.
  - One active Dropbox connection per user.

FR-6. Authentication selection:
  - If user-bound OAuth tokens exist and are valid, use OAuth for that user.
  - Else raise clear `CloudAuthError` and require the user to connect Dropbox via OAuth.

FR-7. Workspace handling must remain identical to legacy behavior (PathRoot + relative path conversion) and continue to work under OAuth.

FR-8. Minimum operation that must work: authenticate (verify with `users_get_current_account`). Optional: list files/dirs in a known folder.

FR-9. UI:
  - Simple views: "Connect Dropbox" (start), "Dropbox callback" (finish), "Disconnect Dropbox".
  - Basic templates or admin action to trigger connect/disconnect in development.

## Non-Goals (Out of Scope)

- New cloud providers; team endpoints; background syncing; workflow wiring.
- Full UX polish; complex permission matrices; audit trails.

## Design Considerations

- Directory structure (approved):

```
web/
  integrations/
    cloud/{protocols.py, models.py, errors.py, factory.py, config.py}
    dropbox/{auth.py, dropbox_service.py, workspace_handler.py}
```

- Use Django settings for defaults and app credentials: `CLOUD_PROVIDER` (optional), `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REDIRECT_URI`.
- OAuth requires adding the redirect URI in Dropbox App Console (e.g., `http://localhost:8000/integrations/dropbox/callback/`).
- Token storage: encrypt refresh token at rest (e.g., Fernet with a key derived from Django `SECRET_KEY` or a dedicated `DROPBOX_CRYPTO_KEY`).
- Thread safety: create clients per request/user; do not share clients between users.

## Technical Considerations

- Cloud protocols remain unchanged; `cloud.factory` gains user-aware resolution.
- For OAuth, use `dropbox.oauth` helpers to start and finish flows; ensure `state` CSRF protection.
- Token refresh: use Dropbox SDK refresh mechanism; update stored expiry on refresh.
- Logging: keep `logging.getLogger(__name__)`; configured by Django.
- Live Dropbox calls allowed in dev; stub/mock in CI as needed.

## Success Metrics

- A user can complete OAuth and we can call `users_get_current_account()` using their tokens.
- Workspace paths behave identically to legacy (manual verification against a workspace folder).

## Open Questions

1. Encryption key source for refresh tokens (dedicated env vs Django `SECRET_KEY`-derived)?
2. Multi-account support per user needed later, or enforce single link?
3. Admin UI vs user-facing settings page for connect/disconnect?
4. Exact scopes required for the app (e.g., files.metadata.read, files.content.read, sharing.read/write)?


