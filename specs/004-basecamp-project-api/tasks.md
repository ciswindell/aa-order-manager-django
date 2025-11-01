# Tasks: Basecamp Project API Extension

**Feature**: 004-basecamp-project-api | **Branch**: `004-basecamp-project-api`  
**Input**: Design documents from `/specs/004-basecamp-project-api/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not required per feature specification - manual testing via Django shell

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project setup required - extending existing `BasecampService` class

**Status**: ✅ Setup already complete - existing infrastructure in place

- Existing file: `web/integrations/basecamp/basecamp_service.py`
- Existing auth: `web/integrations/basecamp/auth.py` (BasecampOAuthAuth)
- Existing model: `web/integrations/models.py` (BasecampAccount)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core validation and error handling infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 Add validation helper `_validate_id(value, param_name)` in `web/integrations/basecamp/basecamp_service.py`
- [x] T002 [P] Add validation helper `_validate_name(value, max_length=255)` in `web/integrations/basecamp/basecamp_service.py`
- [x] T003 [P] Add validation helper `_validate_description(value)` in `web/integrations/basecamp/basecamp_service.py`
- [x] T004 [P] Add validation helper `_validate_date_format(value)` in `web/integrations/basecamp/basecamp_service.py`
- [x] T005 Add error handling method `_handle_api_error(response, context)` with exponential backoff for 429 in `web/integrations/basecamp/basecamp_service.py`
- [x] T006 Add logging helper `_log_api_request(method, endpoint, status, context)` with tiered levels (INFO/WARNING/ERROR) in `web/integrations/basecamp/basecamp_service.py`

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Retrieve Basecamp Projects (Priority: P1) 🎯 MVP

**Goal**: Retrieve and display Basecamp projects so workflow automation can identify which project to create tasks in

**Independent Test**: Call `list_projects()` and `get_project()` in Django shell, verify returned data contains project ID, name, and dock with todoset

### Implementation for User Story 1

- [x] T007 [P] [US1] Implement `list_projects(account_id)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T008 [P] [US1] Implement `get_project(account_id, project_id)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T009 [US1] Implement `_get_todoset_id(account_id, project_id)` helper method in `web/integrations/basecamp/basecamp_service.py`
- [x] T010 [US1] Add input validation (account_id, project_id) for project methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T011 [US1] Add error handling (401, 404, 429) for project methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T012 [US1] Add logging for project retrieval operations in `web/integrations/basecamp/basecamp_service.py`

**Manual Test**:
```python
# Django shell
from web.integrations.basecamp.basecamp_service import BasecampService
from web.integrations.models import BasecampAccount

account = BasecampAccount.objects.first()
service = BasecampService(account.access_token)

# Test list projects
projects = service.list_projects(account.account_id)
assert len(projects) > 0
assert 'id' in projects[0]
assert 'name' in projects[0]

# Test get project
project = service.get_project(account.account_id, projects[0]['id'])
assert 'dock' in project
assert any(item['name'] == 'todoset' for item in project['dock'])
```

**Checkpoint**: At this point, User Story 1 should be fully functional - projects can be retrieved with todoset IDs

---

## Phase 4: User Story 2 - Create and Manage To-Do Lists (Priority: P2)

**Goal**: Create to-do lists within Basecamp projects with duplicate detection to organize tasks into logical groupings

**Independent Test**: Create a to-do list in test project, verify it appears in Basecamp UI, attempt duplicate creation to verify validation error

### Implementation for User Story 2

- [x] T013 [P] [US2] Implement `list_todolists(account_id, project_id)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T014 [US2] Implement `_check_duplicate_todolist(account_id, project_id, name)` helper method with case-sensitive name matching in `web/integrations/basecamp/basecamp_service.py`
- [x] T015 [US2] Implement `create_todolist(account_id, project_id, name, description="")` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T016 [US2] Add input validation (name max 255 chars, description max 10,000 chars) for to-do list methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T017 [US2] Integrate duplicate detection check before to-do list creation in `web/integrations/basecamp/basecamp_service.py`
- [x] T018 [US2] Add error handling (404 project, 422 validation, 429 rate limit) for to-do list methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T019 [US2] Add logging for to-do list operations in `web/integrations/basecamp/basecamp_service.py`

**Manual Test**:
```python
# Django shell (continuing from User Story 1)
project_id = projects[0]['id']

# Test create to-do list
todolist = service.create_todolist(account.account_id, project_id, "Test Order - 20251101")
assert 'id' in todolist
assert todolist['name'] == "Test Order - 20251101"

# Test duplicate detection (should raise ValueError)
try:
    duplicate = service.create_todolist(account.account_id, project_id, "Test Order - 20251101")
    assert False, "Should have raised duplicate error"
except ValueError as e:
    assert "already exists" in str(e)

# Verify in Basecamp UI
print(f"View in Basecamp: {todolist['app_url']}")
```

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - projects can be retrieved, to-do lists can be created with duplicate prevention

