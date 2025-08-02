# Product Requirements Document: Externalize Configuration (Phase 2)

## Introduction/Overview

Phase 2 of the Order Manager refactoring focuses on externalizing all hard-coded configuration values from processor classes into a centralized, configurable system. This phase eliminates scattered configuration throughout the codebase and creates a foundation for agency-agnostic processing that supports rapid expansion to new agency types.

The current system has configuration values hard-coded directly in processor classes, making it difficult to maintain and extend. This change will reduce maintenance burden and prepare the system for future expansion by making agency differences explicit and configurable.

## Goals

1. **Eliminate Hard-Coded Configuration**: Remove all hard-coded column names, widths, folder structures, and agency-specific values from processor classes
2. **Centralize Configuration Management**: Create a single source of truth for all agency-specific configuration
3. **Enable Rapid Agency Expansion**: Make it possible to add new agency types by simply adding configuration entries
4. **Maintain System Reliability**: Ensure robust validation and clear error handling for configuration issues
5. **Prepare for Strategy Pattern**: Create the configuration foundation needed for Phase 3's strategy pattern implementation

## User Stories

### Story 1: Developer Adding New Agency
**As a** developer adding support for a new agency type  
**I want** to define agency-specific behavior through configuration  
**So that** I can add new agencies without modifying processor code

### Story 2: Developer Maintaining Configuration
**As a** developer maintaining the system  
**I want** all configuration values in one centralized location  
**So that** I can easily find and update agency-specific settings

### Story 3: System Administrator
**As a** system administrator  
**I want** clear error messages when configuration is invalid  
**So that** I can quickly identify and fix configuration issues

## Functional Requirements

### Core Configuration Management

1. **Hybrid Configuration System**: Create a hybrid configuration system with separate static configuration (dataclass) and behavioral configuration (callables) to support both Phase 3 strategy patterns and future plugin architecture

2. **Static Configuration Dataclass**: Create `AgencyStaticConfig` dataclass for type-safe static data (column widths, folder structure, Dropbox agency names)

3. **Behavioral Configuration Class**: Create `AgencyBehaviorConfig` class that handles search function mappings and dynamic column generation logic

4. **Configuration Registry**: Implement a `AGENCY_CONFIGS` dictionary that maps agency names to their combined static and behavioral configurations

5. **Configuration Factory**: Create factory methods to retrieve and validate agency configurations by name, returning both static and behavioral components

6. **Configuration Validation**: Implement robust validation that checks for required fields, validates data types, validates callable functions, and ensures logical consistency

### Processor Updates

7. **Remove Hard-Coded Values**: Eliminate all hard-coded configuration from `NMSLOProcessor` and `FederalProcessor` classes

8. **Static Configuration Integration**: Update processors to read column widths, folder structures, and Dropbox names from static configuration

9. **Behavioral Configuration Integration**: Update processors to use behavioral configuration for search function mappings and dynamic column generation

10. **Dynamic Column Management**: Replace static column definitions with configuration-driven column lists that support both static metadata and dynamic search columns

11. **Search Function Mapping**: Replace hard-coded search logic with configurable function mappings that can be easily extended

### Error Handling & Validation

12. **Configuration Validation**: Validate both static and behavioral configuration completeness and consistency on system startup

13. **Invalid Agency Handling**: Provide clear error messages when invalid agency types are requested

14. **Missing Configuration Handling**: Gracefully handle missing or incomplete static/behavioral configuration with descriptive errors

15. **Callable Validation**: Validate that behavioral configuration functions are callable and return expected data types

16. **Configuration Schema Validation**: Ensure all required static configuration fields are present and properly typed

17. **Behavioral Configuration Testing**: Validate that search function mappings work correctly with sample data during startup

## Non-Goals (Out of Scope)

1. **GUI Changes**: This phase will not modify the user interface or user-facing functionality
2. **New Agency Implementation**: Will not actually implement new agency types, only prepare the foundation
3. **Performance Optimization**: Will not focus on performance improvements beyond configuration access
4. **Database Integration**: Will not implement database-backed configuration (Python-based config only)
5. **Runtime Configuration Changes**: Will not support changing configuration without application restart
6. **Backward Compatibility**: Will not maintain old hard-coded approach alongside new configuration

## Design Considerations

