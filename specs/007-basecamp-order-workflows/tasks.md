# Tasks: Basecamp Order Workflows

**Input**: Design documents from `/specs/007-basecamp-order-workflows/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.md, quickstart.md

**Tests**: NOT REQUESTED - Tests are optional per constitution and not specified in feature spec

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Each user story delivers a complete, testable increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `web/` (backend), `frontend/src/` (frontend)
- Backend: Django app structure (`web/orders/services/`, `web/api/`)
- Frontend: Next.js App Router structure (`frontend/src/app/`, `frontend/src/lib/`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and project structure for workflow service

**Estimated Time**: 30 minutes

- [x] T001 Add Basecamp project ID environment variables to `.env` (BASECAMP_PROJECT_FEDERAL_RUNSHEETS, BASECAMP_PROJECT_FEDERAL_ABSTRACTS, BASECAMP_PROJECT_STATE_RUNSHEETS, BASECAMP_PROJECT_STATE_ABSTRACTS)
- [x] T002 Add Basecamp project ID settings to `web/order_manager_project/settings.py` (load from environment variables with env() function)
- [x] T003 Create workflow service directory structure in `web/orders/services/workflow/` (workflow/, workflow/strategies/)
- [x] T004 Create `web/orders/services/workflow/__init__.py` (empty init file)
- [x] T005 [P] Create `web/orders/services/workflow/strategies/__init__.py` (empty init file)
- [x] T006 [P] Create `web/orders/views/workflows.py` (empty file, will hold API view)
- [x] T007 [P] Create `web/api/serializers/workflows.py` (empty file, will hold serializers)
- [x] T008 [P] Create `frontend/src/lib/api/workflows.ts` (empty file, will hold API client)

**Verification**: Directory structure exists, settings load without errors (`docker compose exec web python3 manage.py check`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core workflow infrastructure that MUST be complete before ANY user story can be implemented

**Estimated Time**: 4 hours

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Implement ProductConfig dataclass in `web/orders/services/workflow/config.py` (frozen dataclass with name, project_id_env_var, agency, report_types, workflow_strategy fields)
- [x] T010 [P] Implement WorkflowStrategy abstract base class in `web/orders/services/workflow/strategies/base.py` (ABC with create_workflow abstract method)
- [x] T011 [P] Implement WorkflowResult dataclass in `web/orders/services/workflow/executor.py` (success, workflows_created, failed_products, error_details, total_count fields)
- [x] T012 Implement WorkflowExecutor class skeleton in `web/orders/services/workflow/executor.py` (execute method signature, product detection logic, error handling structure)
- [x] T013 Create PRODUCT_CONFIGS dictionary skeleton in `web/orders/services/workflow/config.py` (4 ProductConfig entries: federal_runsheets, federal_abstracts, state_runsheets, state_abstracts with forward references)
- [x] T014 Implement WorkflowResultSerializer in `web/api/serializers/workflows.py` (serialize WorkflowResult dataclass with success, workflows_created, failed_products, total_count, message fields)
- [x] T015 Create API view skeleton in `web/orders/views/workflows.py` (trigger_workflow function with authentication, order validation, Basecamp connection check)
- [x] T016 Add URL route in `web/api/urls.py` (POST /api/orders/<int:order_id>/workflows/ → trigger_workflow view)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

**Verification**: All imports resolve, settings reference correct environment variables, URL route registered

---

## Phase 3: User Story 1 - Create Federal Runsheet Workflows (Priority: P1) 🎯 MVP

**Goal**: User clicks "Push to Basecamp" on order with Federal runsheet reports → creates 1 to-do list in Federal Runsheets project with 1 task per unique BLM lease (grouped by lease number)

**Independent Test**: Create test order with 2 BLM RUNSHEET reports referencing same lease NMNM 11111 → trigger workflow → verify 1 to-do list with 1 to-do showing both legal descriptions

**Estimated Time**: 1 day

**⚠️ CORRECTED 2025-11-02**: Changed from "1 to-do per report" to "1 to-do per unique lease" with grouped legal descriptions. See `CORRECTIONS.md` for details.

### Implementation for User Story 1 (Backend - Pattern A)

- [X] T017 [P] [US1] Implement RunsheetWorkflowStrategy class in `web/orders/services/workflow/strategies/runsheet.py` (inherit from WorkflowStrategy)
- [X] T018 [US1] Implement `_get_project_id()` helper method in `web/orders/services/workflow/strategies/runsheet.py` (load project ID from Django settings using ProductConfig.project_id_env_var, raise ValueError if missing)
- [X] T019 [US1] Implement `_group_reports_by_lease()` helper method in `web/orders/services/workflow/strategies/runsheet.py` (group reports by lease number, return dict mapping lease_number to (reports_list, lease_object)) **[CORRECTED]**
- [X] T020 [US1] Implement `_create_todolist()` method in `web/orders/services/workflow/strategies/runsheet.py` (create to-do list with format "Order {number} - {YYYYMMDD}", include delivery_link in description)
- [X] T021 [US1] Implement `_create_todos()` method in `web/orders/services/workflow/strategies/runsheet.py` (for each unique lease: create ONE to-do with all legal descriptions from reports sharing that lease, format as "Reports Needed:" bulleted list + "Lease Data:" archive link) **[CORRECTED]**
- [X] T022 [US1] Implement `create_workflow()` main method in `web/orders/services/workflow/strategies/runsheet.py` (orchestrate project ID retrieval, report grouping by lease, to-do list creation, to-do creation, return dict with todolist_ids and todo_count) **[CORRECTED]**
- [X] T023 [US1] Update PRODUCT_CONFIGS in `web/orders/services/workflow/config.py` (set federal_runsheets workflow_strategy to RunsheetWorkflowStrategy class)
- [X] T024 [US1] Implement product detection logic in WorkflowExecutor.execute() in `web/orders/services/workflow/executor.py` (filter reports by report_type="RUNSHEET" and agency="BLM", instantiate RunsheetWorkflowStrategy, call create_workflow())
- [X] T025 [US1] Add comprehensive logging to RunsheetWorkflowStrategy in `web/orders/services/workflow/strategies/runsheet.py` (INFO for success, ERROR for failures with order_id, user_id, report IDs, lease IDs, exc_info=True)
- [X] T026 [US1] Implement error handling in WorkflowExecutor.execute() for US1 in `web/orders/services/workflow/executor.py` (catch ValueError for config errors, catch HTTPError for API failures, append to workflows_created or failed_products, continue with other products)
- [X] T027 [US1] Complete trigger_workflow API view in `web/orders/views/workflows.py` (instantiate WorkflowExecutor, call execute(), serialize WorkflowResult, return 200 OK with success or 422/500 with errors)

**Checkpoint**: At this point, Federal Runsheet workflows can be created via API. User Story 1 backend is complete and testable.

### Frontend for User Story 1

- [X] T028 [P] [US1] Implement WorkflowResult TypeScript interface in `frontend/src/lib/api/types.ts` (success, workflows_created, failed_products, total_count, message fields)
- [X] T029 [P] [US1] Implement triggerWorkflow API client function in `frontend/src/lib/api/workflows.ts` (POST to /api/orders/{id}/workflows/, return WorkflowResult, use axios with withCredentials)
- [X] T030 [US1] Add "Push to Basecamp" button to order details page in `frontend/src/app/dashboard/orders/[id]/page.tsx` (import triggerWorkflow, add loading state, add click handler with toast notifications)
- [X] T031 [US1] Implement button click handler in `frontend/src/app/dashboard/orders/[id]/page.tsx` (call triggerWorkflow, show loading state, display success toast with message, display error toast on failure, handle 422/500 errors)

**Checkpoint**: User Story 1 is fully functional end-to-end - Users can create Federal Runsheet workflows via button click

**Manual Verification**:
1. Create order with 2 BLM RUNSHEET reports, 3 BLM leases
2. Navigate to order details page
3. Click "Push to Basecamp" button
4. Verify success toast appears
5. Check Federal Runsheets Basecamp project for new to-do list with 3 tasks

---

## Phase 4: User Story 2 - Create Federal Abstract Workflows (Priority: P2)

**Goal**: User clicks "Push to Basecamp" on order with Federal abstract reports → creates 1 to-do list per report in Federal Abstracts project with 6 department groups and workflow steps

**Independent Test**: Create test order with 1 BLM BASE_ABSTRACT report containing 2 BLM leases → trigger workflow → verify 1 to-do list with 6 groups (Setup, Workup, Imaging, Indexing, Assembly, Delivery) and fixed/lease-specific steps

**Estimated Time**: 1 day

### Implementation for User Story 2 (Backend - Pattern B)

- [ ] T032 [P] [US2] Implement AbstractWorkflowStrategy class in `web/orders/services/workflow/strategies/abstract.py` (inherit from WorkflowStrategy)
- [ ] T033 [US2] Define WORKFLOW_GROUPS constant in `web/orders/services/workflow/strategies/abstract.py` (list: Setup, Workup, Imaging, Indexing, Assembly, Delivery)
- [ ] T034 [US2] Define WORKFLOW_STEPS placeholder structure in `web/orders/services/workflow/strategies/abstract.py` (dict mapping groups to step lists, include lease-specific placeholders like "File Index NMLC-{lease_number}")
- [ ] T035 [US2] Implement `_get_project_id()` helper method in `web/orders/services/workflow/strategies/abstract.py` (load project ID from Django settings, raise ValueError if missing)
- [ ] T036 [US2] Implement `_extract_abstract_type()` helper method in `web/orders/services/workflow/strategies/abstract.py` (extract "Base", "Supplemental", or "DOL" from report_type enum)
- [ ] T037 [US2] Implement `_create_todolist()` method in `web/orders/services/workflow/strategies/abstract.py` (create to-do list per report with format "Order {number}- {abstract_type} Abstract {report_id} - {YYYYMMDD}", include report type, date range, lease numbers, legal_description, delivery_link in description)
- [ ] T038 [US2] Implement `_create_groups()` method in `web/orders/services/workflow/strategies/abstract.py` (create 6 Basecamp groups in order using BasecampService.create_group(), return dict mapping group name to group_id)
- [ ] T039 [US2] Implement `_create_steps()` method in `web/orders/services/workflow/strategies/abstract.py` (for each group: create fixed steps, create lease-specific steps with {lease_number} substitution, assign to group via group_id parameter)
- [ ] T040 [US2] Implement `create_workflow()` main method in `web/orders/services/workflow/strategies/abstract.py` (for each report: create to-do list, create groups, create steps, collect todolist_ids and todo_count)
- [ ] T041 [US2] Update PRODUCT_CONFIGS in `web/orders/services/workflow/config.py` (set federal_abstracts workflow_strategy to AbstractWorkflowStrategy class, report_types to ["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"])
- [ ] T042 [US2] Extend product detection logic in WorkflowExecutor.execute() in `web/orders/services/workflow/executor.py` (add filtering for abstract report types with agency="BLM", instantiate AbstractWorkflowStrategy, call create_workflow())
- [ ] T043 [US2] Add comprehensive logging to AbstractWorkflowStrategy in `web/orders/services/workflow/strategies/abstract.py` (INFO for success, ERROR for failures with report_id, group names, step counts, exc_info=True)

**Checkpoint**: User Story 2 is complete - Federal Abstract workflows can be created via API, independent of User Story 1

**Manual Verification**:
1. Create order with 1 BLM BASE_ABSTRACT report, 2 BLM leases
2. Click "Push to Basecamp" button
3. Verify success toast appears
4. Check Federal Abstracts Basecamp project for new to-do list with 6 groups and workflow steps

---

## Phase 5: User Story 3 - Create State Product Workflows (Priority: P3)

**Goal**: User clicks "Push to Basecamp" on order with State (NMSLO) reports → creates workflows in State Runsheets and/or State Abstracts projects following same patterns as Federal products

**Independent Test**: Create test order with 1 NMSLO RUNSHEET report and 1 NMSLO BASE_ABSTRACT report → trigger workflow → verify 2 workflows created in State Runsheets and State Abstracts projects

**Estimated Time**: 2 hours

### Implementation for User Story 3 (Extend to State)

- [ ] T044 [P] [US3] Update PRODUCT_CONFIGS in `web/orders/services/workflow/config.py` (add state_runsheets config with agency="NMSLO", report_types=["RUNSHEET"], workflow_strategy=RunsheetWorkflowStrategy)
- [ ] T045 [P] [US3] Update PRODUCT_CONFIGS in `web/orders/services/workflow/config.py` (add state_abstracts config with agency="NMSLO", report_types=["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"], workflow_strategy=AbstractWorkflowStrategy)
- [ ] T046 [US3] Extend product detection logic in WorkflowExecutor.execute() in `web/orders/services/workflow/executor.py` (iterate through all 4 PRODUCT_CONFIGS, detect applicable products based on report_type and agency filters for both BLM and NMSLO)
- [ ] T047 [US3] Update success message generation in WorkflowResultSerializer in `web/api/serializers/workflows.py` (handle multiple product names: "Workflows created: Federal Runsheets, State Abstracts")

**Checkpoint**: User Story 3 is complete - State products (both runsheets and abstracts) can be created via API, independent of US1 and US2

**Manual Verification**:
1. Create order with 1 NMSLO RUNSHEET report and 1 NMSLO BASE_ABSTRACT report
2. Click "Push to Basecamp" button
3. Verify success toast lists both "State Runsheets, State Abstracts"
4. Check both State projects in Basecamp for new workflows

---

## Phase 6: User Story 4 - Handle Multi-Product Orders (Priority: P4)

**Goal**: User clicks "Push to Basecamp" on order with multiple product types → creates workflows in all applicable Basecamp projects simultaneously

**Independent Test**: Create test order with 2 BLM RUNSHEET reports, 1 BLM BASE_ABSTRACT report, 1 NMSLO RUNSHEET report → trigger workflow → verify 3 workflows created across 3 different Basecamp projects (Federal Runsheets, Federal Abstracts, State Runsheets)

**Estimated Time**: 3 hours

### Implementation for User Story 4 (Multi-Product Integration)

- [ ] T048 [US4] Implement partial success handling in WorkflowExecutor.execute() in `web/orders/services/workflow/executor.py` (if one product fails, continue with remaining products, track failed_products and error_details)
- [ ] T049 [US4] Implement no applicable products handling in WorkflowExecutor.execute() in `web/orders/services/workflow/executor.py` (if no reports match any ProductConfig, return WorkflowResult with success=False, message="No workflows to create for this order")
- [ ] T050 [US4] Update WorkflowResultSerializer in `web/api/serializers/workflows.py` (handle partial success in message: "Workflows created: X, Y (1 product failed)", include failed_products in response if present)
- [ ] T051 [US4] Update trigger_workflow API view in `web/orders/views/workflows.py` (return 200 OK for partial success, include failed_products in response, log warnings for partial failures)
- [ ] T052 [US4] Update frontend button handler in `frontend/src/app/dashboard/orders/[id]/page.tsx` (display success toast even with failed_products, show warning icon or separate toast for partial failures)

**Checkpoint**: User Story 4 is complete - Multi-product orders create workflows across all applicable projects, with graceful partial failure handling

**Manual Verification**:
1. Create order with 2 BLM RUNSHEET, 1 BLM BASE_ABSTRACT, 1 NMSLO RUNSHEET report
2. Click "Push to Basecamp" button
3. Verify success toast lists all 3 products
4. Check all 3 Basecamp projects for new workflows

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, validation, and documentation

**Estimated Time**: 4 hours

- [ ] T053 [P] Implement missing Basecamp connection validation in trigger_workflow view in `web/orders/views/workflows.py` (check BasecampAccount exists for user, return 422 with "Basecamp not connected" message)
- [ ] T054 [P] Implement missing project ID configuration error handling in WorkflowExecutor in `web/orders/services/workflow/executor.py` (catch ValueError from _get_project_id(), append to failed_products with clear error message)
- [ ] T055 [P] Add empty reports edge case handling in RunsheetWorkflowStrategy in `web/orders/services/workflow/strategies/runsheet.py` (if no leases found, return {"todolist_ids": [], "todo_count": 0} without creating anything)
- [ ] T056 [P] Add empty reports edge case handling in AbstractWorkflowStrategy in `web/orders/services/workflow/strategies/abstract.py` (if report has no leases, create fixed steps only, skip lease-specific steps)
- [ ] T057 [P] Implement to-do name truncation in strategies in `web/orders/services/workflow/strategies/runsheet.py` and `abstract.py` (truncate to 255 characters if lease number or abstract type is very long)
- [ ] T058 [P] Add order authorization check in trigger_workflow view in `web/orders/views/workflows.py` (verify user has permission to access this order, return 403 Forbidden if not)
- [ ] T059 Validate all logging includes comprehensive context in both strategies in `web/orders/services/workflow/strategies/runsheet.py` and `abstract.py` (order_id, user_id, report_ids, lease_ids, API errors, HTTP status codes, exc_info=True for failures)
- [ ] T060 [P] Update project README.md with Basecamp workflow automation section (document environment variables, usage instructions, configuration requirements)
- [ ] T061 Run quickstart.md validation (manually test all success criteria from spec.md: single button click, <30s completion, 95% success rate, correct workflows created)

**Checkpoint**: All edge cases handled, comprehensive error messages, ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1 - Federal Runsheets): Can start after Foundational - MVP target
  - User Story 2 (P2 - Federal Abstracts): Can start after Foundational - Independent of US1
  - User Story 3 (P3 - State Products): Can start after Foundational - Extends US1/US2 patterns
  - User Story 4 (P4 - Multi-Product): Can start after Foundational - Integrates US1-US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (Federal Runsheets - P1)**: 
  - Depends on: Foundational (Phase 2)
  - No dependencies on other user stories
  - MVP target - complete and validate first
  
- **User Story 2 (Federal Abstracts - P2)**:
  - Depends on: Foundational (Phase 2)
  - Independent of US1 (different strategy, different project)
  - Can be implemented in parallel with US1 if team capacity allows
  
- **User Story 3 (State Products - P3)**:
  - Depends on: Foundational (Phase 2)
  - Extends existing strategies from US1/US2 (RunsheetWorkflowStrategy, AbstractWorkflowStrategy)
  - Should complete after US1 and US2 to leverage tested strategies
  
- **User Story 4 (Multi-Product - P4)**:
  - Depends on: Foundational (Phase 2)
  - Integrates all product types from US1-US3
  - Should complete last to ensure all individual products work independently

### Within Each User Story

**User Story 1 (Federal Runsheets)**:
- Backend tasks (T017-T027) before Frontend tasks (T028-T031)
- Within backend: Strategy implementation (T017-T022) → PRODUCT_CONFIGS update (T023) → WorkflowExecutor integration (T024-T027)
- Frontend tasks (T028-T031) can start in parallel once backend API is available

**User Story 2 (Federal Abstracts)**:
- Backend tasks (T032-T043) can proceed independently of US1
- Strategy implementation (T032-T040) → PRODUCT_CONFIGS update (T041) → WorkflowExecutor integration (T042-T043)
- No frontend changes needed (same button triggers all workflows)

**User Story 3 (State Products)**:
- All tasks (T044-T047) can run in parallel (different ProductConfigs)
- No strategy changes needed (reuses existing strategies)

**User Story 4 (Multi-Product)**:
- Backend tasks (T048-T051) → Frontend task (T052)
- Error handling and integration tasks

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T005, T006, T007, T008 can run in parallel (different files)

**Within Foundational (Phase 2)**:
- T009, T010, T011 can run in parallel (different files)

**Within User Story 1**:
- T028, T029 can run in parallel (different frontend files)

**Within User Story 2**:
- T032 initial structure can start in parallel with US1 work if team has capacity

**Within User Story 3**:
- T044, T045 can run in parallel (different ProductConfigs)

**Within Polish (Phase 7)**:
- T053, T054, T055, T056, T057, T058, T060 can run in parallel (different files/concerns)

**Across User Stories** (if team capacity allows):
- Once Foundational (Phase 2) completes, US1 and US2 can proceed in parallel
- US3 should wait for US1/US2 strategies to be tested
- US4 should wait for US1-US3 to be complete

---

## Parallel Example: User Story 1

```bash
# Backend Strategy Implementation (sequential within story):
Task T017: "Implement RunsheetWorkflowStrategy class"
Task T018: "Implement _get_project_id() helper"
Task T019: "Implement _extract_leases() helper"
Task T020: "Implement _create_todolist() method"
Task T021: "Implement _create_todos() method"
Task T022: "Implement create_workflow() main method"
Task T023: "Update PRODUCT_CONFIGS"
Task T024: "Implement product detection in WorkflowExecutor"
Task T025: "Add comprehensive logging"
Task T026: "Implement error handling in WorkflowExecutor"
Task T027: "Complete trigger_workflow API view"

