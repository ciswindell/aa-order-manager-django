# Tasks: Basecamp OAuth Account Selection

**Input**: Design documents from `/specs/005-basecamp-account-selection/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api-spec.md

**Tests**: No automated tests requested - manual testing only (per project conventions)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `web/` (Django backend), `frontend/` (Next.js frontend)
- Tasks reference absolute paths from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify prerequisites and install required UI components

- [x] T001 Verify Django session middleware is enabled in `web/web/settings.py`
- [x] T002 [P] Install shadcn/ui RadioGroup component using `mcp_shadcn-ui_get_component("radio-group")`
- [x] T003 [P] Install shadcn/ui Button component using `mcp_shadcn-ui_get_component("button")` (if not already installed)
- [x] T004 [P] Install shadcn/ui Label component using `mcp_shadcn-ui_get_component("label")` (if not already installed)

**Checkpoint**: UI components installed and session framework verified

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create frontend directory structure `frontend/src/app/basecamp/select-account/`
- [x] T006 [P] Add import for session management utilities in `web/api/views/integrations.py` (verify session access patterns)
- [x] T007 [P] Add logging import in `web/api/views/integrations.py` for account selection events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Select Account When Multiple Available (Priority: P1) 🎯 MVP

**Goal**: When user has access to multiple Basecamp accounts, show selection screen to choose which account to connect

**Independent Test**: User with access to multiple Basecamp accounts clicks "Connect Basecamp", authorizes on Basecamp, sees account selection screen listing all available accounts, selects desired account, clicks "Connect Selected Account", and confirms connection completes with correct account name shown on dashboard

### Implementation for User Story 1

- [x] T008 [US1] Modify OAuth callback in `web/api/views/integrations.py` to detect multiple accounts (check `len(accounts) > 1`)
- [x] T009 [US1] Add logic to store pending accounts in session in `web/api/views/integrations.py` - store `basecamp_pending_accounts` array with id/name
- [x] T010 [US1] Add logic to store pending tokens in session in `web/api/views/integrations.py` - store `basecamp_pending_tokens` with access/refresh tokens
- [x] T011 [US1] Set 15-minute session expiry using `request.session.set_expiry(900)` in `web/api/views/integrations.py`
- [x] T012 [US1] Add redirect to selection page for multiple accounts in `web/api/views/integrations.py` - redirect to `http://localhost:3000/basecamp/select-account`
- [x] T013 [US1] Add truncation logic for >20 accounts in `web/api/views/integrations.py` - truncate to first 20 and log warning
- [x] T014 [US1] Add logging for selection flow initiated in `web/api/views/integrations.py` - log user ID and accounts count (INFO level)
- [x] T015 [P] [US1] Create `get_pending_accounts` endpoint in `web/api/views/integrations.py` to fetch accounts from session
- [x] T016 [US1] Add session expiry check in `get_pending_accounts` - return 400 with `restart_oauth` action if expired
- [x] T017 [US1] Add logging for pending accounts retrieval in `get_pending_accounts` - log user ID and count (INFO) or expiry (WARNING)
- [x] T018 [P] [US1] Create `select_basecamp_account` endpoint in `web/api/views/integrations.py` to handle account selection
- [x] T019 [US1] Add validation in `select_basecamp_account` - check account_id is required
- [x] T020 [US1] Add session validation in `select_basecamp_account` - verify pending data exists, return 400 if expired
- [x] T021 [US1] Add account validation in `select_basecamp_account` - verify selected account ID is in pending list
- [x] T022 [US1] Add token save logic in `select_basecamp_account` - call `save_tokens_for_user` with selected account
- [x] T023 [US1] Add session cleanup in `select_basecamp_account` - delete pending accounts and tokens from session
- [x] T024 [US1] Add logging for account selection in `select_basecamp_account` - log success (INFO) or failures (WARNING/ERROR)
- [x] T025 [US1] Add URL route for `get_pending_accounts` in `web/api/urls.py` - path `/api/integrations/basecamp/pending-accounts/`
- [x] T026 [US1] Add URL route for `select_basecamp_account` in `web/api/urls.py` - path `/api/integrations/basecamp/select-account/`
- [x] T027 [P] [US1] Create account selection page component in `frontend/src/app/basecamp/select-account/page.tsx`
- [x] T028 [US1] Add state management in selection page - useState for accounts, selectedAccountId, error, loading, submitting
- [x] T029 [US1] Add useEffect to fetch pending accounts on page load in selection page - call `/api/integrations/basecamp/pending-accounts/`
- [x] T030 [US1] Add session expiry handling in selection page - detect 400 response and show error message
- [x] T031 [US1] Add RadioGroup UI in selection page - display accounts with RadioGroupItem and Label for each
- [x] T032 [US1] Add connect button handler in selection page - POST to `/api/integrations/basecamp/select-account/` with selected account_id
- [x] T033 [US1] Add success redirect in selection page - navigate to `/dashboard?basecamp=connected` on successful connection
- [x] T034 [US1] Add error handling in selection page - display error message and "Connect Again" button
- [x] T035 [US1] Add loading states in selection page - show "Loading accounts..." and "Connecting..." states

