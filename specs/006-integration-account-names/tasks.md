# Tasks: Integration Account Names Display

**Feature**: Integration Account Names Display  
**Branch**: `006-integration-account-names`  
**Created**: November 2, 2025  
**Status**: Ready for implementation

## Overview

Display account names and connection information on the integrations page to help users identify which specific accounts they're connected to. Feature organized into 3 independent user stories deliverable incrementally.

**Total Tasks**: 26 tasks across 5 phases  
**Estimated Time**: 2-3 hours  
**Parallel Opportunities**: 8 tasks marked [P]

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify environment and prepare for implementation

- [x] T001 Verify Django environment running via `docker compose ps`
- [x] T002 Verify frontend dev server running on `localhost:3000`
- [x] T003 Create log masking utility in `web/integrations/utils/log_masking.py` for PII protection (email/name masking)

**Checkpoint**: Development environment ready, log masking utility available for all phases

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend core data structures used by all user stories

**Goal**: Update IntegrationStatus DTO to support new account identification fields

- [x] T004 Add `account_name` field (Optional[str]) to IntegrationStatus dataclass in `web/integrations/status/dto.py`
- [x] T005 Add `account_email` field (Optional[str]) to IntegrationStatus dataclass in `web/integrations/status/dto.py`
- [x] T006 Add `connected_at` field (Optional[datetime]) to IntegrationStatus dataclass in `web/integrations/status/dto.py`
- [x] T007 Update IntegrationStatusSerializer in `web/api/serializers.py` to include new fields (account_name, account_email, connected_at)
- [x] T008 Extend IntegrationStatus TypeScript interface in `frontend/src/lib/api/types.ts` with optional fields

**Checkpoint**: Core data structures extended, ready for strategy implementations

---

## Phase 3: User Story 1 - Display Basecamp Account Name (Priority: P1) 🎯 MVP

**Goal**: Show Basecamp organization name on integrations card

**Why this priority**: Quick win - data already exists in database, no migration needed, provides immediate value for multi-account users

**Independent Test**: User with connected Basecamp account "American Abstract LLC" views integrations page and sees "Connected as: American Abstract LLC" displayed on Basecamp card

### Implementation for User Story 1

- [x] T009 [US1] Modify BasecampStatusStrategy.assess() in `web/integrations/status/strategies/basecamp.py` to retrieve account_name from tokens
- [x] T010 [US1] Add logic to get BasecampAccount.created_at for connected_at field in `web/integrations/status/strategies/basecamp.py`
- [x] T011 [US1] Set account_name and connected_at on IntegrationStatus object before returning in `web/integrations/status/strategies/basecamp.py`
- [x] T012 [P] [US1] Update integrations page component in `frontend/src/app/dashboard/integrations/page.tsx` to display account_name when available
- [x] T013 [P] [US1] Add CSS truncation for account names >50 chars with ellipsis in `frontend/src/app/dashboard/integrations/page.tsx`
- [x] T014 [P] [US1] Add title attribute to account name display for full text on hover in `frontend/src/app/dashboard/integrations/page.tsx`

**Manual Test Script**:
```bash
# 1. Ensure Basecamp account "American Abstract LLC" is connected
# 2. Navigate to http://localhost:3000/dashboard/integrations
# 3. Verify Basecamp card shows "Connected as: American Abstract LLC"
# 4. Verify no additional clicks needed to see account name
# 5. Test with long account name (>50 chars) - verify truncation with ellipsis
# 6. Hover over truncated name - verify full name appears in tooltip
```

**Checkpoint**: Basecamp account names display correctly. P1 story complete and independently testable. MVP deliverable.

---

## Phase 4: User Story 2 - Display Dropbox Account Information (Priority: P2)

**Goal**: Show Dropbox display name and email on integrations card

**Why this priority**: Requires database migration and OAuth callback updates. Provides clarity for users with multiple Dropbox accounts.

**Independent Test**: User connects new Dropbox account, completes OAuth, views integrations page and sees "Connected as: Chris Windell (chris@example.com)" on Dropbox card

