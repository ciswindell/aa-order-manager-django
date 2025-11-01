# Research: Basecamp Project API Extension

**Feature**: 004-basecamp-project-api | **Date**: 2025-11-01 | **Phase**: 0 (Research)

## Research Questions

### Q1: What Basecamp 3 API endpoints are required for project and task management?

**Decision**: Use Basecamp 3 REST API endpoints for projects, to-do sets, to-do lists, and to-dos

**Rationale**:
- Basecamp 3 API is well-documented at https://github.com/basecamp/bc3-api
- REST endpoints provide full CRUD operations for projects, to-do lists, and tasks
- Existing `BasecampService` already uses requests library with same pattern
- API uses standard JSON request/response format
- Authentication already implemented via OAuth 2.0 Bearer tokens

**Required Endpoints**:

1. **List Projects**: `GET /projects.json`
   - Returns all projects for the authenticated account

2. **Get Project**: `GET /{account_id}/projects/{project_id}.json`
   - Returns specific project details

3. **Get To-Do Set**: `GET /{account_id}/buckets/{project_id}/todosets/{todoset_id}.json`
   - Required to get the to-do set ID before creating to-do lists
   - Every project has exactly one to-do set

4. **List To-Do Lists**: `GET /{account_id}/buckets/{project_id}/todolists.json`
   - Returns all to-do lists in a project (needed for duplicate detection)

5. **Create To-Do List**: `POST /{account_id}/buckets/{project_id}/todosets/{todoset_id}/todolists.json`
   - Creates new to-do list in project's to-do set

6. **Create To-Do**: `POST /{account_id}/buckets/{project_id}/todolists/{todolist_id}/todos.json`
   - Creates new task in a to-do list

7. **Update To-Do**: `PUT /{account_id}/buckets/{project_id}/todos/{todo_id}.json`
   - Updates existing task (name, description, assignees, due date, completion)

8. **Create Comment**: `POST /{account_id}/buckets/{project_id}/recordings/{recording_id}/comments.json`
   - Adds comment to a to-do or to-do list (recording_id is the todo/todolist ID)

**Alternatives Considered**:
- Basecamp 2 API: Deprecated and lacks OAuth 2.0 support
- Basecamp Classic API: Legacy, not suitable for new integrations
- GraphQL: Not supported by Basecamp 3

**Implementation Notes**:
- All endpoints require `Authorization: Bearer {access_token}` header
- All endpoints require `User-Agent: AA Order Manager (support@example.com)` header
- Base URL: `https://3.basecampapi.com/{account_id}`
- Rate limit: Not explicitly documented, but API returns 429 when exceeded
- Timeout: Default to 10 seconds per existing pattern

---

### Q2: What is the Basecamp 3 to-do set architecture?

**Decision**: Every project has one to-do set container; to-do lists are created within that set

**Rationale**:
- Basecamp 3 uses a hierarchical structure: Project → To-Do Set → To-Do Lists → To-Dos
- The to-do set is automatically created when a project is created
- To-do lists cannot be created directly in a project; must be created in the to-do set
- This requires an additional API call to get the to-do set ID before creating lists

**Required Flow**:
1. Get project details to extract dock items
2. Find the to-do set from dock items (type: "todoset")
3. Use to-do set ID when creating to-do lists

**Dock Structure**:
```json
{
  "dock": [
    {
      "id": 123456789,
      "title": "To-dos",
      "name": "todoset",
      "enabled": true,
      "url": "https://3.basecampapi.com/1234567/buckets/9999999/todosets/123456789.json"
    }
  ]
}
```

**Alternatives Considered**:
- Creating to-do lists directly in project: Not supported by Basecamp 3 API architecture
- Caching to-do set IDs: Premature optimization; fetch on-demand first

**Implementation Notes**:
- Cache to-do set ID per project for duration of operation (not persistent storage)
- Extract to-do set ID from project's dock array (filter by name: "todoset")
- Handle case where to-do set is disabled (should be rare)

---

### Q3: How should duplicate to-do list detection be implemented?

**Decision**: Fetch all to-do lists in project and check for exact name match before creation

