# Cloud-Agnostic Service Architecture Implementation Tasks

## Relevant Files

- `src/integrations/cloud/__init__.py` - New cloud integration package initialization
- `src/integrations/cloud/models.py` - Cloud-agnostic data models (CloudFile, ShareLink, CloudError)
- `src/integrations/cloud/protocols.py` - Protocol interfaces for cloud operations
- `src/integrations/cloud/factory.py` - CloudServiceFactory for provider instantiation
- `src/integrations/cloud/errors.py` - Generic cloud error types and mapping utilities
- `src/integrations/dropbox/service_legacy.py` - Renamed original DropboxService for reference
- `src/integrations/dropbox/auth.py` - Simplified auth service with DropboxTokenAuth and DropboxOAuthAuth
- `src/integrations/dropbox/cloud_service.py` - New DropboxCloudService implementing protocols
- `src/core/workflows/lease_directory_search.py` - Updated to use cloud protocols
- `src/core/workflows/previous_report_detection.py` - Updated to use cloud protocols  
- `src/config.py` - Updated with cloud provider configuration (simplified, no redundant config dict)
- `src/test_lease_directory_search_integration.py` - Updated integration test
- `tests/integrations/cloud/test_models.py` - Unit tests for cloud models
- `tests/integrations/cloud/test_factory.py` - Unit tests for cloud factory
- `tests/integrations/dropbox/test_cloud_service.py` - Unit tests for Dropbox cloud service

### Notes

- Keep existing integration test as the primary validation tool
- Run integration test after each major step to ensure no regression
- Legacy DropboxService should remain functional for emergency rollback

## Tasks

- [x] 1.0 Create Cloud-Agnostic Data Models and Protocols
  - [x] 1.1 Create `src/integrations/cloud/` directory structure with `__init__.py`
  - [x] 1.2 Define `CloudFile` dataclass in `models.py` with path, name, is_directory, file_id, size, modified_date fields
  - [x] 1.3 Define `ShareLink` dataclass in `models.py` with url, expires_at, is_public fields
  - [x] 1.3.1 Refactor CloudFile to include optional share_link field for better relationship modeling
  - [x] 1.3.2 Add file_id field to CloudFile for provider-agnostic file identification
  - [x] 1.4 Create `CloudAuthentication` protocol in `protocols.py` with authenticate() and is_authenticated() methods
  - [x] 1.5 Create consolidated `CloudOperations` protocol in `protocols.py` with list_files(), list_directories(), create_share_link(), and create_directory() methods
  - [x] 1.8 Define generic error classes in `errors.py` (CloudServiceError, CloudAuthError, CloudNotFoundError)
  - [x] 1.9 Create error mapping utilities in `errors.py` to convert provider-specific errors

- [x] 2.0 Refactor Existing DropboxService to Legacy and Create New Cloud Implementation
  - [x] 2.1 Rename `src/integrations/dropbox/service.py` to `service_legacy.py`
  - [x] 2.2 Update `DropboxService` class name to `DropboxServiceLegacy` in legacy file
  - [x] 2.3 Create new `src/integrations/dropbox/cloud_service.py` implementing cloud protocols
  - [x] 2.4 Create simplified `src/integrations/dropbox/auth.py` with `DropboxTokenAuth` and `DropboxOAuthAuth`
  - [x] 2.5 Refactor `DropboxCloudService` to use simplified auth service with config dictionary
  - [x] 2.6 Implement `CloudOperations` protocol with list_files() and list_directories() returning CloudFile objects
  - [x] 2.7 Implement `CloudOperations` protocol with create_share_link() returning ShareLink objects
  - [x] 2.8 Add method to convert Dropbox metadata to CloudFile objects
  - [x] 2.9 Add method to convert Dropbox share links to ShareLink objects
  - [x] 2.10 Preserve all existing workspace logic within DropboxCloudService implementation
  - [x] 2.11 Map Dropbox exceptions to generic cloud errors using error utilities

- [x] 3.0 Implement Cloud Service Factory and Configuration Integration
  - [x] 3.1 Add `CLOUD_PROVIDER = "dropbox"` setting to `src/config.py`
  - [x] 3.2 Create `CloudServiceFactory` class in `factory.py` with create_service() method
  - [x] 3.3 Implement provider instantiation logic for "dropbox" provider type
  - [x] 3.4 Add factory method to return service implementing all required protocols
  - [x] 3.5 Add provider validation and error handling for unsupported providers
  - [x] 3.6 Create helper function to get configured cloud service instance

- [x] 4.0 Update Workflows to Use Generic Cloud Interfaces
  - [x] 4.1 Update `lease_directory_search.py` imports to use cloud factory instead of DropboxService
  - [x] 4.2 Modify `LeaseDirectorySearchWorkflow.__init__()` to accept cloud service protocols
  - [x] 4.3 Update workflow execute() method to use `list_files()` and `create_share_link()` instead of `get_directory_details()`
  - [x] 4.4 Update `previous_report_detection.py` imports to use cloud factory
  - [x] 4.5 Modify `PreviousReportDetectionWorkflow` to use `list_files()` instead of `list_directory_files()`
  - [x] 4.6 Ensure both workflows maintain identical functionality with new interfaces

- [x] 5.0 Validate Implementation with Integration Tests
  - [x] 5.1 Update `src/test_lease_directory_search_integration.py` to use CloudServiceFactory
  - [x] 5.2 Run integration test to verify identical results with new cloud service
  - [x] 5.3 Create unit tests for CloudFile and ShareLink models in `test_models.py`
  - [x] 5.4 Create unit tests for CloudServiceFactory in `test_factory.py`
  - [x] 5.5 Create unit tests for DropboxCloudService in `test_cloud_service.py`
  - [x] 5.6 Verify all existing Dropbox service tests pass with legacy service
  - [x] 5.7 Run complete test suite to ensure no regressions