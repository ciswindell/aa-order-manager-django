# Tasks: Order Details Page Enhancement

**Input**: Design documents from `/specs/002-order-details-page/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-spec.md, quickstart.md

**Tests**: Tests are OPTIONAL per constitution - not included unless explicitly requested

**Organization**: Tasks grouped by user story to enable independent implementation and testing

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US8)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Backend Verification (Shared Infrastructure)

**Purpose**: Verify backend endpoints and prepare frontend structure

### Backend API Verification

- [x] T001 [P] Verify GET /api/orders/{id}/ endpoint returns single order in web/api/views/orders.py
- [x] T002 [P] Verify GET /api/reports/?order_id={id} filter works in web/api/views/reports.py (add if missing)
- [x] T003 [P] Add search parameter to GET /api/leases/?search={term} in web/api/views/leases.py (if not exists)
- [x] T004 [P] Verify report serializer includes full leases array in web/api/serializers/reports.py

### Frontend Infrastructure Preparation

- [x] T005 [P] Create directory structure: frontend/src/components/orders/
- [x] T006 [P] Create directory structure: frontend/src/components/reports/
- [x] T007 [P] Create directory structure: frontend/src/components/leases/
- [x] T008 [P] Create directory structure: frontend/src/app/dashboard/orders/[id]/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### API Client Functions

- [x] T009 [P] Add getOrder(id) function in frontend/src/lib/api/orders.ts
- [x] T010 [P] Add searchLeases(term) function in frontend/src/lib/api/leases.ts (if backend search added)

### Custom Hooks

- [x] T011 Create useOrderDetails(orderId) hook in frontend/src/hooks/useOrderDetails.ts
- [x] T012 Update useOrders hook to support redirect callback in frontend/src/hooks/useOrders.ts

### Type Definitions

- [x] T013 [P] Extend Order type with OrderDetails interface in frontend/src/lib/api/types.ts
- [x] T014 [P] Add component-specific types (LeaseOption, ReportDialogState, etc.) in frontend/src/lib/api/types.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Order Details with Reports (Priority: P1) 🎯 MVP

**Goal**: Users can navigate to order details page and see order information with associated reports

**Independent Test**: Create order with reports, click order row from list, verify all info displays on dedicated details page without navigation

### Implementation for User Story 1

- [x] T015 [P] [US1] Create OrderDetailsHeader component in frontend/src/components/orders/OrderDetailsHeader.tsx
- [x] T016 [P] [US1] Create OrderReportsSection component in frontend/src/components/orders/OrderReportsSection.tsx
- [x] T017 [US1] Create order details page in frontend/src/app/dashboard/orders/[id]/page.tsx (integrates T015, T016)
- [x] T018 [US1] Add click handler to order rows in frontend/src/app/dashboard/orders/page.tsx for navigation

**Checkpoint**: Users can view order details with reports table. This is the MVP - fully testable at this point!

---

## Phase 4: User Story 2 - Edit Order Information from Details Page (Priority: P1)

**Goal**: Users can edit order details directly from order details page without losing context

**Independent Test**: Navigate to order details, click Edit, modify fields, verify changes reflected immediately

### Implementation for User Story 2

- [x] T019 [US2] Add edit order dialog state management to order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [x] T020 [US2] Integrate existing edit order dialog component (reuse from orders list page) in order details page
- [x] T021 [US2] Add delete order dialog with cascade check in frontend/src/app/dashboard/orders/[id]/page.tsx

**Checkpoint**: Users can edit and delete orders from details page. Combined with US1, provides complete order management view.

---

## Phase 5: User Story 3 - Create Order and Navigate to Details (Priority: P1)

**Goal**: After creating order, user automatically lands on details page ready to add reports

**Independent Test**: Click Create Order, fill form, save, verify redirect to new order's details page with empty reports section

### Implementation for User Story 3

- [x] T022 [US3] Update createOrder success callback to redirect to order details in frontend/src/app/dashboard/orders/page.tsx

**Checkpoint**: Complete P1 functionality - seamless order creation to details workflow established.

---

## Phase 6: User Story 4 - Add Reports to Order (Priority: P2)

**Goal**: Users can create reports directly from order details page without leaving order context

**Independent Test**: From any order details page, click Add Report, fill form with existing leases, verify report appears in table

### Implementation for User Story 4

- [x] T023 [P] [US4] Create LeaseSearchSelect component (basic version without inline create) in frontend/src/components/leases/LeaseSearchSelect.tsx
- [x] T024 [US4] Create ReportFormDialog component with create mode in frontend/src/components/reports/ReportFormDialog.tsx (uses T023)
- [x] T025 [US4] Integrate ReportFormDialog into order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [x] T026 [US4] Add report creation trigger button to OrderReportsSection in frontend/src/components/orders/OrderReportsSection.tsx

**Checkpoint**: Users can add reports to orders. This is the core workflow enhancement over previous separate-pages approach.

---

## Phase 7: User Story 5 - Search and Select Leases for Reports (Priority: P2)

**Goal**: Users can search for leases when creating reports without scrolling through long lists

**Independent Test**: Open add report dialog, type in lease search field, verify list filters in real-time

### Implementation for User Story 5

- [x] T027 [US5] Add real-time search filtering with debouncing (300ms) to LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx
- [x] T028 [US5] Add selected leases display as removable chips/badges in LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx
- [x] T029 [US5] Add keyboard navigation (arrows, enter) to LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx

**Checkpoint**: Enhanced lease selection with search makes report creation faster for organizations with many leases.

---

## Phase 8: User Story 6 - Create Leases Inline During Report Creation (Priority: P3)

**Goal**: Users can create new leases while filling report form without abandoning their work

**Independent Test**: Open add report dialog, click Create New Lease, fill agency and number, verify new lease auto-selected for report

### Implementation for User Story 6

- [x] T030 [P] [US6] Create InlineLeaseCreateForm component in frontend/src/components/leases/InlineLeaseCreateForm.tsx
- [x] T031 [US6] Add inline lease creation toggle to LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx (integrates T030)
- [x] T032 [US6] Update ReportFormDialog to manage inline lease creation state in frontend/src/components/reports/ReportFormDialog.tsx
- [x] T033 [US6] Add success handler to auto-select newly created lease in ReportFormDialog in frontend/src/components/reports/ReportFormDialog.tsx

**Checkpoint**: Advanced workflow feature eliminating need to leave report creation context to create leases.

---

## Phase 9: User Story 7 - Edit and Delete Reports from Order (Priority: P3)

**Goal**: Users can modify or remove reports directly from order details page

**Independent Test**: Click edit on report, modify details, verify changes. Click delete, confirm, verify removal from table.

### Implementation for User Story 7

- [X] T034 [US7] Add edit mode support to ReportFormDialog in frontend/src/components/reports/ReportFormDialog.tsx
- [X] T035 [US7] Add edit report handler to order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [X] T036 [US7] Add delete report confirmation dialog to order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [X] T037 [US7] Add edit and delete action buttons to OrderReportsSection in frontend/src/components/orders/OrderReportsSection.tsx

**Checkpoint**: Complete CRUD operations for reports within order context. All report management can now happen on order details page.

---

## Phase 10: User Story 8 - View Detailed Lease Information (Priority: P3)

**Goal**: Users can access detailed lease info (agency, runsheet status, links) by clicking lease numbers

**Independent Test**: Click lease number in reports table, verify modal/popover shows agency, status, and links

### Implementation for User Story 8

- [X] T038 [P] [US8] Create LeaseDetailsPopover component in frontend/src/components/leases/LeaseDetailsPopover.tsx
- [X] T039 [US8] Add lease number click handlers to OrderReportsSection in frontend/src/components/orders/OrderReportsSection.tsx (integrates T038)
- [X] T040 [US8] Add lease number inline display logic (show 5, "+N more" for overflow) in OrderReportsSection in frontend/src/components/orders/OrderReportsSection.tsx

**Checkpoint**: Complete lease visibility enhancement. Users see lease numbers at a glance and can click for details.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories and final quality assurance

### Accessibility & Keyboard Navigation

- [X] T041 [P] Add ARIA labels to all interactive elements in LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx
- [X] T042 [P] Add ARIA labels and keyboard support to ReportFormDialog in frontend/src/components/reports/ReportFormDialog.tsx
- [X] T043 [P] Verify Tab navigation works correctly through all dialogs and forms

### Error Handling & Loading States

- [X] T044 [P] Add granular loading states to order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [X] T045 [P] Add error boundary and 404 handling to order details page in frontend/src/app/dashboard/orders/[id]/page.tsx
- [X] T046 [P] Add toast notifications for all success/error cases in order details page

### Performance Optimization

- [X] T047 [P] Add lazy loading for ReportFormDialog in frontend/src/app/dashboard/orders/[id]/page.tsx
- [X] T048 [P] Add memoization to filtered leases calculation in LeaseSearchSelect in frontend/src/components/leases/LeaseSearchSelect.tsx
- [X] T049 [P] Verify order details page loads in <2 seconds (performance target)
- [X] T050 [P] Verify lease search filters in <300ms (performance target)

### Code Quality & Documentation

- [X] T051 [P] Add JSDoc comments to all new component props interfaces
- [X] T052 [P] Verify all components follow DRY principle (no duplicate code)
- [X] T053 [P] Verify all components follow SOLID principles (single responsibility)
- [X] T054 Run frontend build to verify no TypeScript errors: npm run build in frontend/
- [X] T055 Run linter to verify code quality: npm run lint in frontend/

### Final Validation

- [X] T056 Execute quickstart.md manual testing checklist for all user stories
- [X] T057 Test responsive design on mobile viewport (320px, 768px, 1024px)
- [X] T058 Verify constitution compliance (no violations introduced)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3-10 (User Stories)**: All depend on Phase 2 completion
  - User stories can proceed in parallel (if staffed) or sequentially by priority
  - P1 stories (US1-3): Critical for MVP
  - P2 stories (US4-5): Core workflow enhancement
  - P3 stories (US6-8): Advanced features
- **Phase 11 (Polish)**: Can start after all desired user stories complete

### User Story Dependencies

**No blocking dependencies between user stories** - each can be implemented and tested independently:

- **US1 (P1)**: View order details → Can implement after Phase 2 ✅ Independent
- **US2 (P1)**: Edit order → Can implement after Phase 2 ✅ Independent (enhances US1 but not required for it)
- **US3 (P1)**: Auto-redirect after create → Can implement after Phase 2 ✅ Independent (enhances workflow but US1-2 work without it)
- **US4 (P2)**: Add reports → Can implement after Phase 2 ✅ Independent (works with basic lease select)
- **US5 (P2)**: Search leases → Can implement after Phase 2 ✅ Independent (enhances US4 but US4 works without it)
- **US6 (P3)**: Inline lease create → Can implement after Phase 2 ✅ Independent (enhances US4-5 but they work without it)
- **US7 (P3)**: Edit/delete reports → Can implement after Phase 2 ✅ Independent (CRUD completion)
- **US8 (P3)**: View lease details → Can implement after Phase 2 ✅ Independent (nice-to-have detail view)

### Within Each User Story

- Components marked [P] can be built in parallel (different files)
- Integration tasks depend on component completion
- Components before page integration
- UI before state management

### Parallel Opportunities

**Phase 1 - All tasks can run in parallel** (different files):
- T001-T004: Backend verification (4 parallel)
- T005-T008: Directory creation (4 parallel)

**Phase 2 - Most tasks can run in parallel**:
- T009-T010: API functions (2 parallel)
- T013-T014: Type definitions (2 parallel)
- T011-T012: Hooks (sequential due to shared patterns)

**Phase 3 (US1) - Components in parallel**:
- T015-T016: Components (2 parallel)
- T017-T018: Page integration (sequential after components)

**Phase 4 (US2) - Sequential** (modifies same page)

**Phase 5 (US3) - Single task**

**Phase 6 (US4) - Component then integration**:
- T023: Component (1 task)
- T024-T026: Integration (sequential after T023)

**Phase 7 (US5) - Enhancements to same component** (sequential)

**Phase 8 (US6) - Component then integration**:
- T030: Component (1 task, parallel with other phases)
- T031-T033: Integration (sequential after T030)

**Phase 9 (US7) - Sequential** (modifies existing components)

**Phase 10 (US8) - Component then integration**:
- T038: Component (1 parallel)
- T039-T040: Integration (sequential after T038)

**Phase 11 - Many tasks can run in parallel**:
- T041-T043: Accessibility (3 parallel)
- T044-T046: Error handling (3 parallel)
- T047-T050: Performance (4 parallel)
- T051-T055: Code quality (5 parallel)
- T056-T058: Validation (sequential)

---

## Parallel Example: User Story 1 (MVP)

```bash
# After Phase 2 completes, launch User Story 1 components in parallel:
Task T015: "Create OrderDetailsHeader component in frontend/src/components/orders/OrderDetailsHeader.tsx"
Task T016: "Create OrderReportsSection component in frontend/src/components/orders/OrderReportsSection.tsx"

