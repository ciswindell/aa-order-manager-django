# Tasks: Basecamp API Integration

**Input**: Design documents from `/specs/003-basecamp-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.md

**Tests**: NOT requested in specification - implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `web/` (Django backend), `frontend/src/` (Next.js frontend)
- Tasks extend existing `web/integrations/` Django app

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and database structure

- [ ] T001 Add Basecamp OAuth environment variables to `web/order_manager_project/settings.py` (BASECAMP_APP_KEY, BASECAMP_APP_SECRET, BASECAMP_OAUTH_REDIRECT_URI)
- [ ] T002 [P] Create Basecamp module directory structure at `web/integrations/basecamp/__init__.py`
- [ ] T003 [P] Add Basecamp URL patterns to `web/integrations/urls.py` (connect, callback, disconnect endpoints)
- [ ] T004 Register Basecamp OAuth application at https://launchpad.37signals.com/integrations (obtain client_id and client_secret)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create BasecampAccount model in `web/integrations/models.py` following data-model.md schema (user, account_id, account_name, access_token, refresh_token_encrypted, expires_at, scope, token_type, timestamps)
- [ ] T006 Generate and apply Django migration for BasecampAccount model in `web/integrations/migrations/`
- [ ] T007 [P] Create Basecamp configuration helpers in `web/integrations/basecamp/config.py` (get_basecamp_app_key, get_basecamp_app_secret, get_redirect_uri)
- [ ] T008 [P] Extend token_store utility in `web/integrations/utils/token_store.py` to support Basecamp provider (get_tokens_for_user with provider='basecamp')
- [ ] T009 [P] Add BasecampAccount to Django admin in `web/integrations/admin.py` for debugging

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Connect Basecamp Account (Priority: P1) 🎯 MVP

**Goal**: Users can authenticate via Basecamp OAuth 2.0, select account, and store encrypted credentials

**Independent Test**: User clicks "Connect Basecamp", completes OAuth flow on Basecamp, returns to app with "Connected" status showing account name

**Acceptance Scenarios** (from spec.md):
1. User navigates to integrations page and sees "Connect Basecamp" option
2. User completes OAuth authorization and system prompts account selection (if multiple)
3. System stores credentials securely after account selection
4. User sees connected account name and "Connected" status
5. User can disconnect and system removes credentials
6. System prevents connecting second account (shows error with option to replace)

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement BasecampOAuthAuth service in `web/integrations/basecamp/auth.py` (authenticate method, token exchange, refresh logic)
- [ ] T011 [P] [US1] Implement BasecampService in `web/integrations/basecamp/basecamp_service.py` (API wrapper for authorization.json endpoint)
- [ ] T012 [US1] Implement OAuth initiation view in `web/integrations/views.py` (POST /api/integrations/basecamp/connect/ - generate authorization URL with state parameter)
- [ ] T013 [US1] Implement OAuth callback handler in `web/integrations/views.py` (GET /api/integrations/basecamp/callback/ - validate state, exchange code, get account details, save BasecampAccount)
- [ ] T014 [US1] Implement disconnect view in `web/integrations/views.py` (DELETE /api/integrations/basecamp/disconnect/ - delete BasecampAccount, log disconnection)
- [ ] T015 [US1] Add CSRF protection via state parameter in OAuth flow (generate and validate in session)
- [ ] T016 [US1] Implement single-account enforcement (FR-004) in OAuth callback (check existing account, prevent duplicate)
- [ ] T017 [US1] Add token encryption/decryption for refresh_token_encrypted field using existing utility
- [ ] T018 [US1] Implement error handling for OAuth errors (FR-015) with user-friendly messages per contracts/api-spec.md
- [ ] T019 [US1] Add authentication event logging (FR-016) for connect/disconnect operations (timestamp, user_id, account_id, status)
- [ ] T020 [US1] Verify frontend integrations page displays "Connect" button and handles OAuth redirect (minimal frontend changes expected - existing UI should work)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can connect/disconnect Basecamp accounts independently

---

## Phase 4: User Story 2 - View Connection Status (Priority: P2)

**Goal**: Users can view current Basecamp connection status with account details and clear call-to-action when not connected

**Independent Test**: View integrations page and see accurate status (Connected with account name, Not Connected with Connect button, or Expired with reconnect prompt)

**Acceptance Scenarios** (from spec.md):
1. Connected user sees status as "Connected" with account details
2. User with expired token sees warning status with re-authentication prompt
3. User without configured OAuth credentials sees configuration error
4. Never-connected user sees "Not Connected" status with "Connect" button

### Implementation for User Story 2

- [ ] T021 [US2] Enhance BasecampStatusStrategy in `web/integrations/status/strategies/basecamp.py` (implement assess_raw method following DropboxStatusStrategy pattern)
- [ ] T022 [US2] Implement status endpoint in `web/integrations/views.py` (GET /api/integrations/basecamp/status/ - return provider, status, connected, authenticated, account details, cta_url)
- [ ] T023 [US2] Add Basecamp serializer in `web/integrations/serializers/integrations.py` for status response format
- [ ] T024 [US2] Implement token expiration detection (FR-009) in status strategy (check expires_at if present)
- [ ] T025 [US2] Add environment validation in status strategy (check BASECAMP_APP_KEY and BASECAMP_APP_SECRET configured)
- [ ] T026 [US2] Implement graceful degradation for token refresh failures (FR-008) - status shows warning, allows app access
- [ ] T027 [US2] Add status caching support using ttl_seconds parameter (SC-002: status displays within 1 second)
- [ ] T028 [US2] Extend cloud factory in `web/integrations/cloud/factory.py` to support Basecamp provider
- [ ] T029 [US2] Add Basecamp to cloud config in `web/integrations/cloud/config.py` (get_cloud_provider support)
- [ ] T030 [US2] Verify frontend integrations page displays Basecamp status correctly using existing status API pattern (no frontend code changes expected)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full OAuth flow and status visibility complete

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T031 [P] Implement automatic token refresh logic (FR-007, SC-003: 95% success rate) in `web/integrations/basecamp/auth.py`
- [ ] T032 [P] Add comprehensive authentication event logging (FR-016) for refresh attempts with metadata (timestamp, user_id, success/failure, error details)
- [ ] T033 [P] Implement rate limiting handling for Basecamp API calls with exponential backoff in `web/integrations/basecamp/basecamp_service.py`
- [ ] T034 [P] Add User-Agent header per Basecamp API guidelines to all API requests
- [ ] T035 [P] Create BasecampAccount admin actions in `web/integrations/admin.py` (manually disconnect, view token status)
- [ ] T036 [P] Add validation for OAuth callback parameters (code format, state format) before processing
- [ ] T037 [P] Document Basecamp OAuth setup in README or quickstart.md additions
- [ ] T038 [P] Add monitoring/alerting considerations for token refresh failures exceeding 5% threshold
- [ ] T039 Verify quickstart.md steps work end-to-end (register OAuth app, configure env, test flow)
- [ ] T040 Code review: Ensure follows constitution (SOLID, DRY, mirrors Dropbox pattern)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T004) completion - BLOCKS all user stories
- **User Stories (Phase 3-4)**: Both depend on Foundational phase (T005-T009) completion
  - User Story 1 (Phase 3) can start after Foundational - no dependencies on US2
  - User Story 2 (Phase 4) can start after Foundational - no dependencies on US1
  - **Can proceed in parallel** if team capacity allows
  - Or sequentially in priority order (P1 → P2) for MVP-first approach
- **Polish (Phase 5)**: Depends on US1 and US2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on US2
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on US1 (status works whether account connected or not)

**Independence Validation**: Each user story delivers value on its own:
- US1 alone: Users can connect Basecamp (even without status page showing details)
- US2 alone: Status page works (shows "Not Connected" if no OAuth flow implemented)
- Combined: Full integration with connection management and status visibility

### Within Each User Story

**User Story 1 (OAuth Flow)**:
- T010, T011 (auth service, API service) can run in parallel
- T012, T013, T014 (views) depend on T010, T011 completion
- T015-T019 (validation, enforcement, logging) depend on views being implemented
- T020 (frontend verification) can happen anytime after T012-T014

**User Story 2 (Status Display)**:
- T021, T023, T025 (strategy, serializer, validation) can run in parallel
- T022 (status endpoint) depends on T021, T023
- T024, T026, T027 (detection, degradation, caching) enhance T021, can be added incrementally
- T028, T029 (factory, config) can run in parallel, independent of status endpoint
- T030 (frontend verification) can happen anytime after T022

### Parallel Opportunities

- **Setup (Phase 1)**: T002, T003 can run in parallel
- **Foundational (Phase 2)**: T007, T008, T009 can run in parallel after T005-T006
- **User Story 1**: T010, T011 can run in parallel
- **User Story 2**: T021, T023, T025, T028, T029 can run in parallel
- **Polish (Phase 5)**: T031, T032, T033, T034, T035, T036, T037, T038 can all run in parallel
- **Cross-Story**: Once Foundational complete, US1 and US2 can proceed in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch authentication infrastructure tasks together:
Task: "Implement BasecampOAuthAuth service in web/integrations/basecamp/auth.py"
Task: "Implement BasecampService in web/integrations/basecamp/basecamp_service.py"

# After auth services complete, launch view implementations:
Task: "Implement OAuth initiation view in web/integrations/views.py (connect)"
Task: "Implement OAuth callback handler in web/integrations/views.py (callback)"  
Task: "Implement disconnect view in web/integrations/views.py (disconnect)"
```