---

## Phase 5: User Story 3 - Create and Manage Tasks (Priority: P3)

**Goal**: Create and update individual tasks within to-do lists with assignees, due dates, and completion status

**Independent Test**: Create task with name, description, assignee, due date; update task; verify changes in Basecamp UI

### Implementation for User Story 3

- [x] T020 [US3] Implement `create_todo(account_id, project_id, todolist_id, content, description="", due_on=None, assignee_ids=None, group_id=None)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T021 [US3] Implement `update_todo(account_id, project_id, todo_id, **kwargs)` method supporting content, description, due_on, assignee_ids, group_id, completed in `web/integrations/basecamp/basecamp_service.py`
- [x] T022 [US3] Add input validation (content max 255 chars, due_on YYYY-MM-DD format, assignee_ids list of ints) for task methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T023 [US3] Add error handling (404 todolist/todo, 422 validation, 429 rate limit) for task methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T024 [US3] Add logging for task creation and update operations in `web/integrations/basecamp/basecamp_service.py`

**Manual Test**:
```python
# Django shell (continuing from User Story 2)
todolist_id = todolist['id']

# Test create task
todo = service.create_todo(
    account.account_id, project_id, todolist_id,
    "Test Task NMNM 001",
    description="Test description",
    due_on="2024-12-01"
)
assert 'id' in todo
assert todo['content'] == "Test Task NMNM 001"

# Test update task
updated = service.update_todo(
    account.account_id, project_id, todo['id'],
    content="Test Task NMNM 001 - Updated"
)
assert updated['content'] == "Test Task NMNM 001 - Updated"

# Verify in Basecamp UI
print(f"View task: {todo['app_url']}")
```

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work - full task management without groups

---

## Phase 6: User Story 4 - Organize Tasks with Groups (Priority: P4)

**Goal**: Create and manage to-do groups within to-do lists to organize tasks into logical sections (Setup, Workup, Imaging, etc.)

**Independent Test**: Create groups in to-do list, assign tasks to groups, verify grouped structure in Basecamp UI

### Implementation for User Story 4

- [x] T025 [P] [US4] Implement `list_groups(account_id, project_id, todolist_id)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T026 [P] [US4] Implement `create_group(account_id, project_id, todolist_id, name)` method in `web/integrations/basecamp/basecamp_service.py`
- [x] T027 [US4] Add input validation (group name max 255 chars) for group methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T028 [US4] Add error handling (404 todolist, 422 validation) for group methods in `web/integrations/basecamp/basecamp_service.py`
- [x] T029 [US4] Add logging for group operations in `web/integrations/basecamp/basecamp_service.py`
- [x] T030 [US4] Update `create_todo()` and `update_todo()` to validate group_id parameter in `web/integrations/basecamp/basecamp_service.py`

**Manual Test**:
```python
# Django shell (continuing from User Story 2)
# Test create groups
group_setup = service.create_group(account.account_id, project_id, todolist_id, "Setup")
group_workup = service.create_group(account.account_id, project_id, todolist_id, "Workup")
assert 'id' in group_setup

# Test list groups
groups = service.list_groups(account.account_id, project_id, todolist_id)
assert len(groups) >= 2

# Test create task in group
todo_grouped = service.create_todo(
    account.account_id, project_id, todolist_id,
    "Setup Abstract Todos",
    group_id=group_setup['id']
)
assert todo_grouped.get('group_id') == group_setup['id']

# Verify grouped structure in Basecamp UI
print(f"View grouped tasks: {todolist['app_url']}")
```

**Checkpoint**: At this point, all task organization features work - groups enable structured workflows matching manual process

---

## Phase 7: User Story 5 - Add Comments and Notes (Priority: P5)

**Goal**: Add comments to tasks and to-do lists to provide contextual information like Dropbox links and report details

**Independent Test**: Add comment with text and URL to task, verify comment appears in Basecamp with clickable link

### Implementation for User Story 5

- [ ] T031 [US5] Implement `add_comment(account_id, project_id, recording_id, content)` method in `web/integrations/basecamp/basecamp_service.py`
- [ ] T032 [US5] Add input validation (content max 10,000 chars, plain text only) for comment method in `web/integrations/basecamp/basecamp_service.py`
- [ ] T033 [US5] Add error handling (404 recording, 422 validation) for comment method in `web/integrations/basecamp/basecamp_service.py`
- [ ] T034 [US5] Add logging for comment operations in `web/integrations/basecamp/basecamp_service.py`

