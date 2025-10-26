# Feature Specification: Next.js Frontend Migration

**Feature Branch**: `001-nextjs-frontend-migration`  
**Created**: 2025-10-26  
**Status**: In Progress  
**Input**: Refactor from pure Django to Django backend with Next.js frontend

## Clarifications

### Session 2025-10-26

- Q: Password Policy & Security Requirements → A: No password requirements - allow any password (rely on user discretion)
- Q: Rate Limiting & API Throttling → A: No rate limiting - allow unlimited requests from any user/IP
- Q: Data Retention & Audit Logging → A: Basic audit logging - track created_at, updated_at timestamps and created_by, updated_by user IDs
- Q: Error Notification Persistence → A: Success toasts auto-dismiss after 5 seconds, error toasts remain until manually dismissed
- Q: Concurrent User Capacity & Performance Under Load → A: Small team scale - system should handle 10-50 concurrent users without performance degradation

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Login & Authentication (Priority: P1)

Users need a secure way to authenticate and access the Order Manager system using modern security standards. Authentication is foundational - without it, no other features are accessible.

**Why this priority**: Critical foundation. All other functionality depends on secure user authentication. This must work before any data management features can be implemented.

**Independent Test**: User can navigate to login page, enter credentials (username: `admin`, password: `admin`), successfully authenticate, and be redirected to the dashboard. Session persists across page refreshes and tab reloads. User can log out and be returned to login page.

**Acceptance Scenarios**:

1. **Given** user is on login page, **When** they enter valid credentials and submit, **Then** they receive secure authentication tokens and are redirected to dashboard
2. **Given** user is authenticated, **When** they refresh the page, **Then** they remain logged in without re-entering credentials
3. **Given** user is authenticated, **When** they click logout, **Then** their session is terminated and they are redirected to login page
4. **Given** user's session expires (15 minutes), **When** they make an API request, **Then** the system automatically refreshes their session without interruption
5. **Given** user tries to access protected pages without authentication, **When** they navigate to dashboard, **Then** they are redirected to login page

---

### User Story 2 - View Dashboard with Integration Status (Priority: P1)

Users need to see a centralized dashboard that displays their account information and the current status of external integrations (Dropbox, Basecamp) to understand system readiness and take action when needed.

**Why this priority**: Primary landing page after login. Provides system overview and surfaces critical integration issues that could block workflow operations.

**Independent Test**: Authenticated user can view dashboard showing welcome message with username, integration status cards for Dropbox and Basecamp (with connection state, last sync, and action buttons), and admin shortcuts if user has staff permissions. User can toggle between light and dark mode with preference persisting across sessions.

**Acceptance Scenarios**:

1. **Given** authenticated user navigates to dashboard, **When** page loads, **Then** they see welcome message with their username
2. **Given** user is staff member, **When** viewing dashboard, **Then** they see admin action buttons (Django Admin link, Manage Integrations)
3. **Given** Dropbox is connected, **When** viewing dashboard, **Then** Dropbox card shows "Connected" badge with last sync time and disconnect option
4. **Given** Dropbox is not connected, **When** viewing dashboard, **Then** Dropbox card shows "Not Connected" status with connect button
5. **Given** user toggles dark mode, **When** they reload page, **Then** dark mode preference is maintained

---

### User Story 3 - Manage External Integrations (Priority: P2)

Users need to connect and disconnect external services (Dropbox for file storage, Basecamp for project management) to enable automated workflows and maintain control over data access.

**Why this priority**: Enables automated file discovery and synchronization workflows. Required before order processing can leverage cloud storage features. Not blocking P1 functionality but needed for production workflows.

**Independent Test**: User can navigate to integrations page, view status of all available integrations, initiate OAuth connection flow for Dropbox (redirected to Dropbox for authorization, returned to app with success message), verify connected status updates immediately, and disconnect integration when needed with confirmation prompt.

