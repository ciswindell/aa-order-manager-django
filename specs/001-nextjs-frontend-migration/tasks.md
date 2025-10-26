# Tasks: Next.js Frontend Migration

**Input**: Design documents from `/specs/001-nextjs-frontend-migration/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-spec.md, quickstart.md

**Tests**: Tests are OPTIONAL - this feature specification does not explicitly request TDD approach, so test tasks are excluded. Manual testing will be performed per quickstart.md test plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `web/` directory containing Django application
- **Frontend**: `frontend/` directory containing Next.js application
- Paths shown are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify Docker Compose configuration includes all services (db, redis, web, worker, flower, frontend) in docker-compose.yml
- [x] T002 [P] Add djangorestframework, djangorestframework-simplejwt, django-cors-headers to web/requirements.txt
- [x] T003 [P] Install Python backend dependencies: docker compose exec web pip install -r requirements.txt
- [x] T004 [P] Install Next.js frontend dependencies: docker compose exec frontend npm install
- [x] T005 [P] Create frontend/.env.local with NEXT_PUBLIC_API_URL=http://localhost:8000/api
- [x] T006 Verify .gitignore includes frontend/node_modules/, frontend/.next/, frontend/.env.local, web/__pycache__/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend API Foundation

- [x] T007 [P] Configure Django REST Framework in web/order_manager_project/settings.py (add to INSTALLED_APPS, configure REST_FRAMEWORK defaults)
- [x] T008 [P] Configure djangorestframework-simplejwt in web/order_manager_project/settings.py (add to INSTALLED_APPS, configure SIMPLE_JWT settings with 15min access, 7 day refresh)
- [x] T009 [P] Configure django-cors-headers in web/order_manager_project/settings.py (add to INSTALLED_APPS and MIDDLEWARE, set CORS_ALLOWED_ORIGINS=['http://localhost:3000'], CORS_ALLOW_CREDENTIALS=True)
- [x] T010 Create api Django app: python manage.py startapp api in web/ directory
- [x] T011 Add api to INSTALLED_APPS in web/order_manager_project/settings.py
- [x] T012 [P] Create web/api/serializers/ directory with __init__.py
- [x] T013 [P] Create web/api/views/ directory with __init__.py
- [x] T014 Create web/api/urls.py file with empty urlpatterns list
- [x] T015 Include api.urls in web/order_manager_project/urls.py at path('api/', include('api.urls'))

### Database Migrations for Audit Fields

- [x] T016 [P] Add created_at (DateTimeField auto_now_add) and updated_at (DateTimeField auto_now) to Order model in web/orders/models.py
- [x] T017 [P] Add created_by and updated_by (ForeignKey to User, null=True) to Order model in web/orders/models.py
- [x] T018 [P] Add created_at, updated_at, created_by, updated_by fields to Report model in web/orders/models.py
- [x] T019 [P] Add created_at, updated_at, created_by, updated_by fields to Lease model in web/orders/models.py
- [x] T020 Create Django migration: python manage.py makemigrations orders
- [x] T021 Apply migration: python manage.py migrate

### Frontend Scaffold

- [x] T022 Verify Next.js 16 with App Router structure exists in frontend/src/app/
- [x] T023 Initialize shadcn/ui: npx shadcn-ui@latest init (if not done) in frontend/ directory with default settings
- [x] T024 [P] Create frontend/src/lib/api/ directory
- [x] T025 [P] Create frontend/src/lib/auth/ directory
- [x] T026 [P] Create frontend/src/hooks/ directory
- [x] T027 [P] Create frontend/src/components/ui/ directory (if not exists from shadcn init)
- [x] T028 [P] Create frontend/src/components/auth/ directory
- [x] T029 Install TanStack Query: npm install @tanstack/react-query in frontend/
- [x] T030 [P] Install next-themes: npm install next-themes in frontend/
- [x] T031 [P] Install sonner (toast): npm install sonner in frontend/
- [x] T032 [P] Install date-fns: npm install date-fns in frontend/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Secure Login & Authentication (Priority: P1) 🎯 MVP

**Goal**: Implement JWT authentication with HTTP-only cookies, login page, logout, and session persistence

**Independent Test**: User can navigate to login page, enter credentials (admin/admin), successfully authenticate, be redirected to dashboard, refresh page and remain logged in, and logout to return to login page.

### Implementation for User Story 1

#### Backend Authentication API

- [x] T033 [P] [US1] Create UserSerializer in web/api/serializers/auth.py with fields: id, username, email, is_staff
- [x] T034 [US1] Create CustomTokenObtainPairSerializer extending TokenObtainPairSerializer to include user data in web/api/serializers/auth.py
- [x] T035 [US1] Create CustomTokenObtainPairView in web/api/views/auth.py that sets access_token and refresh_token as HTTP-only cookies
- [x] T036 [US1] Implement logout_view in web/api/views/auth.py that blacklists refresh token and deletes cookies
- [x] T037 [US1] Implement user_profile_view in web/api/views/auth.py (GET endpoint returning current user)
- [x] T038 [US1] Add authentication URL patterns to web/api/urls.py: auth/login/, auth/refresh/, auth/logout/, auth/user/

#### Frontend Authentication Infrastructure

- [x] T039 [P] [US1] Install shadcn button component: npx shadcn-ui@latest add button in frontend/
- [x] T040 [P] [US1] Install shadcn input component: npx shadcn-ui@latest add input in frontend/
- [x] T041 [P] [US1] Install shadcn label component: npx shadcn-ui@latest add label in frontend/
- [x] T042 [P] [US1] Install shadcn form component: npx shadcn-ui@latest add form in frontend/
- [x] T043 [P] [US1] Install shadcn card component: npx shadcn-ui@latest add card in frontend/
- [x] T044 [US1] Create frontend/src/lib/api/client.ts with fetch wrapper including credentials: 'include'
- [x] T045 [US1] Create TypeScript User interface in frontend/src/lib/api/types.ts
- [x] T046 [US1] Create auth API functions (login, logout, getUserProfile) in frontend/src/lib/auth/api.ts
- [x] T047 [US1] Create userStorage functions (get, set, clear) for localStorage in frontend/src/lib/auth/storage.ts
- [x] T048 [US1] Create AuthProvider with useAuth hook in frontend/src/hooks/useAuth.tsx with user state, login, logout functions
- [x] T049 [US1] Create Toaster component wrapper in frontend/src/app/layout.tsx by importing sonner's Toaster
- [x] T050 [US1] Wrap children with AuthProvider in frontend/src/app/layout.tsx

#### Login Page & Route Protection

- [x] T051 [P] [US1] Get login-01 block demo: mcp_shadcn-ui_get_component_demo('login-01')
- [x] T052 [US1] Create login form component in frontend/src/components/auth/login-form.tsx using shadcn form components
- [x] T053 [US1] Create login page at frontend/src/app/login/page.tsx that uses LoginForm component
- [x] T054 [US1] Create Next.js middleware in frontend/src/middleware.ts to protect authenticated routes (check access_token cookie)
- [x] T055 [US1] Create root page redirect logic in frontend/src/app/page.tsx (redirect to /dashboard if authenticated, /login otherwise)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can login, session persists, logout works, protected routes redirect to login.

---

## Phase 4: User Story 2 - View Dashboard with Integration Status (Priority: P1) 🎯 MVP

**Goal**: Create dashboard page showing welcome message, integration status cards, admin links (if staff), and dark mode toggle

**Independent Test**: Authenticated user can view dashboard with welcome message, integration status cards (Dropbox, Basecamp), admin links (if staff), toggle dark mode with preference persisting across page reloads.

### Implementation for User Story 2

#### Backend Dashboard & Integration APIs

- [x] T056 [P] [US2] Create IntegrationStatusSerializer in web/api/serializers/integrations.py with fields: provider, is_connected, is_authenticated, last_sync, blocking_problem
- [x] T057 [US2] Create dashboard_view in web/api/views/dashboard.py returning user info, integration statuses, and stats
- [x] T058 [US2] Create get_integration_status view in web/api/views/integrations.py using existing IntegrationStatusService
- [x] T059 [US2] Add dashboard and integration status endpoints to web/api/urls.py: api/dashboard/, api/integrations/status/

#### Frontend Dashboard Page & Dark Mode

- [x] T060 [P] [US2] Install shadcn dropdown-menu component: npx shadcn-ui@latest add dropdown-menu in frontend/
- [x] T061 [US2] Create ThemeProvider component in frontend/src/components/theme-provider.tsx using next-themes
- [x] T062 [US2] Wrap children with ThemeProvider in frontend/src/app/layout.tsx (add suppressHydrationWarning to <html>)
- [x] T063 [US2] Create ThemeToggle component in frontend/src/components/theme-toggle.tsx with Light/Dark/System options using dropdown-menu
- [x] T064 [US2] Create dashboard API function (getDashboard) in frontend/src/lib/api/dashboard.ts
- [x] T065 [US2] Create IntegrationStatus TypeScript interface in frontend/src/lib/api/types.ts
- [x] T066 [US2] Create dashboard page at frontend/src/app/dashboard/page.tsx with welcome message, user info, ThemeToggle, and logout button
- [x] T067 [US2] Fetch and display integration status cards on dashboard (Dropbox, Basecamp) with connection state badges
- [x] T068 [US2] Conditionally render admin action buttons (Django Admin link, Manage Integrations) if user.is_staff

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can login, view dashboard, see integration status, toggle dark mode, and logout.

---

## Phase 5: User Story 3 - Manage External Integrations (Priority: P2)

**Goal**: Create integrations page allowing users to connect/disconnect Dropbox and view Basecamp placeholder

**Independent Test**: User can navigate to integrations page, view all integration statuses, click "Connect Dropbox" to initiate OAuth, disconnect with confirmation, and see "Coming Soon" for Basecamp.

### Implementation for User Story 3

#### Backend Integration Actions

- [x] T069 [US3] Create connect_dropbox view in web/api/views/integrations.py (POST endpoint returning OAuth URL, staff only)
- [x] T070 [US3] Create disconnect_dropbox view in web/api/views/integrations.py (POST endpoint clearing tokens, staff only)
- [x] T071 [US3] Add integration action endpoints to web/api/urls.py: api/integrations/dropbox/connect/, api/integrations/dropbox/disconnect/

#### Frontend Integrations Page

- [x] T072 [P] [US3] Install shadcn alert component: npx shadcn-ui@latest add alert in frontend/
- [x] T073 [P] [US3] Install shadcn badge component: npx shadcn-ui@latest add badge in frontend/
- [x] T074 [P] [US3] Install shadcn dialog component: npx shadcn-ui@latest add dialog in frontend/
- [x] T075 [US3] Create integrations API functions (getIntegrationStatus, connectDropbox, disconnectDropbox) in frontend/src/lib/api/integrations.ts
- [x] T076 [US3] Create integrations page at frontend/src/app/dashboard/integrations/page.tsx
- [x] T077 [US3] Display Dropbox integration card with status badge, last sync time, and connect/disconnect button based on status
- [x] T078 [US3] Implement connect button handler that calls API and redirects to OAuth URL
- [x] T079 [US3] Implement disconnect button handler that shows confirmation dialog, then calls API
- [x] T080 [US3] Display Basecamp integration card with "Coming Soon" placeholder and disabled connect button
- [x] T081 [US3] Display success toast on successful connect/disconnect (auto-dismiss after 5 seconds per clarifications)
- [x] T082 [US3] Display error toast on failures (manual dismiss per clarifications)

**Checkpoint**: User Stories 1, 2, AND 3 should all work independently. Users have complete authentication, dashboard, and integration management.

---

## Phase 6: User Story 4 - Manage Orders (Priority: P3)

**Goal**: Create orders page with CRUD operations, pagination, and table display

**Independent Test**: User can view paginated list of orders, create new order with order number and date, edit existing order, delete order with confirmation, and see changes reflected with success toasts.

### Implementation for User Story 4

#### Backend Orders API

- [x] T083 [P] [US4] Create OrderSerializer in web/api/serializers/orders.py with all fields including audit fields and report_count SerializerMethodField
- [x] T084 [US4] Create OrderViewSet in web/api/views/orders.py with list, create, retrieve, update, destroy actions
- [x] T085 [US4] Override perform_create and perform_update in OrderViewSet to set created_by/updated_by from request.user
- [x] T086 [US4] Add validation in destroy method to prevent deletion if order has reports
- [x] T087 [US4] Register OrderViewSet router in web/api/urls.py at api/orders/

#### Frontend Orders Page

- [x] T088 [P] [US4] Install shadcn table component: npx shadcn-ui@latest add table in frontend/
- [x] T089 [P] [US4] Create Order TypeScript interface in frontend/src/lib/api/types.ts
- [x] T090 [US4] Create orders API functions (getOrders, createOrder, updateOrder, deleteOrder) in frontend/src/lib/api/orders.ts
- [x] T091 [US4] Create useOrders hook with TanStack Query in frontend/src/hooks/useOrders.ts
- [x] T092 [US4] Create orders page at frontend/src/app/dashboard/orders/page.tsx
- [x] T093 [US4] Implement orders table with columns: order number, order date, delivery link, report count, actions
- [x] T094 [US4] Add pagination controls (previous, next, page number) at page_size=20
- [x] T095 [US4] Implement "Create Order" button that opens dialog with form (order_number, order_date, delivery_link optional)
- [x] T096 [US4] Implement edit action that opens dialog with pre-filled form data
- [x] T097 [US4] Implement delete action that shows confirmation dialog before calling API
- [x] T098 [US4] Display success toast on successful create/update/delete (5s auto-dismiss)
- [x] T099 [US4] Display error toast on failures (manual dismiss), including validation errors and "cannot delete with reports" message
- [x] T100 [US4] Implement optimistic updates with TanStack Query mutations

**Checkpoint**: Orders management fully functional. Users can perform all CRUD operations with proper feedback.

---

## Phase 7: User Story 5 - Manage Reports (Priority: P3)

**Goal**: Create reports page with CRUD operations, order filtering, and lease count display

**Independent Test**: User can view paginated list of reports, filter by order, create new report with type and legal description, edit report, and navigate to associated leases.

### Implementation for User Story 5

#### Backend Reports API

- [x] T101 [P] [US5] Create ReportSerializer in web/api/serializers/reports.py with all fields including nested order (id, order_number) and lease_count SerializerMethodField
- [x] T102 [US5] Create ReportViewSet in web/api/views/reports.py with list, create, retrieve, update, destroy actions
- [x] T103 [US5] Add filter_backends to ReportViewSet for filtering by order_id query parameter
- [x] T104 [US5] Override perform_create and perform_update in ReportViewSet to set created_by/updated_by from request.user
- [x] T105 [US5] Add validation in destroy method to prevent deletion if report has leases
- [x] T106 [US5] Register ReportViewSet router in web/api/urls.py at api/reports/

#### Frontend Reports Page

- [x] T107 [P] [US5] Create Report TypeScript interface in frontend/src/lib/api/types.ts
- [x] T108 [US5] Create reports API functions (getReports, createReport, updateReport, deleteReport) in frontend/src/lib/api/reports.ts
- [x] T109 [US5] Create useReports hook with TanStack Query in frontend/src/hooks/useReports.ts
- [x] T110 [US5] Create reports page at frontend/src/app/dashboard/reports/page.tsx
- [x] T111 [US5] Implement reports table with columns: order number, report type, legal description (truncated), lease count, dates, actions
- [x] T112 [US5] Add order filter dropdown that fetches orders and filters reports by selected order_id
- [x] T113 [US5] Add pagination controls at page_size=20
- [x] T114 [US5] Implement "Create Report" button that opens dialog with form (order dropdown, report_type dropdown, legal_description textarea, report_date optional)
- [x] T115 [US5] Implement report_type dropdown with options: Runsheet, Base Abstract, Current Owner, Full Abstract, Title Opinion, Other
- [x] T116 [US5] Implement edit action that opens dialog with pre-filled form data
- [x] T117 [US5] Implement delete action with confirmation dialog
- [x] T118 [US5] Display lease_count as clickable link that navigates to /dashboard/leases?report_id=X
- [x] T119 [US5] Display success toast on CRUD operations (5s auto-dismiss)
- [x] T120 [US5] Display error toast on failures (manual dismiss)
- [x] T121 [US5] Implement optimistic updates with TanStack Query mutations

**Checkpoint**: Reports management fully functional with order filtering and lease navigation.

---

## Phase 8: User Story 6 - Manage Leases (Priority: P3)

**Goal**: Create leases page with CRUD operations, agency filtering, runsheet status badges, and external links

**Independent Test**: User can view paginated list of leases, filter by agency, see runsheet discovery status badges, click external links to Dropbox, edit lease details.

### Implementation for User Story 6

#### Backend Leases API

- [x] T122 [P] [US6] Create LeaseSerializer in web/api/serializers/leases.py with all fields including nested report (id, order_number), runsheet_status computed field, runsheet_archive_link, document_archive_link
- [x] T123 [US6] Create LeaseViewSet in web/api/views/leases.py with list, create, retrieve, update, destroy actions
- [x] T124 [US6] Add filter_backends to LeaseViewSet for filtering by agency_name and report_id query parameters
- [x] T125 [US6] Override perform_create and perform_update in LeaseViewSet to set created_by/updated_by from request.user
- [x] T126 [US6] Implement runsheet_status SerializerMethodField that returns "Found", "Not Found", or "Pending" based on runsheet_report_found and runsheet_link
- [x] T127 [US6] Register LeaseViewSet router in web/api/urls.py at api/leases/

#### Frontend Leases Page

- [x] T128 [P] [US6] Create Lease TypeScript interface in frontend/src/lib/api/types.ts with runsheet_status type: 'Found' | 'Not Found' | 'Pending'
- [x] T129 [US6] Create leases API functions (getLeases, createLease, updateLease, deleteLease) in frontend/src/lib/api/leases.ts
- [x] T130 [US6] Create useLeases hook with TanStack Query in frontend/src/hooks/useLeases.ts
- [x] T131 [US6] Create leases page at frontend/src/app/dashboard/leases/page.tsx
- [x] T132 [US6] Implement leases table with columns: agency, lease number, runsheet status badge, runsheet link icon, documents link icon, actions
- [x] T133 [US6] Add agency filter dropdown with unique agency names from fetched leases
- [x] T134 [US6] Add pagination controls at page_size=20
- [x] T135 [US6] Implement runsheet status badge with colors: green for "Found", red for "Not Found", yellow for "Pending"
- [x] T136 [US6] Implement external link icons (lucide-react ExternalLink) for runsheet_link and document_archive_link that open in new tab
- [x] T137 [US6] Implement "Create Lease" button that opens dialog with form (report dropdown, agency_name input, lease_number input)
- [x] T138 [US6] Implement edit action that opens dialog with pre-filled form (note: runsheet fields are read-only, managed by Celery)
- [x] T139 [US6] Implement delete action with confirmation dialog
- [x] T140 [US6] Display success toast on CRUD operations (5s auto-dismiss)
- [x] T141 [US6] Display error toast on failures (manual dismiss)
- [x] T142 [US6] Implement optimistic updates with TanStack Query mutations

**Checkpoint**: All user stories (US1-US6) should now be independently functional. Complete feature parity achieved.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T143 [P] Add navigation component in frontend/src/components/layout/nav.tsx with links to Dashboard, Integrations, Orders, Reports, Leases
- [x] T144 [P] Add active link highlighting using usePathname in navigation component
- [x] T145 [P] Conditionally render admin links in navigation if user.is_staff
- [x] T146 Add navigation to dashboard layout wrapper (shared across all authenticated pages)
- [x] T147 [P] Create loading.tsx files for each route to show loading states (frontend/src/app/dashboard/loading.tsx, etc.)
- [x] T148 [P] Create error.tsx files for each route to show error boundaries (frontend/src/app/dashboard/error.tsx, etc.)
- [x] T149 [P] Verify all form inputs have proper validation with error messages
- [x] T150 [P] Verify all date fields use date-fns for formatting (format(date, 'yyyy-MM-dd'))
- [x] T151 [P] Add CORS headers verification: docker compose logs web | grep CORS
- [x] T152 [P] Test token refresh flow by waiting 15 minutes and making API call
- [x] T153 [P] Test logout clears cookies and redirects to login
- [x] T154 [P] Test middleware protects all /dashboard/* routes
- [x] T155 [P] Verify dark mode preference persists after browser restart
- [x] T156 [P] Test all success toasts auto-dismiss after 5 seconds
- [x] T157 [P] Test all error toasts require manual dismiss
- [x] T158 [P] Verify pagination works with >20 items
- [x] T159 [P] Test delete prevention for orders with reports and reports with leases
- [x] T160 [P] Run quickstart.md manual test plan for all 6 user stories
- [x] T161 Code cleanup: Remove unused imports, components, and console.logs
- [x] T162 [P] Run TypeScript build: cd frontend && npm run build (verify no errors)
- [x] T163 [P] Run Django tests: docker compose exec web python manage.py test
- [x] T164 Update README.md with Next.js frontend setup instructions
- [x] T165 Update DOCKER_DEV_README.md with frontend service documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational - No dependencies on other stories ✅ MVP
  - US2 (Phase 4): Depends on US1 (requires authentication) - Still qualifies for MVP with US1
  - US3 (Phase 5): Depends on US1 (requires authentication) - Can run in parallel with US2
  - US4 (Phase 6): Depends on US1 (requires authentication) - Can run in parallel with US2, US3
  - US5 (Phase 7): Depends on US1, US4 (reports reference orders) - Must wait for US4
  - US6 (Phase 8): Depends on US1, US5 (leases reference reports) - Must wait for US5
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

```
US1 (Auth) ──┬──> US2 (Dashboard)
             ├──> US3 (Integrations)
             └──> US4 (Orders) ──> US5 (Reports) ──> US6 (Leases)

