# Task List: Dropbox API Integration for Automated Lease Folder Links

Based on: `prd-dropbox-link-integration.md`

## Relevant Files

- `dropbox_service.py` - Main Dropbox service class implementing all API interactions with clear interfaces, scoped directory search using Dropbox API v2, exact path matching, agency-specific search logic, shareable link generation with existing link checking, and comprehensive error handling with performance optimization
- `dropbox_auth.py` - OAuth 2.0 authentication handler with web browser flow, offline access, secure refresh token storage, automatic token refresh, and comprehensive error handling
- `dropbox_config.py` - Configuration management for app credentials and agency-specific root directory path mappings with support for config files, environment variables, and search path generation (Federal + "NMLC 123456" → "/Federal/NMLC 123456/")
- `requirements.txt` - Add dropbox package dependency
- `app.py` - GUI modifications to add Dropbox checkbox option in the Options section
- `processors.py` - Modified both NMStateOrderProcessor and FederalOrderProcessor constructors to accept optional dropbox_service parameter and updated create_order_worksheet methods to populate Link column with Dropbox shareable links when service is available (with agency-specific directory search and graceful error handling)
- `tests/test_dropbox_service.py` - Unit tests for dropbox_service.py (comprehensive tests for interface, exceptions, authentication, agency-specific search, link generation, integration workflows, and bulk operations)
- `tests/test_dropbox_auth.py` - Unit tests for dropbox_auth.py (comprehensive tests for OAuth flows, token management, browser integration, and error handling)
- `tests/test_dropbox_config.py` - Unit tests for dropbox_config.py (comprehensive tests for configuration loading, agency directory management, environment variables, file operations, and validation)
- `tests/test_integration.py` - End-to-end integration tests for complete Dropbox workflow with order processors (tests both Federal and State processors with various Dropbox scenarios, error handling, GUI workflow simulation, and worksheet generation with Link column population)

### Notes

- All Dropbox functionality is designed as a standalone module following SOLID/DRY principles for reusability
- Use dependency injection to loosely couple Dropbox service with existing order processors
- Implement graceful error handling to ensure worksheet export continues even if Dropbox is unavailable
- Search process: Agency determines root directory (Federal → "/Federal/", NMState → "/NMState/"), then search for lease subdirectory within that scope

## Tasks

- [x] 1.0 Create Modular Dropbox Service Module
  - [x] 1.1 Create `dropbox_service.py` with main DropboxService class and clean interfaces
  - [x] 1.2 Define abstract base class or interface for service contract
  - [x] 1.3 Implement error handling framework with custom exceptions
  - [x] 1.4 Add logging functionality for debugging and monitoring
  - [x] 1.5 Create unit tests for service module structure

- [x] 2.0 Implement OAuth 2.0 Authentication System
  - [x] 2.1 Create `dropbox_auth.py` with OAuth 2.0 flow implementation
  - [x] 2.2 Implement web browser authentication with offline access
  - [x] 2.3 Build secure local refresh token storage mechanism
  - [x] 2.4 Add automatic token refresh handling using official SDK
  - [x] 2.5 Implement authentication error handling and user feedback
  - [x] 2.6 Create unit tests for authentication flows

- [x] 3.0 Develop Directory Search and Link Generation
  - [x] 3.1 Create `dropbox_config.py` for agency-specific root directory path configuration (e.g., Federal → "/Federal/", NMState → "/NMState/")
  - [x] 3.2 Implement scoped directory search within agency root directories using exact name matching and Dropbox API v2
  - [x] 3.3 Add agency-specific directory path mapping and subdirectory search logic (Federal + "NMLC 123456" → "/Federal/NMLC 123456/")
  - [x] 3.4 Implement shareable link generation for found directories
  - [x] 3.5 Handle cases where no matching directory is found
  - [x] 3.6 Add search performance optimization and error handling
  - [x] 3.7 Create unit tests for search and link generation functionality

- [x] 4.0 Integrate GUI Controls and User Options
  - [x] 4.1 Add Dropbox checkbox to existing Options section in `app.py`
  - [x] 4.2 Implement checkbox state management and user interaction handling
  - [x] 4.3 Add progress indication/feedback during Dropbox operations
  - [x] 4.4 Ensure checkbox is disabled by default to maintain existing workflow
  - [x] 4.5 Add user feedback for authentication and error states

- [x] 5.0 Integrate Dropbox Service with Order Processors
  - [x] 5.1 Add `dropbox` package to `requirements.txt`
  - [x] 5.2 Modify `NMStateOrderProcessor` to optionally use Dropbox service
  - [x] 5.3 Modify `FederalOrderProcessor` to optionally use Dropbox service
  - [x] 5.4 Implement dependency injection for loose coupling
  - [x] 5.5 Add Dropbox link population to `create_order_worksheet` methods with agency-specific directory search
  - [x] 5.6 Ensure graceful fallback when Dropbox integration fails
  - [x] 5.7 Create integration tests for end-to-end workflow 