**Acceptance Scenarios**:

1. **Given** user on integrations page with Dropbox disconnected, **When** they click "Connect Dropbox", **Then** OAuth flow initiates and redirects to Dropbox authorization
2. **Given** user completes Dropbox OAuth, **When** redirected back to app, **Then** Dropbox status updates to "Connected" and success toast displays
3. **Given** Dropbox is connected, **When** user clicks "Disconnect", **Then** confirmation dialog appears asking to confirm action
4. **Given** user confirms disconnection, **When** disconnect completes, **Then** Dropbox status updates to "Not Connected" and tokens are cleared
5. **Given** Basecamp integration not yet implemented, **When** viewing integrations page, **Then** Basecamp card shows "Coming Soon" placeholder

---

### User Story 4 - Manage Orders (Priority: P3)

Users need to create, view, edit, and delete orders to track work assignments and organize reports. Orders are the top-level container for grouping related reports and leases.

**Why this priority**: Core business entity but can be implemented after authentication and integrations are working. Lower priority than P1/P2 because manual workflows can continue while this is built.

**Independent Test**: User can view list of all orders in paginated table, create new order with order number and delivery date, edit existing order details, delete order (with confirmation), and see changes reflected immediately with success notifications.

**Acceptance Scenarios**:

1. **Given** user on orders page, **When** page loads, **Then** they see table of all orders with columns: order number, order date, delivery link, actions
2. **Given** user clicks "Create Order", **When** dialog opens, **Then** they can enter order number and order date
3. **Given** user submits valid order data, **When** create completes, **Then** new order appears in table and success toast displays
4. **Given** user clicks edit on existing order, **When** dialog opens with pre-filled data, **Then** they can modify order details
5. **Given** user clicks delete on order, **When** confirmation dialog appears and user confirms, **Then** order is removed and success toast displays

---

### User Story 5 - Manage Reports (Priority: P3)

Users need to create and manage reports that are associated with orders. Reports contain legal descriptions and are linked to one or more leases. Reports must be filterable by order for easy navigation.

**Why this priority**: Same as P3 orders - core business entity but not blocking authentication or integration workflows. Reports depend on orders existing.

**Independent Test**: User can view list of reports filtered by order, create new report with type and legal description, link report to existing leases, edit report details, and navigate to associated leases.

**Acceptance Scenarios**:

1. **Given** user on reports page, **When** page loads, **Then** they see table with columns: order number, report type, legal description, lease count, dates
2. **Given** user selects order filter, **When** filter applied, **Then** only reports for selected order are displayed
3. **Given** user creates new report, **When** submitting form, **Then** they specify report type (Runsheet, Base Abstract, etc.), legal description, and associated order
4. **Given** report has associated leases, **When** viewing report row, **Then** lease count is displayed with link to view leases
5. **Given** user edits report, **When** saving changes, **Then** updates are reflected immediately

---

### User Story 6 - Manage Leases (Priority: P3)

Users need to view and manage individual leases associated with reports. Leases contain agency information, lease numbers, and links to runsheet reports and document archives stored in Dropbox.

**Why this priority**: Same as P3 orders/reports - core business entity. Leases are the most granular level and depend on reports existing.

**Independent Test**: User can view list of leases with agency and lease number, see runsheet discovery status badges, access external links to runsheet reports and document archives, edit lease details, and filter leases by agency.

**Acceptance Scenarios**:

1. **Given** user on leases page, **When** page loads, **Then** they see table with columns: agency, lease number, runsheet status, runsheet link, documents link, actions
2. **Given** lease has discovered runsheet, **When** viewing lease row, **Then** status badge shows "Found" and runsheet link is active
3. **Given** lease has discovered document archive, **When** user clicks documents link, **Then** external link opens Dropbox folder in new tab
4. **Given** user clicks edit on lease, **When** dialog opens, **Then** they can modify lease details (agency, number, links)
5. **Given** user selects agency filter, **When** filter applied, **Then** only leases for selected agency are displayed

