# Feature Specification: Order Details Page Enhancement

**Feature Branch**: `002-order-details-page`  
**Created**: October 26, 2025  
**Status**: Draft  
**Input**: User description: "Create dedicated order details page with inline report and lease management. Users should be able to create orders, then add reports to those orders, and create/select leases within the report creation flow without navigating between multiple pages."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Order Details with Reports (Priority: P1)

As an order manager, I want to see all information about a specific order in one place, including all its associated reports, so I can understand the complete status of an order without navigating between multiple pages.

**Why this priority**: This is the foundation of the feature - without a dedicated order details view, users cannot benefit from the streamlined workflow. This delivers immediate value by consolidating fragmented information.

**Independent Test**: Can be fully tested by creating an order with existing reports, clicking on it from the orders list, and verifying all order information and reports are displayed together on a single page. Delivers value by eliminating the need to cross-reference multiple pages.

**Acceptance Scenarios**:

1. **Given** I am viewing the orders list page, **When** I click on an order row, **Then** I am navigated to a dedicated order details page showing the order number, date, notes, delivery link, and creator information
2. **Given** I am on an order details page, **When** the page loads, **Then** I see a reports section displaying all reports associated with this order in a table format
3. **Given** an order has no reports, **When** I view the order details page, **Then** I see an empty state message "No reports added yet" with a prominent "Add Report" button
4. **Given** I am on an order details page, **When** I want to return to the orders list, **Then** I can click a back button that navigates me back to the orders list
5. **Given** I am viewing order details, **When** I view the reports table, **Then** I see each report's type, legal description, date range, and lease count

---

### User Story 2 - Edit Order Information from Details Page (Priority: P1)

As an order manager, I want to edit order information directly from the order details page, so I can update order data while reviewing its reports without losing context.

**Why this priority**: Essential for maintaining data accuracy while working with orders. Without this, users would need to navigate back to the orders list to make simple updates, breaking their workflow.

**Independent Test**: Can be fully tested by navigating to an order details page, clicking "Edit Order Details", updating fields, and verifying changes are reflected immediately. Delivers value by enabling contextual editing.

**Acceptance Scenarios**:

1. **Given** I am on an order details page, **When** I click the "Edit Order Details" button, **Then** a modal dialog opens with the current order information pre-filled
2. **Given** the edit order modal is open, **When** I modify the order number, date, notes, or delivery link and click "Save", **Then** the order is updated and the page refreshes to show the new information
3. **Given** the edit order modal is open, **When** I click "Cancel", **Then** the modal closes without making any changes
4. **Given** I am on an order details page with reports, **When** I click "Delete Order", **Then** I see a warning message indicating the number of associated reports that must be deleted first

---

### User Story 3 - Create Order and Navigate to Details (Priority: P1)

As an order manager, I want to create a new order and immediately land on its details page, so I can start adding reports right away without searching for the order I just created.

**Why this priority**: This establishes the seamless workflow pattern. Without automatic navigation to the details page after creation, users lose the context-preserving benefit of the feature.

**Independent Test**: Can be fully tested by clicking "Create Order" from the orders list, filling in order details, saving, and verifying automatic redirect to the new order's details page with empty reports section.

**Acceptance Scenarios**:

1. **Given** I am on the orders list page, **When** I click "Create Order", enter order details, and click "Save", **Then** I am automatically redirected to the newly created order's details page
2. **Given** I just created a new order, **When** the order details page loads, **Then** I see the order information I entered and an empty reports section inviting me to add the first report
3. **Given** I created an order and was redirected to its details page, **When** I want to create another order, **Then** I can use the back button to return to the orders list

---

### User Story 4 - Add Reports to Order (Priority: P2)

As an order manager, I want to add reports to an order directly from the order details page, so I can build up the complete order without leaving the order context.

**Why this priority**: Core workflow enhancement that reduces page transitions. Depends on P1 (order details page existing) but is independently valuable once the foundation is in place.

**Independent Test**: Can be fully tested by navigating to any order details page, clicking "Add Report", filling in report details with existing leases, and verifying the report appears in the order's reports table.

**Acceptance Scenarios**:

1. **Given** I am on an order details page, **When** I click the "Add Report" button, **Then** a modal dialog opens with a form to create a new report
2. **Given** the add report modal is open, **When** I select a report type, enter a legal description, and select at least one existing lease, **Then** I can save the report
3. **Given** I am creating a report, **When** I enter optional start date, end date, and notes, **Then** these fields are saved with the report
4. **Given** I successfully created a report, **When** the modal closes, **Then** the reports table refreshes and displays the new report with its details
5. **Given** the reports table has multiple reports, **When** I view the table, **Then** each report shows its type, truncated legal description (with full text on hover), date range, and lease count

