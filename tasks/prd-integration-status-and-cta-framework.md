# PRD: Integration Status & CTA Framework

## Introduction/Overview
Implement a simple, SOLID/DRY framework to evaluate per-user integration readiness and surface a gentle, non‑blocking call‑to‑action (CTA) wherever needed in the UI. Initial providers: Dropbox and Basecamp (Basecamp placeholder until OAuth is wired). The framework centralizes status rules, minimizes live API calls via short TTL caching, and exposes a consistent DTO consumable by views/templates and (later) decorators.

## Goals
- Provide a single service API to assess a user’s integration status per provider.
- Show a soft, non‑blocking CTA only when background tasks would fail without user action.
- Keep logic reusable across pages and future features; adhere to SOLID/DRY.
- Minimize latency via short‑TTL caching; no persistence or JSON API.
- Be ready to add Basecamp with the same rules and outputs.

## User Stories
- As a signed‑in user, I see an action prompt only when my integration setup would cause background tasks to fail; otherwise, I’m not interrupted.
- As a developer, I can include a small partial on any page to render a consistent CTA for one or more providers.
- As a developer, I can check readiness in code via a single service and branch behavior accordingly.

## Functional Requirements
1. Service API
   - Provide `IntegrationStatusService.assess(user, provider) -> IntegrationStatus`.
   - Support `provider in {dropbox, basecamp}`; basecamp returns placeholder status until OAuth is integrated.
2. DTO
   - `IntegrationStatus` fields: `provider` (str), `connected` (bool), `authenticated` (bool), `has_refresh` (bool), `blocking_problem` (bool), `reason` (str), `cta_label` (str|None), `cta_url` (str|None), `last_checked` (datetime), `ttl_seconds` (int).
3. Status Rules (shared policy for all providers)
   - Not connected ⇒ `blocking_problem=True`, CTA “Connect”.
   - Connected but not authenticated now ⇒ `blocking_problem=True`, CTA “Reconnect”.
   - Connected+authenticated but no refresh token ⇒ `blocking_problem=True`, CTA “Reconnect”.
   - Missing app credentials (env) ⇒ `blocking_problem=True`; reason targeted to staff; still surface gently to user.
   - Otherwise ⇒ `blocking_problem=False`; no CTA.
4. Caching
   - Use an in‑process TTL cache (default 10 minutes). No Redis or Celery required.
   - Design a simple cache adapter so Redis can be dropped in later without changing call sites.
5. UI Integration
   - Context processor injects `integration_statuses` (mapping for all enabled providers) into templates.
   - Reusable template partial (e.g., `integrations/_cta.html`) that renders the CTA when `blocking_problem=True`; renders nothing otherwise.
   - Base layout can include a global banner; specific pages can include the partial where needed.
6. Extensibility
   - Provider strategies: `DropboxStatusStrategy`, `BasecampStatusStrategy` (placeholder returns `connected=False` until OAuth is live).
   - All rules live in a shared policy module, applied per strategy to keep behavior uniform.

## Non-Goals (Out of Scope)
- Database persistence/snapshots or history of statuses.
- JSON API endpoints for status.
- Hard enforcement/redirects (decorators) now; can be added later.
- Analytics or accessibility/i18n work beyond basic semantics.
- Cross‑org/tenant tokens.

## Design Considerations
- Keep the CTA gentle: inline banner/box; no blocking modals.
- Single partial ensures consistent copy and styling.
- Copy: short and action‑oriented (e.g., “Action required: Dropbox refresh token is missing. Reconnect to grant offline access.”).

## Technical Considerations
- Default TTL: 10 minutes; allow a force‑refresh flag for views that need an immediate re‑check.
- Prefer “cheap” checks (presence of tokens, `expires_at`, env vars). Only probe API if cache is stale or required.
- Drop‑in cache adapter interface: start with in‑process dict; future Redis adapter can implement the same interface.
- Basecamp strategy mirrors Dropbox flags (connected/authenticated/has_refresh), but initially returns placeholder status and CTA “Connect Basecamp”.

## Success Metrics
- CTA displays only when `blocking_problem=True`; otherwise absent.
- No background task failures due to missing/expired tokens after users act on the CTA.
- Minimal latency impact (target <5 ms average from cached reads).
- No duplication of status logic inside views (views consume the DTO only).

## Open Questions
- Evaluate both providers on every request vs. only those a user has connected? (Recommendation: evaluate both; cheap cached reads.)
- Confirm TTL (default 10 min). Acceptable alternatives: 5 or 15.
- Exact placement in base template (top banner vs. below navbar)?
- Staff‑only detail: show extra reason text (e.g., missing env vars) only to staff while keeping user copy generic?


