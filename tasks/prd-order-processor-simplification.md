# PRD: OrderProcessorService Simplification

## Introduction/Overview

This refactoring aims to ensure the `OrderProcessorService` class only handles downstream processing from the GUI, taking standardized data and orchestrating the creation of complete `OrderData`/`OrderItemData` objects. Currently, GUI validation logic exists in `app.py` and the service has some overengineered elements. The goal is to establish clear separation between GUI concerns and business logic while removing redundant code and improving maintainability.

## Goals

1. **Establish Clear Boundaries**: Ensure OrderProcessorService only handles downstream processing from GUI
2. **Standardize Data Input**: Service should receive standardized, validated data and orchestrate order creation
3. **Remove Redundant Code**: Eliminate the `process_order_end_to_end()` convenience function
4. **Maintain SOLID/DRY Principles**: Ensure single responsibility and avoid code duplication
5. **Preserve Functionality**: Keep all existing behavior intact during refactoring

## User Stories

- **As a developer maintaining the codebase**, I want a simplified service class so that I can easily understand and modify the order processing logic
- **As a developer adding new features**, I want clean separation of concerns so that I can extend functionality without touching unrelated code
- **As a code reviewer**, I want consistent patterns so that I can quickly verify correctness and adherence to coding standards

## Functional Requirements

1. **Remove Redundant Function**: The system must eliminate the `process_order_end_to_end()` convenience function that duplicates class functionality
2. **Maintain Core Processing**: The system must preserve all existing order processing capabilities through the main `OrderProcessorService` class  
3. **Keep Business Logic Mapping**: The system must retain static methods (`create_order_data_from_form`, `map_agency_type`, `_map_order_type`) for converting GUI data to business objects
4. **Preserve Progress Callback**: The system must maintain the `ProgressCallback` protocol for future extensibility
5. **Ensure Downstream Focus**: The service must only handle processing after receiving standardized data from GUI layer
6. **Maintain Complete Order Creation**: The service must orchestrate creation of complete `OrderData`/`OrderItemData` objects with all necessary data points

## Non-Goals (Out of Scope)

- Moving GUI validation logic from `app.py` to GUI layer (separate concern)
- Moving GUI mapping methods to GUI layer (these are business logic converters)
- Modifying `app.py` or other dependent files beyond removing redundant function usage
- Changing the `ProgressCallback` protocol implementation  
- Broader architectural changes beyond the identified overengineering
- Performance optimizations
- Adding new functionality

## Technical Considerations

- **Dependencies**: Ensure removal of `process_order_end_to_end()` doesn't affect any imports or usage
- **Class Structure**: Maintain existing `OrderProcessorService` constructor and public methods
- **Static Methods**: Keep `create_order_data_from_form()`, `map_agency_type()`, and `_map_order_type()` as they handle business logic conversion
- **Error Handling**: Preserve all existing error handling and validation logic
- **Type Hints**: Maintain all existing type annotations

## Success Metrics

1. **Reduced Line Count**: Eliminate approximately 28 lines of redundant code
2. **Simplified Interface**: Single entry point through `OrderProcessorService` class instead of both class and function
3. **Maintained Functionality**: All existing tests pass without modification
4. **Code Quality**: No introduction of new linting errors or violations
5. **Documentation Clarity**: Cleaner, more focused class responsibility

## Open Questions

- Should the convenience function removal be accompanied by inline documentation explaining the preferred usage pattern?
- Are there any hidden dependencies on `process_order_end_to_end()` that need to be identified before removal?