---

### User Story 5 - Search and Select Leases for Reports (Priority: P2)

As an order manager, I want to search for leases when creating or editing reports, so I can quickly find and associate the correct leases without scrolling through long lists.

**Why this priority**: Improves usability for the report creation flow established in P2. Essential for organizations with many leases, but the report creation feature works without advanced search.

**Independent Test**: Can be fully tested by opening the add/edit report dialog, typing in the lease search field, and verifying that the lease list filters to show only matching results.

**Acceptance Scenarios**:

1. **Given** I am creating or editing a report, **When** I view the lease selection component, **Then** I see a searchable field with all available leases listed below in the format "LEASE_NUMBER" (e.g., "NMNM 12345")
2. **Given** the lease search field is active, **When** I type an agency name or partial lease number, **Then** the lease list filters in real-time to show only matching leases
3. **Given** I am selecting leases, **When** I click on a lease in the list, **Then** it is added to my selection and appears as a chip/badge above the search field
4. **Given** I have selected leases, **When** I click the X on a lease chip, **Then** that lease is removed from my selection
5. **Given** no leases match my search term, **When** I search, **Then** I see a message "No leases found"

---

### User Story 6 - Create Leases Inline During Report Creation (Priority: P3)

As an order manager, I want to create new leases while filling out a report form, so I can handle the discovery of new lease requirements without abandoning my current work.

**Why this priority**: Advanced workflow enhancement that eliminates the need to leave the report creation context. Valuable but not essential for the core workflow - users can create leases separately and return.

**Independent Test**: Can be fully tested by opening the add report dialog, clicking "Create New Lease" within the lease selection area, filling in agency and lease number, and verifying the new lease is automatically selected for the report.

**Acceptance Scenarios**:

1. **Given** I am creating or editing a report, **When** I view the lease selection component, **Then** I see a "Create New Lease" button below the lease search/list area
2. **Given** I click "Create New Lease", **When** the inline form appears, **Then** I see fields for agency (dropdown) and lease number (text input)
3. **Given** the inline lease creation form is displayed, **When** I select an agency, enter a lease number, and click "Create", **Then** the lease is created and automatically added to my report's lease selection
4. **Given** I successfully created a lease inline, **When** the creation succeeds, **Then** I see a success notification and the inline form closes, returning me to the report form with the new lease selected
5. **Given** I am creating a lease inline, **When** I click "Cancel", **Then** the inline form closes without creating a lease and I return to the report form
6. **Given** I try to create a lease inline, **When** I enter an agency and lease number combination that already exists, **Then** I see an error message and the form remains open for correction

---

### User Story 7 - Edit and Delete Reports from Order (Priority: P3)

As an order manager, I want to edit or delete reports directly from the order details page, so I can make corrections or remove outdated information without navigating elsewhere.

**Why this priority**: Completes the report management workflow but is lower priority than creation. Users can work around missing edit/delete by managing reports from the separate reports page.

**Independent Test**: Can be fully tested by navigating to an order with reports, clicking edit on a report, modifying its details, and verifying changes are reflected in the table. Similarly, testing delete functionality independently.

**Acceptance Scenarios**:

1. **Given** I am viewing an order's reports table, **When** I click the edit icon on a report row, **Then** a modal opens with the report's current information pre-filled
2. **Given** the edit report modal is open, **When** I modify any field (type, legal description, dates, notes, or leases) and click "Update", **Then** the report is updated and the table refreshes
3. **Given** I am editing a report, **When** I add or remove leases using the same selection component as create, **Then** the lease associations are updated
4. **Given** I am viewing a report in the table, **When** I click the delete icon, **Then** a confirmation dialog appears asking if I'm sure
5. **Given** the delete confirmation dialog is open, **When** I confirm deletion, **Then** the report is deleted and removed from the table
6. **Given** a report has associated leases, **When** I delete it, **Then** I see a note that the leases will remain in the system and can be used with other reports

---

### User Story 8 - View Report's Associated Leases (Priority: P3)

As an order manager, I want to see which leases are associated with a specific report, so I can verify correctness and access lease details if needed.

