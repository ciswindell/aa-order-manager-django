# API Contract: Basecamp 3 Project and Task Management

**Feature**: 004-basecamp-project-api | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This document defines the Basecamp 3 API endpoints used by the extended `BasecampService` for project, to-do list, and task management. These are **external API endpoints** provided by Basecamp 3, not internal application endpoints.

**Base URL**: `https://3.basecampapi.com/{account_id}`

**Authentication**: OAuth 2.0 Bearer token (from existing `BasecampAccount.access_token`)

**Required Headers** (all endpoints):
```http
Authorization: Bearer {access_token}
User-Agent: AA Order Manager (support@example.com)
Content-Type: application/json (for POST/PUT requests)
```

**Reference**: https://github.com/basecamp/bc3-api

---

## Endpoints

### 1. List Projects

**Purpose**: Retrieve all projects accessible by authenticated account

```http
GET /projects.json
```

**Request**:
- Headers: Authorization, User-Agent
- Body: None
- Query Parameters: None

**Response** (200 OK):
```json
[
  {
    "id": 2085958499,
    "status": "active",
    "created_at": "2024-10-26T10:28:57.873-05:00",
    "updated_at": "2024-10-26T10:28:58.365-05:00",
    "name": "Federal Runsheets",
    "description": "Order management and tracking",
    "purpose": "topic",
    "bookmarked": false,
    "dock": [
      {
        "id": 123456789,
        "title": "To-dos",
        "name": "todoset",
        "enabled": true
      }
    ]
  }
]
```

**Response Fields**:
- `id` (integer): Project ID
- `name` (string): Project name
- `description` (string): Project description
- `status` (string): "active" or "archived"
- `dock` (array): Enabled features (contains todoset)

**Error Responses**:

**401 Unauthorized**: Token expired or invalid
```json
{
  "error": "Unauthorized"
}
```

**429 Too Many Requests**: Rate limit exceeded
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

**Implementation Notes**:
- Returns all projects (active and archived)
- Filter by `status: "active"` in application if needed
- Extract todoset ID from dock for to-do list operations

---

### 2. Get Project Details

**Purpose**: Retrieve specific project with full details including dock

```http
GET /{account_id}/projects/{project_id}.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID

**Request**:
- Headers: Authorization, User-Agent
- Body: None

**Response** (200 OK):
```json
{
  "id": 2085958499,
  "status": "active",
  "created_at": "2024-10-26T10:28:57.873-05:00",
  "updated_at": "2024-10-26T10:28:58.365-05:00",
  "name": "Federal Runsheets",
  "description": "Order management and tracking",
  "purpose": "topic",
  "bookmarked": false,
  "dock": [
    {
      "id": 123456789,
      "title": "To-dos",
      "name": "todoset",
      "enabled": true,
      "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todosets/123456789.json"
    }
  ]
}
```

**Error Responses**:

**404 Not Found**: Project doesn't exist or not accessible
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Use to extract todoset ID before creating to-do lists
- todoset is always present in dock if To-dos feature is enabled

---

### 3. List To-Do Lists

**Purpose**: Retrieve all to-do lists in a project (for duplicate detection)

```http
GET /{account_id}/buckets/{project_id}/todolists.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)

**Request**:
- Headers: Authorization, User-Agent
- Body: None

**Response** (200 OK):
```json
[
  {
    "id": 987654321,
    "status": "active",
    "created_at": "2024-10-26T12:15:33.456-05:00",
    "updated_at": "2024-10-26T12:15:33.456-05:00",
    "title": "Order 1943 - 20251022",
    "name": "Order 1943 - 20251022",
    "description": "Dropbox link: https://www.dropbox.com/...",
    "completed": false,
    "completed_ratio": "3/8"
  }
]
```

**Response Fields**:
- `id` (integer): To-do list ID
- `name` (string): To-do list name (use for duplicate detection)
- `description` (string): Optional description
- `completed` (boolean): All tasks completed
- `completed_ratio` (string): "X/Y" format

**Error Responses**:

**404 Not Found**: Project doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Use for duplicate name detection before creation
- Compare names case-sensitive with whitespace normalization

---

### 4. Create To-Do List

**Purpose**: Create new to-do list in project's to-do set

```http
POST /{account_id}/buckets/{project_id}/todosets/{todoset_id}/todolists.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todoset_id` (string): To-do set ID (from project.dock)

**Request**:
- Headers: Authorization, User-Agent, Content-Type: application/json
- Body:
```json
{
  "name": "Order 1943 - 20251022",
  "description": "Dropbox link: https://www.dropbox.com/..."
}
```

**Request Fields**:
- `name` (string, required): To-do list name, max 255 characters
- `description` (string, optional): Description, max 10,000 characters

