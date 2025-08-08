# Tasks: Processors Deprecation and Workflow System Implementation

## Relevant Files

- `src/core/processors.py` - Current monolithic processor code that needs to be renamed to legacy_processors.py
- `src/core/legacy_processors.py` - Renamed legacy code preserved for reference and testing (COMPLETED: renamed from processors.py, added deprecation warnings)
- `src/core/utils/parsing_utils.py` - Utility module containing lease number processing logic (ALREADY EXISTS: LeaseNumberParser and ParsedColumnGenerator classes)
- `src/core/services/__init__.py` - New services package initialization (COMPLETED: created with minimal content)
- `src/core/services/order_form_parser.py` - Service to parse order form files into OrderItemData instances (COMPLETED: single function, minimal code)
- `src/core/services/workflow_orchestrator.py` - Service to execute workflows in sequence for order items (COMPLETED: minimal orchestration class)
- `src/core/services/order_worksheet_exporter.py` - Service to convert processed data back to order worksheet format (COMPLETED: Strategy Pattern with LegacyFormatStrategy and MinimalFormatStrategy)
- `src/core/services/order_processor.py` - Main service that coordinates the entire processing pipeline (COMPLETED: clean coordinator with ProgressCallback protocol for GUI substitution)
- `app.py` - GUI application that needs integration with new services and progress feedback (COMPLETED: fully integrated with new OrderProcessorService, progress feedback, and cloud-agnostic service)
- `tests/core/services/` - Test directory for new service modules
- `tests/core/services/test_order_form_parser.py` - Unit tests for order form parser service (COMPLETED: basic tests for class and function)
- `tests/core/services/test_workflow_orchestrator.py` - Unit tests for workflow orchestrator
- `tests/core/services/test_order_worksheet_exporter.py` - Unit tests for order worksheet exporter service (COMPLETED: comprehensive tests for both strategies)
- `tests/core/services/test_order_processor.py` - Integration tests for main order processor (COMPLETED: basic integration tests for OrderProcessorService)

### Notes

- All new services should be kept minimal with the bare minimum lines of code
- Leverage existing utilities from `src/core/utils/` instead of creating new ones
- Use existing workflow framework and data models without additional abstractions
- Unit tests should verify functionality but remain simple and focused

## Tasks

- [x] 1.0 Rename Legacy Code and Extract Utilities
  - [x] 1.1 Rename `src/core/processors.py` to `src/core/legacy_processors.py`
  - [x] 1.2 Extract lease number parsing logic from legacy processors into `src/core/utils/lease_parsing.py`
  - [x] 1.3 Update any imports that reference the old processors file (if any exist)
  - [x] 1.4 Add deprecation warnings/comments to legacy_processors.py

- [x] 2.0 Create Order Form Parser Service
  - [x] 2.1 Create `src/core/services/` directory and `__init__.py`
  - [x] 2.2 Implement `src/core/services/order_form_parser.py` with single `parse_order_form_to_order_items()` function
  - [x] 2.3 Map Excel columns to OrderItemData fields using pandas operations
  - [x] 2.4 Handle agency-specific column differences (NMSLO vs Federal)
  - [x] 2.5 Add basic input validation and error handling
  - [x] 2.6 Create unit tests in `tests/core/services/test_order_form_parser.py`

- [x] 3.0 Create Workflow Orchestrator Service
  - [x] 3.1 Implement `src/core/services/workflow_orchestrator.py` with minimal orchestration logic
  - [x] 3.2 Execute LeaseDirectorySearchWorkflow for each OrderItemData instance
  - [x] 3.3 Execute PreviousReportDetectionWorkflow after directory search completes
  - [x] 3.4 Handle workflow errors gracefully without stopping other order items
  - [x] 3.5 Return updated OrderItemData instances with workflow results
  - [x] 3.6 Create unit tests in `tests/core/services/test_workflow_orchestrator.py`

- [x] 4.0 Create Order Worksheet Exporter Service
  - [x] 4.1 Implement `src/core/services/order_worksheet_exporter.py` using existing utilities
  - [x] 4.2 Convert OrderItemData list to pandas DataFrame
  - [x] 4.3 Add agency-specific columns using existing `BlankColumnManager` and `ColumnManager`
  - [x] 4.4 Apply formatting using existing `ExcelWriter.save_with_formatting()`
  - [x] 4.5 Generate output filename using existing `FilenameGenerator`
  - [x] 4.6 Create unit tests in `tests/core/services/test_order_worksheet_exporter.py`

- [x] 5.0 Update GUI Integration and Add Progress Feedback
  - [x] 5.1 Create `src/core/services/order_processor.py` as main coordinator service
  - [x] 5.2 Remove "Generate Lease Folders" and "Add Dropbox Links" options from GUI
  - [x] 5.3 Add simple progress feedback window with basic status updates
  - [x] 5.4 Update `process_order()` function in `app.py` to use new service layer
  - [x] 5.5 Replace legacy processor instantiation with new OrderProcessingService
  - [x] 5.6 Add basic error handling and user-friendly error messages
  - [x] 5.7 Test end-to-end functionality with both NMSLO and Federal sample files
  