# Tasks: Processors Deprecation and Workflow System Implementation

## Relevant Files

- `src/core/processors.py` - Current monolithic processor code that needs to be renamed to legacy_processors.py
- `src/core/legacy_processors.py` - Renamed legacy code preserved for reference and testing
- `src/core/utils/lease_parsing.py` - New utility module for extracted lease number processing logic
- `src/core/services/__init__.py` - New services package initialization
- `src/core/services/excel_parser.py` - Service to parse Excel files into OrderItemData instances
- `src/core/services/workflow_orchestrator.py` - Service to execute workflows in sequence for order items
- `src/core/services/excel_exporter.py` - Service to convert processed data back to Excel format
- `src/core/services/order_processor.py` - Main service that coordinates the entire processing pipeline
- `app.py` - GUI application that needs integration with new services and progress feedback
- `tests/core/services/` - Test directory for new service modules
- `tests/core/services/test_excel_parser.py` - Unit tests for Excel parser service
- `tests/core/services/test_workflow_orchestrator.py` - Unit tests for workflow orchestrator
- `tests/core/services/test_excel_exporter.py` - Unit tests for Excel exporter service
- `tests/core/services/test_order_processor.py` - Integration tests for main order processor

### Notes

- All new services should be kept minimal with the bare minimum lines of code
- Leverage existing utilities from `src/core/utils/` instead of creating new ones
- Use existing workflow framework and data models without additional abstractions
- Unit tests should verify functionality but remain simple and focused

## Tasks

- [ ] 1.0 Rename Legacy Code and Extract Utilities
  - [ ] 1.1 Rename `src/core/processors.py` to `src/core/legacy_processors.py`
  - [ ] 1.2 Extract lease number parsing logic from legacy processors into `src/core/utils/lease_parsing.py`
  - [ ] 1.3 Update any imports that reference the old processors file (if any exist)
  - [ ] 1.4 Add deprecation warnings/comments to legacy_processors.py

- [ ] 2.0 Create Excel Parser Service
  - [ ] 2.1 Create `src/core/services/` directory and `__init__.py`
  - [ ] 2.2 Implement `src/core/services/excel_parser.py` with single `parse_excel_to_order_items()` function
  - [ ] 2.3 Map Excel columns to OrderItemData fields using pandas operations
  - [ ] 2.4 Handle agency-specific column differences (NMSLO vs Federal)
  - [ ] 2.5 Add basic input validation and error handling
  - [ ] 2.6 Create unit tests in `tests/core/services/test_excel_parser.py`

- [ ] 3.0 Create Workflow Orchestrator Service
  - [ ] 3.1 Implement `src/core/services/workflow_orchestrator.py` with minimal orchestration logic
  - [ ] 3.2 Execute LeaseDirectorySearchWorkflow for each OrderItemData instance
  - [ ] 3.3 Execute PreviousReportDetectionWorkflow after directory search completes
  - [ ] 3.4 Handle workflow errors gracefully without stopping other order items
  - [ ] 3.5 Return updated OrderItemData instances with workflow results
  - [ ] 3.6 Create unit tests in `tests/core/services/test_workflow_orchestrator.py`

- [ ] 4.0 Create Excel Exporter Service
  - [ ] 4.1 Implement `src/core/services/excel_exporter.py` using existing utilities
  - [ ] 4.2 Convert OrderItemData list to pandas DataFrame
  - [ ] 4.3 Add agency-specific columns using existing `BlankColumnManager` and `ColumnManager`
  - [ ] 4.4 Apply formatting using existing `ExcelWriter.save_with_formatting()`
  - [ ] 4.5 Generate output filename using existing `FilenameGenerator`
  - [ ] 4.6 Create unit tests in `tests/core/services/test_excel_exporter.py`

- [ ] 5.0 Update GUI Integration and Add Progress Feedback
  - [ ] 5.1 Create `src/core/services/order_processor.py` as main coordinator service
  - [ ] 5.2 Remove "Generate Lease Folders" and "Add Dropbox Links" options from GUI
  - [ ] 5.3 Add simple progress feedback window with basic status updates
  - [ ] 5.4 Update `process_order()` function in `app.py` to use new service layer
  - [ ] 5.5 Replace legacy processor instantiation with new OrderProcessingService
  - [ ] 5.6 Add basic error handling and user-friendly error messages
  - [ ] 5.7 Test end-to-end functionality with both NMSLO and Federal sample files