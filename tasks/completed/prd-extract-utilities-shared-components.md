# PRD: Extract Utilities & Shared Components (Phase 1)

## Introduction/Overview

This feature focuses on extracting duplicate code from the existing `NMStateOrderProcessor` and `FederalOrderProcessor` classes into reusable utility components. The current codebase contains significant code duplication that creates maintenance overhead when making changes, as developers must update the same logic in multiple places. This refactoring will create focused, single-responsibility utility classes that eliminate duplication and establish a foundation for future workflow types including external project management API integrations.

The goal is to improve code maintainability by eliminating duplicate logic while preserving all existing functionality through functionally equivalent (but not necessarily identical) output.

## Goals

1. **Eliminate Code Duplication**: Extract all duplicate code between State and Federal processors into reusable utilities
2. **Improve Maintainability**: Reduce maintenance overhead by consolidating common logic into single-responsibility classes  
3. **Enable Future Extensibility**: Create utilities generic enough to support future workflow types and external API integrations
4. **Maintain Functional Parity**: Ensure all existing functionality is preserved with functionally equivalent results
5. **Establish Testing Foundation**: Create comprehensive unit tests for all new utility components
6. **Reduce Complexity**: Decrease overall cyclomatic complexity and lines of code in processor classes

## User Stories

1. **As a developer**, I want to modify date cleaning logic in one place so that changes apply consistently across all processors without risk of missing updates.

2. **As a developer**, I want to add new Excel formatting options so that I can enhance all worksheets without duplicating code changes.

3. **As a developer**, I want to reuse data processing utilities so that I can quickly implement new workflow types (like Abstract processing) without rewriting common functionality.

4. **As a developer**, I want clear, focused utility classes so that I can understand and test individual components in isolation.

5. **As a developer**, I want to integrate external project management APIs so that I can leverage existing data processing utilities rather than creating duplicate logic.

## Functional Requirements

### FR1: Data Processing Utilities (`src/core/data_utils.py`)

1.1. **DataCleaner class** must provide a class method `clean_date_column()` that:
- Accepts a pandas DataFrame and column name as parameters
- Converts Excel serial dates to datetime objects
- Handles string date formats and converts to datetime
- Sets text values like "Inception" to None
- Returns the DataFrame with the specified column cleaned
- Raises ValueError for invalid DataFrame or column parameters

1.2. **ColumnManager class** must provide a class method `add_metadata_columns()` that:
- Accepts DataFrame and metadata values (agency, order_type, order_date, order_number)
- Adds ["Agency", "Order Type", "Order Number", "Order Date"] columns at the beginning
- Populates columns with provided metadata values
- Skips columns that already exist
- Returns the modified DataFrame
- Raises ValueError for invalid DataFrame parameter

1.3. **BlankColumnManager class** must provide a class method `add_blank_columns()` that:
- Accepts DataFrame and list of column names
- Adds empty columns with specified names to the end of the DataFrame
- Returns the modified DataFrame
- Raises ValueError for invalid parameters

### FR2: Excel Operations Utilities (`src/core/excel_utils.py`)

2.1. **WorksheetStyler class** must provide class methods for:
- `apply_standard_formatting()`: Apply Calibri 11pt font, left-aligned, wrap text formatting to all cells
- `apply_date_formatting()`: Apply "M/D/YYYY" format to specified date columns
- `apply_column_widths()`: Set column widths based on provided dictionary mapping
- `freeze_header_row()`: Freeze the top row for scrolling
- `add_auto_filter()`: Add auto-filter to the header row
- All methods must accept worksheet and data parameters and raise ValueError for invalid inputs

2.2. **ExcelWriter class** must provide a class method `save_with_formatting()` that:
- Accepts DataFrame, output path, and column widths dictionary
- Creates ExcelWriter with openpyxl engine
- Saves DataFrame to "Worksheet" sheet
- Applies all standard formatting through WorksheetStyler
- Closes writer properly
- Returns the output file path as string
- Raises IOError for file access issues

### FR3: Filename Utilities (`src/core/file_utils.py`)

3.1. **FilenameGenerator class** must provide a class method `generate_order_filename()` that:
- Accepts order_number, agency, and order_type parameters
- Creates filename format: "Order_{OrderNumber}_{Agency}_{OrderType}.xlsx"
- Defaults missing values to "Unknown"
- Sanitizes filename by replacing invalid characters with underscores
- Returns cleaned filename string
- Raises ValueError for invalid character encoding

### FR4: Search Column Utilities (`src/core/search_utils.py`)

4.1. **SearchColumnGenerator class** must provide class methods:
- `add_state_search_columns()`: Add "Full Search" and "Partial Search" columns using LeaseNumberParser
- `add_federal_search_columns()`: Add "Files Search" and "Tractstar Search" columns using LeaseNumberParser  
- Both methods accept DataFrame with "Lease" column and return modified DataFrame
- Raise ValueError if "Lease" column is missing

### FR5: Processor Integration

5.1. **Both existing processors** must be updated to use the new utility classes instead of duplicate code
5.2. **All processor functionality** must remain functionally equivalent after refactoring
5.3. **Error handling** must be preserved - utilities raise exceptions for caller to handle
5.4. **Import statements** must be added for new utility modules
5.5. **Naming Convention Update** must change all references from "NMState" to "NMSLO" throughout the codebase

## Non-Goals (Out of Scope)

- Changing the existing test suite or updating existing tests
- Implementing edge case handling (malformed Excel files, invalid date formats)
- Adding logging functionality to utilities (exceptions only)
- Performance optimization or requirements
- Modifying GUI code or external interfaces
- Changing existing file formats or column structures
- Implementing new features beyond extracting existing functionality

## Technical Considerations

- **Dependencies**: New utilities must work with existing pandas, openpyxl, and pathlib imports
- **Error Handling**: Utilities should raise appropriate exceptions (ValueError, IOError) for invalid inputs
- **Future Compatibility**: Design utilities to be generic enough for external PM API integration workflows
- **Testing Framework**: Use same testing approach as existing Dropbox integration tests
- **Module Structure**: Follow existing project structure with utilities in `src/core/` directory

## Success Metrics

### Code Quality Metrics
- **Lines of Code Reduction**: Eliminate at least 200+ lines of duplicate code from processors
- **Cyclomatic Complexity**: Reduce complexity of individual processor methods by 40%+ 
- **Code Duplication**: Zero identical code blocks between State and Federal processors
- **Test Coverage**: 100% unit test coverage for all new utility classes (excluding edge cases)

### Maintainability Metrics  
- **Single Point of Change**: Each type of processing logic (date cleaning, Excel formatting, etc.) modified in only one location
- **Component Isolation**: Each utility class testable independently without processor dependencies
- **Future Readiness**: Utilities usable by future workflow types without modification

### Functional Verification
- **Output Equivalence**: Refactored processors produce functionally equivalent Excel files to original implementation
- **Error Behavior**: Exception handling and error messages remain consistent with original behavior
- **Performance Parity**: No measurable performance degradation in worksheet generation

## Open Questions

1. Should the `LeaseNumberParser` class be moved to the search utilities module or remain in processors.py? yes or just a general utilities module
2. Are there any specific coding standards or naming conventions for utility classes that should be followed? No but I would like to change all references of NMSTate which is New Mexico State to NMSLO.
3. Should utility classes use class methods instead of static methods for better extensibility? Yes
4. What is the preferred approach for handling optional parameters in utility methods (None defaults vs required parameters)? Not sure