### Hybrid Configuration Architecture
- **Static Configuration**: Use dataclasses for type-safe static data (column widths, folder structures, agency names)
- **Behavioral Configuration**: Use callable mappings for dynamic behavior (search functions, column generation logic)
- **Strategy Pattern Ready**: This hybrid approach directly supports Phase 3's strategy pattern where strategies need both data and behavior
- **Plugin Architecture Ready**: Future plugins can register new behavioral configurations without code changes

### Configuration Structure Benefits
- **Type Safety**: Dataclasses provide IDE support and type checking for static configuration
- **Extensibility**: Behavioral configuration supports lambda functions, method references, and future plugin callables
- **Testability**: Both static and behavioral configurations can be easily mocked and tested
- **Phase 3 Compatibility**: Strategies can directly consume both configuration types without transformation

### File Organization
- Place configuration in `src/core/config.py` to align with existing structure
- Keep static and behavioral configurations together for cohesive agency definitions
- Align with current DropboxConfig patterns while extending for behavioral needs

### Validation Strategy
- Implement fail-fast validation for both static data and callable functions during system initialization
- Test behavioral configurations with sample data to catch runtime issues early
- Provide detailed error messages that help developers fix both data and logic issues
- Use dataclass field validation for static configuration, custom validation for behavioral configuration

## Technical Considerations

### Dependencies
- Must complete Phase 1 (Extract Utilities & Shared Components) before starting
- Builds foundation for Phase 3 (Strategy Pattern implementation)
- Should integrate with existing DropboxConfig patterns

### Configuration Format
- **Static Configuration**: Use Python dataclasses for type safety and IDE support
- **Behavioral Configuration**: Use callable mappings and function references for dynamic behavior
- **Registry Structure**: Store configuration as structured dictionaries with separate static/behavioral sections
- **Phase 3 Integration**: Design configuration to be directly consumable by strategy pattern classes
- **Extensibility**: Support lambda functions, method references, and future plugin callables

### Testing Integration
- Configuration changes should not break existing test suites
- New configuration system must support test environment setup
- Mock configuration should be easily created for unit tests

## Success Metrics

### Code Quality
- **Zero Hard-Coded Values**: No configuration values remaining in processor classes
- **100% Configuration Coverage**: All agency-specific behavior captured in configuration
- **Validation Coverage**: All configuration paths properly validated

### Maintainability
- **New Agency Time**: Theoretical time to add new agency type reduced to < 30 minutes
- **Configuration Location**: Single source of truth for all agency-specific behavior
- **Error Clarity**: Clear error messages for all configuration failure modes

### System Reliability
- **No Regression**: All existing functionality preserved
- **Robust Validation**: Invalid configurations caught before processing begins
- **Clear Diagnostics**: Configuration errors provide actionable information

## Open Questions

1. **Behavioral Configuration Security**: Should we restrict behavioral configuration to predefined function references only, or allow arbitrary lambda functions?

2. **Configuration File Format**: Should we also support JSON/YAML for static configuration while keeping behavioral configuration in Python?

3. **Configuration Versioning**: Do we need to consider configuration versioning for future compatibility between phases?

4. **Environment-Specific Config**: Should different environments (dev/test/prod) have different configuration approaches?

5. **Plugin Registration**: How should future plugins register their behavioral configurations with the system?

## Configuration Example

```python
# Example of hybrid configuration structure:
AGENCY_CONFIGS = {
    "NMSLO": {
        "static": AgencyStaticConfig(
            column_widths={"Agency": 15, "Order Type": 20, ...},
            folder_structure=["^Document Archive", "^MI Index", "Runsheets"],
            dropbox_agency_name="NMSLO"
        ),
        "behavioral": AgencyBehaviorConfig(
            search_mappings={
                "Full Search": lambda x: LeaseNumberParser(x).search_full(),
                "Partial Search": lambda x: LeaseNumberParser(x).search_partial()
            },
            blank_columns=["New Format", "Tractstar", "Old Format", "MI Index", "Documents", "Search Notes", "Link"]
        )
    }
}
```

## Acceptance Criteria

- [ ] Zero hard-coded configuration values in processor classes
- [ ] All agency differences captured in centralized configuration
- [ ] Configuration validation with clear error messages for invalid agency types
- [ ] Easy addition of new agency types through configuration alone
- [ ] All existing functionality preserved (regression tests pass)
- [ ] 100% unit test coverage for configuration management
- [ ] Clear error handling for missing or invalid configuration
- [ ] Documentation updated to reflect new configuration system 