## Parallel Example: User Story 2

```bash
# Launch status infrastructure tasks together:
Task: "Enhance BasecampStatusStrategy in web/integrations/status/strategies/basecamp.py"
Task: "Add Basecamp serializer in web/integrations/serializers/integrations.py"
Task: "Add environment validation in status strategy"
Task: "Extend cloud factory in web/integrations/cloud/factory.py"
Task: "Add Basecamp to cloud config in web/integrations/cloud/config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004) - ~30 minutes
2. Complete Phase 2: Foundational (T005-T009) - ~1 hour (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (T010-T020) - ~4-6 hours
4. **STOP and VALIDATE**: Test OAuth flow end-to-end independently
   - Register OAuth app, configure env, test connect/disconnect
   - Verify BasecampAccount records created/deleted
   - Confirm single-account enforcement works
5. Deploy/demo if ready - **MVP delivered!**

**MVP Scope**: Users can connect their Basecamp account via OAuth. This establishes the authentication foundation for all future Basecamp workflows (project linking, file uploads, message posting).

### Incremental Delivery

1. **Complete Setup + Foundational** → Foundation ready (~1.5 hours)
2. **Add User Story 1** → Test independently → **Deploy/Demo (MVP!)** (~4-6 hours total)
   - Value: Users can authorize Basecamp access
3. **Add User Story 2** → Test independently → Deploy/Demo (~3-4 hours)
   - Value: Users can monitor connection health
4. **Add Polish** → Enhance reliability → Deploy/Demo (~2-3 hours)
   - Value: Production-ready with monitoring and error handling

**Total Estimated Time**: ~11-15 hours (1.5-2 days) for complete feature

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T009) - ~1.5 hours
2. **Once Foundational is done**:
   - **Developer A**: User Story 1 (T010-T020) - OAuth flow
   - **Developer B**: User Story 2 (T021-T030) - Status display
   - Both can work in parallel (different files, no conflicts)
3. **Merge and integrate** - Stories complete and integrate independently
4. **Polish together** (T031-T040) - Cross-cutting improvements

**Parallel Completion Time**: ~6-8 hours (1 day) with 2 developers

---

## Task Count Summary

- **Total Tasks**: 40
- **Setup (Phase 1)**: 4 tasks
- **Foundational (Phase 2)**: 5 tasks (CRITICAL PATH)
- **User Story 1 (Phase 3)**: 11 tasks (OAuth connection flow)
- **User Story 2 (Phase 4)**: 10 tasks (Status visibility)
- **Polish (Phase 5)**: 10 tasks (Production readiness)

**Parallel Tasks**: 24 tasks marked [P] can run in parallel within their phase

---

## Success Criteria Mapping

Each task maps to success criteria from spec.md:

- **SC-001** (OAuth <2 min): T010-T014, T018 (efficient OAuth flow)
- **SC-002** (Status <1 sec): T021-T022, T027 (fast status checks with caching)
- **SC-003** (95% refresh): T031 (automatic token refresh)
- **SC-004** (Zero unauthorized access): T005, T017 (encrypted storage)
- **SC-005** (99% accurate status): T021-T025 (reliable status detection)
- **SC-006** (90% first-time success): T012-T014, T018 (clear error messages)
- **SC-007** (Complete logging): T019, T032 (authentication event audit trail)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [US1]/[US2] labels map tasks to specific user stories for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included per specification (tests are optional and not requested)
- Follow constitution: SOLID principles, DRY (mirrors Dropbox pattern), PEP 8
- Preserve existing comments in code
- Use python3 command explicitly on Linux