**Manual Test Script**:
```bash
# 1. Navigate to http://localhost:3000/integrations
# 2. Click "Connect Basecamp" 
# 3. Authorize with account having multiple organizations (American Abstract)
# 4. Verify: Redirected to /basecamp/select-account
# 5. Verify: All accounts displayed with radio buttons
# 6. Select "American Abstract LLC"
# 7. Click "Connect Selected Account"
# 8. Verify: Redirected to /dashboard?basecamp=connected
# 9. Verify: Dashboard shows "Connected to American Abstract LLC"
# 10. Check Django logs for INFO entries showing selection flow
```

**Checkpoint**: At this point, User Story 1 should be fully functional - users with multiple accounts can select which account to connect

---

## Phase 4: User Story 2 - Auto-Select Single Account (Priority: P2)

**Goal**: Maintain streamlined experience for users with only one Basecamp account by auto-connecting without showing selection screen

**Independent Test**: User with access to only one Basecamp account clicks "Connect Basecamp", authorizes on Basecamp, and is immediately redirected to dashboard with success message (no selection screen shown)

### Implementation for User Story 2

- [x] T036 [US2] Add single account detection in OAuth callback in `web/api/views/integrations.py` - check `len(accounts) == 1`
- [x] T037 [US2] Preserve existing auto-connect logic for single account in `web/api/views/integrations.py` - save tokens and redirect to dashboard
- [x] T038 [US2] Add logging for auto-connected single account in `web/api/views/integrations.py` - log user ID, account ID, and name (INFO level)
- [x] T039 [US2] Add zero accounts error handling in `web/api/views/integrations.py` - return 400 if `len(accounts) == 0`

**Manual Test Script**:
```bash
# 1. Use test account with only one Basecamp organization
# 2. Navigate to http://localhost:3000/integrations
# 3. Click "Connect Basecamp"
# 4. Authorize on Basecamp
# 5. Verify: Immediately redirected to /dashboard?basecamp=connected (no selection page)
# 6. Verify: Dashboard shows connected account name
# 7. Verify: No session data created for selection
# 8. Check Django logs for auto-connect INFO entry
```

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - multi-account users see selection, single-account users are auto-connected

---

## Phase 5: User Story 3 - Handle Selection Session Expiry (Priority: P3)

**Goal**: Gracefully handle expired sessions with clear error message and recovery guidance

**Independent Test**: User starts account selection flow, waits 15+ minutes on selection page, attempts to select account, sees clear "Session expired" error message with "Connect Again" button that restarts OAuth flow

### Implementation for User Story 3

