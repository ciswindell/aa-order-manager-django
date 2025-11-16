# Feature Specification: Basecamp Order Workflows

**Feature Branch**: `007-basecamp-order-workflows`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Create Basecamp workflows from orders for runsheets and abstracts"

## Clarifications

### Session 2025-11-02

- Q: What are the complete abstract workflow steps, organized by group? → A: Defer workflow steps to implementation phase - focus on getting the basics working first; exact steps to be finalized later
- Q: Are "RUNSHEET" and "BASE_ABSTRACT" the exact report_type enum values? → A: Report types are RUNSHEET, BASE_ABSTRACT, SUPPLEMENTAL_ABSTRACT, DOL_ABSTRACT (found in ReportType model). All non-runsheet types are abstracts; to-do list title should include the abstract type (Base, Supplemental, or DOL)
- Q: Should multi-product success messages display multiple direct links to created to-do lists? → A: Summary only - display generic success message with total count, no direct links to individual to-do lists
- Q: What information should be logged for debugging failed workflow creation? → A: Comprehensive - all context including order/report/lease IDs, API errors, stack traces for rapid diagnosis
- Q: Should the system retry failed Basecamp API calls during workflow creation? → A: Yes - retry with exponential backoff (matches existing basecamp_service.py pattern for consistent failure handling)

## User Scenarios & Testing *(mandatory)*

This feature automates the creation of Basecamp task workflows from order data. The system supports 4 product types across 2 distinct workflow patterns: Runsheets (lease-centric, flat structure) and Abstracts (report-centric, grouped by department).

### User Story 1 - Create Federal Runsheet Workflows (Priority: P1) 🎯 MVP

A user with an order containing Federal (BLM agency) runsheet reports clicks "Push to Basecamp" and the system automatically creates a to-do list in the Federal Runsheets Basecamp project with one task per BLM lease.

**Why this priority**: Simplest workflow pattern (flat, lease-based). Validates end-to-end integration without complexity. Delivers immediate value for Federal runsheet orders.

**Independent Test**: User views order with 3 BLM runsheet reports, clicks "Push to Basecamp", and verifies a single to-do list appears in Federal Runsheets project with 3 tasks (one per lease). Each task includes lease number, legal description, and archive link.

**Acceptance Scenarios**:

1. **Given** an order with 2 Federal runsheet reports containing 3 BLM leases, **When** user clicks "Push to Basecamp", **Then** system creates 1 to-do list named "Order {number} - {date}" in Federal Runsheets project with 3 to-do items (one per lease)

2. **Given** a BLM lease where previous runsheet report was found, **When** workflow is created, **Then** the to-do item is named "{lease_number} - Previous Report"

3. **Given** a BLM lease where no previous runsheet report was found, **When** workflow is created, **Then** the to-do item is named "{lease_number}" (without suffix)

4. **Given** runsheet to-dos created, **When** viewing in Basecamp, **Then** each to-do includes legal description and runsheet archive link in the description

5. **Given** workflow creation succeeds, **When** user views result, **Then** system displays success message with workflow creation summary

---

### User Story 2 - Create Federal Abstract Workflows (Priority: P2)

A user with an order containing Federal (BLM agency) abstract reports clicks "Push to Basecamp" and the system creates one to-do list per report in the Federal Abstracts project, with workflow steps organized by department groups (Setup, Workup, Imaging, Indexing, Assembly, Delivery).

**Why this priority**: More complex pattern with grouped steps. Builds on P1 infrastructure. Covers second major workflow type.

**Independent Test**: User views order with 1 BLM abstract report containing 2 leases, clicks "Push to Basecamp", and verifies a to-do list appears in Federal Abstracts project with 6 department groups and fixed workflow steps, with some steps duplicated per lease (e.g., "Create Abstract Worksheet" appears twice).

**Acceptance Scenarios**:

1. **Given** an order with 1 Federal BASE_ABSTRACT report containing 2 leases, **When** user clicks "Push to Basecamp", **Then** system creates 1 to-do list named "Order {number}- Base Abstract {report_id} - {date}" in Federal Abstracts project

2. **Given** abstract to-do list created, **When** viewing in Basecamp, **Then** to-do list contains 6 groups: Setup, Workup, Imaging, Indexing, Assembly, Delivery

3. **Given** abstract workflow with 2 leases, **When** workflow is created, **Then** lease-specific steps (File Index, Create/Review Worksheet) are created once per lease within appropriate groups

4. **Given** abstract to-do list created, **When** viewing description, **Then** it includes report type, date range, all lease numbers, legal description, and delivery link

5. **Given** an order with 2 abstract reports, **When** user clicks "Push to Basecamp", **Then** system creates 2 separate to-do lists in Federal Abstracts project (one per report)

---

### User Story 3 - Create State Product Workflows (Priority: P3)

A user with an order containing State (NMSLO agency) reports (runsheets or abstracts) clicks "Push to Basecamp" and the system creates workflows in State Runsheets and/or State Abstracts projects following the same patterns as Federal products.

**Why this priority**: Extends existing patterns to new agency. No new logic required, just configuration. Completes coverage of all 4 product types.

**Independent Test**: User views order with 1 NMSLO runsheet report and 1 NMSLO abstract report, clicks "Push to Basecamp", and verifies workflows are created in both State Runsheets and State Abstracts projects following the same structure as Federal products.

**Acceptance Scenarios**:

1. **Given** an order with NMSLO runsheet reports, **When** user clicks "Push to Basecamp", **Then** system creates to-do list in State Runsheets project following Pattern A (lease-centric, flat)

2. **Given** an order with NMSLO abstract reports, **When** user clicks "Push to Basecamp", **Then** system creates to-do lists in State Abstracts project following Pattern B (report-centric, grouped)

3. **Given** NMSLO workflows created, **When** comparing to BLM workflows, **Then** structure and naming conventions are identical (only project location differs)

---

### User Story 4 - Handle Multi-Product Orders (Priority: P4)

A user with an order containing multiple product types (e.g., both Federal and State, both runsheets and abstracts) clicks "Push to Basecamp" and the system creates workflows in all applicable Basecamp projects simultaneously.

**Why this priority**: Handles real-world complexity where orders contain mixed products. Validates that workflow strategies work independently and can run in parallel.

**Independent Test**: User views order with 2 BLM runsheet reports, 1 BLM abstract report, and 1 NMSLO runsheet report, clicks "Push to Basecamp", and verifies 3 to-do lists are created across 3 different Basecamp projects.

**Acceptance Scenarios**:

1. **Given** an order with both Federal runsheets and Federal abstracts, **When** user clicks "Push to Basecamp", **Then** system creates workflows in both Federal Runsheets and Federal Abstracts projects

2. **Given** an order with both Federal and State products, **When** user clicks "Push to Basecamp", **Then** system creates workflows in all applicable projects (up to 4 projects)

3. **Given** multi-product workflow creation, **When** one product fails, **Then** system continues creating workflows for other products and reports partial success

4. **Given** multi-product workflow succeeds, **When** user views result, **Then** system displays which product workflows were created (e.g., "Workflows created: Federal Runsheets, Federal Abstracts, State Runsheets")

---

### Edge Cases

- **Order with no applicable reports**: System displays message "No workflows to create for this order" without creating anything
- **Order already has workflows created**: System allows duplicate creation (Basecamp permits duplicate to-do list names for workflow iteration)
- **Missing Basecamp connection**: System displays error "Basecamp not connected" with link to integrations page
- **Missing project ID configuration**: System displays clear error identifying which project ID environment variable is not configured
- **Basecamp API timeout or failure**: System retries with exponential backoff (consistent with existing service), logs comprehensive error details, displays user-friendly message, and continues with other products if multi-product order
- **Empty legal descriptions or missing links**: System creates workflow with empty description fields rather than failing
- **Report with no leases**: Runsheet workflows skip the report; Abstract workflows create standard steps without lease-specific duplications
- **Lease with very long lease number**: System truncates to-do name at Basecamp's limit while preserving readability

