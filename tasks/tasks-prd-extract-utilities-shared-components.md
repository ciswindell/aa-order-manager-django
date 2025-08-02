# Task List: Extract Utilities & Shared Components (Phase 1)

Based on PRD: `prd-extract-utilities-shared-components.md`

## Relevant Files

- `src/core/utils/__init__.py` - Utils package initialization with exports
- `src/core/utils/data_utils.py` - New module containing DataCleaner, ColumnManager, and BlankColumnManager utility classes
- `tests/core/test_data_utils.py` - Unit tests for data processing utilities
- `src/core/utils/excel_utils.py` - New module containing WorksheetStyler and ExcelWriter utility classes
- `tests/core/test_excel_utils.py` - Unit tests for Excel operation utilities
- `src/core/utils/file_utils.py` - New module containing FilenameGenerator utility class
- `tests/core/test_file_utils.py` - Unit tests for filename utilities
- `src/core/utils/parsing_utils.py` - New module containing ParsedColumnGenerator and moved LeaseNumberParser classes
- `tests/core/test_parsing_utils.py` - Unit tests for parsing utilities
- `src/core/processors.py` - Existing file to be refactored to use new utilities and update NMState to NMSLO
- `src/integrations/dropbox/service.py` - Existing file that may need NMState to NMSLO updates
- `src/integrations/dropbox/config.py` - Existing file that may need NMState to NMSLO updates

### Notes

- Unit tests should be placed in `/tests` directory mirroring source structure (e.g., `tests/core/` for `src/core/` modules)
- Use `python3 -m pytest [optional/path/to/test/file]` to run tests (following user's Linux python3 preference)
- All new utility classes use class methods instead of static methods for better extensibility
- Preserve existing functionality while eliminating code duplication between processors

## Tasks

- [x] 1.0 Create Data Processing Utilities Module
  - [x] 1.1 Create `src/core/utils/data_utils.py` with DataCleaner class and clean_date_column() class method
  - [x] 1.2 Implement ColumnManager class with add_metadata_columns() class method for adding Agency/Order metadata
  - [x] 1.3 Implement BlankColumnManager class with add_blank_columns() class method for adding empty columns
  - [x] 1.4 Add proper error handling with ValueError exceptions for invalid inputs
  - [x] 1.5 Add docstrings and type hints for all methods and classes

- [x] 2.0 Create Excel Operations Utilities Module
  - [x] 2.1 Create `src/core/utils/excel_utils.py` with WorksheetStyler class containing formatting class methods
  - [x] 2.2 Implement apply_standard_formatting() class method for Calibri 11pt, left-aligned, wrap text formatting
  - [x] 2.3 Implement apply_date_formatting() class method for "M/D/YYYY" date column formatting
  - [x] 2.4 Implement apply_column_widths(), freeze_header_row(), and add_auto_filter() class methods
  - [x] 2.5 Create ExcelWriter class with save_with_formatting() class method that orchestrates all formatting
  - [x] 2.6 Add proper error handling with ValueError and IOError exceptions

- [x] 3.0 Create Filename and Search Utilities Modules
  - [x] 3.1 Create `src/core/utils/file_utils.py` with FilenameGenerator class and generate_order_filename() class method
  - [x] 3.2 Implement filename sanitization and "Unknown" defaults for missing values
  - [x] 3.3 Create `src/core/utils/parsing_utils.py` and move LeaseNumberParser class from processors.py
  - [x] 3.4 Create ParsedColumnGenerator class with add_state_search_columns() and add_federal_search_columns() class methods
  - [x] 3.5 Ensure search methods properly use LeaseNumberParser for generating search terms

- [x] 4.0 Update Existing Processors to Use New Utilities
  - [x] 4.1 Update NMSLOOrderProcessor to import and use DataCleaner for date cleaning logic
  - [x] 4.2 Update FederalOrderProcessor to import and use DataCleaner for date cleaning logic
  - [x] 4.3 Replace duplicate metadata column logic in both processors with ColumnManager.add_metadata_columns()
  - [x] 4.4 Replace duplicate blank column logic in both processors with BlankColumnManager.add_blank_columns()
  - [x] 4.5 Replace duplicate Excel formatting and writing logic with ExcelWriter.save_with_formatting()
  - [x] 4.6 Replace generate_filename() method calls with FilenameGenerator.generate_order_filename()
  - [x] 4.7 Update search column generation to use ParsedColumnGenerator class methods
  - [x] 4.8 Change all "NMState" references to "NMSLO" throughout processors.py
  - [x] 4.9 Verify functional equivalence by testing with sample data files

- [x] 4.0 Update Existing Processors to Use New Utilities

- [ ] 5.0 Implement Comprehensive Unit Testing
  - [ ] 5.1 Create `/tests/core/` directory and `tests/core/__init__.py` file
  - [ ] 5.2 Create `tests/core/test_data_utils.py` with unit tests for DataCleaner.clean_date_column() with various date formats from `src/core/utils/data_utils.py`
  - [ ] 5.3 Add unit tests for ColumnManager.add_metadata_columns() including existing column handling scenarios
  - [ ] 5.4 Add unit tests for BlankColumnManager.add_blank_columns() with various column scenarios
  - [ ] 5.5 Create `tests/core/test_excel_utils.py` with unit tests for all WorksheetStyler class methods using mock worksheet objects
  - [ ] 5.6 Add unit tests for ExcelWriter.save_with_formatting() with mock file operations and error handling
  - [ ] 5.7 Create `tests/core/test_file_utils.py` with unit tests for FilenameGenerator.generate_order_filename() with various input combinations
  - [ ] 5.8 Create `tests/core/test_parsing_utils.py` with unit tests for ParsedColumnGenerator methods and moved LeaseNumberParser functionality
  - [ ] 5.9 Verify 100% test coverage for all new utility classes (excluding edge cases as per PRD)
  - [ ] 5.10 Run integration tests to ensure refactored processors produce equivalent output to original implementation 