Legend:
━━━> Hard dependency (must wait)
- - -> Soft dependency (auth required but can parallelize)
```

**Critical Path**: US1 → US4 → US5 → US6 (longest sequential chain)

**Parallelizable**: US2 and US3 can be implemented simultaneously with US4 once US1 is complete

### Within Each User Story

- Backend serializers and viewsets before frontend pages
- shadcn components before page implementation
- API client functions before TanStack Query hooks
- Hooks before page components
- Core CRUD before polish (toasts, optimistic updates)

### Parallel Opportunities

#### Setup Phase (Phase 1)
```bash
# All these can run simultaneously:
Task T002: Add backend dependencies to requirements.txt
Task T004: Install frontend dependencies
Task T005: Create frontend .env.local
Task T006: Verify .gitignore
```

#### Foundational Phase (Phase 2)
```bash
# Backend configuration (parallel):
Task T007: Configure DRF
Task T008: Configure JWT
Task T009: Configure CORS

# Database migrations (parallel):
Task T016: Add audit fields to Order
Task T017: Add FK fields to Order
Task T018: Add audit fields to Report
Task T019: Add audit fields to Lease

# Frontend directories (parallel):
Task T024-T028: Create all directory structures
Task T029-T032: Install all npm packages
```

#### User Story 1 (Phase 3)
```bash
# Backend API (parallel):
Task T033: Create UserSerializer
Task T034: Create CustomTokenObtainPairSerializer

