# Data Model: Basecamp Project API Extension

**Feature**: 004-basecamp-project-api | **Date**: 2025-11-01 | **Phase**: 1 (Design)

## Overview

This feature does **not introduce new Django models**. It extends the existing `BasecampService` to interact with Basecamp 3 API data structures. All data is retrieved/created via API calls and not persisted locally (except existing `BasecampAccount` for authentication).

## External Data Structures (Basecamp API)

These are the JSON data structures returned by Basecamp 3 API that our service will consume and produce.

### BasecampProject

**Source**: `GET https://3.basecampapi.com/{account_id}/projects.json`

**Purpose**: Represents a Basecamp project containing to-do lists and other resources

**Structure**:
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
  "bookmark": {
    "url": "https://3.basecampapi.com/1234567/buckets/2085958499/bookmark.json"
  },
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

**Key Fields**:
- `id` (integer): Unique project identifier
- `name` (string): Project display name
- `description` (string): Project description
- `status` (string): "active" or "archived"
- `dock` (array): Array of enabled tools/features (we need "todoset" for to-do list operations)

**Relationships**:
- Contains one to-do set (found in `dock` array)
- Contains multiple to-do lists (via to-do set)

---

### BasecampTodoSet

**Source**: Extracted from project's `dock` array or `GET https://3.basecampapi.com/{account_id}/buckets/{project_id}/todosets/{todoset_id}.json`

**Purpose**: Container for all to-do lists in a project (every project has exactly one)

**Structure**:
```json
{
  "id": 123456789,
  "status": "active",
  "visible_to_clients": false,
  "created_at": "2024-10-26T10:28:58.021-05:00",
  "updated_at": "2024-10-26T10:28:58.021-05:00",
  "title": "To-dos",
  "inherits_status": true,
  "type": "Todoset",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todosets/123456789.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todosets/123456789",
  "todolists_count": 5,
  "todolists_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todosets/123456789/todolists.json"
}
```

**Key Fields**:
- `id` (integer): Unique to-do set identifier (required for creating to-do lists)
- `todolists_count` (integer): Number of to-do lists in this set
- `todolists_url` (string): API endpoint to list all to-do lists

**Usage**:
- Extract `id` from project's dock to create to-do lists
- Not stored locally; retrieved on-demand per operation

---

### BasecampTodoList

**Source**: `GET https://3.basecampapi.com/{account_id}/buckets/{project_id}/todolists.json`
**Created**: `POST https://3.basecampapi.com/{account_id}/buckets/{project_id}/todosets/{todoset_id}/todolists.json`

**Purpose**: Organizes related tasks/to-dos (e.g., "Order 1943 - 20251022")

**Structure**:
```json
{
  "id": 987654321,
  "status": "active",
  "visible_to_clients": false,
  "created_at": "2024-10-26T12:15:33.456-05:00",
  "updated_at": "2024-10-26T12:15:33.456-05:00",
  "title": "Order 1943 - 20251022",
  "inherits_status": true,
  "type": "Todolist",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/987654321",
  "bookmark_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321/bookmark.json",
  "subscription_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321/subscription.json",
  "comments_count": 0,
  "comments_url": "https://3.basecampapi.com/1234567/buckets/2085958499/recordings/987654321/comments.json",
  "position": 1,
  "parent": {
    "id": 123456789,
    "title": "To-dos",
    "type": "Todoset",
    "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todosets/123456789.json",
    "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todosets/123456789"
  },
  "bucket": {
    "id": 2085958499,
    "name": "Federal Runsheets",
    "type": "Project"
  },
  "creator": {
    "id": 1049715915,
    "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmM...",
    "name": "Chris Landman",
    "email_address": "chris@example.com",
    "personable_type": "User",
    "title": "Administrator",
    "bio": null,
    "location": null,
    "created_at": "2024-10-26T10:28:57.540-05:00",
    "updated_at": "2024-10-26T10:28:57.540-05:00",
    "admin": true,
    "owner": true,
    "client": false,
    "employee": true,
    "time_zone": "America/Chicago",
    "avatar_url": "https://bc3-production.s3.amazonaws.com/...",
    "company": {
      "id": 1033447819,
      "name": "AA Order Manager"
    }
  },
  "description": "Dropbox link: https://www.dropbox.com/scl/fo/...",
  "completed": false,
  "completed_ratio": "3/8",
  "name": "Order 1943 - 20251022",
  "todos_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321/todos.json",
  "groups_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321/groups.json",
  "app_todos_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/987654321"
}
```

