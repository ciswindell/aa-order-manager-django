# Quickstart: Basecamp Project API Extension

**Feature**: 004-basecamp-project-api | **Branch**: `004-basecamp-project-api`

## What to Build

Extend `web/integrations/basecamp/basecamp_service.py` with 8 new methods to interact with Basecamp 3 API for project and task management.

## Implementation Checklist

### Phase 1: Project Retrieval (Priority P1)
- [ ] Add `list_projects(account_id)` method
- [ ] Add `get_project(account_id, project_id)` method
- [ ] Add `_get_todoset_id(account_id, project_id)` helper method
- [ ] Test in Django shell: retrieve projects and extract todoset ID

### Phase 2: To-Do List Management (Priority P2)
- [ ] Add `list_todolists(account_id, project_id)` method
- [ ] Add `_check_duplicate_todolist(account_id, project_id, name)` helper
- [ ] Add `create_todolist(account_id, project_id, name, description="")` method
- [ ] Test in Django shell: create to-do list and verify duplicate prevention

### Phase 3: Task Management (Priority P3)
- [ ] Add `create_todo(account_id, project_id, todolist_id, content, **kwargs)` method
- [ ] Add `update_todo(account_id, project_id, todo_id, **kwargs)` method
- [ ] Test in Django shell: create and update tasks with assignees and due dates

### Phase 4: Group Management (Priority P4)
- [ ] Add `list_groups(account_id, project_id, todolist_id)` method
- [ ] Add `create_group(account_id, project_id, todolist_id, name)` method
- [ ] Test in Django shell: create groups and assign tasks to groups

### Phase 5: Comments (Priority P5)
- [ ] Add `add_comment(account_id, project_id, recording_id, content)` method
- [ ] Test in Django shell: add comments with URLs

### Phase 5: Validation & Error Handling
- [ ] Add input validation for all methods (IDs, strings, dates)
- [ ] Implement exponential backoff for HTTP 429
- [ ] Handle token refresh for HTTP 401
- [ ] Add structured logging for all API calls
- [ ] Return consistent error responses

### Phase 6: Final Verification
- [ ] Test all methods in Django shell with real Basecamp account
- [ ] Verify objects appear correctly in Basecamp UI
- [ ] Test error scenarios (invalid IDs, duplicates, rate limits)
- [ ] Document any edge cases discovered

## Key Files

| File | Purpose |
|------|---------|
| `web/integrations/basecamp/basecamp_service.py` | Extend with new methods |
| `specs/004-basecamp-project-api/contracts/api-spec.md` | Basecamp API endpoint reference |
| `specs/004-basecamp-project-api/data-model.md` | Response structure reference |
| `specs/004-basecamp-project-api/research.md` | Implementation decisions |

## Method Signatures

### Project Methods
```python
def list_projects(self, account_id: str) -> list[dict]:
    """Get all projects for account."""

def get_project(self, account_id: str, project_id: str) -> dict:
    """Get specific project details."""

def _get_todoset_id(self, account_id: str, project_id: str) -> str:
    """Extract todoset ID from project dock (helper)."""
```

### To-Do List Methods
```python
def list_todolists(self, account_id: str, project_id: str) -> list[dict]:
    """Get all to-do lists in project."""

def _check_duplicate_todolist(self, account_id: str, project_id: str, name: str) -> bool:
    """Check if to-do list with name exists (helper)."""

def create_todolist(self, account_id: str, project_id: str, name: str, description: str = "") -> dict:
    """Create to-do list in project."""
```

### Task Methods
```python
def create_todo(self, account_id: str, project_id: str, todolist_id: str, content: str, 
                description: str = "", due_on: str = None, assignee_ids: list[int] = None,
                group_id: int = None) -> dict:
    """Create task in to-do list. Optionally assign to group."""

def update_todo(self, account_id: str, project_id: str, todo_id: str, **kwargs) -> dict:
    """Update existing task. Accepts: content, description, due_on, assignee_ids, group_id, completed."""
```

### Group Methods
```python
def list_groups(self, account_id: str, project_id: str, todolist_id: str) -> list[dict]:
    """Get all groups in to-do list."""

def create_group(self, account_id: str, project_id: str, todolist_id: str, name: str) -> dict:
    """Create group (section) in to-do list."""
```

### Comment Methods
```python
def add_comment(self, account_id: str, project_id: str, recording_id: str, content: str) -> dict:
    """Add comment to task or to-do list."""
```

## Validation Rules

