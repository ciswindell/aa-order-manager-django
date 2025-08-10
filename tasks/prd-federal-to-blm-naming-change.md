# Product Requirements Document: Federal to BLM Naming Change

## Introduction/Overview

The AA Order Manager currently uses "Federal" as the user-facing term for BLM (Bureau of Land Management) agency operations. This creates confusion and inconsistency throughout the application, as the business logic correctly uses `AgencyType.BLM` while the GUI and validation messages use "Federal". This feature will standardize all naming to use "BLM" consistently across the entire codebase, except for existing Dropbox directory paths which must remain unchanged to maintain compatibility with existing folder structures.

**Goal:** Eliminate naming confusion by replacing all instances of "Federal" with "BLM" throughout the codebase while preserving compatibility with existing Dropbox directory structures.

## Goals

1. **Consistency**: Achieve uniform naming throughout the application using "BLM" instead of "Federal"
2. **User Clarity**: Provide clear, business-accurate terminology in all user-facing elements
3. **Developer Experience**: Simplify code maintenance by removing the need for mapping functions between GUI and business logic
4. **Zero Downtime**: Implement changes without breaking existing functionality or data compatibility

## User Stories

1. **As an end user**, I want to see "BLM" in the agency dropdown instead of "Federal" so that the interface uses accurate business terminology.

2. **As an end user**, I want validation messages to reference "BLM" instead of "Federal" so that error messages are consistent with the interface.

3. **As a developer**, I want consistent naming throughout the codebase so that I don't need to mentally map between "Federal" and "BLM" when working on different parts of the application.

4. **As a developer**, I want to remove the `@map_agency_type` function complexity so that the code is more straightforward and maintainable.

5. **As a system administrator**, I want existing Dropbox folder structures to continue working so that no data migration is required.

## Functional Requirements

### GUI Components
1. The agency dropdown in `src/gui/main_window.py` must display "BLM" instead of "Federal"
2. All GUI-related comments and documentation must reference "BLM" instead of "Federal"

### Validation Layer
3. Form validation messages must reference "BLM" instead of "Federal" in user-friendly error messages
4. Valid agency lists must contain "BLM" instead of "Federal"
5. All validation error message templates must use "BLM" terminology

### Service Layer
6. The `map_agency_type` function must accept "BLM" instead of "Federal" as input
7. All service layer comments and documentation must reference "BLM" instead of "Federal"

### Configuration
8. Agency configuration keys must use "BLM" instead of "Federal"
9. The alias mapping `AGENCY_CONFIGS["BLM"] = AGENCY_CONFIGS["Federal"]` must be removed
10. Configuration access patterns must use "BLM" directly

### Workflow Components
11. Workflow components must return "BLM" instead of "Federal" for agency identification
12. All workflow documentation and comments must reference "BLM"
13. Agency mapping dictionaries must use "BLM" consistently

### Utility Functions
14. Utility function documentation must reference "BLM" instead of "Federal"
15. All code comments in utility modules must use "BLM" terminology

### Test Files
16. All test cases must use "BLM" instead of "Federal" in test data
17. Test assertions must expect "BLM" values instead of "Federal"
18. Test documentation and comments must reference "BLM"

## Non-Goals (Out of Scope)

1. **Dropbox Directory Paths**: Existing directory paths like `/Federal/` and `/Federal Workspace/` will NOT be changed to maintain compatibility with existing folder structures
2. **Historical Data**: No migration of existing user data files or Excel files containing "Federal" references
3. **External API Changes**: No changes to external system integrations that might expect "Federal" terminology
4. **Database Schema**: No database schema changes (if any exist)
5. **Backwards Compatibility**: No support for accepting both "Federal" and "BLM" simultaneously during a transition period

## Design Considerations

- **User Interface**: The change should be seamless from a user perspective - the dropdown will simply show "BLM" instead of "Federal"
- **Code Organization**: Maintain existing code structure and patterns while updating terminology
- **Error Handling**: Ensure all error messages maintain the same clarity and helpfulness with updated terminology

## Technical Considerations

- **Configuration Management**: The change requires updating the `AGENCY_CONFIGS` dictionary structure in `src/config.py`
- **Validation Framework**: Updates needed across the centralized validation framework in `src/core/validation/`
- **Workflow System**: Agency identification logic in workflows must be updated to handle "BLM" consistently
- **Testing Coverage**: Comprehensive test updates required to maintain coverage with new terminology

## Success Metrics

1. **Code Consistency**: 100% of "Federal" references (excluding Dropbox paths) replaced with "BLM"
2. **Test Coverage**: All existing tests pass with updated terminology
3. **User Experience**: No user-visible errors or confusion in the GUI
4. **Developer Experience**: Elimination of the `@map_agency_type` function complexity
5. **Zero Regression**: No functional changes to application behavior, only terminology updates

## Open Questions

1. Should we add a comment or documentation note explaining why Dropbox paths still contain "Federal" for future developers?
2. Are there any external documentation or README files that should be updated to reflect the change?
3. Should we implement any validation to prevent accidental reintroduction of "Federal" terminology in future development?

---

**Created**: $(date)  
**Priority**: Medium  
**Estimated Effort**: 2-3 hours  
**Dependencies**: None  
**Risk Level**: Low (terminology change only, no functional changes)