**Response** (201 Created):
```json
{
  "id": 987654321,
  "status": "active",
  "created_at": "2024-10-26T12:15:33.456-05:00",
  "updated_at": "2024-10-26T12:15:33.456-05:00",
  "title": "Order 1943 - 20251022",
  "name": "Order 1943 - 20251022",
  "description": "Dropbox link: https://www.dropbox.com/...",
  "completed": false,
  "completed_ratio": "0/0",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/987654321"
}
```

**Error Responses**:

**422 Unprocessable Entity**: Validation error
```json
{
  "error": "Name can't be blank"
}
```

**404 Not Found**: Project or todoset doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Must get todoset_id from project.dock before calling
- Check for duplicates before calling (app-enforced, not API-enforced)
- Return created todolist with ID for subsequent task creation

---

### 5. Create To-Do (Task)

**Purpose**: Create new task in a to-do list

```http
POST /{account_id}/buckets/{project_id}/todolists/{todolist_id}/todos.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todolist_id` (string): To-do list ID

**Request**:
- Headers: Authorization, User-Agent, Content-Type: application/json
- Body:
```json
{
  "content": "NMNM 0002889",
  "description": "Reports Needed: 24S-32E, Sec. 3-NESW From 9/1/2020",
  "due_on": "2024-11-15",
  "assignee_ids": [1049715916, 1049715917]
}
```

**Request Fields**:
- `content` (string, required): Task name, max 255 characters
- `description` (string, optional): Task description, max 10,000 characters
- `due_on` (string, optional): Due date in YYYY-MM-DD format
- `assignee_ids` (array, optional): Array of Basecamp user IDs (integers)
- `group_id` (integer, optional): Group ID to assign task to (creates task within group)

**Response** (201 Created):
```json
{
  "id": 112233445,
  "status": "active",
  "created_at": "2024-10-26T12:20:15.789-05:00",
  "updated_at": "2024-10-26T12:20:15.789-05:00",
  "title": "NMNM 0002889",
  "content": "NMNM 0002889",
  "description": "Reports Needed: 24S-32E, Sec. 3-NESW From 9/1/2020",
  "completed": false,
  "due_on": "2024-11-15",
  "assignees": [
    {
      "id": 1049715916,
      "name": "Brandon P.",
      "email_address": "brandon@example.com"
    }
  ],
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todos/112233445"
}
```

**Error Responses**:

**422 Unprocessable Entity**: Validation error
```json
{
  "error": "Content can't be blank"
}
```

**404 Not Found**: To-do list doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- `content` is the task name (Basecamp terminology)
- Invalid assignee IDs are silently ignored by Basecamp (filter them out)
- `due_on` must be YYYY-MM-DD format (validate before sending)
- If `group_id` omitted, task appears at top of to-do list (ungrouped)
- `group_id` must reference an existing group in the same to-do list

---

### 6. Update To-Do (Task)

**Purpose**: Update existing task properties

```http
PUT /{account_id}/buckets/{project_id}/todos/{todo_id}.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todo_id` (string): To-do ID

**Request**:
- Headers: Authorization, User-Agent, Content-Type: application/json
- Body (all fields optional):
```json
{
  "content": "NMNM 0002889 - Updated",
  "description": "Updated description",
  "due_on": "2024-12-01",
  "assignee_ids": [1049715916]
}
```

**Request Fields** (all optional):
- `content` (string): New task name, max 255 characters
- `description` (string): New description, max 10,000 characters
- `due_on` (string): New due date in YYYY-MM-DD format, or null to remove
- `assignee_ids` (array): New list of assignee IDs (replaces existing)
- `group_id` (integer): Move task to different group, or null to remove from group

**Response** (200 OK):
```json
{
  "id": 112233445,
  "status": "active",
  "updated_at": "2024-10-26T14:30:22.456-05:00",
  "content": "NMNM 0002889 - Updated",
  "description": "Updated description",
  "due_on": "2024-12-01",
  "assignees": [
    {
      "id": 1049715916,
      "name": "Brandon P."
    }
  ]
}
```

**Error Responses**:

**404 Not Found**: To-do doesn't exist
```json
{
  "error": "Not Found"
}
```

**422 Unprocessable Entity**: Validation error
```json
{
  "error": "Content can't be blank"
}
```

**Implementation Notes**:
- Only include fields you want to update
- Setting `assignee_ids: []` removes all assignees
- Setting `due_on: null` removes due date
- Setting `group_id: null` removes task from group (moves to top of list)
- Setting `group_id: 12345` moves task to that group

---

### 7. Complete/Reopen To-Do

**Purpose**: Mark task as completed or reopen completed task

**Complete Task**:
```http
POST /{account_id}/buckets/{project_id}/todos/{todo_id}/completion.json
```

**Reopen Task**:
```http
DELETE /{account_id}/buckets/{project_id}/todos/{todo_id}/completion.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todo_id` (string): To-do ID