**Key Fields**:
- `id` (integer): Unique to-do list identifier
- `name` (string): Display name (used for duplicate detection)
- `description` (string): Optional description/notes
- `completed_ratio` (string): Progress indicator "X/Y" format
- `parent` (object): Reference to parent to-do set
- `bucket` (object): Reference to parent project

**Validation Rules**:
- `name`: Required, max 255 characters, must be unique within project (app-enforced)
- `description`: Optional, max 10,000 characters

**Relationships**:
- Belongs to one to-do set (parent)
- Contains multiple to-dos (tasks)
- Can have comments

---

### BasecampTodo

**Source**: `GET https://3.basecampapi.com/{account_id}/buckets/{project_id}/todolists/{todolist_id}/todos.json`
**Created**: `POST https://3.basecampapi.com/{account_id}/buckets/{project_id}/todolists/{todolist_id}/todos.json`
**Updated**: `PUT https://3.basecampapi.com/{account_id}/buckets/{project_id}/todos/{todo_id}.json`

**Purpose**: Individual task/work item (e.g., "NMNM 0002889")

**Structure**:
```json
{
  "id": 112233445,
  "status": "active",
  "visible_to_clients": false,
  "created_at": "2024-10-26T12:20:15.789-05:00",
  "updated_at": "2024-10-26T12:20:15.789-05:00",
  "title": "NMNM 0002889",
  "inherits_status": true,
  "type": "Todo",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todos/112233445",
  "bookmark_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445/bookmark.json",
  "subscription_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445/subscription.json",
  "comments_count": 1,
  "comments_url": "https://3.basecampapi.com/1234567/buckets/2085958499/recordings/112233445/comments.json",
  "position": 3,
  "parent": {
    "id": 987654321,
    "title": "Order 1943 - 20251022",
    "type": "Todolist",
    "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321.json",
    "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/987654321"
  },
  "bucket": {
    "id": 2085958499,
    "name": "Federal Runsheets",
    "type": "Project"
  },
  "creator": {
    "id": 1049715915,
    "name": "Chris Landman",
    "email_address": "chris@example.com"
  },
  "description": "Reports Needed: 24S-32E, Sec. 3-NESW From 9/1/2020",
  "completed": false,
  "content": "NMNM 0002889",
  "starts_on": null,
  "due_on": "2024-11-15",
  "group_id": 445566778,
  "assignees": [
    {
      "id": 1049715916,
      "attachable_sgid": "BAh7CEkiCGdpZAY6BkVUSSIrZ2lkOi8vYmM...",
      "name": "Brandon P.",
      "email_address": "brandon@example.com",
      "personable_type": "User",
      "title": "Project Manager",
      "avatar_url": "https://bc3-production.s3.amazonaws.com/..."
    }
  ],
  "completion_subscribers": [],
  "completion_url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445/completion.json"
}
```

**Key Fields**:
- `id` (integer): Unique task identifier
- `content` (string): Task name/title (Basecamp calls it "content" but displays as title)
- `description` (string): Optional detailed description
- `completed` (boolean): Task completion status
- `due_on` (string): Due date in YYYY-MM-DD format (optional)
- `group_id` (integer): Group ID if task belongs to a group (optional)
- `assignees` (array): List of assigned users (optional)
- `parent` (object): Reference to parent to-do list
- `comments_count` (integer): Number of comments

**Validation Rules**:
- `content`: Required, max 255 characters
- `description`: Optional, max 10,000 characters
- `due_on`: Optional, must be YYYY-MM-DD format
- `group_id`: Optional, must be valid group ID (integer)
- `assignees`: Optional, array of user IDs (integers)

**State Transitions**:
- Created → `completed: false`
- Completed → `completed: true` (POST to completion_url)
- Reopened → `completed: false` (DELETE to completion_url)

**Relationships**:
- Belongs to one to-do list (parent)
- Optionally belongs to one group (within parent to-do list)
- Has multiple assignees (users)
- Can have comments

---

### BasecampGroup

