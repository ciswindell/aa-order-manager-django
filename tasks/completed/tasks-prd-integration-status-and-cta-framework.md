## Relevant Files

- `web/integrations/status/dto.py` - Defines `IntegrationStatus` DTO.
- `web/integrations/status/__init__.py` - Exposes `IntegrationStatus` for easy imports.
- `web/integrations/status/policy.py` - Shared policy mapping raw signals to DTO.
- `web/integrations/status/strategies/base.py` - Strategy protocol for providers.
- `web/integrations/status/strategies/dropbox.py` - Dropbox strategy implementation.
- `web/integrations/status/strategies/basecamp.py` - Basecamp placeholder strategy.
- `web/integrations/status/cache.py` - In-process TTL cache adapter.
- `tasks/tasks-prd-integration-status-and-cta-framework.md` - Progress tracking for this PRD task list.
- `web/integrations/status/strategies/dropbox.py` - Dropbox status strategy.
- `web/integrations/status/strategies/basecamp.py` - Basecamp placeholder strategy.
- `web/integrations/status/service.py` - `IntegrationStatusService` orchestrating strategies and cache.
- `web/integrations/status/cache.py` - In-process TTL cache (adapter pattern; Redis-ready later).
- `web/integrations/context.py` - Context processor exposing `integration_statuses` to templates.
- `web/integrations/templatetags/integration_cta.py` - Template tag to render CTA from DTO.
- `web/integrations/templates/integrations/_cta.html` - CTA partial template.
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
  - [x] 1.1 Create `IntegrationStatus` DTO with fields: provider, connected, authenticated, has_refresh, blocking_problem, reason, cta_label, cta_url, last_checked, ttl_seconds
  - [x] 1.2 Implement shared policy helper that maps raw provider signals → DTO fields
  - [x] 1.3 Define provider strategy protocol (`assess_raw(user) -> RawStatusSignals`) and concrete classes for Dropbox and Basecamp (placeholder)
  - [x] 1.4 Basecamp placeholder returns connected/authenticated false and CTA to connect
- [ ] 2.0 Implement `IntegrationStatusService` with TTL cache adapter (in-process, Redis-ready)
  - [x] 2.1 Implement in-process TTL cache with get/set(key, ttl) and monotonic timestamps
  - [x] 2.2 Service composes strategies; key: `integration_status:{provider}:{user_id}`; default TTL 600s; force_refresh flag
  - [x] 2.3 Add adapter interface to allow future Redis drop-in without changing service API
  - [x] 2.4 Unit tests covering cache hit/miss, TTL expiry, and force refresh
- [ ] 3.0 Add UI delivery: context processor and reusable CTA template partial; wire into base layout optionally
  - [x] 3.1 Context processor: returns `{ 'integration_statuses': { 'dropbox': dto, 'basecamp': dto } }`
  - [x] 3.2 Template partial `_cta.html` that renders only when `blocking_problem` is true; accepts `status` (DTO) and optional `compact` flag
  - [x] 3.3 Template tag `{% integration_cta 'dropbox' %}` to render provider CTA using the service (for pages not using the context processor)
  - [x] 3.4 Include global CTA banner in `core/base.html` via the partial; keep off by default behind a simple template block
  - [x] 3.5 Example usage in `core/templates/core/dashboard.html` using the tag
  - [x] 3.5 Example usage in `core/views.py` and `core/templates/core/dashboard.html` (replace current inline logic)
- [ ] 4.0 Implement Dropbox strategy and Basecamp placeholder; unify shared status policy and copy
  - [x] 4.1 Dropbox: use stored tokens and env settings; prefer cheap checks (presence, expires_at); perform live `users_get_current_account` only when stale
  - [x] 4.2 Policy rules: not connected, not authenticated now, missing refresh token, env missing → set DTO fields and CTAs accordingly
  - [x] 4.3 Basecamp placeholder mirrors fields; CTA to connect; no live calls
  - [x] 4.4 Centralize CTA copy constants for consistency across providers
- [ ] 5.0 Add tests and developer docs (service, strategies, caching, template rendering)
  - [x] 5.1 Unit tests for strategies, service cache behavior, and context processor
  - [x] 5.2 Template/tag tests ensure CTA renders only when `blocking_problem` is true
  - [x] 5.3 Update/author README section for the new framework and migration notes (replace inline dashboard logic)