---

### Edge Cases

- What happens when user's session expires mid-form? System should refresh token automatically and preserve form data
- How does system handle network errors during API calls? Display user-friendly error messages via toast notifications and allow retry
- What happens if Dropbox OAuth callback fails? Display error message and allow user to retry connection
- What happens when user tries to delete order with associated reports? System should prevent deletion and display warning about dependent records
- How does system handle concurrent edits to same record? Last write wins with optimistic UI updates
- What happens when JWT refresh token expires (7 days)? User is logged out and redirected to login with informational message
- What happens when pagination has many pages? Provide jump-to-page controls and display current page/total pages

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization**
- **FR-001**: System MUST authenticate users via username and password with no password complexity requirements (user discretion)
- **FR-002**: System MUST issue JWT access tokens valid for 15 minutes and refresh tokens valid for 7 days
- **FR-003**: System MUST store tokens in HTTP-only cookies to prevent XSS attacks
- **FR-004**: System MUST automatically refresh expired access tokens without user interaction
- **FR-005**: System MUST redirect unauthenticated users to login page when accessing protected routes
- **FR-006**: System MUST log out users and clear all session data when user clicks logout
- **FR-007**: System MUST restrict staff-only features (admin links, manage integrations) to users with staff permissions

**Dashboard**
- **FR-008**: System MUST display authenticated user's username on dashboard
- **FR-009**: System MUST display integration status cards for all configured integrations (Dropbox, Basecamp)
- **FR-010**: System MUST show connection state, last sync time, and available actions for each integration
- **FR-011**: System MUST display admin action buttons only to staff users

**Integration Management**
- **FR-012**: System MUST allow users to initiate OAuth connection flow for Dropbox
- **FR-013**: System MUST store Dropbox access tokens securely after successful OAuth
- **FR-014**: System MUST allow users to disconnect integrations with confirmation
- **FR-015**: System MUST update integration status immediately after connection/disconnection
- **FR-016**: System MUST display clear status indicators (Connected, Not Connected, Authenticated)

**Orders Management**
- **FR-017**: System MUST display all orders in paginated table (20 per page)
- **FR-018**: System MUST allow users to create new orders with order number and order date
- **FR-019**: System MUST allow users to edit existing order details
- **FR-020**: System MUST allow users to delete orders with confirmation dialog
- **FR-021**: System MUST prevent deletion of orders with dependent reports
- **FR-022**: System MUST track created_at, updated_at timestamps and created_by, updated_by user IDs for all orders

**Reports Management**
- **FR-023**: System MUST display all reports in paginated table
- **FR-024**: System MUST allow users to filter reports by order
- **FR-025**: System MUST allow users to create reports with type, legal description, and order association
- **FR-026**: System MUST display count of associated leases for each report
- **FR-027**: System MUST allow users to navigate from report to its leases
- **FR-028**: System MUST track created_at, updated_at timestamps and created_by, updated_by user IDs for all reports

**Leases Management**
- **FR-029**: System MUST display all leases in paginated table
- **FR-030**: System MUST allow users to filter leases by agency
- **FR-031**: System MUST display runsheet discovery status badges (Found, Not Found, Pending)
- **FR-032**: System MUST display external links to runsheet reports and document archives
- **FR-033**: System MUST allow users to edit lease details (agency, number)
- **FR-034**: System MUST track created_at, updated_at timestamps and created_by, updated_by user IDs for all leases

**User Interface**
- **FR-035**: System MUST provide consistent navigation bar across all authenticated pages
- **FR-036**: System MUST support dark mode with user preference persisting across sessions
- **FR-037**: System MUST display loading states during API requests
- **FR-038**: System MUST display error messages via toast notifications that remain visible until manually dismissed
- **FR-039**: System MUST display success messages via toast notifications that auto-dismiss after 5 seconds
- **FR-040**: System MUST highlight currently active page in navigation