# Frontend components (parallel):
Task T039-T043: Install all shadcn components

# After backend complete, frontend (parallel):
Task T044: Create API client
Task T045: Create TypeScript types
Task T046: Create auth API functions
Task T047: Create storage functions
```

#### User Story 2 (Phase 4)
```bash
# Backend (parallel):
Task T056: Create IntegrationStatusSerializer
Task T057: Create dashboard_view

# Frontend (parallel):
Task T060: Install dropdown-menu
Task T061-T063: Create theme components
Task T064-T065: Create dashboard API and types
```

#### User Stories 4, 5, 6 (Phases 6, 7, 8)
```bash
# After US1 complete, US4 can start
# After US4 complete, US5 can start
# After US5 complete, US6 can start
# US2 and US3 can run in parallel with US4
```

#### Polish Phase
```bash
# Most polish tasks can run in parallel:
Task T143-T150: UI improvements (all parallel)
Task T151-T160: Testing (all parallel)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Dashboard with dark mode)
5. **STOP and VALIDATE**: Test login, dashboard, dark mode, logout independently
6. Deploy/demo if ready

**MVP Delivers**: Users can login securely, see dashboard with integration status, toggle dark mode, and logout. This is a complete, usable slice of functionality.

### Incremental Delivery (All User Stories)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (**MVP!**)
3. Add User Story 2 → Test independently → Deploy/Demo (Enhanced MVP)
4. Add User Story 3 (Integrations) → Test independently → Deploy/Demo
5. Add User Story 4 (Orders) → Test independently → Deploy/Demo
6. Add User Story 5 (Reports) → Test independently → Deploy/Demo
7. Add User Story 6 (Leases) → Test independently → Deploy/Demo (Full Feature Complete)
8. Polish phase → Final testing → Production deployment

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T032)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Authentication) - **MUST COMPLETE FIRST**
3. After US1 complete:
   - **Developer A**: User Story 2 (Dashboard)
   - **Developer B**: User Story 3 (Integrations)
   - **Developer C**: User Story 4 (Orders)