# Frontend Implementation (can run in parallel once API is ready):
Task T028: "WorkflowResult TypeScript interface" [P]
Task T029: "triggerWorkflow API client function" [P]
Task T030: "Add Push to Basecamp button"
Task T031: "Implement button click handler"
```

---

## Parallel Example: Across User Stories

```bash
# With multiple developers, after Foundational (Phase 2) completes:

Developer A (US1 - Federal Runsheets):
  Tasks T017-T027 → T028-T031

Developer B (US2 - Federal Abstracts):
  Tasks T032-T043 (can proceed independently)

# After US1 and US2 complete:

Developer A (US3 - State Products):
  Tasks T044-T047 (extends tested strategies)

Developer B (US4 - Multi-Product):
  Tasks T048-T052 (integrates all products)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (30 minutes)
2. Complete Phase 2: Foundational (4 hours) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 - Federal Runsheets (1 day)
4. **STOP and VALIDATE**: 
   - Test with real order containing BLM RUNSHEET reports
   - Verify to-do list created in Federal Runsheets Basecamp project
   - Verify to-dos match leases with correct naming
   - Verify button shows success message
5. **Deploy/Demo MVP**: Single-product workflow automation working end-to-end

**MVP Success Criteria**:
- User can create Federal Runsheet workflows with single button click
- Workflow creation completes within 30 seconds
- Each BLM lease appears as exactly one to-do item
- Success message displays with workflow creation summary