**Manual Test**:
```python
# Django shell (continuing from User Story 3)
# Test add comment
comment = service.add_comment(
    account.account_id, project_id, todo['id'],
    "Lease Data: https://www.dropbox.com/scl/fo/example"
)
assert 'id' in comment
assert 'dropbox.com' in comment['content']

# Verify comment in Basecamp UI (URLs should be auto-linked)
print(f"View task with comment: {todo['app_url']}")
```

**Checkpoint**: All user stories complete - full Basecamp API integration ready for workflow automation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation, and refinements

- [ ] T035 [P] Add comprehensive docstrings for all public methods in `web/integrations/basecamp/basecamp_service.py`
- [ ] T036 Run full integration test suite via Django shell using quickstart.md test commands
- [ ] T037 Verify all objects appear correctly in Basecamp UI (to-do lists, groups, tasks, comments)
- [ ] T038 Test error scenarios (invalid IDs, rate limits, expired tokens, duplicate names)
- [ ] T039 [P] Code review and refactoring for DRY principles in `web/integrations/basecamp/basecamp_service.py`
- [ ] T040 [P] Update quickstart.md with any edge cases or lessons learned discovered during implementation
- [ ] T041 Verify all success criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: ✅ Already complete - no new setup required
- **Foundational (Phase 2)**: No dependencies - BLOCKS all user stories (T001-T006)
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) and User Story 1 (needs `get_project()` to get todoset_id)
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) and User Story 2 (needs todolist_id)
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2), User Story 2 (needs todolist_id), and extends User Story 3 (updates task methods)
- **User Story 5 (Phase 7)**: Depends on Foundational (Phase 2) and User Story 3 (needs todo_id) - Can work with todolist_id from User Story 2
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational (T001-T006)
    ↓
User Story 1 (T007-T012) - Project Retrieval
    ↓
User Story 2 (T013-T019) - To-Do List Management
    ↓
User Story 3 (T020-T024) - Task Management
    ↓
    ├─→ User Story 4 (T025-T030) - Group Management (extends US3)
    └─→ User Story 5 (T031-T034) - Comments (uses US3 todo_id)
    ↓
Polish (T035-T041)
```

### Within Each User Story

1. **Foundational**: Validation helpers first (T001-T004), then error handling (T005), then logging (T006)
2. **User Story 1**: Parallel methods (T007-T008), then helper (T009), then validation/error/logging (T010-T012)
3. **User Story 2**: List method (T013), then duplicate check (T014), then create (T015), then validation/error/logging (T016-T019)
4. **User Story 3**: Create method (T020), then update (T021), then validation/error/logging (T022-T024)
5. **User Story 4**: Parallel methods (T025-T026), then validation/error/logging (T027-T029), then extend US3 (T030)
6. **User Story 5**: Create method (T031), then validation/error/logging (T032-T034)
7. **Polish**: Parallel documentation/testing (T035-T038, T040), then review (T039), then final verification (T041)

### Parallel Opportunities

**Within Foundational (Phase 2)**:
- T002, T003, T004 can run in parallel (different validation helpers)

**Within User Story 1 (Phase 3)**:
- T007, T008 can run in parallel (different methods, no shared dependencies)

**Within User Story 2 (Phase 4)**:
- T013 must complete before T014 (duplicate check needs list method)

**Within User Story 4 (Phase 6)**:
- T025, T026 can run in parallel (different methods)

**Within Polish (Phase 8)**:
- T035, T036, T037, T038, T040 can run in parallel (different activities)

**Note**: Most work is in a single file (`basecamp_service.py`), so true parallelization is limited. Sequential implementation is recommended.

---

## Parallel Example: Foundational Phase

```bash
# Launch validation helpers together:
Task: "Add validation helper _validate_name() in basecamp_service.py"
Task: "Add validation helper _validate_description() in basecamp_service.py"
Task: "Add validation helper _validate_date_format() in basecamp_service.py"

# Then sequentially:
Task: "Add error handling method _handle_api_error()"
Task: "Add logging helper _log_api_request()"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 2: Foundational (T001-T006)
2. Complete Phase 3: User Story 1 - Projects (T007-T012)
3. Complete Phase 4: User Story 2 - To-Do Lists (T013-T019)
4. Complete Phase 5: User Story 3 - Tasks (T020-T024)
5. **STOP and VALIDATE**: Test full workflow in Django shell
6. This provides enough functionality for hardcoded workflow PoC (Phase 2 of overall plan)

