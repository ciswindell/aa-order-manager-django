# Task List: Centralized Validation Service Architecture

## Relevant Files

- `src/core/validation/__init__.py` - Package exports and common validator imports
- `src/core/validation/protocols.py` - Validator protocol and ValidatorBase ABC
- `src/core/validation/messages.py` - Standardized validation message templates
- `src/core/validation/validators.py` - Concrete validator implementations (FormData, ExcelFile, etc.)
- `tests/core/validation/test_protocols.py` - Unit tests for protocols and base classes
- `tests/core/validation/test_messages.py` - Unit tests for message system
- `tests/core/validation/test_validators.py` - Unit tests for all validator implementations
- `app.py` - Main application file that needs validation logic refactored
- `src/core/models.py` - OrderData/OrderItemData models that need validator integration
- `src/core/services/order_form_parser.py` - Service that needs Excel validation integration
- `src/core/services/order_processor.py` - Service that may need validation integration

### Notes

- Unit tests should be placed in `tests/core/validation/` directory mirroring the source structure
- Use `python3 -m pytest tests/core/validation/` to run validation-specific tests
- Follow existing test patterns from `tests/core/test_models.py` for model integration tests

## Tasks

- [ ] 1.0 Create Core Validation Infrastructure
  - [ ] 1.1 Create `src/core/validation/` directory structure
  - [ ] 1.2 Implement Validator protocol in `protocols.py` with `validate(data) -> Tuple[bool, str]` interface
  - [ ] 1.3 Implement ValidatorBase ABC in `protocols.py` with shared functionality
  - [ ] 1.4 Create `__init__.py` with proper exports for protocols
  - [ ] 1.5 Write unit tests for protocols and base classes

- [ ] 2.0 Implement Message System
  - [ ] 2.1 Create MessageType enum in `messages.py` with USER_FRIENDLY and TECHNICAL categories
  - [ ] 2.2 Implement ValidationMessages class with template dictionaries for both message types
  - [ ] 2.3 Implement `format_message()` class method with parameter substitution
  - [ ] 2.4 Add message templates for common validation scenarios (required fields, type errors, file errors)
  - [ ] 2.5 Write comprehensive unit tests for message formatting and template coverage

- [ ] 3.0 Create Placeholder Validators
  - [ ] 3.1 Implement FormDataValidator stub with TODO comments for GUI form validation (agency, order type, file path)
  - [ ] 3.2 Implement ExcelFileValidator stub with TODO comments for file existence, accessibility, and type validation
  - [ ] 3.3 Implement OrderFormStructureValidator stub with TODO comments for DataFrame column validation
  - [ ] 3.4 Implement OrderDataValidator stub with TODO comments for OrderData business object validation
  - [ ] 3.5 Implement OrderItemDataValidator stub with TODO comments for OrderItemData business object validation
  - [ ] 3.6 Implement WorkflowInputValidator stub with TODO comments for workflow-specific validation base
  - [ ] 3.7 Implement BusinessRulesValidator stub with TODO comments for business logic validation
  - [ ] 3.8 Update `__init__.py` to export all validator classes
  - [ ] 3.9 Write basic unit test stubs for all validators that test the TODO implementation returns True

- [ ] 4.0 Integrate with Existing Services
  - [ ] 4.1 Integrate OrderDataValidator with `OrderData.__post_init__()` method
  - [ ] 4.2 Integrate OrderItemDataValidator with `OrderItemData.__post_init__()` method
  - [ ] 4.3 Integrate OrderFormStructureValidator with `OrderFormParser._validate_columns()` method
  - [ ] 4.4 Update existing services to use validation service instead of local validation logic
  - [ ] 4.5 Ensure all existing tests still pass after integration changes

- [ ] 5.0 Refactor app.py to Use Validation Service
  - [ ] 5.1 Import FormDataValidator, ExcelFileValidator, and BusinessRulesValidator in app.py
  - [ ] 5.2 Replace agency selection validation (lines 24-30) with FormDataValidator
  - [ ] 5.3 Replace order type validation (lines 32-38) with FormDataValidator  
  - [ ] 5.4 Replace Abstract workflow check (lines 40-45) with BusinessRulesValidator
  - [ ] 5.5 Replace order number format validation (lines 47-56) with FormDataValidator
  - [ ] 5.6 Replace file selection and validation (lines 58-95) with ExcelFileValidator
  - [ ] 5.7 Update error message handling to use validator return tuples instead of hardcoded messages
  - [ ] 5.8 Test that app.py functionality works identically after refactoring
  - [ ] 5.9 Verify app.py validation logic is reduced from ~70 lines to ~10 lines as per success metrics