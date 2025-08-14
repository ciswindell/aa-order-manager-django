# Dashboard and Dropbox Soft Auth Prompt

## Introduction/Overview

Create a minimal, generic dashboard shown to all authenticated users at the root path `/`. The dashboard provides a clear entry point to the system and surfaces Dropbox connection status with a soft prompt to connect (no hard enforcement, no dismissal). For staff users, include a link to the Django Admin. This supports continued migration by ensuring users are aware of Dropbox auth status without blocking navigation.

## Goals

- Provide a post-login landing page at `/` for all users
- Show Dropbox connection status and prompt non-connected users to connect
- Show Admin link to staff users only
- Support clean redirect behavior after Dropbox OAuth (back to the dashboard or the last page, when safe)
- Keep implementation minimal and maintainable to unblock further workflow migration

## User Stories

- As an authenticated user, I want to land on a simple dashboard after login so that I have a clear starting point.
- As an authenticated user, I want to see whether my Dropbox account is connected so that I can take action if needed.
- As an authenticated user without a Dropbox connection, I want a clear “Connect Dropbox” button so that I can grant access quickly.
- As staff, I want a link to the Django Admin on the dashboard so that I can manage data and configurations.
- As a user who just completed Dropbox OAuth, I want to be returned to where I came from (or the dashboard) so that my flow isn’t interrupted.

## Functional Requirements

1. Dashboard Route and Access
   - The dashboard is served at path `/`.
   - Access requires authentication (login required). Unauthenticated users are redirected to the login page.
   - All authenticated users see the same dashboard content, except the Admin link which is staff-only.

2. App Placement and URLs
   - Create a generic app `web/core` to host the dashboard view/template.
   - Root URL configuration includes the `core` app URLs at the site root.
   - Include Django’s built-in auth URLs under `accounts/` for login/logout/password flows.
   - Configure `LOGIN_REDIRECT_URL` to the dashboard route.

3. Admin Link Visibility
   - The dashboard shows a link to the Django Admin only for users with `is_staff=True`.
   - Non-staff users do not see the Admin link.

4. Dropbox Connection Status and Soft Prompt
   - The dashboard determines Dropbox connection status per-user via existing helper `integrations.utils.token_store.get_tokens_for_user(user)`.
   - If tokens are missing (no connected account), show a prominent, non-dismissable banner with:
     - Message: “Dropbox is not connected.”
     - Button: “Connect Dropbox” linking to the existing `integrations:dropbox_connect` endpoint.
   - If tokens exist, do not show the banner.

5. Dropbox Misconfiguration Warning (Staff Only)
   - If Dropbox app credentials are misconfigured (e.g., missing `DROPBOX_APP_KEY` or `DROPBOX_APP_SECRET`), show a warning banner on the dashboard to staff users only.
   - Non-staff users never see configuration warnings.

6. Reconnect Prompt
   - If the user has a stored Dropbox account but tokens are invalid/expired or fail validation, show a banner prompting to “Reconnect Dropbox” that links to the same connect endpoint.
   - The system should not perform heavy Dropbox API calls on every page load. A failed Dropbox call in normal use can set a flag or surface a message for subsequent page views.

7. OAuth Redirect Behavior
   - After a successful Dropbox OAuth callback, redirect the user to:
     - A validated/safe `next` URL parameter if present and local, otherwise
     - The dashboard route `/`.
   - Preserve CSRF/state handling as in current Dropbox OAuth implementation.

8. Templates and Layout
   - Provide a minimal base template (simple app template) with a header/title and a messages area.
   - Provide a dashboard template that:
     - Greets the user (e.g., shows username)
     - Shows the Admin link conditionally for staff users
     - Renders the Dropbox soft prompt or reconnect prompt when applicable
     - Shows a logout button when logged in

9. Security and Access
   - All dashboard routes require authentication.
   - Do not gate general navigation behind Dropbox connection (soft prompt only).
   - Admin link must not be shown to non-staff users.
   - Only staff see environment/configuration warnings.

## Non-Goals (Out of Scope)

- No order-related widgets, analytics, or data summaries on the dashboard
- No advanced navigation or layout beyond the basic template and links described
- No visual framework (e.g., Bootstrap) or styling beyond minimal presentational HTML/CSS
- No dismissal/remembering of the Dropbox prompt in this iteration
- No background validation/pinging Dropbox on every request

## Design Considerations (Optional)

- Use semantic HTML and minimal styles to keep complexity low.
- Keep the banner noticeable but not blocking; ensure the connect button stands out.
- Prepare the template structure so we can easily add navigation and widgets later without refactoring.

## Technical Considerations (Optional)

- Reuse existing Dropbox OAuth endpoints in `integrations`.
- Use `get_tokens_for_user(request.user)` to determine connection status.
- Keep redirects safe by validating `next` is a local URL.
- Set `LOGIN_REDIRECT_URL` to `/` and include `django.contrib.auth.urls` under `accounts/`.
- Place dashboard logic and templates under `web/core` to remain app-agnostic.
- Continue passing `user=request.user` to cloud services in future Dropbox-backed actions.

## Success Metrics

- After login, users land on `/` and see the dashboard.
- Staff users see an Admin link; non-staff do not.
- Users without a Dropbox connection see a banner with a “Connect Dropbox” button.
- Users with a valid Dropbox connection do not see the banner.
- After completing Dropbox OAuth, users are redirected to a safe `next` URL if provided or `/` otherwise.
- Staff users see a clear warning if Dropbox app credentials are misconfigured; non-staff do not.

## Open Questions

- For “Reconnect” detection, should we surface reconnect on the next request after a cloud-service failure via Django messages, or introduce a lightweight, periodic validation endpoint visible only on the dashboard? (Initial approach: message-based, no periodic checks.)
- Should we show any minimal footer links (e.g., integrations index) on the dashboard for dev convenience, or keep strictly minimal?