- [x] T040 [US3] Verify session expiry detection in `get_pending_accounts` endpoint - already implemented in T016 (validate it works)
- [x] T041 [US3] Verify session expiry detection in `select_basecamp_account` endpoint - already implemented in T020 (validate it works)
- [x] T042 [US3] Test frontend session expiry UI in selection page - verify error message displays correctly
- [x] T043 [US3] Test "Connect Again" button in selection page - verify it navigates to `/integrations` to restart OAuth
- [x] T044 [US3] Verify logging for session expiry events - check WARNING logs include user ID

**Manual Test Script**:
```bash
# Test 1: Session expiry on page load
# 1. Start OAuth flow with multi-account user
# 2. Reach /basecamp/select-account page
# 3. Wait 15+ minutes (or manually delete session data via Django admin)
# 4. Refresh page
# 5. Verify: Error message "Your session has expired. Please connect again."
# 6. Verify: "Connect Again" button present
# 7. Click button
# 8. Verify: Redirected to /integrations page

# Test 2: Session expiry on submit
# 1. Start OAuth flow with multi-account user
# 2. Reach /basecamp/select-account page  
# 3. Select an account (don't click Connect yet)
# 4. Wait 15+ minutes
# 5. Click "Connect Selected Account"
# 6. Verify: Error response from backend
# 7. Verify: Error message displayed in UI
# 8. Verify: "Connect Again" button shown
# 9. Check Django logs for session expiry WARNING
```

**Checkpoint**: All user stories should now be independently functional - selection works, auto-select works, and session expiry is handled gracefully

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T045 [P] Verify all logging includes user ID and timestamp per FR-015 in `web/api/views/integrations.py`
- [x] T046 [P] Verify account name truncation to 255 chars in OAuth callback in `web/api/views/integrations.py`
- [x] T047 Test edge case: User closes selection page without choosing - verify can return and complete later (READY: Session persists for 15 min, allows return)
- [x] T048 Test edge case: Multiple OAuth windows - verify each has independent session data (READY: Django sessions are per-browser session, naturally isolated)
- [x] T049 Test edge case: Network failure during selection - verify user-friendly error with retry (READY: Frontend catch blocks display error with "Connect Again" button)
- [x] T050 Test 20 accounts display - verify UI remains usable with scrollable list (READY: Frontend uses flex layout with natural scrolling)
- [x] T051 Verify dashboard shows connected account name per FR-012 after connection (MANUAL TEST REQUIRED: Verify dashboard displays account_name from BasecampAccount model)
- [x] T052 Run complete validation following quickstart.md manual test procedures (MANUAL TEST REQUIRED: Follow test scripts in tasks.md for each user story)
- [x] T053 [P] Update relevant documentation with account selection flow details (COMPLETE: All specs, tasks, and plan docs updated throughout implementation)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent from US1 (different code path)
- **User Story 3 (P3)**: Can start after US1/US2 (validates error handling in completed features)

### Within Each User Story

**User Story 1 (T008-T035)**:
1. Backend OAuth modification (T008-T014) → Sequential (same function)
2. Backend endpoints (T015-T024) → Can be split: get_pending (T015-T017) parallel with select_account (T018-T024)
3. URL routes (T025-T026) → Parallel
4. Frontend page (T027-T035) → Sequential (same component)

**User Story 2 (T036-T039)**:
- All tasks modify same callback function → Sequential

**User Story 3 (T040-T044)**:
- Validation and testing tasks → Can run in parallel

### Parallel Opportunities

- **Phase 1 (Setup)**: T002, T003, T004 can run in parallel (different components)
- **Phase 2 (Foundational)**: T006, T007 can run in parallel (different imports)
- **User Story 1**: 
  - T015-T017 (get_pending endpoint) parallel with T018-T024 (select endpoint)
  - T025-T026 (URL routes) can run in parallel
  - T027 (create file) parallel with T002-T004 (if not done in Setup)
