# Cloud-Agnostic Service Architecture Implementation Tasks

## Relevant Files

- `src/integrations/cloud/__init__.py` - New cloud integration package initialization
- `src/integrations/cloud/models.py` - Cloud-agnostic data models (CloudFile, ShareLink, CloudError)
- `src/integrations/cloud/protocols.py` - Protocol interfaces for cloud operations
- `src/integrations/cloud/factory.py` - CloudServiceFactory for provider instantiation
- `src/integrations/cloud/errors.py` - Generic cloud error types and mapping utilities
- `src/integrations/dropbox/service_legacy.py` - Renamed original DropboxService for reference
- `src/integrations/dropbox/cloud_service.py` - New DropboxCloudService implementing protocols
- `src/core/workflows/lease_directory_search.py` - Updated to use cloud protocols
- `src/core/workflows/previous_report_detection.py` - Updated to use cloud protocols  
- `src/config.py` - Updated with cloud provider configuration
- `src/test_lease_directory_search_integration.py` - Updated integration test
- `tests/integrations/cloud/test_models.py` - Unit tests for cloud models
- `tests/integrations/cloud/test_factory.py` - Unit tests for cloud factory
- `tests/integrations/dropbox/test_cloud_service.py` - Unit tests for Dropbox cloud service

### Notes

- Keep existing integration test as the primary validation tool
- Run integration test after each major step to ensure no regression
- Legacy DropboxService should remain functional for emergency rollback

## Tasks

- [ ] 1.0 Create Cloud-Agnostic Data Models and Protocols
  - [ ] 1.1 Create `src/integrations/cloud/` directory structure with `__init__.py`
  - [ ] 1.2 Define `CloudFile` dataclass in `models.py` with path, name, is_directory, size, modified_date fields
  - [ ] 1.3 Define `ShareLink` dataclass in `models.py` with url, expires_at, is_public fields
  - [ ] 1.4 Create `CloudAuthentication` protocol in `protocols.py` with authenticate() and is_authenticated() methods
  - [ ] 1.5 Create `CloudFileOperations` protocol in `protocols.py` with find_file() and list_files() methods
  - [ ] 1.6 Create `CloudSharingOperations` protocol in `protocols.py` with create_share_link() method
  - [ ] 1.7 Create placeholder `CloudDirectoryOperations` protocol in `protocols.py` for future directory creation
  - [ ] 1.8 Define generic error classes in `errors.py` (CloudServiceError, CloudAuthError, CloudNotFoundError)
  - [ ] 1.9 Create error mapping utilities in `errors.py` to convert provider-specific errors

- [ ] 2.0 Refactor Existing DropboxService to Legacy and Create New Cloud Implementation
  - [ ] 2.1 Rename `src/integrations/dropbox/service.py` to `service_legacy.py`
  - [ ] 2.2 Update `DropboxService` class name to `DropboxServiceLegacy` in legacy file
  - [ ] 2.3 Create new `src/integrations/dropbox/cloud_service.py` implementing cloud protocols
  - [ ] 2.4 Implement `CloudAuthentication` protocol in `DropboxCloudService` class
  - [ ] 2.5 Implement `CloudFileOperations` protocol with find_file() returning CloudFile objects
  - [ ] 2.6 Implement `CloudSharingOperations` protocol with create_share_link() returning ShareLink objects
  - [ ] 2.7 Add method to convert Dropbox metadata to CloudFile objects
  - [ ] 2.8 Add method to convert Dropbox share links to ShareLink objects
  - [ ] 2.9 Preserve all existing workspace logic within DropboxCloudService implementation
  - [ ] 2.10 Map Dropbox exceptions to generic cloud errors using error utilities

- [ ] 3.0 Implement Cloud Service Factory and Configuration Integration
  - [ ] 3.1 Add `CLOUD_PROVIDER = "dropbox"` setting to `src/config.py`
  - [ ] 3.2 Create `CloudServiceFactory` class in `factory.py` with create_service() method
  - [ ] 3.3 Implement provider instantiation logic for "dropbox" provider type
  - [ ] 3.4 Add factory method to return service implementing all required protocols
  - [ ] 3.5 Add provider validation and error handling for unsupported providers
  - [ ] 3.6 Create helper function to get configured cloud service instance

- [ ] 4.0 Update Workflows to Use Generic Cloud Interfaces
  - [ ] 4.1 Update `lease_directory_search.py` imports to use cloud factory instead of DropboxService
  - [ ] 4.2 Modify `LeaseDirectorySearchWorkflow.__init__()` to accept cloud service protocols
  - [ ] 4.3 Update workflow execute() method to work with CloudFile objects instead of Dropbox-specific responses
  - [ ] 4.4 Update `previous_report_detection.py` imports to use cloud factory
  - [ ] 4.5 Modify `PreviousReportDetectionWorkflow` to work with cloud protocols
  - [ ] 4.6 Ensure both workflows maintain identical functionality with new interfaces

- [ ] 5.0 Validate Implementation with Integration Tests
  - [ ] 5.1 Update `src/test_lease_directory_search_integration.py` to use CloudServiceFactory
  - [ ] 5.2 Run integration test to verify identical results with new cloud service
  - [ ] 5.3 Create unit tests for CloudFile and ShareLink models in `test_models.py`
  - [ ] 5.4 Create unit tests for CloudServiceFactory in `test_factory.py`
  - [ ] 5.5 Create unit tests for DropboxCloudService in `test_cloud_service.py`
  - [ ] 5.6 Verify all existing Dropbox service tests pass with legacy service
  - [ ] 5.7 Run complete test suite to ensure no regressions