**Why this priority**: Nice-to-have detail view that enhances transparency but isn't required for core workflow. Users can infer lease associations from the lease count and manage leases separately.

**Independent Test**: Can be fully tested by clicking on a report's lease count in the order details table and verifying a list/modal appears showing all associated lease details.

**Acceptance Scenarios**:

1. **Given** I am viewing the reports table on an order details page, **When** I click on a report's lease count, **Then** a modal or expanded section opens showing all leases associated with that report
2. **Given** the lease details modal is open, **When** I view the content, **Then** I see each lease's agency, lease number, runsheet status, and any available links
3. **Given** I am viewing a report's leases, **When** I click on a lease, **Then** I can navigate to the main leases page with a filter applied for that lease
4. **Given** the lease details view is open, **When** I click close or outside the modal, **Then** I return to the order details page

---

### Edge Cases

- **Order with many reports**: What happens when an order has more than 20 reports? Consider pagination or virtual scrolling for the reports table.

- **Concurrent edits**: How does the system handle two users editing the same order or report simultaneously? Implement optimistic updates with rollback on error.

- **Duplicate lease creation**: What happens when a user tries to create a lease inline that already exists (same agency + lease number)? Display clear error message and keep form open for correction.

- **Orphaned data**: How does the system handle when a user tries to view an order that has been deleted by another user? Display error message with link back to orders list.

- **Network failures during creation**: What happens when a user creates a report and the network fails before confirmation? Show error message with retry option, do not close the modal.

- **Empty search results**: How does the system handle when no leases match the search criteria during report creation? Display "No leases found" message and ensure "Create New Lease" button is always accessible.

- **Navigation during unsaved changes**: What happens if a user starts creating a report and clicks the back button? Consider warning about unsaved changes.

- **Order deletion with reports**: What happens when a user tries to delete an order that has reports? Display warning message requiring deletion of reports first, showing the count.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a dedicated page accessible via `/dashboard/orders/[id]` route that displays complete order information including order number, date, notes, delivery link, creator, and creation date

- **FR-002**: System MUST make order rows clickable on the orders list page, navigating to the corresponding order details page when clicked

- **FR-003**: System MUST automatically redirect users to the order details page immediately after successfully creating a new order

- **FR-004**: Order details page MUST display a reports section showing all reports associated with the order in a tabular format with columns for report type, legal description, date range, lease count, and action buttons

- **FR-005**: System MUST display an empty state with "No reports added yet" message and prominent "Add Report" button when an order has no associated reports

- **FR-006**: Users MUST be able to edit order information (order number, date, notes, delivery link) from the order details page via a modal dialog that reuses the existing edit order component

- **FR-007**: System MUST provide a back/return button on the order details page that navigates users back to the orders list page

- **FR-008**: Users MUST be able to create new reports from the order details page by clicking an "Add Report" button that opens a report creation modal

- **FR-009**: Report creation form MUST include fields for report type (dropdown), legal description (textarea), start date (optional date picker), end date (optional date picker), report notes (optional textarea), and lease selection (required multi-select)

- **FR-010**: System MUST provide a searchable lease selection component that filters leases in real-time based on user input matching lease number or agency name

- **FR-011**: Lease selection component MUST display selected leases as removable chips/badges above the search field

- **FR-012**: System MUST display leases in the format "LEASE_NUMBER" (e.g., "NMNM 12345") in the selection dropdown

- **FR-013**: Users MUST be able to create new leases inline during report creation by clicking a "Create New Lease" button within the lease selection component

- **FR-014**: Inline lease creation form MUST include fields for agency (dropdown with options BLM, NMSLO) and lease number (text input)

- **FR-015**: System MUST automatically add newly created leases to the report's lease selection without closing the report creation modal

- **FR-016**: System MUST validate that agency + lease number combinations are unique and display error messages for duplicates during inline lease creation

- **FR-017**: Users MUST be able to edit existing reports from the order details page via an edit icon/button that opens a pre-populated modal with the same form as report creation

- **FR-018**: Users MUST be able to delete reports from the order details page via a delete icon/button that opens a confirmation dialog

- **FR-019**: System MUST refresh the reports table immediately after creating, updating, or deleting a report without requiring a full page reload

- **FR-020**: Users MUST be able to view all leases associated with a report by clicking on the lease count in the reports table

- **FR-021**: System MUST display a warning when attempting to delete an order that has associated reports, indicating the reports must be deleted first

- **FR-022**: System MUST truncate long legal descriptions in the reports table with ellipsis and show the full text on hover

