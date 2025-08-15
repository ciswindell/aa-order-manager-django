# Runsheet Archive Naming Convention PRD

## Introduction/Overview

The current codebase uses "lease directory" terminology throughout, but this doesn't match the actual business domain language. In our business context, we refer to these as "runsheet archives" - directories that contain runsheet reports and related documents for specific leases. This naming mismatch creates confusion for both developers and business stakeholders.

The goal is to systematically rename all code references from "lease directory" to "runsheet archive" to align the technical implementation with business terminology, improving code clarity and maintainability.

## Goals

1. **Consistency**: Achieve 100% consistency between business terminology and code naming
2. **Clarity**: Improve code readability and understanding for both developers and business stakeholders
3. **Maintainability**: Make future development easier by using domain-appropriate language
4. **Zero Breaking Changes**: Ensure all existing functionality continues to work after the rename
5. **Complete Coverage**: Update all relevant files, functions, variables, and database fields

## User Stories

- **As a developer**, I want the code to use "runsheet archive" terminology so that it matches our business domain language and reduces cognitive load when working with the codebase.

- **As a business stakeholder**, I want the technical documentation and code comments to use familiar business terminology so that I can better understand and communicate about the system.

- **As a new team member**, I want consistent naming between business requirements and code implementation so that I can quickly understand the system's purpose and structure.

- **As a maintainer**, I want domain-appropriate naming conventions so that future development and debugging is more intuitive and less error-prone.

## Functional Requirements

1. **File Renames**: Rename `web/orders/services/lease_directory_search.py` to `web/orders/services/runsheet_archive_search.py`

2. **Function Renames**: Update all function names from `run_lease_directory_search()` to `run_runsheet_archive_search()`

3. **Class Renames**: Update all class names from `LeaseDirectorySearchWorkflow` to `RunsheetArchiveSearchWorkflow`

4. **Business-Specific Variable Renames**: Update only business-specific variable names that refer to runsheet archives. Do NOT rename generic variables like `directory_path` or `base_path` that are used for any directory operations. Do NOT touch cloud service interfaces, Dropbox service methods, or any generic cloud operations.

5. **Database Field Rename**: Rename the database field from `runsheet_directory` to `runsheet_archive` in the Lease model

6. **Task Rename**: Update Celery task name from `lease_directory_search_task` to `runsheet_archive_search_task`

7. **Import Updates**: Update all import statements across the codebase to reference the new file and function names

8. **Test Updates**: Update all test class names, function names, and assertions to use the new naming convention

9. **Documentation Updates**: Update all comments, docstrings, and log messages to use "runsheet archive" terminology

10. **Configuration Updates**: Update configuration field names from `auto_create_lease_directories` to `auto_create_runsheet_archives`

11. **Migration Creation**: Create a database migration to rename the field from `runsheet_directory` to `runsheet_archive`

12. **Legacy Code Exclusion**: Ensure no changes are made to files in the `legacy/` directory (this codebase is being deprecated and will be deleted soon)

## Non-Goals (Out of Scope)

- **Legacy Code Changes**: No modifications to any files in the `legacy/` directory (deprecated codebase)
- **Cloud Service Interfaces**: No changes to cloud service protocols, Dropbox service methods, or generic cloud operations
- **Generic Directory Operations**: No changes to generic directory path variables or cloud service method signatures
- **External API Changes**: No changes to external-facing APIs or interfaces
- **Third-party Integrations**: No modifications to third-party service integrations
- **Performance Optimizations**: No performance-related changes beyond the naming updates
- **Feature Additions**: No new functionality beyond the naming convention changes
- **UI/UX Changes**: No changes to user interface or user experience

## Design Considerations

- **Backward Compatibility**: All existing functionality must continue to work exactly as before
- **Database Seeding**: Preserve the ability to recreate database seeding data
- **Test Coverage**: Maintain 100% test coverage with all tests passing after the changes
- **Code Quality**: Follow existing code style and PEP 8 standards throughout the changes

## Technical Considerations

- **Database Migration**: The database field rename requires a migration that can be safely applied to an empty database
- **Import Dependencies**: Careful attention needed to update all import statements in the correct order
- **Cloud Service Boundaries**: Must preserve all cloud service interfaces, protocols, and generic directory operations
- **Test Dependencies**: All test files must be updated to reference the new naming convention
- **Configuration Dependencies**: Agency storage configuration references need updating
- **Celery Task Registration**: Task names in Celery configuration may need updating

## Success Metrics

1. **Code Coverage**: 100% of identified files successfully updated with new naming convention
2. **Test Pass Rate**: All existing tests continue to pass after the naming changes
3. **Zero Breaking Changes**: No functionality is broken or altered beyond the naming updates
4. **Consistency**: No remaining references to "lease directory" terminology in active codebase
5. **Database Integrity**: Database migration successfully applies and maintains data integrity
6. **Development Experience**: Improved code readability and reduced confusion for developers

## Open Questions

1. **Migration Strategy**: Should the database migration be applied immediately or staged?
2. **Rollback Plan**: What is the rollback strategy if issues are discovered during implementation?
3. **Documentation Updates**: Should external documentation (README, API docs) be updated as part of this PRD or separately?
4. **Code Review Process**: What level of code review is required for these naming changes?
5. **Testing Strategy**: Should additional integration tests be added to verify the naming changes don't break workflows?

## Implementation Notes

- This work will be done in a separate branch until completion
- The database is currently empty and can be safely reset if needed
- All existing tests should continue to pass after the changes
- No third-party services will be affected by these changes
- The legacy directory should be completely excluded from all changes