**Rationale**:
- Basecamp API allows duplicate names but spec requires prevention (FR-003a)
- Name comparison should be case-sensitive to match Basecamp's behavior
- Whitespace should be normalized (trim) to avoid accidental duplicates
- Fetch is required before every create operation (cannot cache due to concurrent modifications)

**Implementation Approach**:
```python
def _check_duplicate_todolist(self, account_id: str, project_id: str, name: str) -> bool:
    """Check if to-do list with name already exists in project."""
    todolists = self.list_todolists(account_id, project_id)
    normalized_name = name.strip()
    return any(todo['name'].strip() == normalized_name for todo in todolists)
```

**Performance Considerations**:
- Average project has 5-20 to-do lists (manageable for in-memory comparison)
- API call adds ~200-500ms latency per creation
- Acceptable tradeoff for data quality guarantee

**Alternatives Considered**:
- Local database cache of to-do lists: Adds complexity, stale data risk
- Substring matching: Too restrictive, users may want similar names
- Case-insensitive matching: Doesn't match Basecamp's behavior

**Implementation Notes**:
- Return clear validation error when duplicate detected
- Include existing to-do list ID in error message for reference
- Normalize both input and existing names with `.strip()`

---

### Q4: What error handling patterns should be used for Basecamp API calls?

**Decision**: Implement exponential backoff for 429, auto-refresh for 401, clear errors for 4xx/5xx

**Rationale**:
- Basecamp API returns standard HTTP status codes
- 429 (rate limit) requires retry with exponential backoff
- 401 (unauthorized) indicates expired token, trigger refresh
- 403 (forbidden) indicates permission issue, don't retry
- 4xx client errors should not retry (except 429)
- 5xx server errors may retry (Basecamp temporary issues)

**Error Handling Strategy**:

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200-299 | Success | Return data |
| 401 | Unauthorized (token expired) | Refresh token, retry once |
| 403 | Forbidden (no permission) | Return error, don't retry |
| 404 | Not Found (invalid ID) | Return error, don't retry |
| 422 | Unprocessable Entity (validation error) | Return error, don't retry |
| 429 | Rate Limit Exceeded | Exponential backoff, retry up to 3 times |
| 500-599 | Server Error | Retry up to 2 times with backoff |

**Exponential Backoff Formula**:
- Initial delay: 1 second
- Multiplier: 2x
- Max delay: 32 seconds
- Max retries: 3 attempts

**Alternatives Considered**:
- Fixed delay retry: Less respectful of API rate limits
- Unlimited retries: Risk of infinite loops
- Circuit breaker pattern: Overly complex for current needs

**Implementation Notes**:
- Leverage existing `_make_request_with_retry` from `BasecampOAuthAuth`
- Log all retry attempts with reason
- Include original error in final failure message
- Use `Retry-After` header when provided by 429 response

---

### Q5: How are to-do groups used to organize tasks?

**Decision**: Use Basecamp 3 to-do groups to create section headers within to-do lists

**Rationale**:
- Groups provide visual organization within to-do lists (e.g., "Setup", "Workup", "Imaging")
- Current manual workflow uses groups extensively for task categorization
- Groups are optional containers; tasks can exist with or without groups
- Groups appear as section headers in Basecamp UI
- Tasks within groups are visually nested under group headers

**Required Endpoints**:

1. **Create Group**: `POST /{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json`
   - Creates named section within to-do list

2. **List Groups**: `GET /{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json`
   - Returns all groups in a to-do list

3. **Assign Task to Group**: Include `group_id` parameter when creating/updating to-do
   - Tasks without group_id appear at top of to-do list (ungrouped)
   - Tasks with group_id appear under that group header

**Structure**:
```
To-Do List: "Order 1950"
├── Task (ungrouped, appears at top)
├── Group: "Setup"
│   ├── Setup Abstract Todos
│   └── Verify Lease Files
├── Group: "Workup"
│   ├── Workup
│   └── Microfilm SRP xLeasex
└── Group: "Imaging"
    ├── Unfiled Documents xLeasex
    └── Image xLeasex
```

**Alternatives Considered**:
- Multiple to-do lists per order: Creates clutter, harder to see full order workflow
- Task naming conventions (prefixes): Less visual, harder to scan
- ✅ Groups: Built-in Basecamp feature, matches current workflow

