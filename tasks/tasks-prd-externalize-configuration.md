# Task List: Externalize Configuration (Phase 2)

## Relevant Files

- `src/core/config.py` - New file containing hybrid configuration system with AgencyStaticConfig dataclass and AgencyBehaviorConfig class
- `src/core/config.test.py` - Unit tests for configuration system
- `src/core/processors.py` - Existing processors to be updated to use configuration instead of hard-coded values
- `tests/core/test_processors.py` - Existing processor tests to be updated for configuration integration
- `src/core/models.py` - Might need updates for configuration integration
- `tests/core/test_config.py` - Comprehensive unit tests for new configuration system
- `app.py` - May need minor updates for configuration error handling

### Notes

- Unit tests should be placed in the `tests/` directory structure mirroring the source structure
- Use `python3 -m pytest tests/` to run all tests
- Configuration validation should happen at startup to fail fast
- Both static and behavioral configurations need separate validation approaches

## Tasks

- [ ] 1.0 Create Hybrid Configuration System
  - [ ] 1.1 Create `src/core/config.py` file with necessary imports
  - [ ] 1.2 Implement `AgencyStaticConfig` dataclass with column_widths, folder_structure, and dropbox_agency_name fields
  - [ ] 1.3 Implement `AgencyBehaviorConfig` class with search_mappings and blank_columns attributes
  - [ ] 1.4 Add validation methods to `AgencyBehaviorConfig` for callable functions
  - [ ] 1.5 Create `AGENCY_CONFIGS` registry dictionary with State and Federal configurations
  - [ ] 1.6 Implement configuration factory methods (`get_agency_config`, `get_static_config`, `get_behavioral_config`)
  - [ ] 1.7 Add configuration helper methods (`get_all_columns`, `validate_agency_type`)

- [ ] 2.0 Update Processors to Use Configuration  
  - [ ] 2.1 Remove hard-coded column width dictionaries from both State and Federal processors
  - [ ] 2.2 Remove hard-coded folder structure lists from both processors
  - [ ] 2.3 Remove hard-coded search column names and logic from processors
  - [ ] 2.4 Update `StateProcessor` to use static configuration for column widths and folder structure
  - [ ] 2.5 Update `FederalProcessor` to use static configuration for column widths and folder structure
  - [ ] 2.6 Update `StateProcessor` to use behavioral configuration for search column generation
  - [ ] 2.7 Update `FederalProcessor` to use behavioral configuration for search column generation
  - [ ] 2.8 Update both processors to use configuration for Dropbox agency names
  - [ ] 2.9 Add configuration dependency injection to processor constructors

- [ ] 3.0 Implement Configuration Validation and Error Handling
  - [ ] 3.1 Create static configuration validation methods (type checking, required fields)
  - [ ] 3.2 Create behavioral configuration validation methods (callable validation, return type checking)
  - [ ] 3.3 Implement startup configuration validation that tests all agency configs
  - [ ] 3.4 Create custom exception classes for configuration errors (`ConfigurationError`, `InvalidAgencyError`)
  - [ ] 3.5 Add sample data testing for behavioral configurations to catch runtime issues
  - [ ] 3.6 Implement clear error messages for missing or invalid configurations
  - [ ] 3.7 Add configuration validation to factory methods with descriptive error handling

- [ ] 4.0 Create Comprehensive Test Suite
  - [ ] 4.1 Create unit tests for `AgencyStaticConfig` dataclass validation and methods
  - [ ] 4.2 Create unit tests for `AgencyBehaviorConfig` class and validation methods
  - [ ] 4.3 Create unit tests for configuration factory methods with valid and invalid inputs
  - [ ] 4.4 Create mock configurations for testing purposes
  - [ ] 4.5 Update existing processor tests to use configuration instead of hard-coded values
  - [ ] 4.6 Create integration tests for configuration validation and error handling
  - [ ] 4.7 Create tests for behavioral configuration callable validation
  - [ ] 4.8 Add performance tests to ensure configuration access doesn't impact processing speed

- [ ] 5.0 Integration Testing and Documentation
  - [ ] 5.1 Run full regression test suite to ensure no functionality changes
  - [ ] 5.2 Test configuration system with real order processing workflows
  - [ ] 5.3 Verify all hard-coded values have been successfully externalized
  - [ ] 5.4 Update docstrings and inline documentation for new configuration system
  - [ ] 5.5 Create configuration usage examples and best practices documentation
  - [ ] 5.6 Test error handling with intentionally invalid configurations
  - [ ] 5.7 Verify Phase 3 readiness by ensuring configuration supports strategy pattern requirements 