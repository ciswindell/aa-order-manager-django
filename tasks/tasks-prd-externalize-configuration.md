# Task List: Externalize Configuration (Phase 2)

## Relevant Files

- `src/core/config/` - New configuration package with modular structure
- `src/core/config/__init__.py` - Public API exports for configuration package
- `src/core/config/exceptions.py` - Configuration exception classes
- `src/core/config/models.py` - AgencyStaticConfig dataclass and AgencyBehaviorConfig class
- `src/core/config/registry.py` - AGENCY_CONFIGS registry and validation
- `src/core/config/factory.py` - Factory methods and helper utilities
- `src/core/processors.py` - Existing processors to be updated to use configuration instead of hard-coded values
- `tests/core/test_processors.py` - Existing processor tests to be updated for configuration integration
- `src/core/models.py` - Might need updates for configuration integration
- `tests/core/config/test_exceptions.py` - Unit tests for configuration exceptions
- `tests/core/config/test_models.py` - Unit tests for configuration models 
- `tests/core/config/test_registry.py` - Unit tests for configuration registry
- `tests/core/config/test_factory.py` - Unit tests for factory methods and helpers
- `app.py` - May need minor updates for configuration error handling

### Notes

- Unit tests should be placed in the `tests/` directory structure mirroring the source structure
- Use `python3 -m pytest tests/` to run all tests
- Configuration validation should happen at startup to fail fast
- Both static and behavioral configurations need separate validation approaches

## Tasks

- [x] 1.0 Create Hybrid Configuration System
  - [x] 1.1 Create `src/core/config.py` file with necessary imports
  - [x] 1.2 Implement `AgencyStaticConfig` dataclass with column_widths, folder_structure, and dropbox_agency_name fields
  - [x] 1.3 Implement `AgencyBehaviorConfig` class with search_mappings and blank_columns attributes
  - [x] 1.4 Add validation methods to `AgencyBehaviorConfig` for callable functions
  - [x] 1.5 Create `AGENCY_CONFIGS` registry dictionary with NMSLO and Federal configurations
  - [x] 1.6 Implement configuration factory methods (`get_agency_config`, `get_static_config`, `get_behavioral_config`)
  - [x] 1.7 Add configuration helper methods (`get_all_columns`, `validate_agency_type`)
  - [x] 1.8 Refactor configuration into modular directory structure

- [x] 2.0 Rename "State" to "NMSLO" for Specificity and Consistency
  - [x] 2.1 Update configuration registry to use "NMSLO" instead of "State" 
  - [x] 2.2 Update all processor references from "State" to "NMSLO"
  - [x] 2.3 Update test files to use "NMSLO" instead of "State"
  - [x] 2.4 Update GUI and application code to use "NMSLO"
  - [x] 2.5 Update documentation and comments to use "NMSLO"
  - [x] 2.6 Search codebase for any remaining "State" references and update
  - [x] 2.7 Verify configuration validation still works with "NMSLO"

- [x] 3.0 Update Processors to Use Configuration  
  - [x] 3.1 Remove hard-coded column width dictionaries from both NMSLO and Federal processors
  - [x] 3.2 Remove hard-coded folder structure lists from both processors
  - [x] 3.3 Remove hard-coded search column names and logic from processors
  - [x] 3.4 Update `NMSLOOrderProcessor` to use static configuration for column widths and folder structure
  - [x] 3.5 Update `FederalOrderProcessor` to use static configuration for column widths and folder structure
  - [x] 3.6 Update `NMSLOOrderProcessor` to use behavioral configuration for search column generation
  - [x] 3.7 Update `FederalOrderProcessor` to use behavioral configuration for search column generation
  - [x] 3.8 Update both processors to use configuration for Dropbox agency names
  - [x] 3.9 Add configuration dependency injection to processor constructors

- [ ] 4.0 Implement Configuration Validation and Error Handling
  - [x] 4.1 Create static configuration validation methods (type checking, required fields)
  - [x] 4.2 Create behavioral configuration validation methods (callable validation, return type checking)
  - [x] 4.3 Implement startup configuration validation that tests all agency configs
  - [x] 4.4 Create custom exception classes for configuration errors (`ConfigurationError`, `InvalidAgencyError`)
  - [x] 4.5 Add sample data testing for behavioral configurations to catch runtime issues
  - [x] 4.6 Implement clear error messages for missing or invalid configurations
  - [x] 4.7 Add configuration validation to factory methods with descriptive error handling

- [ ] 5.0 Create Comprehensive Test Suite
  - [x] 5.1 Create unit tests for `AgencyStaticConfig` dataclass validation and methods
  - [x] 5.2 Create unit tests for `AgencyBehaviorConfig` class and validation methods
  - [x] 5.3 Create unit tests for configuration factory methods with valid and invalid inputs
  - [x] 5.4 Create mock configurations for testing purposes
  - [x] 5.5 Update existing processor tests to use configuration instead of hard-coded values
  - [x] 5.6 Create integration tests for configuration validation and error handling
  - [x] 5.7 Create tests for behavioral configuration callable validation
  - [x] 5.8 Add performance tests to ensure configuration access doesn't impact processing speed

- [ ] 6.0 Integration Testing and Documentation
  - [x] 6.1 Run full regression test suite to ensure no functionality changes
  - [x] 6.2 Test configuration system with real order processing workflows
  - [x] 6.3 Verify all hard-coded values have been successfully externalized
  - [x] 6.4 Update docstrings and inline documentation for new configuration system
  - [x] 6.5 Create configuration usage examples and best practices documentation
  - [x] 6.6 Test error handling with intentionally invalid configurations
  - [x] 6.7 Verify Phase 3 readiness by ensuring configuration supports strategy pattern requirements 