**API Requirements**
- **FR-041**: All API endpoints MUST require authentication except login
- **FR-042**: All API endpoints MUST return consistent JSON response structure
- **FR-043**: All list endpoints MUST support pagination
- **FR-044**: All API endpoints MUST validate input data and return clear error messages
- **FR-045**: API MUST use proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- **FR-046**: API MUST NOT implement rate limiting or throttling (allow unlimited requests)

### Key Entities *(include if feature involves data)*

- **User**: Represents authenticated user with username, email, staff status, and permissions. Used for authentication and authorization decisions.

- **Order**: Top-level container with order number, order date, and optional delivery link. Groups related reports. One-to-many relationship with Reports. Includes audit fields: created_at, updated_at timestamps and created_by, updated_by user references.

- **Report**: Contains legal description, report type (Runsheet, Base Abstract, etc.), and dates. Associated with one Order and one or more Leases. Many-to-one with Order, one-to-many with Leases. Includes audit fields: created_at, updated_at timestamps and created_by, updated_by user references.

- **Lease**: Individual lease record with agency name, lease number, and links to external resources (runsheet report URL, document archive URL). Associated with one Report. Has runsheet discovery status tracking. Includes audit fields: created_at, updated_at timestamps and created_by, updated_by user references.

- **Integration Status**: Represents connection state of external services (Dropbox, Basecamp). Includes connection state, authentication status, last sync time, and available actions.

- **Authentication Token**: JWT tokens (access and refresh) stored in HTTP-only cookies. Access token expires in 15 minutes, refresh token expires in 7 days.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete login flow in under 10 seconds with valid credentials
- **SC-002**: Users can toggle dark mode and verify preference persists across browser restart
- **SC-003**: Dashboard loads and displays integration status in under 2 seconds
- **SC-004**: Users can complete Dropbox OAuth connection flow in under 30 seconds
- **SC-005**: Users can create, edit, and delete orders/reports/leases with changes reflected within 1 second
- **SC-006**: 100% of authenticated API requests succeed with valid tokens
- **SC-007**: System maintains user session through page refreshes without requiring re-login
- **SC-008**: All form validations provide immediate feedback (within 100ms of input)
- **SC-009**: Users can navigate between all main pages (Dashboard, Integrations, Orders, Reports, Leases) with active page highlighted
- **SC-010**: System automatically refreshes expired access tokens without user awareness or workflow interruption
- **SC-011**: All API errors display user-friendly messages (no raw error dumps or stack traces)
- **SC-012**: Pagination controls allow navigation through lists of 100+ records efficiently
- **SC-013**: System maintains performance targets (login <10s, dashboard <2s, operations <1s) with 10-50 concurrent users

## Assumptions

1. **Technology Choice**: Next.js 16 with App Router is selected for frontend framework based on team expertise and modern React patterns
2. **Authentication Method**: JWT with HTTP-only cookies chosen for security (prevents XSS token theft) and developer experience
3. **Component Library**: shadcn/ui selected for accessible, customizable components with Tailwind CSS integration
4. **Development Environment**: Docker Compose used for consistent local development with PostgreSQL, Redis, Celery services
5. **API Design**: RESTful JSON API is sufficient for current requirements (WebSockets deferred to future work)
6. **Mobile Support**: Desktop-focused for initial release; responsive mobile design deferred
7. **Testing Strategy**: Manual testing sufficient for MVP; automated E2E tests deferred to future
8. **Existing Data**: Migration preserves all existing orders, reports, and leases in PostgreSQL database
9. **Django Admin**: Kept functional for staff administrative tasks; not replaced with React admin
10. **CORS Policy**: Localhost origins allowed in development; production will require configured domain whitelist
11. **User Scale**: System designed for small team usage (10-50 concurrent users); no special horizontal scaling or caching infrastructure required