**Implementation Notes**:
- Groups must be created before assigning tasks to them
- Group IDs are stable and can be reused across multiple tasks
- Groups can be empty (no tasks assigned)
- Basecamp returns groups in order (can be reordered via position parameter, but not in Phase 1)

---

### Q6: What validation should occur before making API calls?

**Decision**: Validate required parameters, string lengths, and ID formats before HTTP requests

**Rationale**:
- Reduces unnecessary network calls for invalid input
- Provides faster feedback to caller
- Prevents cryptic API errors from reaching application layer
- Follows "fail fast" principle

**Validation Rules**:

| Parameter | Validation | Error Message |
|-----------|------------|---------------|
| account_id | Non-empty string, numeric | "Invalid account_id: must be numeric string" |
| project_id | Non-empty string, numeric | "Invalid project_id: must be numeric string" |
| todolist_id | Non-empty string, numeric | "Invalid todolist_id: must be numeric string" |
| todo_id | Non-empty string, numeric | "Invalid todo_id: must be numeric string" |
| name | Non-empty after strip, max 255 chars | "Name required and must be ≤255 characters" |
| description | Optional, max 10,000 chars | "Description must be ≤10,000 characters" |
| due_on | Optional, ISO date format (YYYY-MM-DD) | "Invalid due_on: must be YYYY-MM-DD format" |
| assignee_ids | Optional, list of numeric strings | "Invalid assignee_ids: must be list of numeric strings" |
| group_id | Optional, numeric string | "Invalid group_id: must be numeric string" |
| group_name | Required for groups, max 255 chars | "Group name required and must be ≤255 characters" |

**Implementation Approach**:
```python
def _validate_id(value: str, param_name: str) -> None:
    """Validate ID parameter is non-empty numeric string."""
    if not value or not str(value).strip().isdigit():
        raise ValueError(f"Invalid {param_name}: must be numeric string")

def _validate_name(value: str) -> None:
    """Validate name is non-empty and within length limit."""
    if not value or not value.strip():
        raise ValueError("Name required")
    if len(value) > 255:
        raise ValueError("Name must be ≤255 characters")
```

**Alternatives Considered**:
- Pydantic models: Adds dependency, overkill for simple validation
- Let API validate: Slower feedback, harder to debug
- No validation: Risky, poor user experience

**Implementation Notes**:
- Raise `ValueError` for validation errors (caught by caller)
- Validation errors should not trigger retries
- Log validation failures for debugging

---

## Best Practices

### Basecamp API Guidelines

From https://github.com/basecamp/bc3-api/blob/master/README.md:

1. **User-Agent Header**: Required for all requests
   - Format: `"Your App Name (your-email@example.com)"`
   - Already implemented in existing `BasecampService.headers`

2. **Rate Limiting**: No explicit limit documented, but enforce good practices
   - Respect 429 responses
   - Use exponential backoff
   - Don't make unnecessary calls (validate first)

3. **JSON Formatting**: All request bodies must be JSON
   - Set `Content-Type: application/json` header
   - Use `requests.post(..., json=data)` for automatic serialization

4. **Date Formatting**: Use ISO 8601 format
   - Due dates: `YYYY-MM-DD` (date only, no time)
   - Timestamps: `YYYY-MM-DDTHH:MM:SSZ` (ISO 8601 with timezone)

5. **Pagination**: Use `Link` header for paginated responses
   - Not needed for initial implementation (projects/to-do lists typically <100 items)
   - Can add pagination support in future if needed

### Python requests Library Patterns

1. **Timeout**: Always specify timeout to prevent hanging
   - Use 10 seconds default (matches existing pattern)
   - Allow override for specific cases

2. **Error Handling**: Use `response.raise_for_status()` to detect HTTP errors
   - Catch `requests.exceptions.RequestException` for network errors
   - Catch `requests.exceptions.Timeout` for timeout errors

3. **JSON Parsing**: Use `response.json()` with error handling
   - Catch `json.JSONDecodeError` for malformed responses
   - Validate response structure before accessing fields

### Django Logging Best Practices