### Full Feature (All User Stories)

1. Complete MVP (User Stories 1-3)
2. Add Phase 6: User Story 4 - Groups (T025-T030) - Matches current manual workflow structure
3. Add Phase 7: User Story 5 - Comments (T031-T034) - Adds context to tasks
4. Complete Phase 8: Polish (T035-T041) - Final verification

### Incremental Delivery

- **After User Story 1**: Can browse Basecamp projects programmatically
- **After User Story 2**: Can create to-do lists with duplicate protection
- **After User Story 3**: Can create complete workflows with tasks (MVP for automation)
- **After User Story 4**: Can organize tasks into sections (matches manual process)
- **After User Story 5**: Can add context and links to tasks (complete feature)

---

## Testing Strategy

### Manual Testing via Django Shell

All testing done via Django shell (no automated tests per spec):

```bash
# Start Django shell
cd /home/chris/Code/aa-order-manager
docker-compose exec web python3 manage.py shell
```

### Test Sequence (follows implementation order)

**After Foundational + User Story 1** (T001-T012):
```python
from web.integrations.basecamp.basecamp_service import BasecampService
from web.integrations.models import BasecampAccount

account = BasecampAccount.objects.first()
service = BasecampService(account.access_token)
aid = account.account_id

# Test projects
projects = service.list_projects(aid)
project = service.get_project(aid, projects[0]['id'])
print(f"✓ Projects working: {len(projects)} found")
```

**After User Story 2** (T013-T019):
```python
# Test to-do list creation and duplicate detection
pid = projects[0]['id']
todolist = service.create_todolist(aid, pid, "Test Order - 20251101")
print(f"✓ To-do list created: {todolist['id']}")

try:
    duplicate = service.create_todolist(aid, pid, "Test Order - 20251101")
except ValueError as e:
    print(f"✓ Duplicate detection works: {e}")
```

**After User Story 3** (T020-T024):
```python
# Test task creation and update
todo = service.create_todo(aid, pid, todolist['id'], "Test Task", 
                           description="Test", due_on="2024-12-01")
updated = service.update_todo(aid, pid, todo['id'], content="Updated")
print(f"✓ Tasks working: {todo['id']}")
```

**After User Story 4** (T025-T030):
```python
# Test group creation and task assignment
group = service.create_group(aid, pid, todolist['id'], "Setup")
groups = service.list_groups(aid, pid, todolist['id'])
todo_grouped = service.create_todo(aid, pid, todolist['id'], "Grouped Task",
                                   group_id=group['id'])
print(f"✓ Groups working: {len(groups)} groups, task in group {todo_grouped.get('group_id')}")
```

**After User Story 5** (T031-T034):
```python
# Test comment creation
comment = service.add_comment(aid, pid, todo['id'], 
                               "Link: https://example.com")
print(f"✓ Comments working: {comment['id']}")
print(f"\nView in Basecamp: {todolist['app_url']}")
```

### Error Scenario Testing

Test these scenarios during Phase 8 (Polish):

1. **Invalid IDs**: Test with non-numeric, empty, or non-existent IDs
2. **Rate Limiting**: Verify exponential backoff on 429 responses
3. **Token Expiration**: Verify automatic refresh on 401 responses
4. **Validation Errors**: Test max length, invalid date formats
5. **Duplicate Detection**: Verify case-sensitive, whitespace-normalized matching
6. **Invalid Group ID**: Test assigning task to non-existent or wrong todolist group

---

## Success Criteria Checklist

From spec.md success criteria:

- [ ] **SC-001**: All API methods return expected data within 3 seconds
- [ ] **SC-002**: Rate limiting (429) handled with automatic retry, 95% success rate
- [ ] **SC-003**: Token expiration (401) handled with refresh and retry, 95% success rate
- [ ] **SC-004**: Clear error messages for all failures without sensitive data
- [ ] **SC-005**: All methods testable in Django shell with mock data
- [ ] **SC-006**: Zero unhandled exceptions that crash application
- [ ] **SC-007**: Response parsing handles unexpected formats gracefully
- [ ] **SC-008**: Consistent error handling across all methods
- [ ] **SC-009**: Logging provides clear visibility (INFO/WARNING/ERROR levels)

---

## Notes

- All work in single file: `web/integrations/basecamp/basecamp_service.py`
- No new models or migrations required
- Extends existing authentication infrastructure
- Manual testing sufficient per spec (no automated tests)
- Commit after each user story completion for clean history
- Verify each user story in Basecamp UI before proceeding
- Reference documents in `/specs/004-basecamp-project-api/` for implementation details