### Database Migration

- [x] T015 [US2] Add display_name field (CharField max_length=255, blank=True, default='') to DropboxAccount model in `web/integrations/models.py`
- [x] T016 [US2] Add email field (EmailField blank=True, default='') to DropboxAccount model in `web/integrations/models.py`
- [x] T017 [US2] Create and run Django migration: `docker compose exec web python3 manage.py makemigrations integrations --name add_dropbox_account_info`
- [x] T018 [US2] Apply migration: `docker compose exec web python3 manage.py migrate`

### OAuth Enhancement

- [x] T019 [US2] Modify dropbox_callback in `web/api/views/integrations.py` to create Dropbox client after token exchange
- [x] T020 [US2] Add call to dbx.users_get_current_account() in `web/api/views/integrations.py` to fetch account info
- [x] T021 [US2] Extract display_name from account_info.name.display_name (truncate to 255 chars) in `web/api/views/integrations.py`
- [x] T022 [US2] Extract email from account_info.email in `web/api/views/integrations.py`
- [x] T023 [US2] Add retry logic: if fetch fails, wait 2 seconds and retry once in `web/api/views/integrations.py`
- [x] T024 [US2] Include display_name and email in tokens dict passed to save_tokens_for_user in `web/api/views/integrations.py`
- [x] T025 [US2] Apply log masking to account info in OAuth logs using masking utility in `web/api/views/integrations.py`

### Token Storage

- [x] T026 [US2] Update save_tokens_for_user in `web/integrations/utils/token_store.py` to save display_name field when provider='dropbox'
- [x] T027 [US2] Update save_tokens_for_user in `web/integrations/utils/token_store.py` to save email field when provider='dropbox'

### Status Strategy

- [x] T028 [US2] Modify DropboxStatusStrategy.assess() in `web/integrations/status/strategies/dropbox.py` to query DropboxAccount model
- [x] T029 [US2] Extract display_name from account.display_name (set to None if empty) in `web/integrations/status/strategies/dropbox.py`
- [x] T030 [US2] Extract email from account.email (set to None if empty) in `web/integrations/status/strategies/dropbox.py`
- [x] T031 [US2] Extract connected_at from account.created_at in `web/integrations/status/strategies/dropbox.py`
- [x] T032 [US2] Set account_name, account_email, and connected_at on IntegrationStatus before returning in `web/integrations/status/strategies/dropbox.py`

### Frontend Display

- [x] T033 [P] [US2] Update Dropbox card display in `frontend/src/app/dashboard/integrations/page.tsx` to show account_name and account_email in format "Name (email)"
- [x] T034 [P] [US2] Add conditional rendering for legacy connections (show generic "Connected" if account_name is null) in `frontend/src/app/dashboard/integrations/page.tsx`
- [x] T035 [P] [US2] Apply same CSS truncation and hover tooltip as Basecamp in `frontend/src/app/dashboard/integrations/page.tsx`

**Manual Test Script**:
```bash
# Test 1: New Dropbox connection
# 1. Disconnect existing Dropbox connection: http://localhost:3000/dashboard/integrations
# 2. Click "Connect Dropbox"
# 3. Complete OAuth authorization
# 4. Verify integrations page shows display name and email
# 5. Verify format is "Connected as: [Name] ([email])"

# Test 2: OAuth API failure handling
# 1. Monitor Django logs during new connection
# 2. If fetch fails, verify retry attempt after 2 seconds
# 3. If both fail, verify connection saved with generic "Connected" message

# Test 3: Legacy connection display
# 1. Create test account without display_name/email via Django shell
# 2. Verify integrations page shows generic "Connected" (not blank or error)
# 3. Reconnect Dropbox
# 4. Verify account info now displays
```

**Checkpoint**: Dropbox account information displays for new connections. Legacy connections show generic message. P2 story complete and independently testable.

---

## Phase 5: User Story 3 - Show Connection Timestamps (Priority: P3)

**Goal**: Display when each integration was first connected

**Why this priority**: Optional enhancement using existing created_at data. Helps users track integration history.