## Requirements *(mandatory)*

### Functional Requirements

#### Workflow Trigger
- **FR-001**: System MUST provide "Push to Basecamp" button on order details page visible to authenticated users
- **FR-002**: System MUST validate user has active Basecamp connection before creating workflows
- **FR-003**: Button MUST be disabled during workflow creation with loading indicator

#### Product Detection
- **FR-004**: System MUST analyze order to determine which product types are present (Federal Runsheets, Federal Abstracts, State Runsheets, State Abstracts)
- **FR-005**: System MUST filter reports by report_type (RUNSHEET for runsheets; BASE_ABSTRACT, SUPPLEMENTAL_ABSTRACT, DOL_ABSTRACT for abstracts) and lease agency (BLM or NMSLO) to determine applicability
- **FR-006**: System MUST create workflows for all applicable product types in a single button click

#### Runsheet Workflow Creation (Pattern A)
- **FR-007**: For runsheet products, system MUST create one to-do list per order in the configured Basecamp project
- **FR-008**: To-do list name MUST follow format: "Order {order_number} - {order_date_YYYYMMDD}"
- **FR-009**: System MUST create one to-do item per lease for the matching agency (BLM or NMSLO)
- **FR-010**: To-do item name MUST be "{lease_number} - Previous Report" if lease.runsheet_report_found is True, otherwise "{lease_number}"
- **FR-011**: To-do description MUST include report legal description and lease runsheet_archive_link
- **FR-012**: To-do list description MUST include order delivery_link if present
- **FR-013**: Runsheet workflows MUST NOT create groups (flat structure)

#### Abstract Workflow Creation (Pattern B)
- **FR-014**: For abstract products, system MUST create one to-do list per report (not per order) in the configured Basecamp project
- **FR-015**: To-do list name MUST follow format: "Order {order_number}- {abstract_type} Abstract {report_id} - {order_date_YYYYMMDD}" where abstract_type is "Base", "Supplemental", or "DOL" based on report_type
- **FR-016**: System MUST create 6 Basecamp groups in order: Setup, Workup, Imaging, Indexing, Assembly, Delivery
- **FR-017**: System MUST create workflow steps within each group (exact steps to be finalized during implementation based on existing Basecamp abstract workflows)
- **FR-018**: For lease-specific steps (examples: File Index, Create Worksheet, Review Worksheet), system MUST create one instance per lease
- **FR-019**: To-do list description MUST include: report type, date range, list of lease numbers, legal description, delivery link
- **FR-020**: Each to-do MUST be assigned to its corresponding group

#### Configuration
- **FR-021**: System MUST load Basecamp project IDs from environment configuration for: federal_runsheets, federal_abstracts, state_runsheets, state_abstracts
- **FR-022**: System MUST fail gracefully with clear error message if required project ID is not configured

#### Error Handling
- **FR-023**: System MUST log all workflow creation attempts with comprehensive context: order ID, user ID, product types, outcome, and for failures: report IDs, lease IDs, API error responses, HTTP status codes, and stack traces
- **FR-024**: System MUST retry failed Basecamp API calls using exponential backoff strategy (consistent with existing BasecampService behavior)
- **FR-025**: System MUST continue creating workflows for remaining products if one product fails (partial success)
- **FR-026**: System MUST display user-friendly error messages without exposing technical details
- **FR-027**: System MUST display success message with count of created workflows (no direct links to individual to-do lists)

#### Multi-Product Support
- **FR-028**: System MUST detect and create workflows for all applicable products in a single order
- **FR-029**: System MUST handle orders with no applicable products gracefully (display "No workflows to create")
- **FR-030**: Success message MUST list which product workflows were created

### Key Entities

