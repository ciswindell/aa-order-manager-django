## Relevant Files

- `web/order_manager_project/settings.py` - Add `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and ensure `core` app in `INSTALLED_APPS`.
- `web/order_manager_project/urls.py` - Include `core` URLs at root and Django auth URLs under `accounts/`.
- `web/core/apps.py` - App config for the new `core` app.
- `web/core/urls.py` - Route for the dashboard at `/`.
- `web/core/views.py` - `login_required` dashboard view that computes Dropbox status.
- `web/core/templates/core/base.html` - Minimal base template with messages area.
- `web/core/templates/core/dashboard.html` - Dashboard template showing admin link (staff only), Dropbox banner, and logout link.
- `web/integrations/views.py` - Support "next" param storage in `dropbox_connect` and safe redirect in `dropbox_callback`.
- `web/integrations/utils/token_store.py` - Used to check per-user Dropbox token presence.
- `web/integrations/utils/reconnect.py` - Helper to surface a reconnect prompt via Django messages.
- `web/core/tests/test_dashboard.py` - Tests for access control and UI visibility.
- `web/integrations/tests/test_oauth_redirect.py` - Tests for OAuth callback redirect behavior.
 - `web/integrations/tests/test_oauth_redirect.py` - Tests for OAuth callback redirect behavior.

### Notes

- Place tests alongside app code (e.g., `web/core/tests/`).
- Use Django’s test client for login and redirects.
- Validate redirect targets are local (avoid open redirect).

## Tasks

- [x] 1.0 Set up core app and URL routing
  - [x] 1.1 Create `web/core/` app (config, `__init__`, basic files) and add `core` to `INSTALLED_APPS`.
  - [x] 1.2 Add `path("", include("core.urls"))` to `web/order_manager_project/urls.py`.
  - [x] 1.3 Add `path("accounts/", include("django.contrib.auth.urls"))` to `web/order_manager_project/urls.py`.
  - [x] 1.4 In settings, set `LOGIN_URL = "login"` and `LOGIN_REDIRECT_URL = "/"`.

- [x] 2.0 Implement dashboard view and templates
  - [x] 2.1 Create `core.urls` with route for `/` to `dashboard` view and name `dashboard`.
  - [x] 2.2 Implement `dashboard` view with `@login_required`.
  - [x] 2.3 In the view, compute: `is_staff`, `dropbox_connected` (via `get_tokens_for_user`), and `dropbox_misconfigured` (missing app key/secret).
  - [x] 2.4 Create `templates/core/base.html` with minimal header and messages area.
  - [x] 2.5 Create `templates/core/dashboard.html` showing username, staff-only Admin link, Dropbox banner, and a logout link.

- [ ] 3.0 Dropbox soft prompt and reconnect handling
  - [x] 3.1 If `dropbox_connected` is false, show a non-dismissable banner with a "Connect Dropbox" button linking to `integrations:dropbox_connect`.
  - [x] 3.2 If `dropbox_misconfigured` is true, show a configuration warning to staff users only.
  - [x] 3.3 Add a simple mechanism to surface a "Reconnect Dropbox" prompt when a Dropbox API failure is detected (e.g., via Django messages in calling views/services).

- [ ] 4.0 OAuth callback redirect handling
  - [x] 4.1 Update `integrations.views.dropbox_connect` to accept/store an optional `next` URL in session (e.g., `request.session['post_oauth_next']`).
  - [x] 4.2 Update `integrations.views.dropbox_callback` to read and clear `post_oauth_next`, validate it as a safe local URL, and redirect; fallback to `/`.
  - [x] 4.3 Ensure CSRF/state handling with Dropbox OAuth remains intact.

- [ ] 5.0 Basic tests for access, visibility, and redirect behavior
  - [x] 5.1 Dashboard requires login (unauthenticated → redirects to login).
  - [x] 5.2 Staff users see Admin link; non-staff do not.
  - [x] 5.3 When no tokens exist, Dropbox connect banner is present.
  - [x] 5.4 When tokens exist, Dropbox banner is absent.
  - [x] 5.5 Misconfiguration warning appears for staff when app key/secret missing.
  - [x] 5.6 OAuth redirect: `dropbox_connect` stores `next`, `dropbox_callback` safely redirects to `next` or `/`.