### Incremental Delivery

1. **Foundation** (Phase 1 + 2): 5 hours
   - Environment configured
   - Strategy Pattern infrastructure ready
   - API endpoint skeleton ready
   
2. **MVP** (Phase 3 - US1): 1 day
   - Federal Runsheet workflows working end-to-end
   - Deploy and validate with users
   
3. **Increment 2** (Phase 4 - US2): 1 day
   - Add Federal Abstract workflows (grouped, complex)
   - Deploy and validate
   
4. **Increment 3** (Phase 5 - US3): 2 hours
   - Add State products (both runsheets and abstracts)
   - Deploy and validate
   
5. **Increment 4** (Phase 6 - US4): 3 hours
   - Add multi-product support
   - Deploy and validate
   
6. **Polish** (Phase 7): 4 hours
   - Edge cases, error handling, documentation
   - Final production deployment

**Total Estimated Time**: 3-5 days

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup + Foundational (5 hours)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (1 day)
   - Developer B: User Story 2 (1 day in parallel)
3. **After US1 and US2 complete**:
   - Developer A: User Story 3 (2 hours)
   - Developer B: User Story 4 (3 hours in parallel)
4. **Together**: Polish (4 hours)

**Total Time with 2 developers**: 2-3 days

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- Environment variables must be set before any workflow creation
- Strategies are reusable - US3 leverages US1/US2 strategy implementations
- Tests are optional per constitution - not included unless explicitly requested

