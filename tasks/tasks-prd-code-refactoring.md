# Task List: Code Refactoring for Scalable Organization

## Relevant Files

- `src/__init__.py` - Main package init file for the new src directory structure
- `src/core/__init__.py` - Core module package initialization  
- `src/core/processors.py` - Moved from root `processors.py`
- `src/core/models.py` - Moved from root `models.py`
- `src/integrations/__init__.py` - Integrations package initialization
- `src/integrations/dropbox/__init__.py` - Dropbox integration package initialization
- `src/integrations/dropbox/auth.py` - Moved from root `dropbox_auth.py`
- `src/integrations/dropbox/config.py` - Moved from root `dropbox_config.py`
- `src/integrations/dropbox/service.py` - Moved from root `dropbox_service.py`
- `app.py` - Main entry point (import statements updated)
- `tests/__init__.py` - Test package initialization
- `tests/core/` - New directory for core module tests (empty, no existing core tests)
- `tests/integrations/dropbox/test_auth.py` - Moved from `tests/test_dropbox_auth.py` with updated imports
- `tests/integrations/dropbox/test_config.py` - Moved from `tests/test_dropbox_config.py` with updated imports
- `tests/integrations/dropbox/test_service.py` - Moved from `tests/test_dropbox_service.py` with updated imports
- `tests/integrations/dropbox/test_integration.py` - Moved from `tests/test_integration.py` with updated imports

### Notes

- All file contents remain identical except for import statement updates
- Test structure mirrors the new source code organization
- Use `python3 -m pytest` to run tests after refactoring

## Tasks

- [x] 1.0 Create new directory structure and package initialization files
  - [x] 1.1 Create `src/` directory in project root
  - [x] 1.2 Create `src/__init__.py` file (empty)
  - [x] 1.3 Create `src/core/` directory
  - [x] 1.4 Create `src/core/__init__.py` file (empty)
  - [x] 1.5 Create `src/integrations/` directory
  - [x] 1.6 Create `src/integrations/__init__.py` file (empty)
  - [x] 1.7 Create `src/integrations/dropbox/` directory
  - [x] 1.8 Create `src/integrations/dropbox/__init__.py` file (empty)
- [x] 2.0 Move core application files to src/core/ directory
  - [x] 2.1 Move `processors.py` to `src/core/processors.py`
  - [x] 2.2 Move `models.py` to `src/core/models.py`
  - [x] 2.3 Delete original `processors.py` from root
  - [x] 2.4 Delete original `models.py` from root
- [x] 3.0 Move Dropbox integration files to src/integrations/dropbox/ directory
  - [x] 3.1 Move `dropbox_auth.py` to `src/integrations/dropbox/auth.py`
  - [x] 3.2 Move `dropbox_config.py` to `src/integrations/dropbox/config.py`
  - [x] 3.3 Move `dropbox_service.py` to `src/integrations/dropbox/service.py`
  - [x] 3.4 Delete original `dropbox_auth.py` from root
  - [x] 3.5 Delete original `dropbox_config.py` from root
  - [x] 3.6 Delete original `dropbox_service.py` from root
- [x] 4.0 Update all import statements throughout the codebase
  - [x] 4.1 Update imports in `app.py` to use new paths (processors, models, dropbox modules)
  - [x] 4.2 Update any internal imports within moved files if they reference each other
  - [x] 4.3 Check and update any cross-references between core and integration modules
- [x] 5.0 Reorganize test directory to mirror new source structure
  - [x] 5.1 Create `tests/__init__.py` file (empty)
  - [x] 5.2 Create `tests/core/` directory
  - [x] 5.3 Create `tests/integrations/` directory  
  - [x] 5.4 Create `tests/integrations/dropbox/` directory
  - [x] 5.5 Move test files to match new structure:
    - [x] 5.5.1 No existing core tests to move (processors.py has no dedicated test file)
    - [x] 5.5.2 Move `tests/test_dropbox_auth.py` to `tests/integrations/dropbox/test_auth.py`
    - [x] 5.5.3 Move `tests/test_dropbox_config.py` to `tests/integrations/dropbox/test_config.py`
    - [x] 5.5.4 Move `tests/test_dropbox_service.py` to `tests/integrations/dropbox/test_service.py`
    - [x] 5.5.5 Move `tests/test_integration.py` to `tests/integrations/dropbox/test_integration.py`
  - [x] 5.6 Update import statements in all moved test files to reference new module paths
  - [x] 5.7 Delete original test files from root tests directory
- [x] 6.0 Validate refactoring by running tests and application
  - [x] 6.1 Run all tests with `python3 -m pytest tests/` to ensure they pass
  - [x] 6.2 Run the main application `python3 app.py` to verify GUI loads correctly
  - [x] 6.3 Test basic functionality (file selection, agency selection) to ensure no import errors
  - [x] 6.4 Fix any import issues discovered during testing
  - [x] 6.5 Verify all files are in their correct new locations
  - [x] 6.6 Confirm original files have been properly deleted from root directory 