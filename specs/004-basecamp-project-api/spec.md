# Feature Specification: Basecamp Project API Extension

**Feature Branch**: `004-basecamp-project-api`  
**Created**: 2025-11-01  
**Status**: Draft  
**Input**: User description: "Extend Basecamp API service with methods to interact with projects, to-do lists, and tasks"

## Clarifications

### Session 2025-11-01

- Q: Should Phase 1 include deletion operations (delete projects, to-do lists, tasks, groups)? → A: Out of scope for Phase 1 - defer deletion to future phase when workflow management is implemented
- Q: How should system handle concurrent workflow creation attempts for the same order? → A: Not applicable - single-user workflow creation only, concurrent access won't occur in practice
- Q: What logging detail level should be used for API requests? → A: INFO for success, WARNING for retries, ERROR for failures - standard tiered approach with structured context
- Q: What timeout values should be used for API requests? → A: 10 second default for all operations - simple, consistent, matches existing pattern
- Q: What comment formatting is supported? → A: Plain text only with auto-linked URLs - correct the spec to match Basecamp's actual capability

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Basecamp Projects (Priority: P1)

System needs to retrieve and display Basecamp projects so that future workflow automation can identify which project to create tasks in.

**Why this priority**: Without the ability to retrieve projects, no other project-based operations are possible. This is the foundational capability that enables all subsequent task and to-do list management.

**Independent Test**: Can be fully tested by calling the project retrieval method with a valid account ID and verifying that a list of projects is returned with correct project details (ID, name, description). Delivers value by enabling project discovery for workflow automation.

**Acceptance Scenarios**:

1. **Given** authenticated Basecamp connection exists, **When** system requests all projects for an account, **Then** system returns list of all accessible projects with ID, name, and basic metadata
2. **Given** authenticated Basecamp connection exists, **When** system requests a specific project by ID, **Then** system returns complete project details including ID, name, description, and status
3. **Given** invalid account ID is provided, **When** system requests projects, **Then** system returns appropriate error message without crashing
4. **Given** Basecamp API is unavailable, **When** system requests projects, **Then** system handles timeout gracefully and returns error status

---

### User Story 2 - Create and Manage To-Do Lists (Priority: P2)

System needs to create to-do lists within Basecamp projects so that workflows can organize tasks into logical groupings (e.g., "Order 1943 - 20251022" to-do list).

**Why this priority**: To-do lists are the primary containers for tasks in Basecamp. This capability enables the basic structure for order-based workflow creation.

**Independent Test**: Can be fully tested by creating a to-do list in a test project, verifying it appears in Basecamp UI with correct name and description, and confirming the returned to-do list ID can be used for subsequent task creation. Delivers value by enabling workflow structure creation.

**Acceptance Scenarios**:

1. **Given** valid project ID exists, **When** system creates to-do list with name and description, **Then** to-do list is created in Basecamp and system returns to-do list ID
2. **Given** to-do list with same name already exists in project, **When** system attempts to create duplicate to-do list, **Then** system returns validation error preventing duplicate creation
3. **Given** to-do list name contains special characters, **When** system creates to-do list, **Then** name is properly encoded and to-do list is created successfully
4. **Given** to-do list name exceeds Basecamp's character limit, **When** system attempts creation, **Then** system returns validation error before making API call
5. **Given** project ID is invalid or inaccessible, **When** system attempts to create to-do list, **Then** system returns clear error message indicating project issue

---

### User Story 3 - Create and Manage Tasks (Priority: P3)

System needs to create and update individual tasks (to-dos) within to-do lists so that specific work items can be assigned and tracked (e.g., "NMNM 0002889" task with assignee and due date).

**Why this priority**: Tasks are the actionable work items that users complete. This capability enables the detailed workflow execution that mirrors the current manual Basecamp setup.

**Independent Test**: Can be fully tested by creating a task in a test to-do list with name, description, assignee, and due date, verifying it appears correctly in Basecamp, then updating the task and confirming changes are reflected. Delivers value by enabling complete workflow task management.

**Acceptance Scenarios**:

1. **Given** valid to-do list ID exists, **When** system creates task with name and description, **Then** task is created in Basecamp and system returns task ID
2. **Given** task creation includes assignee IDs, **When** system creates task, **Then** task is assigned to specified Basecamp users
3. **Given** task creation includes due date, **When** system creates task, **Then** task has correct due date set in Basecamp
4. **Given** existing task ID, **When** system updates task with new information, **Then** task is updated in Basecamp with new values
5. **Given** task update includes status change, **When** system updates task, **Then** task status is changed (completed/incomplete)
6. **Given** invalid assignee ID is provided, **When** system attempts to create task, **Then** system returns error indicating invalid assignee

---

### User Story 4 - Organize Tasks with Groups (Priority: P4)

System needs to create and manage to-do groups within to-do lists so that tasks can be organized into logical sections (e.g., "Setup", "Workup", "Imaging", "Indexing").