- **FR-023**: System MUST display appropriate loading states while fetching order or report data

- **FR-024**: System MUST display clear error messages when orders or reports fail to load, create, update, or delete

- **FR-025**: System MUST maintain the order ID context when creating reports (order_id is pre-set and not user-selectable in the create report form)

### Key Entities

- **Order**: Represents a customer order containing basic information including order number, order date, notes, delivery link, creator, creation timestamp, and update timestamp. An order serves as a container for multiple reports.

- **Report**: Represents a document associated with an order, containing report type (runsheet, abstract, etc.), legal description, optional date range (start and end), optional notes, and associations to one or more leases. Reports track the specific work being performed for an order.

- **Lease**: Represents a government land lease from agencies (BLM or NMSLO) identified by agency and lease number. Leases can be associated with multiple reports and contain tracking information for runsheet documents and status.

**Entity Relationships**:
- One Order has many Reports (one-to-many)
- One Report has many Leases (many-to-many)
- Reports belong to exactly one Order
- Leases are independent entities that can be associated with multiple Reports

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the workflow of creating an order and adding a report with leases in a single continuous flow without navigating away from the order context

- **SC-002**: Time to create an order with reports is reduced by at least 40% compared to the current workflow requiring navigation between three separate pages

- **SC-003**: Users can view all information about an order and its reports on a single page load without clicking through to multiple pages

- **SC-004**: 100% of report creation workflows that require new leases can be completed without leaving the report creation modal

- **SC-005**: Lease search filters results in under 300 milliseconds as users type, providing responsive feedback

- **SC-006**: Order details page loads and displays all order information and reports table in under 2 seconds

- **SC-007**: Users can successfully create a report with inline lease creation in under 3 minutes for a typical case (1 report with 2-3 leases)

- **SC-008**: Zero navigation steps required to add multiple reports to an order after the initial order creation

- **SC-009**: 90% of users successfully complete their first order-with-reports creation using the new workflow without assistance

- **SC-010**: User task completion rate for "create order with reports and leases" increases by at least 50% (fewer abandoned workflows)

---

## Assumptions

1. **Performance**: Assumes most orders will have fewer than 20 reports; if orders regularly exceed this, pagination will be needed
2. **Lease Count**: Assumes the organization has a manageable number of leases (< 10,000) that can be loaded for search; larger datasets may require backend filtering
3. **Permissions**: Assumes all users who can view orders can also create/edit/delete orders and reports; if role-based permissions are needed, this will require additional authorization checks
4. **Browser Support**: Assumes users access the application on modern browsers with JavaScript enabled
5. **Concurrency**: Assumes low likelihood of simultaneous edits to the same order; optimistic updates with rollback are sufficient
6. **Data Integrity**: Assumes backend enforces referential integrity (e.g., cannot delete order with existing reports)
7. **Search Implementation**: Assumes client-side filtering is acceptable for lease search; server-side search may be needed for large datasets

---

## Out of Scope

The following are explicitly **not** included in this feature:

1. **Bulk Operations**: Bulk creation/deletion of multiple reports or orders at once
2. **Report Templates**: Pre-configured report templates with default values
3. **Report Versioning**: Tracking history of changes to reports
4. **Advanced Filtering**: Filtering reports by type, date range, or lease on the order details page
5. **Export Functionality**: Exporting order details and reports to PDF or other formats
6. **Notifications**: Email or in-app notifications when orders or reports are created/updated
7. **Collaborative Editing**: Real-time collaborative editing of orders or reports by multiple users
8. **Mobile Optimization**: Touch-optimized interfaces for mobile devices (desktop-first approach)
9. **Offline Support**: Ability to create/edit orders offline with sync when connection is restored
10. **Report Approval Workflow**: Multi-step approval process for reports before finalization

---

## Dependencies

- **Existing API Endpoints**: Requires existing backend API endpoints for orders, reports, and leases to support the required CRUD operations
- **Authentication System**: Depends on existing user authentication to identify creators and control access
- **Routing System**: Depends on Next.js dynamic routing to support parameterized order detail pages
- **UI Component Library**: Relies on existing shadcn/ui components (dialogs, tables, forms, buttons, etc.)
- **State Management**: Requires TanStack Query for data fetching, caching, and optimistic updates

---

## Open Questions

*No critical open questions remain. All decisions have been made with reasonable defaults documented in the Assumptions section.*

---

**Document End**