**Source**: `GET https://3.basecampapi.com/{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json`
**Created**: `POST https://3.basecampapi.com/{account_id}/buckets/{project_id}/todolists/{todolist_id}/groups.json`

**Purpose**: Organize tasks into logical sections within a to-do list (e.g., "Setup", "Workup", "Imaging")

**Structure**:
```json
{
  "id": 445566778,
  "status": "active",
  "visible_to_clients": false,
  "created_at": "2024-10-26T11:00:00.123-05:00",
  "updated_at": "2024-10-26T11:00:00.123-05:00",
  "title": "Setup",
  "inherits_status": true,
  "type": "Todolist::Group",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/groups/445566778.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/groups/445566778",
  "position": 1,
  "parent": {
    "id": 987654321,
    "title": "Order 1943 - 20251022",
    "type": "Todolist",
    "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todolists/987654321.json"
  },
  "bucket": {
    "id": 2085958499,
    "name": "Federal Runsheets",
    "type": "Project"
  },
  "creator": {
    "id": 1049715915,
    "name": "Chris Landman",
    "email_address": "chris@example.com"
  },
  "name": "Setup"
}
```

**Key Fields**:
- `id` (integer): Unique group identifier (used when assigning tasks to group)
- `name` (string): Group display name (e.g., "Setup", "Workup", "Imaging")
- `position` (integer): Order within to-do list (lower numbers appear first)
- `parent` (object): Reference to parent to-do list
- `bucket` (object): Reference to parent project

**Validation Rules**:
- `name`: Required, max 255 characters

**Relationships**:
- Belongs to one to-do list (parent)
- Contains multiple to-dos (tasks)
- Tasks reference groups via `group_id` field

**Usage**:
```json
// Create group first
POST /todolists/{todolist_id}/groups.json
{"name": "Setup"}
// Returns: {"id": 445566778, "name": "Setup", ...}

// Then create tasks in group
POST /todolists/{todolist_id}/todos.json
{"content": "Setup Abstract Todos", "group_id": 445566778}
```

---

### BasecampComment

**Source**: `GET https://3.basecampapi.com/{account_id}/buckets/{project_id}/recordings/{recording_id}/comments.json`
**Created**: `POST https://3.basecampapi.com/{account_id}/buckets/{project_id}/recordings/{recording_id}/comments.json`

**Purpose**: Add context, links, or notes to tasks or to-do lists