1. **Log Level Guidelines**:
   - `logger.info()`: Successful operations, important state changes
   - `logger.warning()`: Recoverable errors, retry attempts
   - `logger.error()`: Unrecoverable errors, API failures
   - `logger.debug()`: Detailed request/response data (not in production)

2. **Structured Logging**: Include context in every log message
   - Format: `"Basecamp API {action} | account_id={id} | status={status}"`
   - Include timing information for performance monitoring

3. **Security**: Never log sensitive data
   - Don't log access tokens or refresh tokens
   - Truncate long payloads (show first 100 chars)

---

## Technology Integration

### Existing Codebase Integration

**Reuse from `BasecampOAuthAuth`**:
- `_make_request_with_retry()`: Exponential backoff logic (can extract to shared utility)
- Token refresh flow: Already handles 401 responses
- Logging pattern: Already uses structured logging

**Extend in `BasecampService`**:
- Add new methods following existing pattern
- Use `self.headers` (already includes Authorization and User-Agent)
- Use `self.access_token` for authentication
- Follow existing method signature patterns

**Example Method Signature** (following existing pattern):
```python
def list_projects(self, account_id: str) -> list[dict]:
    """Get all projects for account.
    
    Args:
        account_id: Basecamp account ID
        
    Returns:
        list: Project objects with id, name, description
        
    Raises:
        requests.exceptions.RequestException: If API call fails
    """
    response = requests.get(
        f"{BASECAMP_API_BASE}/{account_id}/projects.json",
        headers=self.headers,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
```

### Testing Approach

**Manual Testing in Django Shell**:
```python
from web.integrations.basecamp.basecamp_service import BasecampService
from web.integrations.models import BasecampAccount

# Get authenticated service
account = BasecampAccount.objects.get(user=request.user)
service = BasecampService(account.access_token)

# Test project retrieval
projects = service.list_projects(account.account_id)
print(f"Found {len(projects)} projects")

# Test to-do list creation
project_id = projects[0]['id']
todolist = service.create_todolist(
    account.account_id, 
    project_id, 
    "Test Order - 20251101"
)
print(f"Created to-do list: {todolist['id']}")

# Test task creation
todo = service.create_todo(
    account.account_id,
    project_id,
    todolist['id'],
    "Test Task NMNM 001",
    description="Test report task"
)
print(f"Created task: {todo['id']}")
```

**Verification Steps**:
1. Verify objects appear in Basecamp UI
2. Verify duplicate detection prevents second creation
3. Verify assignees and due dates are correct
4. Verify comments appear with proper formatting
5. Test error handling with invalid IDs

---

## Implementation Sequencing

**Recommended Order** (aligns with user story priorities):

1. **Phase 1**: Project retrieval (P1 - US1)
   - `list_projects(account_id)`
   - `get_project(account_id, project_id)`
   - `_get_todoset_id(account_id, project_id)` (helper)

2. **Phase 2**: To-do list management (P2 - US2)
   - `list_todolists(account_id, project_id)`
   - `_check_duplicate_todolist(account_id, project_id, name)` (helper)
   - `create_todolist(account_id, project_id, name, description="")`

3. **Phase 3**: Task management (P3 - US3)
   - `create_todo(account_id, project_id, todolist_id, content, **kwargs)`
   - `update_todo(account_id, project_id, todo_id, **kwargs)`

4. **Phase 4**: Group management (P4 - US4)
   - `list_groups(account_id, project_id, todolist_id)`
   - `create_group(account_id, project_id, todolist_id, name)`

5. **Phase 5**: Comments (P5 - US5)
   - `add_comment(account_id, project_id, recording_id, content)`

**Rationale**: Each phase builds on the previous and can be independently tested. Matches prioritization in feature spec.

---

## Summary

All research questions resolved. Ready to proceed to Phase 1 (design). Key decisions:
- Use Basecamp 3 REST API with standard request/response pattern
- Understand to-do set architecture (required intermediate step)
- Implement duplicate detection via pre-creation list fetch
- Use exponential backoff for 429, auto-refresh for 401
- Validate parameters before API calls for fast failure
- Extend existing `BasecampService` following established patterns
- Test manually in Django shell before integration