---

## Task Summary

- **Total Tasks**: 61
- **Setup Tasks**: 8 (Phase 1)
- **Foundational Tasks**: 8 (Phase 2)
- **User Story 1 Tasks**: 15 (Phase 3)
- **User Story 2 Tasks**: 12 (Phase 4)
- **User Story 3 Tasks**: 4 (Phase 5)
- **User Story 4 Tasks**: 5 (Phase 6)
- **Polish Tasks**: 9 (Phase 7)
- **Parallel Opportunities**: 18 tasks marked [P]
- **Independent Tests**: 4 user stories can be validated independently

---

## Success Criteria Mapping

Per spec.md success criteria, this task list enables:

- **SC-001**: Single button click → Task T030-T031 (button with handler)
- **SC-002**: <30s completion → All workflow tasks use existing BasecampService (efficient API calls)
- **SC-003**: 95% success rate → Task T048-T051, T053-T059 (comprehensive error handling)
- **SC-004**: Success message within 5s → Task T031, T050, T052 (immediate API response, toast notifications)
- **SC-005**: Runsheet to-dos correct → Task T019-T021 (lease extraction, correct naming)
- **SC-006**: Abstract 6 groups → Task T033, T038 (group creation in order)
- **SC-007**: Multi-product without manual intervention → Task T048-T052 (automatic product detection, parallel creation)
- **SC-008**: Errors resolved in 2 minutes → Task T053-T054 (clear error messages for config issues)
- **SC-009**: No duplicates/missing workflows → Task T046, T048-T049 (correct filtering, partial success handling)

---

**Status**: ✅ Ready for implementation

**Suggested First Command**: `/speckit.implement Phase 1`

