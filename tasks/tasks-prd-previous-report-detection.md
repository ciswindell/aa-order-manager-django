# Task List: Previous Report Detection Workflow

Generated from: `prd-previous-report-detection.md`

## Relevant Files

- `src/core/models.py` - Contains OrderItemData model that needs report_directory_path field enhancement
- `src/core/workflows/lease_directory_search.py` - Needs enhancement to store directory paths
- `src/integrations/dropbox/service.py` - Needs new list_directory_files() method for file listing
- `src/core/workflows/previous_report_detection.py` - New workflow implementation for Master Documents detection
- `src/core/workflows/__init__.py` - Import and expose new workflow
- `tests/core/test_models.py` - Tests for OrderItemData enhancements
- `tests/core/workflows/test_lease_directory_search.py` - Tests for LeaseDirectorySearchWorkflow enhancements
- `tests/integrations/dropbox/test_service.py` - Tests for DropboxService file listing functionality
- `tests/core/workflows/test_previous_report_detection.py` - Unit tests for new workflow implementation
- `tests/core/workflows/test_previous_report_detection_integration.py` - Integration tests for complete workflow execution
- `tests/core/workflows/test_end_to_end_workflow_orchestration.py` - End-to-end tests combining both workflows
- `tests/core/workflows/test_previous_report_detection_performance.py` - Performance tests with large directories

### Notes

- All tests should use mocking for external Dropbox API calls to ensure reliable, fast test execution
- File listing functionality must handle business account namespaces and authentication properly
- Pattern matching should be thoroughly tested with various filename variations
- Integration tests should validate end-to-end workflow execution with mock data

## Tasks

- [x] 1.0 Enhance OrderItemData Model with Directory Path Storage
  - [x] 1.1 Add optional `report_directory_path: Optional[str] = None` field to OrderItemData dataclass
  - [x] 1.2 Update OrderItemData validation in `__post_init__` to handle report_directory_path field
  - [x] 1.3 Add report_directory_path field documentation and examples to model docstring
  - [x] 1.4 Update existing OrderItemData unit tests to include report_directory_path field scenarios
  - [x] 1.5 Test report_directory_path field with None, valid path, and edge case values

- [x] 2.0 Enhance LeaseDirectorySearchWorkflow to Store Directory Paths
  - [x] 2.1 Modify `execute()` method to extract directory path from Dropbox API response
  - [x] 2.2 Store directory path in `order_item_data.report_directory_path` alongside shareable link generation
  - [x] 2.3 Update workflow result to include directory path information for debugging
  - [x] 2.4 Add validation to ensure directory path is captured when shareable link is generated
  - [x] 2.5 Update existing LeaseDirectorySearchWorkflow tests to verify directory path storage
  - [x] 2.6 Add test scenarios for directory path extraction from various Dropbox response formats

- [x] 3.0 Enhance DropboxService with File Listing Capabilities
  - [x] 3.1 Add `list_directory_files(directory_path: str) -> List[Dict[str, Any]]` method to DropboxService
  - [x] 3.2 Implement Dropbox API `/2/files/list_folder` endpoint integration with proper error handling
  - [x] 3.3 Handle business account namespace requirements and authentication headers
  - [x] 3.4 Add comprehensive error handling for API rate limits, authentication, and network issues
  - [x] 3.5 Add pagination support for directories with large file counts using list_folder/continue
  - [x] 3.6 Write unit tests for file listing with mocked Dropbox API responses
  - [x] 3.7 Add integration tests with various directory scenarios (empty, large, permission denied)

- [x] 4.0 Implement PreviousReportDetectionWorkflow
  - [x] 4.1 Create `PreviousReportDetectionWorkflow` class inheriting from `WorkflowBase`
  - [x] 4.2 Implement `_create_default_identity()` with workflow_type "previous_report_detection"
  - [x] 4.3 Implement `validate_inputs()` to check OrderItemData, report_directory_path, and DropboxService availability
  - [x] 4.4 Implement `execute()` method with directory file listing and pattern matching logic
  - [x] 4.5 Add regex pattern matching using `.*[Mm]aster [Dd]ocuments.*` for case-insensitive detection
  - [x] 4.6 Update `OrderItemData.previous_report_found` with boolean result (true/false/null)
  - [x] 4.7 Add comprehensive error handling for Dropbox API errors and directory access issues
  - [x] 4.8 Write unit tests for workflow logic with mocked DropboxService and various file scenarios
  - [x] 4.9 Add test cases for pattern matching with different filename variations and edge cases

- [x] 5.0 Add Workflow Integration and Testing
  - [x] 5.1 Register PreviousReportDetectionWorkflow with WorkflowExecutor in workflow system
  - [x] 5.2 Add workflow import and export to `src/core/workflows/__init__.py`
  - [x] 5.3 Create integration tests for complete workflow execution with mock Dropbox data
  - [x] 5.4 Add end-to-end test scenarios combining LeaseDirectorySearchWorkflow and PreviousReportDetectionWorkflow
  - [x] 5.5 Test workflow orchestration scenarios with both successful and failed directory searches
  - [x] 5.6 Validate error handling and graceful degradation when directory access fails
  - [x] 5.7 Add performance testing for file listing with large directories (100+ files)
  - [x] 5.8 Update workflow framework documentation with PreviousReportDetectionWorkflow usage examples