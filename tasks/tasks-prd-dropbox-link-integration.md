# Task List: Dropbox API Integration for Automated Lease Folder Links

Based on: `prd-dropbox-link-integration.md`

## Relevant Files

- `dropbox_service.py` - Main Dropbox service class implementing all API interactions with clear interfaces
- `dropbox_auth.py` - OAuth 2.0 authentication handler with web browser flow and token management
- `dropbox_config.py` - Configuration management for app credentials and agency directory mappings
- `requirements.txt` - Add dropbox package dependency
- `app.py` - GUI modifications to add Dropbox checkbox option in the Options section
- `processors.py` - Modify both NMStateOrderProcessor and FederalOrderProcessor to integrate Dropbox service
- `tests/test_dropbox_service.py` - Unit tests for dropbox_service.py
- `tests/test_dropbox_auth.py` - Unit tests for dropbox_auth.py
- `tests/test_dropbox_config.py` - Unit tests for dropbox_config.py

### Notes

- All Dropbox functionality is designed as a standalone module following SOLID/DRY principles for reusability
- Use dependency injection to loosely couple Dropbox service with existing order processors
- Implement graceful error handling to ensure worksheet export continues even if Dropbox is unavailable

## Tasks

- [ ] 1.0 Create Modular Dropbox Service Module
  - [ ] 1.1 Create `dropbox_service.py` with main DropboxService class and clean interfaces
  - [ ] 1.2 Define abstract base class or interface for service contract
  - [ ] 1.3 Implement error handling framework with custom exceptions
  - [ ] 1.4 Add logging functionality for debugging and monitoring
  - [ ] 1.5 Create unit tests for service module structure

- [ ] 2.0 Implement OAuth 2.0 Authentication System
  - [ ] 2.1 Create `dropbox_auth.py` with OAuth 2.0 flow implementation
  - [ ] 2.2 Implement web browser authentication with offline access
  - [ ] 2.3 Build secure local refresh token storage mechanism
  - [ ] 2.4 Add automatic token refresh handling using official SDK
  - [ ] 2.5 Implement authentication error handling and user feedback
  - [ ] 2.6 Create unit tests for authentication flows

- [ ] 3.0 Develop Directory Search and Link Generation
  - [ ] 3.1 Create `dropbox_config.py` for agency-specific directory configuration
  - [ ] 3.2 Implement exact name matching directory search using Dropbox API v2
  - [ ] 3.3 Add agency-specific directory path mapping (Federal vs NMState)
  - [ ] 3.4 Implement shareable link generation for found directories
  - [ ] 3.5 Handle cases where no matching directory is found
  - [ ] 3.6 Add search performance optimization and error handling
  - [ ] 3.7 Create unit tests for search and link generation functionality

- [ ] 4.0 Integrate GUI Controls and User Options
  - [ ] 4.1 Add Dropbox checkbox to existing Options section in `app.py`
  - [ ] 4.2 Implement checkbox state management and user interaction handling
  - [ ] 4.3 Add progress indication/feedback during Dropbox operations
  - [ ] 4.4 Ensure checkbox is disabled by default to maintain existing workflow
  - [ ] 4.5 Add user feedback for authentication and error states

- [ ] 5.0 Integrate Dropbox Service with Order Processors
  - [ ] 5.1 Add `dropbox` package to `requirements.txt`
  - [ ] 5.2 Modify `NMStateOrderProcessor` to optionally use Dropbox service
  - [ ] 5.3 Modify `FederalOrderProcessor` to optionally use Dropbox service
  - [ ] 5.4 Implement dependency injection for loose coupling
  - [ ] 5.5 Add Dropbox link population to `create_order_worksheet` methods
  - [ ] 5.6 Ensure graceful fallback when Dropbox integration fails
  - [ ] 5.7 Create integration tests for end-to-end workflow 