**Independent Test**: User views integrations page and sees "Connected on: Nov 1, 2025" below each connected integration's account name

### Implementation for User Story 3

- [x] T036 [P] [US3] Verify BasecampStatusStrategy populates connected_at field (already done in T010, verify only)
- [x] T037 [P] [US3] Verify DropboxStatusStrategy populates connected_at field (already done in T031, verify only)
- [x] T038 [US3] Add connection date display in `frontend/src/app/dashboard/integrations/page.tsx` using format(new Date(connected_at), 'MMM d, yyyy')
- [x] T039 [US3] Add conditional rendering (only show if connected_at exists) in `frontend/src/app/dashboard/integrations/page.tsx`
- [x] T040 [US3] Style connection date with text-xs and text-muted-foreground for subtle display in `frontend/src/app/dashboard/integrations/page.tsx`

**Manual Test Script**:
```bash
# 1. View integrations page with at least one connected integration
# 2. Verify "Connected on: [Date]" displays below account name
# 3. Verify date format matches "Nov 2, 2025" pattern
# 4. Verify date is accurate (matches actual connection date)
# 5. Test with both Basecamp and Dropbox connections
```

**Checkpoint**: Connection timestamps display for all integrations. P3 story complete and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and edge case handling

- [x] T041 Verify log masking applied to all account name and email log statements in OAuth and status code
- [x] T042 Test edge case: Account name exactly 50 characters (verify no ellipsis, no truncation)
- [x] T043 Test edge case: Account name 51 characters (verify truncation at 50 with "...")
- [x] T044 Test edge case: Account name with UTF-8 characters (emojis, non-Latin) - verify displays correctly
- [x] T045 Test edge case: Dropbox API timeout during OAuth - verify connection still saved
- [x] T046 Review all modified files for PEP 8 compliance (Python) and TypeScript strict types
- [x] T047 Verify no duplicate code introduced - check for reusable utilities extracted
- [x] T048 Run linter on modified files: `docker compose exec web python3 -m flake8 web/integrations/ web/api/`
- [x] T049 Verify frontend builds without errors: `cd frontend && npm run build`
- [x] T050 Perform final manual test of all 3 user stories following test scripts above

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on at least one user story being complete (can run after P1 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent from US1 (different models/flows)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent from US1/US2 (display enhancement only)

**Key Insight**: All 3 user stories are INDEPENDENT after foundational phase. Can be developed in parallel or any order.

### Within Each User Story

**User Story 1 (T009-T014)**:
1. Backend strategy updates (T009-T011) → Sequential (same file)
2. Frontend display (T012-T014) → Can run in parallel with backend after T004-T008 complete

**User Story 2 (T015-T035)**:
1. Database migration (T015-T018) → Sequential (must complete first)
2. After migration: These can run in parallel:
   - OAuth enhancement (T019-T025)
   - Token storage (T026-T027)
   - Status strategy (T028-T032)
3. Frontend display (T033-T035) → After backend complete

**User Story 3 (T036-T040)**:
- T036-T037: Verification only (parallel)
- T038-T040: Frontend display (sequential, same file)

### Parallel Opportunities

- **Phase 2 (Foundational)**: T004-T006 can run in parallel (different fields in same file, quick changes)
- **User Story 1**: T012-T014 can run in parallel (different concerns in same file)
- **User Story 2**: 
  - After migration: T019-T025 parallel with T026-T027 parallel with T028-T032 (different files)
  - T033-T035 can run in parallel (different display logic)
- **User Story 3**: T036-T037 can run in parallel (verification tasks)

---

## Parallel Example: User Story 2

### After Migration Complete

```bash
# These can run in parallel - different files/concerns:
Task Group A (T019-T025): "Update OAuth callback to fetch Dropbox account info"
Task Group B (T026-T027): "Update token storage to save account info"
Task Group C (T028-T032): "Update status strategy to include account info"

# Then:
Task Group D (T033-T035): "Update frontend display for Dropbox" (after all backend complete)
```

### Backend Components (After Database Migration)

```bash
# OAuth enhancement - web/api/views/integrations.py
Tasks T019-T025

# Token storage - web/integrations/utils/token_store.py
Tasks T026-T027

# Status strategy - web/integrations/status/strategies/dropbox.py
Tasks T028-T032
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003) → ~10 minutes
2. Complete Phase 2: Foundational (T004-T008) → ~15 minutes
3. Complete Phase 3: User Story 1 (T009-T014) → ~30 minutes
4. **STOP and VALIDATE**: Test Basecamp account name display
5. Demo P1 working

**Time Estimate**: ~1 hour for fully functional Basecamp account name display

### Incremental Delivery

1. **Hour 1 - MVP**: Setup + Foundational + US1 → Basecamp account names visible
   - Deploy and get user feedback on account identification improvement
   
2. **Hour 2-2.5 - Enhancement**: Add US2 → Dropbox account info visible
   - Verify backward compatibility with legacy connections
   - Database migration in non-peak hours
   
3. **Hour 2.5-3 - Polish**: Add US3 → Connection timestamps visible
   - Optional enhancement, can defer if time constrained

4. **Final 30 min - Validation**: Complete Phase 6 → Edge cases tested, production ready

**Total Time Estimate**: 2-3 hours (MVP in 1 hour, full feature in 3 hours)

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup + Foundational (T001-T008) → ~25 minutes

2. **Split by user story** (after T008 complete):
   - **Developer A**: User Story 1 (T009-T014) → Basecamp
   - **Developer B**: User Story 2 Migration (T015-T018) → Database prep
   - Sync point: Both complete before US2 backend work

3. **Continue parallel**:
   - **Developer A**: User Story 2 OAuth (T019-T025) + Token Store (T026-T027)
   - **Developer B**: User Story 2 Status Strategy (T028-T032) + User Story 3 (T036-T040)

4. **Together**: Frontend Display (T012-T014, T033-T035, T038-T040) + Polish (T041-T050)

---

## Task Counts

- **Total Tasks**: 50
- **Setup (Phase 1)**: 3 tasks
- **Foundational (Phase 2)**: 5 tasks (BLOCKS all user stories)
- **User Story 1 (P1)**: 6 tasks (MVP - Quick win)
- **User Story 2 (P2)**: 21 tasks (Main feature)
- **User Story 3 (P3)**: 5 tasks (Optional enhancement)
- **Polish (Phase 6)**: 10 tasks

**Parallel Opportunities**: 8 tasks marked [P] (16% of total)

---

## Success Criteria Validation

### User Story 1 Success Criteria
- ✅ T014: Users can identify Basecamp organization without additional clicks (FR-001, SC-001)
- ✅ T011: Account name retrieved from existing database field (FR-002)
- ✅ T013: UI handles names up to 255 chars with truncation at 50 (FR-012, SC-005)
- ✅ T009-T011: Account name displays immediately after multi-account selection (FR-004)

### User Story 2 Success Criteria
- ✅ T033: Users can identify Dropbox account by name and email (FR-007, SC-002)
- ✅ T020: Account info fetched from Dropbox API during OAuth (FR-006)
- ✅ T023: Retry logic handles API failures gracefully (FR-008)
- ✅ T034: Legacy connections show generic message (handled gracefully)
- ✅ T024-T025: 100% of new connections capture account info (FR-005, SC-004)

### User Story 3 Success Criteria
- ✅ T038: Connection date displays in user-friendly format (FR-011)
- ✅ T010, T031: Timestamps extracted from created_at field (FR-010)

### Cross-Cutting Success Criteria
- ✅ T041: All operations include proper logging with PII masking (FR-016)
- ✅ T042-T044: Edge cases handled (long names, UTF-8, API failures)
- ✅ T048-T049: Code quality maintained (PEP 8, TypeScript strict)

---

## Notes

- [P] tasks = different files/concerns, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **No automated tests** per project conventions - manual testing using scripts above
- Database migration (US2) is reversible if needed
- All tasks include specific file paths for immediate execution
- Commit after completing each user story phase
- MVP (US1) can be deployed independently before US2/US3