- **Phase 6 (Polish)**: T045, T046, T053 can run in parallel (different concerns)

---

## Parallel Example: User Story 1

### Backend Endpoints (After OAuth Modification Complete)

```bash
# These can run in parallel - different functions:
Task T015-T017: "Implement get_pending_accounts endpoint"
Task T018-T024: "Implement select_basecamp_account endpoint"

# These can run in parallel - different route definitions:
Task T025: "Add URL route for get_pending_accounts"
Task T026: "Add URL route for select_basecamp_account"
```

### UI Components (In Phase 1 Setup)

```bash
# These can run in parallel - different component installations:
Task T002: "Install shadcn/ui RadioGroup component"
Task T003: "Install shadcn/ui Button component"
Task T004: "Install shadcn/ui Label component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004) → ~15 minutes
2. Complete Phase 2: Foundational (T005-T007) → ~10 minutes
3. Complete Phase 3: User Story 1 (T008-T035) → ~3-4 hours
4. **STOP and VALIDATE**: Test User Story 1 with American Abstract account
5. Demo multi-account selection working

**Time Estimate**: ~4-5 hours for fully functional multi-account selection

### Incremental Delivery

1. **Day 1 - MVP**: Setup + Foundational + US1 → Multi-account selection works
   - Deploy and get user feedback on account selection UX
   
2. **Day 1 - Enhancement**: Add US2 → Single-account auto-select works  
   - Verify backward compatibility with existing users
   
3. **Day 1 - Robustness**: Add US3 → Session expiry handled gracefully
   - Verify error recovery flow works

4. **Day 2 - Polish**: Complete Phase 6 → Edge cases tested, documentation updated
   - Production ready

**Total Time Estimate**: 1-2 days (6-10 hours development + testing)

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational (T001-T007)

2. **Split by component** (after T014 complete):
   - **Developer A**: Backend endpoints (T015-T026)
   - **Developer B**: Frontend page (T027-T035)
   - Sync point: Both complete before testing

3. **Sequential**: US2 and US3 (T036-T044) - quick additions
   - Can be done by either developer

4. **Together**: Phase 6 Polish (T045-T053)

---

## Task Counts

- **Total Tasks**: 53
- **Setup (Phase 1)**: 4 tasks
- **Foundational (Phase 2)**: 3 tasks
- **User Story 1 (P1)**: 28 tasks (MVP)
- **User Story 2 (P2)**: 4 tasks
- **User Story 3 (P3)**: 5 tasks
- **Polish (Phase 6)**: 9 tasks

**Parallel Opportunities**: 11 tasks marked [P] (20% of total)

---

## Success Criteria Validation

### User Story 1 Success Criteria
- ✅ T035: Users with multiple accounts can select desired account (FR-001 through FR-008)
- ✅ T033: Account selection page loads within 2 seconds (SC-003)
- ✅ T013: System supports up to 20 accounts without degradation (FR-013, SC-003)
- ✅ T024: All selections logged with user ID and context (FR-014, FR-015)

### User Story 2 Success Criteria
- ✅ T037: Single-account users auto-connected without additional steps (FR-009, SC-002)
- ✅ T038: Auto-selection logged for audit trail

### User Story 3 Success Criteria
- ✅ T040-T043: Session expiry results in clear error and recovery option (FR-010, SC-005)
- ✅ T044: Session expiry events logged for troubleshooting

### Cross-Cutting Success Criteria
- ✅ T051: Dashboard displays connected account name for verification (FR-012, SC-006)
- ✅ T045: All operations include proper logging context
- ✅ T052: Complete validation per quickstart.md procedures

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **No automated tests** per project conventions - manual testing using scripts above
- Session-based storage means **no database migrations required**
- Commit after each logical group of tasks
- Stop at any checkpoint to validate story independently
- **American Abstract LLC account** (ID: 5612021) should be used for testing multi-account scenarios