**Why this priority**: Groups provide visual organization and structure within to-do lists, matching the current manual Basecamp workflow. While not required for basic task creation, groups significantly improve task organization and user experience.

**Independent Test**: Can be fully tested by creating groups in a to-do list, assigning tasks to groups, verifying the grouped structure appears correctly in Basecamp UI with proper section headers. Delivers value by enabling the same organizational structure currently used in manual workflows.

**Acceptance Scenarios**:

1. **Given** valid to-do list ID exists, **When** system creates group with name, **Then** group is created in Basecamp and system returns group ID
2. **Given** groups exist in to-do list, **When** system lists groups, **Then** system returns all groups with IDs and names
3. **Given** valid group ID exists, **When** system creates task with group_id parameter, **Then** task is created within that group in Basecamp
4. **Given** task exists in a group, **When** system updates task with different group_id, **Then** task is moved to new group
5. **Given** group name exceeds character limit, **When** system attempts creation, **Then** system returns validation error before making API call

---

### User Story 5 - Add Comments and Notes (Priority: P5)

System needs to add comments to tasks and to-do lists so that contextual information like Dropbox links and report details can be attached to tasks.

**Why this priority**: Comments provide additional context and links that users need to complete tasks. This capability enhances the workflow with supporting information but is not required for basic task creation.

**Independent Test**: Can be fully tested by adding a comment with text and links to a test task, verifying the comment appears in Basecamp with proper formatting, and confirming links are clickable. Delivers value by enabling rich task context and documentation.

**Acceptance Scenarios**:

1. **Given** valid task ID exists, **When** system adds comment with text content, **Then** comment is added to task in Basecamp
2. **Given** comment includes URLs, **When** system adds comment, **Then** URLs are automatically converted to clickable links by Basecamp
3. **Given** comment is plain text, **When** system adds comment, **Then** text is displayed as-is in Basecamp (no markdown or HTML formatting supported)
4. **Given** comment exceeds Basecamp's character limit, **When** system attempts to add comment, **Then** system returns validation error
5. **Given** invalid task ID, **When** system attempts to add comment, **Then** system returns clear error message

---

### Edge Cases

- What happens when Basecamp API returns 429 (rate limit exceeded)?
  - System implements exponential backoff retry mechanism and waits for retry-after period before reattempting

- What happens when Basecamp access token expires during API call?
  - System detects expired token, automatically refreshes using refresh token, and retries the failed API call

- What happens when network connection is lost mid-request?
  - System detects timeout/connection error, logs the failure, and returns error status without leaving partial data

- What happens when Basecamp API response format changes unexpectedly?
  - System validates response structure and returns parsing error rather than crashing

- What happens when creating to-do list with duplicate name in same project?
  - System detects existing to-do list with same name and returns validation error preventing duplicate creation

- What happens when user's Basecamp permissions are revoked mid-operation?
  - System receives 403 Forbidden response and returns clear authentication/authorization error

- What happens when assignee is no longer member of Basecamp project?
  - Basecamp API returns error; system reports invalid assignee and task creation fails gracefully

- What happens when multiple API calls are made concurrently?
  - Each API call is independent and thread-safe; system handles concurrent requests without race conditions
  - Note: Workflow creation is single-user controlled; concurrent workflow attempts for same order not expected in practice

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide method to list all projects for a given Basecamp account ID
- **FR-002**: System MUST provide method to retrieve specific project details by account ID and project ID
- **FR-003**: System MUST provide method to create to-do list within a project with name and optional description
- **FR-003a**: System MUST check for existing to-do lists with the same name in the project before creation and return validation error if duplicate exists
- **FR-004**: System MUST provide method to create task within a to-do list with name, optional description, optional assignee IDs, and optional due date
- **FR-005**: System MUST provide method to update existing task with new name, description, assignees, due date, or completion status
- **FR-005a**: System MUST provide method to create group within a to-do list with name
- **FR-005b**: System MUST provide method to list all groups in a to-do list
- **FR-005c**: System MUST support assigning tasks to groups during creation and update operations
- **FR-006**: System MUST provide method to add comments to tasks and to-do lists
- **FR-007**: System MUST handle Basecamp API authentication using existing OAuth token from BasecampAccount model
- **FR-008**: System MUST implement exponential backoff for rate-limited requests (HTTP 429)
- **FR-009**: System MUST handle expired tokens by triggering automatic refresh before retrying failed request
- **FR-010**: System MUST validate input parameters before making API calls to prevent unnecessary network requests
- **FR-011**: System MUST return structured error responses that distinguish between client errors (400-level) and server errors (500-level)
- **FR-012**: System MUST follow the existing BasecampService pattern in `web/integrations/basecamp/basecamp_service.py`
- **FR-013**: System MUST include User-Agent header in all API requests as required by Basecamp API guidelines
- **FR-014**: System MUST log all API requests with method, endpoint, and response status using tiered levels: INFO for successful requests, WARNING for retry attempts, ERROR for failures; include structured context (account_id, request_id) for debugging
- **FR-015**: System MUST handle timeout errors gracefully with 10 second default timeout for all API requests (matching existing BasecampService pattern)
- **FR-016**: All methods MUST return consistent response format (success data or error object)