**Request**:
- Headers: Authorization, User-Agent
- Body: None

**Response** (200 OK):
```json
{
  "id": 112233445,
  "completed": true,
  "completed_at": "2024-10-26T15:00:00.000-05:00",
  "completer": {
    "id": 1049715915,
    "name": "Chris Landman"
  }
}
```

**Implementation Notes**:
- Use POST to complete, DELETE to reopen
- Separate endpoint from update (different operation)
- Can also update via PUT with `completed: true/false` but completion endpoint preferred

---

### 8. List Groups

**Purpose**: Retrieve all groups in a to-do list

```http
GET /{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todolist_id` (string): To-do list ID

**Request**:
- Headers: Authorization, User-Agent
- Body: None

**Response** (200 OK):
```json
[
  {
    "id": 445566778,
    "status": "active",
    "created_at": "2024-10-26T11:00:00.123-05:00",
    "updated_at": "2024-10-26T11:00:00.123-05:00",
    "name": "Setup",
    "position": 1
  },
  {
    "id": 445566779,
    "status": "active",
    "created_at": "2024-10-26T11:00:05.456-05:00",
    "updated_at": "2024-10-26T11:00:05.456-05:00",
    "name": "Workup",
    "position": 2
  }
]
```

**Response Fields**:
- `id` (integer): Group ID (use when creating tasks)
- `name` (string): Group name
- `position` (integer): Order within to-do list

**Error Responses**:

**404 Not Found**: To-do list doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Returns empty array if no groups exist
- Groups are returned in position order
- Use group IDs when creating tasks with `group_id` parameter

---

### 9. Create Group

**Purpose**: Create new group (section) in a to-do list

```http
POST /{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `todolist_id` (string): To-do list ID

**Request**:
- Headers: Authorization, User-Agent, Content-Type: application/json
- Body:
```json
{
  "name": "Setup"
}
```

**Request Fields**:
- `name` (string, required): Group name, max 255 characters

**Response** (201 Created):
```json
{
  "id": 445566778,
  "status": "active",
  "created_at": "2024-10-26T11:00:00.123-05:00",
  "updated_at": "2024-10-26T11:00:00.123-05:00",
  "name": "Setup",
  "position": 1,
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/groups/445566778.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/groups/445566778"
}
```

**Error Responses**:

**422 Unprocessable Entity**: Validation error
```json
{
  "error": "Name can't be blank"
}
```

**404 Not Found**: To-do list doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Groups are created in order (incrementing position)
- Duplicate group names are allowed by Basecamp API
- Return group ID for use in subsequent task creation

---

### 10. Add Comment

**Purpose**: Add comment/note to a to-do or to-do list

```http
POST /{account_id}/buckets/{project_id}/recordings/{recording_id}/comments.json
```

**Path Parameters**:
- `account_id` (string): Basecamp account ID
- `project_id` (string): Project ID (used as bucket ID)
- `recording_id` (string): To-do ID or to-do list ID (both are "recordings")

**Request**:
- Headers: Authorization, User-Agent, Content-Type: application/json
- Body:
```json
{
  "content": "Lease Data: https://www.dropbox.com/scl/fo/170haai0ivi5zqycmvm0t/..."
}
```

**Request Fields**:
- `content` (string, required): Comment text, max 10,000 characters
- URLs in content are auto-linked by Basecamp

**Response** (201 Created):
```json
{
  "id": 223344556,
  "status": "active",
  "created_at": "2024-10-26T13:45:22.123-05:00",
  "updated_at": "2024-10-26T13:45:22.123-05:00",
  "content": "Lease Data: https://www.dropbox.com/scl/fo/170haai0ivi5zqycmvm0t/...",
  "parent": {
    "id": 112233445,
    "type": "Todo"
  },
  "creator": {
    "id": 1049715915,
    "name": "Chris Landman"
  }
}
```

**Error Responses**:

**422 Unprocessable Entity**: Validation error
```json
{
  "error": "Content can't be blank"
}
```

**404 Not Found**: Recording doesn't exist
```json
{
  "error": "Not Found"
}
```

**Implementation Notes**:
- Works for both to-dos and to-do lists (both are "recordings")
- URLs are automatically converted to clickable links
- Markdown-style formatting is NOT supported (plain text with auto-linked URLs only)

---

## Error Handling

### Standard HTTP Status Codes

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 OK | Success (GET, PUT) | Return data |
| 201 Created | Success (POST) | Return created resource |
| 401 Unauthorized | Token expired/invalid | Refresh token, retry once |
| 403 Forbidden | No permission | Return error, don't retry |
| 404 Not Found | Resource doesn't exist | Return error, don't retry |
| 422 Unprocessable Entity | Validation error | Return error, don't retry |
| 429 Too Many Requests | Rate limit exceeded | Exponential backoff, retry 3x |
| 500-599 Server Error | Basecamp issue | Retry 2x with backoff |

### Rate Limiting

**Detection**: HTTP 429 status code with optional `Retry-After` header

**Strategy**:
- Initial delay: 1 second
- Exponential backoff: 2x multiplier
- Max retries: 3 attempts
- Use `Retry-After` header value if provided

**Example**:
```
Attempt 1: Request fails with 429
Wait 1 second (or Retry-After value)
Attempt 2: Request fails with 429
Wait 2 seconds
Attempt 3: Request fails with 429
Wait 4 seconds
Attempt 4: Final attempt
If fails: Return error
```

### Token Refresh Flow

**Detection**: HTTP 401 status code

**Strategy**:
1. Detect 401 response
2. Call `BasecampOAuthAuth.refresh_access_token()`
3. Update `BasecampAccount.access_token`
4. Retry original request once
5. If second 401: Return authentication error (don't infinite loop)

---

## Performance Considerations

### Timeouts

- Default timeout: 10 seconds per request
- Matches existing `BasecampService` pattern
- Prevents hanging on slow responses

### Caching

**Not Implemented in Phase 1** (future optimization):
- To-do set IDs could be cached per project
- Project lists could be cached with TTL
- To-do list names could be cached for duplicate detection

**Current Approach**: Fetch on-demand for each operation
- Simpler implementation
- No stale data risk
- Acceptable performance for expected usage

### Pagination

**Not Implemented in Phase 1** (future enhancement):
- Basecamp API uses `Link` header for pagination
- Typical projects have <100 to-do lists (single page)
- Typical to-do lists have <50 tasks (single page)
- Can add pagination support if needed

---

## Testing Strategy

### Manual Testing via Django Shell

```python
from web.integrations.basecamp.basecamp_service import BasecampService
from web.integrations.models import BasecampAccount

