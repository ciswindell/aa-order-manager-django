## Relevant Files

- `web/integrations/status/dto.py` - Defines `IntegrationStatus` DTO.
- `web/integrations/status/strategies/dropbox.py` - Dropbox status strategy.
- `web/integrations/status/strategies/basecamp.py` - Basecamp placeholder strategy.
- `web/integrations/status/service.py` - `IntegrationStatusService` orchestrating strategies and cache.
- `web/integrations/status/cache.py` - In-process TTL cache (adapter pattern; Redis-ready later).
- `web/integrations/context.py` - Context processor exposing `integration_statuses` to templates.
- `web/integrations/templatetags/integration_cta.py` - Template tag to render CTA from DTO.
- `web/integrations/templates/integrations/_cta.html` - CTA partial template.
- `web/core/templates/core/base.html` - Include global CTA banner (optional hook).
- `web/core/views.py` - Example page-specific include using the tag/partial.
- Tests: `web/integrations/tests/test_status_service.py`, `test_dropbox_status_strategy.py`, `test_basecamp_status_strategy.py`, `test_context_processor.py`, `test_cta_template.py`.

### Notes

- This task list is generated from `tasks/prd-integration-status-and-cta-framework.md`.
- Sub-tasks and concrete file list will be added after confirmation.

## Tasks

- [ ] 1.0 Define integration status domain model and provider strategies
  - [ ] 1.1 Create `IntegrationStatus` DTO with fields: provider, connected, authenticated, has_refresh, blocking_problem, reason, cta_label, cta_url, last_checked, ttl_seconds
  - [ ] 1.2 Implement shared policy helper that maps raw provider signals → DTO fields
  - [ ] 1.3 Define provider strategy protocol (`assess_raw(user) -> RawStatusSignals`) and concrete classes for Dropbox and Basecamp (placeholder)
  - [ ] 1.4 Basecamp placeholder returns connected/authenticated false and CTA to connect
- [ ] 2.0 Implement `IntegrationStatusService` with TTL cache adapter (in-process, Redis-ready)
  - [ ] 2.1 Implement in-process TTL cache with get/set(key, ttl) and monotonic timestamps
  - [ ] 2.2 Service composes strategies; key: `integration_status:{provider}:{user_id}`; default TTL 600s; force_refresh flag
  - [ ] 2.3 Add adapter interface to allow future Redis drop-in without changing service API
  - [ ] 2.4 Unit tests covering cache hit/miss, TTL expiry, and force refresh
- [ ] 3.0 Add UI delivery: context processor and reusable CTA template partial; wire into base layout optionally
  - [ ] 3.1 Context processor: returns `{ 'integration_statuses': { 'dropbox': dto, 'basecamp': dto } }`
  - [ ] 3.2 Template partial `_cta.html` that renders only when `blocking_problem` is true; accepts `status` (DTO) and optional `compact` flag
  - [ ] 3.3 Template tag `{% integration_cta 'dropbox' %}` to render provider CTA using the service (for pages not using the context processor)
  - [ ] 3.4 Include global CTA banner in `core/base.html` via the partial; keep off by default behind a simple template block
  - [ ] 3.5 Example usage in `core/views.py` and `core/templates/core/dashboard.html` (replace current inline logic)
- [ ] 4.0 Implement Dropbox strategy and Basecamp placeholder; unify shared status policy and copy
  - [ ] 4.1 Dropbox: use stored tokens and env settings; prefer cheap checks (presence, expires_at); perform live `users_get_current_account` only when stale
  - [ ] 4.2 Policy rules: not connected, not authenticated now, missing refresh token, env missing → set DTO fields and CTAs accordingly
  - [ ] 4.3 Basecamp placeholder mirrors fields; CTA to connect; no live calls
  - [ ] 4.4 Centralize CTA copy constants for consistency across providers
- [ ] 5.0 Add tests and developer docs (service, strategies, caching, template rendering)
  - [ ] 5.1 Unit tests for strategies, service cache behavior, and context processor
  - [ ] 5.2 Template/tag tests ensure CTA renders only when `blocking_problem` is true
  - [ ] 5.3 Update/author README section for the new framework and migration notes (replace inline dashboard logic)