### Key Entities

- **BasecampProject**: Represents a Basecamp project with ID, name, description, status, and metadata. Retrieved from Basecamp API, not stored locally.

- **BasecampTodoList**: Represents a to-do list within a project with ID, name, description, and parent project reference. Created via API, used to organize tasks.

- **BasecampTodo**: Represents an individual task with ID, content (name), description, assignees, due date, and completion status. The actionable work items users complete.

- **BasecampGroup**: Represents a section/group within a to-do list with ID and name. Used to organize tasks into logical sections (Setup, Workup, Imaging, etc.).

- **BasecampComment**: Represents a comment/note on a task or to-do list with plain text content, author, and timestamp. URLs in content are auto-linked by Basecamp. Used to provide context and links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All API methods successfully interact with Basecamp and return expected data structures within 3 seconds under normal network conditions
- **SC-002**: API methods handle rate limiting (HTTP 429) with automatic retry and succeed 95% of the time after retry
- **SC-003**: API methods handle expired tokens by refreshing and retrying, succeeding 95% of the time
- **SC-004**: All API methods return clear error messages for all failure scenarios without exposing sensitive data
- **SC-005**: API methods can be tested in isolation using Django shell with mock data
- **SC-006**: Zero API calls result in unhandled exceptions that crash the application
- **SC-007**: API response parsing handles unexpected response formats gracefully with validation errors
- **SC-008**: All API methods follow consistent error handling pattern established by existing Basecamp authentication methods
- **SC-009**: Logging provides clear operational visibility with INFO-level success logging, WARNING-level retry alerts, and ERROR-level failure details

## Assumptions

- Basecamp 3 API documentation is accurate and endpoints are stable
- OAuth authentication is already functional via existing BasecampAccount and BasecampOAuthAuth implementations
- User has active Basecamp account with appropriate permissions to create projects, to-do lists, and tasks
- Basecamp API rate limits are documented and reasonable (not requiring complex queuing mechanisms)
- System enforces stricter validation than Basecamp (e.g., duplicate to-do list prevention) to maintain data quality
- Network connectivity to Basecamp API endpoints is reliable (standard internet connection)
- Basecamp API returns consistent JSON response formats across different API versions
- User-Agent header requirement from Basecamp 3 API can use existing constant from basecamp_service.py
- Python requests library is adequate for all HTTP operations (no need for specialized HTTP client)
- API methods will be called within Django application context (access to logging, settings)
- 10 second timeout is sufficient for all Basecamp API operations under normal network conditions
- Basecamp 3 API supports plain text comments with auto-linked URLs only (no markdown or HTML formatting)
- Basecamp project IDs and to-do list IDs are stable and can be used for subsequent operations
- Error responses from Basecamp API include sufficient detail to diagnose issues
- Workflow creation is controlled by single user per order; no concurrent workflow creation attempts expected

## Dependencies

- Existing `BasecampService` class in `web/integrations/basecamp/basecamp_service.py`
- Existing `BasecampOAuthAuth` for token management and refresh logic
- Existing `BasecampAccount` model for token storage
- Python `requests` library for HTTP calls
- Basecamp 3 API endpoints and documentation at https://github.com/basecamp/bc3-api
- Django logging framework for request/response logging

## Out of Scope

- Deletion operations for any Basecamp entities (projects, to-do lists, tasks, groups, comments) - deferred to Phase 2/3 when workflow management patterns are established
- User interface for browsing or selecting Basecamp projects (future frontend work)
- Storing Basecamp project/task data locally in database (future caching feature)
- Webhooks or real-time synchronization from Basecamp to application (future integration)
- Bulk operations for creating multiple tasks at once (future optimization)
- Reordering groups or tasks within groups (future feature)
- Basecamp schedule/milestone integration (different API endpoints)
- File upload capabilities to Basecamp (future feature)
- Searching or filtering Basecamp projects/tasks (future feature)
- Automatic workflow creation on order creation (Phase 2 of implementation plan)
- Template-based workflow creation (Phase 3 of implementation plan)
- Two-way synchronization of task status between Basecamp and application
- User permission validation within Basecamp (rely on API to enforce)
- Basecamp account or project creation
- Integration with Basecamp's message boards or campfire chat
- Support for Basecamp 2 or Basecamp 4 APIs (only Basecamp 3)

**Note**: This feature extends the existing Basecamp OAuth integration with project and task management capabilities. It establishes the API foundation required for future workflow automation (Phase 2) and template-driven workflow creation (Phase 3).