4. After US4 complete:
   - **Developer C**: User Story 5 (Reports)
5. After US5 complete:
   - **Developer C**: User Story 6 (Leases)
6. All developers: Polish phase (parallel tasks)

**Note**: US1 MUST be complete before any other user story can begin due to authentication dependency.

---

## Parallel Execution Examples

### Example 1: Setup Phase

```bash
# Launch all setup tasks together:
Task T002: Add backend dependencies
Task T004: Install frontend dependencies
Task T005: Create .env.local
Task T006: Verify gitignore

# Total time: ~2 minutes (vs 8 minutes sequential)
```

### Example 2: User Story 1 - Backend

```bash
# Launch all serializers together:
Task T033: UserSerializer
Task T034: CustomTokenObtainPairSerializer

# Total time: ~5 minutes (vs 10 minutes sequential)
```

### Example 3: User Story 1 - Frontend Components

```bash
# Install all shadcn components together:
Task T039: button
Task T040: input
Task T041: label
Task T042: form
Task T043: card

# Total time: ~3 minutes (vs 15 minutes sequential)
```

### Example 4: User Story 4, 5, 6 - Data Management

```bash
# After US1 complete, start these in parallel:
Developer A: US2 (Dashboard)
Developer B: US3 (Integrations)
Developer C: US4 (Orders)

# After US4 complete:
Developer C continues: US5 (Reports) → US6 (Leases)

# Total time: Significantly reduced vs sequential
```

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability (US1-US6)
- Each user story should be independently completable and testable
- Setup and Foundational phases have no story labels (infrastructure)
- Polish phase has no story labels (affects multiple stories)
- Commit after each task or logical group of related tasks
- Stop at any checkpoint to validate story independently
- Tests are OPTIONAL - not included per specification (manual testing via quickstart.md)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Statistics

