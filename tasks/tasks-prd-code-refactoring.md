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
- `tests/core/test_processors.py` - Moved from root test directory
- `tests/integrations/dropbox/test_auth.py` - Moved from root test directory
- `tests/integrations/dropbox/test_config.py` - Moved from root test directory
- `tests/integrations/dropbox/test_service.py` - Moved from root test directory
- `tests/integrations/dropbox/test_integration.py` - Moved from root test directory

### Notes

- All file contents remain identical except for import statement updates
- Test structure mirrors the new source code organization
- Use `python3 -m pytest` to run tests after refactoring

## Tasks

- [ ] 1.0 Create new directory structure and package initialization files
  - [ ] 1.1 Create `src/` directory in project root
  - [ ] 1.2 Create `src/__init__.py` file (empty)
  - [ ] 1.3 Create `src/core/` directory
  - [ ] 1.4 Create `src/core/__init__.py` file (empty)
  - [ ] 1.5 Create `src/integrations/` directory
  - [ ] 1.6 Create `src/integrations/__init__.py` file (empty)
  - [ ] 1.7 Create `src/integrations/dropbox/` directory
  - [ ] 1.8 Create `src/integrations/dropbox/__init__.py` file (empty)
- [ ] 2.0 Move core application files to src/core/ directory
  - [ ] 2.1 Move `processors.py` to `src/core/processors.py`
  - [ ] 2.2 Move `models.py` to `src/core/models.py`
  - [ ] 2.3 Delete original `processors.py` from root
  - [ ] 2.4 Delete original `models.py` from root
- [ ] 3.0 Move Dropbox integration files to src/integrations/dropbox/ directory
  - [ ] 3.1 Move `dropbox_auth.py` to `src/integrations/dropbox/auth.py`
  - [ ] 3.2 Move `dropbox_config.py` to `src/integrations/dropbox/config.py`
  - [ ] 3.3 Move `dropbox_service.py` to `src/integrations/dropbox/service.py`
  - [ ] 3.4 Delete original `dropbox_auth.py` from root
  - [ ] 3.5 Delete original `dropbox_config.py` from root
  - [ ] 3.6 Delete original `dropbox_service.py` from root
- [ ] 4.0 Update all import statements throughout the codebase
  - [ ] 4.1 Update imports in `app.py` to use new paths (processors, models, dropbox modules)
  - [ ] 4.2 Update any internal imports within moved files if they reference each other
  - [ ] 4.3 Check and update any cross-references between core and integration modules
- [ ] 5.0 Reorganize test directory to mirror new source structure
  - [ ] 5.1 Create `tests/__init__.py` file (empty)
  - [ ] 5.2 Create `tests/core/` directory
  - [ ] 5.3 Create `tests/integrations/` directory  
  - [ ] 5.4 Create `tests/integrations/dropbox/` directory
  - [ ] 5.5 Move test files to match new structure:
    - [ ] 5.5.1 No existing core tests to move (processors.py has no dedicated test file)
    - [ ] 5.5.2 Move `tests/test_dropbox_auth.py` to `tests/integrations/dropbox/test_auth.py`
    - [ ] 5.5.3 Move `tests/test_dropbox_config.py` to `tests/integrations/dropbox/test_config.py`
    - [ ] 5.5.4 Move `tests/test_dropbox_service.py` to `tests/integrations/dropbox/test_service.py`
    - [ ] 5.5.5 Move `tests/test_integration.py` to `tests/integrations/dropbox/test_integration.py`
  - [ ] 5.6 Update import statements in all moved test files to reference new module paths
  - [ ] 5.7 Delete original test files from root tests directory
- [ ] 6.0 Validate refactoring by running tests and application
  - [ ] 6.1 Run all tests with `python3 -m pytest tests/` to ensure they pass
  - [ ] 6.2 Run the main application `python3 app.py` to verify GUI loads correctly
  - [ ] 6.3 Test basic functionality (file selection, agency selection) to ensure no import errors
  - [ ] 6.4 Fix any import issues discovered during testing
  - [ ] 6.5 Verify all files are in their correct new locations
  - [ ] 6.6 Confirm original files have been properly deleted from root directory 