# Then integrate (T017 depends on T015, T016 completion):
Task T017: "Create order details page in frontend/src/app/dashboard/orders/[id]/page.tsx"
Task T018: "Add click handler to order rows in frontend/src/app/dashboard/orders/page.tsx"
```

---

## Parallel Example: Multiple User Stories

```bash
# After Phase 2 completes, if you have 3 developers:

Developer A (Focus: MVP - P1 stories):
  - Phase 3: User Story 1 (T015-T018)
  - Phase 4: User Story 2 (T019-T021)
  - Phase 5: User Story 3 (T022)

Developer B (Focus: Core workflow - P2 stories):
  - Phase 6: User Story 4 (T023-T026)
  - Phase 7: User Story 5 (T027-T029)

Developer C (Focus: Advanced features - P3 stories):
  - Phase 8: User Story 6 (T030-T033)
  - Phase 9: User Story 7 (T034-T037)
  - Phase 10: User Story 8 (T038-T040)

All developers then contribute to Phase 11 (Polish) together.
```

---

## Implementation Strategy

### MVP First (P1 Stories Only - Minimum Viable Product)

**Goal**: Deliver basic order details view with editing capability

1. ✅ Complete Phase 1: Setup & Backend Verification
2. ✅ Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. ✅ Complete Phase 3: User Story 1 (View order details)
4. ✅ Complete Phase 4: User Story 2 (Edit order)
5. ✅ Complete Phase 5: User Story 3 (Auto-redirect)
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo MVP if ready (users can view and edit orders in dedicated page)

**MVP Value**: Users no longer need to navigate back to list to edit orders. All order information consolidated in one view.

**Estimated Effort**: ~4-6 hours
**LOC**: ~600-800

---

### Incremental Delivery (Add P2 Stories)

**Goal**: Add core workflow enhancement (report management)

1. MVP complete (P1 stories deployed)
2. ✅ Complete Phase 6: User Story 4 (Add reports to order)
3. Complete Phase 7: User Story 5 (Search leases)
4. **STOP and VALIDATE**: Test P2 stories work + P1 still works
5. Deploy/demo enhanced version

**Enhanced Value**: Users can now create reports without leaving order page. Lease search makes it fast for large lease lists.

**Additional Effort**: ~3-4 hours
**Additional LOC**: ~500-600

---

### Full Feature Delivery (Add P3 Stories)

**Goal**: Complete all advanced features

1. MVP + P2 complete
2. ✅ Complete Phase 8: User Story 6 (Inline lease creation)
3. ✅ Complete Phase 9: User Story 7 (Edit/delete reports)
4. ✅ Complete Phase 10: User Story 8 (View lease details)
5. ✅ Complete Phase 11: Polish & Cross-Cutting
6. **STOP and VALIDATE**: Full feature test
7. Deploy/demo complete feature

**Complete Value**: Users have seamless, complete order and report management workflow without page navigation.

**Additional Effort**: ~4-6 hours
**Additional LOC**: ~600-800

**Total Effort**: 12-16 hours
**Total LOC**: ~1,700-2,200

---

## Task Summary

**Total Tasks**: 58

### Tasks by Phase:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 6 tasks (BLOCKS all stories)
- Phase 3 (US1 - P1): 4 tasks 🎯
- Phase 4 (US2 - P1): 3 tasks 🎯
- Phase 5 (US3 - P1): 1 task 🎯
- Phase 6 (US4 - P2): 4 tasks
- Phase 7 (US5 - P2): 3 tasks
- Phase 8 (US6 - P3): 4 tasks
- Phase 9 (US7 - P3): 4 tasks
- Phase 10 (US8 - P3): 3 tasks
- Phase 11 (Polish): 18 tasks

### Tasks by Priority:
- **P1 (MVP)**: 8 tasks (US1-3) - Must have for basic functionality
- **P2 (Core)**: 7 tasks (US4-5) - Important workflow enhancement
- **P3 (Advanced)**: 11 tasks (US6-8) - Nice-to-have features
- **Infrastructure**: 14 tasks (Setup + Foundational)
- **Polish**: 18 tasks (Quality & validation)

### Parallel Opportunities:
- 35 tasks marked [P] can run in parallel within their phase
- All 8 user stories can be worked on in parallel (if staffed) after Phase 2
- Setup phase: 8 parallel tasks
- Foundational phase: 4 parallel tasks
- Polish phase: 17 parallel tasks

---

## Notes

- [P] = Parallelizable (different files, no dependencies within phase)
- [Story] = Maps to user story (US1-US8) from spec.md
- Each user story independently completable and testable
- Tests are OPTIONAL per constitution - not included
- Stop at any checkpoint to validate story works independently
- MVP (P1 stories) delivers immediate value
- Constitution compliance verified in Phase 11
- All file paths are absolute from repository root