**Total Tasks**: 165

**Tasks by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 26 tasks
- Phase 3 (US1 - Authentication): 23 tasks
- Phase 4 (US2 - Dashboard): 13 tasks
- Phase 5 (US3 - Integrations): 14 tasks
- Phase 6 (US4 - Orders): 18 tasks
- Phase 7 (US5 - Reports): 21 tasks
- Phase 8 (US6 - Leases): 21 tasks
- Phase N (Polish): 23 tasks

**Tasks by User Story**:
- US1 (P1): 23 tasks (Authentication - MVP critical)
- US2 (P1): 13 tasks (Dashboard - MVP critical)
- US3 (P2): 14 tasks (Integrations)
- US4 (P3): 18 tasks (Orders)
- US5 (P3): 21 tasks (Reports)
- US6 (P3): 21 tasks (Leases)
- Infrastructure: 32 tasks (Setup + Foundational)
- Polish: 23 tasks (Cross-cutting)

**Parallel Opportunities**: 87 tasks marked with [P] (~53% can be parallelized)

**MVP Scope**: Phases 1-4 (68 tasks) delivers functional authentication and dashboard

**Independent Test Criteria**:
- US1: Login, session persistence, logout, route protection
- US2: Dashboard display, integration cards, dark mode, admin links
- US3: Integration connect/disconnect, OAuth flow, confirmation dialogs
- US4: Orders CRUD, pagination, validation, delete prevention
- US5: Reports CRUD, order filtering, lease navigation
- US6: Leases CRUD, agency filtering, status badges, external links

---

**Status**: ✅ READY FOR IMPLEMENTATION

Follow quickstart.md for environment setup, then begin with Phase 1 (Setup) tasks. Each user story can be validated independently using the acceptance scenarios from spec.md.

**Suggested First Sprint**: Phases 1-4 (US1 + US2) for MVP delivery