| Parameter | Validation |
|-----------|------------|
| `account_id`, `project_id`, `todolist_id`, `todo_id`, `group_id` | Non-empty, numeric string |
| `name` / `content` | Non-empty after strip, max 255 chars |
| `description` / comment `content` | Max 10,000 chars |
| `due_on` | YYYY-MM-DD format |
| `assignee_ids` | List of integers |

## Error Handling

| Status Code | Action |
|-------------|--------|
| 401 Unauthorized | Refresh token, retry once |
| 403 Forbidden | Return error, don't retry |
| 404 Not Found | Return error, don't retry |
| 422 Validation Error | Return error, don't retry |
| 429 Rate Limit | Exponential backoff (1s, 2s, 4s), retry 3x |
| 500-599 Server Error | Exponential backoff, retry 2x |

## Testing Commands

```bash
# Start Django shell
cd /home/chris/Code/aa-order-manager
docker-compose exec web python3 manage.py shell

# Or if not using Docker
python3 web/manage.py shell
```

```python
# In Django shell
from web.integrations.basecamp.basecamp_service import BasecampService
from web.integrations.models import BasecampAccount

# Get service instance
account = BasecampAccount.objects.first()
service = BasecampService(account.access_token)
aid = account.account_id

# Test projects
projects = service.list_projects(aid)
project = service.get_project(aid, projects[0]['id'])

# Test to-do lists
todolist = service.create_todolist(aid, project['id'], "Test Order")

# Test duplicate prevention (should raise ValueError)
# todolist2 = service.create_todolist(aid, project['id'], "Test Order")

# Test groups
group_setup = service.create_group(aid, project['id'], todolist['id'], "Setup")
group_workup = service.create_group(aid, project['id'], todolist['id'], "Workup")
groups = service.list_groups(aid, project['id'], todolist['id'])

# Test tasks in groups
todo = service.create_todo(aid, project['id'], todolist['id'], "Test Task",
                            description="Test", due_on="2024-12-01",
                            group_id=group_setup['id'])

# Test comments
comment = service.add_comment(aid, project['id'], todo['id'], "Link: https://example.com")

# Verify in Basecamp UI
print(f"View in Basecamp: {todolist['app_url']}")
```

## Common Pitfalls

1. **Forgetting todoset ID**: To-do lists must be created in todoset, not directly in project
2. **Not validating before API call**: Basecamp errors are cryptic; validate first for better UX
3. **Case-sensitive duplicate detection**: Normalize whitespace but keep case-sensitive
4. **Assignee IDs vs User IDs**: Must use Basecamp user IDs, not Django user IDs
5. **Date format**: Must be YYYY-MM-DD, not YYYY-MM-DDTHH:MM:SS
6. **Creating tasks before groups**: Groups must be created before assigning tasks to them
7. **Invalid group_id**: Group ID must exist in the same to-do list as the task

## Integration Points

### Existing Code to Reuse
- `BasecampOAuthAuth._make_request_with_retry()`: Exponential backoff logic
- `BasecampService.headers`: Already includes Authorization and User-Agent
- `BasecampService.access_token`: OAuth token for authentication

### Future Integration (Phase 2)
- Order workflow service will call these methods
- API endpoint will expose workflow creation to frontend
- Frontend button will trigger workflow creation

## Success Criteria

- ✅ All 10 methods successfully interact with Basecamp API (including groups)
- ✅ Duplicate to-do lists are prevented (app-enforced validation)
- ✅ Groups created successfully for organizing tasks
- ✅ Tasks created with correct assignees, due dates, and group assignments
- ✅ Tasks appear under correct group headers in Basecamp UI
- ✅ Comments appear in Basecamp with clickable URLs
- ✅ Rate limiting handled with automatic retry
- ✅ Token expiration handled with automatic refresh
- ✅ All methods testable in Django shell
- ✅ All objects verifiable in Basecamp UI

## Next Steps (Out of Scope)

After this feature is complete:
1. **Phase 2**: Create hardcoded workflow service (`orders/services/basecamp_workflow.py`)
2. **Phase 3**: Build template system for configurable workflows
3. **Frontend**: Add "Create Basecamp Workflow" button to order details page

## Reference Documentation

- **Basecamp 3 API**: https://github.com/basecamp/bc3-api
- **Project Spec**: [spec.md](./spec.md)
- **Research Decisions**: [research.md](./research.md)
- **Data Structures**: [data-model.md](./data-model.md)
- **API Endpoints**: [contracts/api-spec.md](./contracts/api-spec.md)

