# DropboxService Simplification PRD

## Introduction/Overview

The current `DropboxService` class has become bloated with architectural violations, containing ~600 lines of code with business logic that should reside in the workflow layer. This violates separation of concerns and makes the service difficult to maintain. The service layer should be a pure API wrapper, while business logic should live in workflows.

**Problem**: DropboxService contains config_manager dependencies, agency-to-path mapping logic, and complex overlapping private methods that belong in the workflow layer.

**Goal**: Create a simplified DropboxService that serves as a pure API wrapper with zero business logic, reduced complexity, and clean architecture.

## Goals

1. **Remove All Business Logic**: Eliminate config_manager, agency mapping, and path construction from service layer
2. **Simplify Architecture**: Reduce from ~600 lines to ~300 lines with clean separation of concerns  
3. **Consolidate Methods**: Reduce 6+ overlapping private methods to 3 focused ones
4. **Maintain Workflow Compatibility**: Ensure `lease_directory_search.py` and `previous_report_detection.py` continue working
5. **Clean Interface**: Simplify method signatures to pure API operations

## User Stories

- **As a developer working with workflows**, I want the DropboxService to be a simple API wrapper so I can focus on business logic in my workflows without architectural confusion
- **As a maintainer**, I want clear separation between service (API calls) and workflow (business logic) layers so the codebase is easier to understand and modify
- **As a future developer**, I want a simple, focused service class so I can quickly understand what each method does without navigating complex business logic

## Functional Requirements

### New Simplified DropboxService

1. **Constructor Simplification**: 
   - `__init__(self, auth_handler)` - Remove config_manager parameter completely
   - Only accept auth_handler dependency

2. **Method Simplification**:
   - `search_directory(directory_path: str) -> Optional[str]` - Remove agency parameter, take full path only
   - `search_directory_with_metadata(directory_path: str) -> Dict[str, Optional[str]]` - No changes needed
   - `list_directory_files(directory_path: str) -> List[Dict[str, Any]]` - No changes needed
   - `authenticate() -> bool` - No changes needed
   - `is_authenticated() -> bool` - No changes needed

3. **Private Method Consolidation**:
   - `_find_directory(path: str) -> Optional[str]` - Replace multiple search methods
   - `_create_shareable_link(path: str) -> Optional[str]` - Consolidated link creation
   - `_list_files(path: str) -> List[Dict[str, Any]]` - Consolidated file listing

4. **Business Logic Removal**:
   - Remove all config_manager usage and dependencies
   - Remove agency-to-path mapping logic
   - Remove complex error handling layers that duplicate workflow error handling

5. **Source of Truth Test Creation**:
   - Create integration test using `lease_directory_search.py` with known lease "NMLC 0028446A"
   - Test must verify: authentication, directory finding, and shareable link creation
   - Test serves as regression protection during service refactoring

### Interface Updates

6. **Simplified Interface**: Update `DropboxServiceInterface` to match new simplified methods

7. **Test-Driven Migration Strategy**: 
   - Create integration test using `lease_directory_search.py` with known lease number as source of truth
   - Implement new simplified `DropboxService` alongside existing one
   - Verify test passes with new service
   - Replace old service completely and remove legacy code

## Non-Goals (Out of Scope)

1. **Processor Compatibility**: Breaking `processors.py` is acceptable since it's legacy code not in use
2. **Legacy Method Support**: No backward compatibility for old method signatures
3. **Complex Migration**: No gradual migration - clean break to new simplified service
4. **Business Logic Preservation**: Do not move removed business logic back to service layer

## Technical Considerations

1. **Test-First Approach**: Create integration test using `lease_directory_search.py` with known lease "NMLC 0028446A" as source of truth
2. **Implementation Strategy**: Build new simplified service alongside existing one, then replace completely
3. **Legacy Removal**: Remove old service entirely once new service passes all tests (no legacy preservation)
4. **Workflow Updates**: Update imports in `lease_directory_search.py` and `previous_report_detection.py` 
5. **Dependencies**: Remove config_manager dependency completely from service layer
6. **Error Handling**: Simplify to basic exception raising, let workflows handle business error logic

## Success Metrics

1. **Test Coverage**: Source of truth test using "NMLC 0028446A" passes with both old and new service
2. **Line Count Reduction**: Reduce from ~600 lines to under 300 lines
3. **Business Logic Elimination**: Zero config_manager or agency mapping logic in service
4. **Method Consolidation**: Reduce from 6+ private methods to 3 clean methods  
5. **Workflow Compatibility**: Both critical workflows (`lease_directory_search.py`, `previous_report_detection.py`) pass integration tests
6. **Architecture Compliance**: Service layer contains only API operations, no business logic
7. **Interface Simplification**: Clean method signatures with no business logic parameters
8. **Legacy Removal**: Old service code completely removed after successful migration

## Implementation Decisions

1. **Import Updates**: Handle workflow import updates manually (no migration script)
2. **Service Validation**: Keep simplified service completely minimal 
3. **Test Format**: Standard integration test format

---

**Target Audience**: Junior developers should be able to understand the simplified service within 5 minutes of reading it.

**Implementation Priority**: High - this architectural cleanup will improve maintainability and development velocity.