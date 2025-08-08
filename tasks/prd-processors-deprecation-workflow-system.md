# Product Requirements Document: Processors Deprecation and Workflow System Implementation

## Introduction/Overview

The current `processors.py` file contains monolithic, non-SOLID/DRY code that handles order processing for both NMSLO and Federal agencies. This feature will deprecate the existing processors and replace them with a clean, maintainable workflow-based system that leverages the new data models (`OrderData`/`OrderItemData`) and cloud-agnostic service architecture.

The goal is to transform the manual worksheet generation process into an automated data collection platform using established workflow patterns, while maintaining Excel input/output compatibility and providing better user feedback.

## Goals

1. **Deprecate Legacy Code**: Replace `processors.py` with a clean, SOLID/DRY architecture
2. **Implement Workflow System**: Use existing workflow framework for lease directory search and previous report detection
3. **Improve Maintainability**: Create modular, testable services that follow established design patterns
4. **Enhance User Experience**: Add progress feedback window for workflow execution
5. **Enable Future Expansion**: Design system to easily accommodate additional workflows
6. **HIGHEST PRIORITY - Minimize Code Complexity**: Write the simplest possible code with the bare minimum number of lines - NO OVERENGINEERING

## User Stories

**As a user processing an order**, I want to:
- Upload an Excel file and have the system automatically process it using workflows
- See progress feedback during processing so I know the system is working
- Receive a formatted Excel output with populated workflow data
- Have the same reliable experience regardless of agency type (NMSLO/Federal)

**As a developer maintaining the system**, I want to:
- Work with clean, modular code that follows SOLID principles
- Easily add new workflows without modifying existing code
- Test individual components in isolation
- Understand the flow from GUI → Services → Workflows → Output

**As a system administrator**, I want to:
- Have confidence that deprecated code is safely archived
- Know that the new system uses the modern cloud-agnostic architecture
- Trust that error handling prevents system crashes

## Functional Requirements

### Core System Architecture

1. **Service Layer Creation**: The system must create a service layer that bridges the GUI and workflow system
2. **Excel Parser Service**: The system must parse uploaded Excel files into `OrderItemData` instances
3. **Workflow Orchestrator**: The system must execute workflows in sequence for each order item
4. **Excel Exporter Service**: The system must convert processed data back to formatted Excel files
5. **Progress Feedback**: The system must provide a GUI window showing minimal processing feedback

### Data Processing

6. **Data Model Integration**: The system must use `OrderData` and `OrderItemData` classes as the primary data structures
7. **Agency Support**: The system must support both NMSLO and Federal agency processing
8. **Column Mapping**: The system must map only columns that correspond to data class fields (no legacy unused columns)
9. **Cloud Integration**: The system must use the new cloud-agnostic service architecture with Dropbox implementation

### Workflow Execution

10. **Lease Directory Search**: The system must execute `LeaseDirectorySearchWorkflow` for each order item
11. **Previous Report Detection**: The system must execute `PreviousReportDetectionWorkflow` for each order item
12. **Sequential Processing**: The system must execute workflows in the correct dependency order (directory search before report detection)
13. **Error Isolation**: The system must continue processing other order items if one fails

### GUI Updates

14. **Option Removal**: The system must remove "Generate Lease Folders" and "Add Dropbox Links" options (now standard)
15. **Progress Window**: The system must add a progress feedback window with minimal, user-friendly status updates
16. **Error Display**: The system must show user-friendly error messages for processing failures

### Legacy Code Management

17. **File Renaming**: The system must rename `processors.py` to `legacy_processors.py`
18. **Utility Extraction**: The system must extract reusable logic (e.g., lease number processing) into utility classes
19. **Code Preservation**: The system must preserve legacy code for testing and reference during transition

## Non-Goals (Out of Scope)

- **Folder Generation**: Automated folder creation in Dropbox (future feature)
- **Document Management**: Finding and moving documents to lease directories (future feature)
- **JSON Export**: Alternative output formats (future enhancement)
- **Advanced Error Recovery**: Sophisticated retry/recovery mechanisms (future improvement)
- **Performance Optimization**: Processing speed improvements (current performance is acceptable)
- **Batch Processing**: Multiple file processing in single operation (future feature)

## Design Considerations

### CRITICAL: Simplicity First
- **NO OVERENGINEERING**: Use the simplest possible approach with minimal code
- **Bare Minimum Lines**: Every line of code must be essential and purposeful
- **Direct Implementation**: Avoid complex abstractions unless absolutely necessary
- **Leverage Existing**: Use existing utilities and frameworks rather than creating new ones

### Service Architecture
- **OrderProcessingService**: Main orchestrator that coordinates all processing steps (keep minimal)
- **ExcelParserService**: Handles Excel-to-data-model conversion (simple pandas operations)
- **WorkflowOrchestrator**: Manages workflow execution and dependencies (basic sequential execution)
- **ExcelExporterService**: Handles data-model-to-Excel conversion (reuse existing utilities)

### Progress Feedback Window
- Simple modal dialog with progress indicators
- Minimal text updates: "Processing order items...", "Searching directories...", "Generating output..."
- Progress bar or spinner to indicate active processing
- Close automatically on completion or allow manual close on error

### Error Handling Strategy
- Basic try/catch with user-friendly error messages
- Continue processing remaining items when individual items fail
- Log detailed errors for debugging while showing simple messages to users

## Technical Considerations

- **SIMPLICITY MANDATE**: Every technical decision must prioritize minimal code and direct implementation
- **Dependencies**: Must use existing workflow framework (`src/core/workflows/`) - no additional abstractions
- **Cloud Service**: Must use `CloudOperations` protocol with new Dropbox implementation - direct usage only
- **Data Models**: Must use `OrderData`/`OrderItemData` from `src/core/models.py` - no wrapper classes
- **Utilities**: Must leverage existing utilities from `src/core/utils/` - avoid creating new utilities unless absolutely essential
- **Configuration**: Must use existing configuration system for agency-specific settings - no additional config layers
- **Code Philosophy**: If it can be done in 5 lines instead of 20, use 5 lines

## Success Metrics

1. **PARAMOUNT - Code Simplicity**: Minimum possible lines of code while maintaining functionality
2. **Code Quality**: Elimination of SOLID/DRY violations in order processing logic
3. **Maintainability**: Ability to add new workflows without modifying existing services
4. **User Experience**: Successful processing with helpful feedback for both NMSLO and Federal orders
5. **Compatibility**: Generated Excel files maintain same format and data as legacy system
6. **Architecture**: Clean separation between GUI, services, workflows, and cloud operations
7. **No Overengineering**: Code review must confirm no unnecessary abstractions or complexity

## Open Questions

1. Should the progress window be modal or allow users to continue other work?
2. What specific text messages should be shown during each processing phase?
3. Should we implement a "dry run" mode for testing workflows without cloud operations?
4. How should we handle partial failures (some workflows succeed, others fail for same order item)?
5. Should extracted utility functions be placed in existing `src/core/utils/` modules or new dedicated modules?

## Implementation Priority

**Phase 1 (High Priority)**:
- Service layer creation
- Excel parser and exporter services
- Basic workflow orchestration
- GUI integration and progress feedback

**Phase 2 (Medium Priority)**:
- Legacy code cleanup and utility extraction
- Enhanced error handling and user messaging
- Testing and validation against legacy output

**Phase 3 (Future Consideration)**:
- Additional workflow implementations
- Performance optimizations
- Advanced error recovery mechanisms