**Note**: `recording_id` is the ID of the todo or todolist (both are "recordings" in Basecamp's data model)

**Structure**:
```json
{
  "id": 223344556,
  "status": "active",
  "visible_to_clients": false,
  "created_at": "2024-10-26T13:45:22.123-05:00",
  "updated_at": "2024-10-26T13:45:22.123-05:00",
  "title": "Comment on NMNM 0002889",
  "inherits_status": true,
  "type": "Comment",
  "url": "https://3.basecampapi.com/1234567/buckets/2085958499/comments/223344556.json",
  "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/comments/223344556",
  "bookmark_url": "https://3.basecampapi.com/1234567/buckets/2085958499/comments/223344556/bookmark.json",
  "subscription_url": "https://3.basecampapi.com/1234567/buckets/2085958499/comments/223344556/subscription.json",
  "parent": {
    "id": 112233445,
    "title": "NMNM 0002889",
    "type": "Todo",
    "url": "https://3.basecampapi.com/1234567/buckets/2085958499/todos/112233445.json",
    "app_url": "https://3.basecamp.com/1234567/buckets/2085958499/todos/112233445"
  },
  "bucket": {
    "id": 2085958499,
    "name": "Federal Runsheets",
    "type": "Project"
  },
  "creator": {
    "id": 1049715915,
    "name": "Chris Landman",
    "email_address": "chris@example.com"
  },
  "content": "Lease Data: https://www.dropbox.com/scl/fo/170haai0ivi5zqycmvm0t/AHGKfvhCbpk8-BcOlyOzOf1?rlkey=vu641n6zqcdn993q3gqpfdeqa&dl=0",
  "attachments": []
}
```

**Key Fields**:
- `id` (integer): Unique comment identifier
- `content` (string): Comment text (supports URLs and basic formatting)
- `parent` (object): Reference to parent todo or todolist
- `creator` (object): User who created comment
- `attachments` (array): File attachments (not used in this feature)

**Validation Rules**:
- `content`: Required, max 10,000 characters
- URLs in content are auto-linked by Basecamp

**Relationships**:
- Belongs to one todo or todolist (parent recording)

---

## Existing Django Models (No Changes)

### BasecampAccount

**Location**: `web/integrations/models.py`

**Purpose**: Stores OAuth credentials for authenticated Basecamp access

**Fields**:
- `user`: OneToOne relationship to Django User
- `account_id`: Basecamp account ID (used in all API calls)
- `account_name`: Human-readable account name
- `access_token`: Current OAuth access token
- `refresh_token_encrypted`: Encrypted refresh token
- `expires_at`: Token expiration timestamp
- `scope`: OAuth scope
- `created_at`: Creation timestamp
- `updated_at`: Last modification timestamp

**Usage in This Feature**:
- `account_id` used in all Basecamp API endpoint URLs
- `access_token` used in Authorization header
- No modifications to this model

---

## Data Flow

### Creating a Grouped To-Do List Workflow

```
1. User/System initiates: create_todolist(account_id, project_id, "Order 1943")
   ↓
2. Validate inputs (account_id, project_id, name)
   ↓
3. Get project details: GET /projects/{project_id}.json
   ↓
4. Extract to-do set ID from project.dock[name="todoset"]
   ↓
5. Check for duplicates: GET /todolists.json (list all in project)
   ↓
6. Compare names (case-sensitive, whitespace-normalized)
   ↓
7. If duplicate: raise ValueError("To-do list already exists")
   ↓
8. If unique: POST /todosets/{todoset_id}/todolists.json
   ↓
9. Return created todolist object with ID
   ↓
10. Create groups: POST /todolists/{todolist_id}/groups.json for each group
    ↓
11. Return group IDs for use in task creation
```

### Creating a Task with Group Workflow

```
1. User/System initiates: create_todo(account_id, project_id, todolist_id, "NMNM 001", group_id=445566778)
   ↓
2. Validate inputs (IDs, content, due_on format, assignee_ids, group_id)
   ↓
3. Build request body: {content, description, due_on, assignee_ids, group_id}
   ↓
4. POST /todolists/{todolist_id}/todos.json
   ↓
5. Return created todo object with ID and group_id
```

### Creating a Task (Legacy - No Group) Workflow

```
1. User/System initiates: create_todo(account_id, project_id, todolist_id, "NMNM 001", ...)
   ↓
2. Validate inputs (IDs, content, due_on format, assignee_ids)
   ↓
3. Build request body: {content, description, due_on, assignee_ids}
   ↓
4. POST /todolists/{todolist_id}/todos.json
   ↓
5. Return created todo object with ID
```

### Adding a Comment Workflow

```
1. User/System initiates: add_comment(account_id, project_id, todo_id, "Link: https://...")
   ↓
2. Validate inputs (IDs, content)
   ↓
3. Build request body: {content}
   ↓
4. POST /recordings/{todo_id}/comments.json
   ↓
5. Return created comment object with ID
```

---

## Error Handling Data Structures

### ValidationError

**Raised By**: Input validation before API calls

**Structure**:
```python
{
    "error": "validation_error",
    "field": "name",
    "message": "Name must be ≤255 characters",
    "provided_value": "Very long name that exceeds..."
}
```

### DuplicateError

**Raised By**: Duplicate to-do list detection

**Structure**:
```python
{
    "error": "duplicate_todolist",
    "message": "To-do list with name 'Order 1943' already exists",
    "existing_id": 987654321,
    "existing_url": "https://3.basecamp.com/1234567/buckets/2085958499/todolists/987654321"
}
```

### APIError

**Raised By**: Basecamp API error responses

**Structure**:
```python
{
    "error": "api_error",
    "status_code": 403,
    "message": "Forbidden: Insufficient permissions",
    "endpoint": "/buckets/2085958499/todolists.json",
    "request_id": "abc-123-def" 
}
```

---

## Summary

- **Zero new Django models** (extends existing BasecampAccount)
- **Four external data structures** from Basecamp API (Project, TodoSet, TodoList, Todo, Comment)
- **Clear validation rules** for each entity
- **Structured error responses** for validation and API failures
- **Data flows** defined for key operations