- **Order**: Represents a customer order with order_number, order_date, and delivery_link. Contains multiple reports.

- **Report**: Represents a runsheet or abstract report within an order. Has report_type (RUNSHEET, BASE_ABSTRACT, SUPPLEMENTAL_ABSTRACT, or DOL_ABSTRACT), legal_description, start_date, end_date. Associated with multiple leases.

- **Lease**: Represents a land lease with lease_number, agency (BLM or NMSLO), runsheet_report_found (boolean), and runsheet_archive_link. Multiple leases can be associated with a report.

- **Basecamp To-do List**: Container for related tasks in Basecamp. Created per order (runsheets) or per report (abstracts). Has name, description, and contains to-do items.

- **Basecamp To-do Item**: Individual task within a to-do list. Has name (content) and description. May belong to a group (abstracts only).

- **Basecamp Group**: Organizational container within a to-do list for grouping related to-do items by department/phase (abstracts only). Has name (Setup, Workup, Imaging, Indexing, Assembly, Delivery).

- **Product Configuration**: Maps product type (federal_runsheets, federal_abstracts, state_runsheets, state_abstracts) to Basecamp project ID, workflow strategy, and agency filter.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can create workflows for all applicable products in an order with a single button click
- **SC-002**: Workflow creation completes within 30 seconds for orders with up to 10 reports
- **SC-003**: System successfully creates workflows for 95% of orders (excluding configuration/connection errors)
- **SC-004**: Success message displays within 5 seconds of completion with workflow creation summary
- **SC-005**: For runsheet orders, each lease appears as exactly one to-do item with correct naming convention
- **SC-006**: For abstract orders, each report results in exactly one to-do list with 6 department groups
- **SC-007**: Multi-product orders create workflows in all applicable Basecamp projects without manual intervention
- **SC-008**: Workflow creation errors are resolved within 2 minutes by following displayed error messages (configuration errors)
- **SC-009**: System handles orders with mixed product types (Federal/State, Runsheets/Abstracts) without creating duplicate or missing workflows

### Assumptions

1. **Basecamp Connection**: Assumes user has already connected Basecamp account via existing OAuth integration
2. **Project IDs Available**: Assumes all 4 Basecamp project IDs are configured in environment variables before deployment
3. **Stable Workflow Steps**: Assumes abstract workflow steps (Setup → Delivery) remain relatively stable over time
4. **Single Account**: Assumes user has selected correct Basecamp account (account selection is handled by existing OAuth flow)
5. **Network Reliability**: Assumes Basecamp API is available and responsive (standard web application assumptions)
6. **Data Completeness**: Assumes orders contain valid reports and leases (data entry validation exists elsewhere)
7. **Idempotency Not Required**: Assumes users may need to create workflows multiple times for iteration (Basecamp allows duplicate to-do lists)
8. **No Real-Time Sync**: Assumes workflows are created on-demand (button click) rather than automatically on order changes

### Out of Scope

- **Template Customization**: Workflow steps and structure are hardcoded. User customization of workflow templates is Phase 3 (future)
- **Automatic Workflow Creation**: Workflows are not created automatically on order creation or status changes (manual trigger only)
- **Bidirectional Sync**: Changes to Basecamp tasks do not update order data in the system
- **Workflow Deletion**: No ability to delete or rollback created workflows from the system (must be done manually in Basecamp)
- **Assignee Management**: To-do items are created without assignees (assignment happens manually in Basecamp)
- **Due Dates**: To-do items are created without due dates (dates set manually in Basecamp)
- **Progress Tracking**: System does not track completion status of Basecamp to-dos
- **Workflow Validation**: System does not validate that created workflows match business requirements (manual QA required)
- **Bulk Operations**: No ability to create workflows for multiple orders simultaneously
- **Workflow Preview**: No preview or simulation of workflows before creation
- **Custom Workflow Steps**: All workflow steps are hardcoded per product type (no per-order customization)