# Setup
account = BasecampAccount.objects.get(user_id=1)
service = BasecampService(account.access_token)
account_id = account.account_id

# Test 1: List projects
projects = service.list_projects(account_id)
assert len(projects) > 0
assert 'id' in projects[0]
assert 'name' in projects[0]
print(f"✓ Found {len(projects)} projects")

# Test 2: Get project details
project_id = projects[0]['id']
project = service.get_project(account_id, project_id)
assert 'dock' in project
print(f"✓ Got project: {project['name']}")

# Test 3: Create to-do list
todolist = service.create_todolist(
    account_id, project_id, "Test Order - 20251101"
)
assert 'id' in todolist
print(f"✓ Created to-do list: {todolist['id']}")

# Test 4: Duplicate detection
try:
    duplicate = service.create_todolist(
        account_id, project_id, "Test Order - 20251101"
    )
    assert False, "Should have raised duplicate error"
except ValueError as e:
    assert "already exists" in str(e)
    print(f"✓ Duplicate detection works")

# Test 5: Create groups
group_setup = service.create_group(account_id, project_id, todolist['id'], "Setup")
group_workup = service.create_group(account_id, project_id, todolist['id'], "Workup")
assert 'id' in group_setup
print(f"✓ Created groups: {group_setup['id']}, {group_workup['id']}")

# Test 6: Create task in group
todo = service.create_todo(
    account_id, project_id, todolist['id'],
    "Test Task NMNM 001",
    description="Test description",
    due_on="2024-12-01",
    group_id=group_setup['id']
)
assert 'id' in todo
assert todo.get('group_id') == group_setup['id']
print(f"✓ Created task in group: {todo['id']}")

# Test 7: Update task
updated = service.update_todo(
    account_id, project_id, todo['id'],
    content="Test Task NMNM 001 - Updated"
)
assert updated['content'] == "Test Task NMNM 001 - Updated"
print(f"✓ Updated task")

# Test 8: List groups
groups = service.list_groups(account_id, project_id, todolist['id'])
assert len(groups) == 2
print(f"✓ Listed {len(groups)} groups")

# Test 9: Add comment
comment = service.add_comment(
    account_id, project_id, todo['id'],
    "Test comment with link: https://example.com"
)
assert 'id' in comment
print(f"✓ Added comment: {comment['id']}")

print("\n✅ All tests passed!")
```

### Verification in Basecamp UI

After running tests:
1. Open Basecamp project in browser
2. Verify to-do list appears with correct name
3. Verify task appears in to-do list
4. Verify task has correct description, due date
5. Verify comment appears with clickable link

---

## Summary

- **8 Basecamp 3 API endpoints** documented for project and task management
- **Standard REST patterns** with JSON request/response
- **Error handling strategy** for all status codes
- **Rate limiting** with exponential backoff
- **Token refresh** for 401 responses
- **Validation** before API calls to reduce errors
- **Testing strategy** for manual verification

