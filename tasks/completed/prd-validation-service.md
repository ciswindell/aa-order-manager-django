# PRD: Centralized Validation Service Architecture

## Introduction/Overview

The current Order Manager application has validation logic scattered across multiple files (`app.py`, `models.py`, `order_form_parser.py`, workflow files), leading to code duplication and violation of DRY/SOLID principles. This feature will create a centralized, extensible validation service that consolidates all validation logic into a clean, protocol-based architecture.

**Problem:** Validation logic is duplicated between `app.py` (lines 24-95) and service layers, making the codebase harder to maintain and violating SOLID principles.

**Goal:** Create a centralized validation service that removes duplication, follows SOLID/DRY principles, and provides clear extension points for future validation needs.

## Goals

1. **Eliminate Duplication**: Remove duplicate validation logic from `app.py` and centralize it
2. **SOLID Compliance**: Create validation service following Single Responsibility and Open/Closed principles
3. **DRY Architecture**: Single source of truth for each type of validation
4. **Clean Extension**: Provide clear protocols for adding new validators without modifying existing code
5. **Maintain Simplicity**: Avoid overengineering while providing proper abstraction

## User Stories

**As a developer maintaining the codebase, I want:**
- A single place to find and modify validation logic so I don't have to hunt through multiple files
- Clear protocols for adding new validation rules so I can extend validation without breaking existing code
- Consistent validation interfaces so all services use the same patterns

**As the app.py layer, I want:**
- Simple validation calls that return clear success/error results so I can display appropriate messages to users
- Clean validation code that reduces the 70+ lines of validation logic currently in process_order()

**As service layers (OrderFormParser, etc.), I want:**
- Reusable validators that I can call from my business logic so I don't duplicate validation code
- Both exception-throwing and tuple-returning validation modes so I can handle errors appropriately

## Functional Requirements

### Core Validation Infrastructure
1. **Validator Protocol**: The system must define a `Validator` protocol with a standard `validate(data) -> Tuple[bool, str]` interface
2. **ValidatorBase ABC**: The system must provide an optional abstract base class for validators that need shared functionality
3. **Message System**: The system must provide standardized validation message templates with two categories:
   - **User-friendly messages**: Clear, actionable messages for GUI display
   - **Technical messages**: Precise, structured messages for business logic and debugging

### Placeholder Validators (Implementation Stubs)
4. **FormDataValidator**: Must validate GUI form data (agency selection, order type, order number format, file path presence)
5. **ExcelFileValidator**: Must validate Excel file existence, accessibility, and file type
6. **OrderFormStructureValidator**: Must validate Excel DataFrame has required columns ("Lease", "Requested Legal")
7. **OrderDataValidator**: Must validate OrderData business objects (replaces `__post_init__` logic)
8. **OrderItemDataValidator**: Must validate OrderItemData business objects (replaces `__post_init__` logic)
9. **WorkflowInputValidator**: Must provide base for workflow-specific input validation
10. **BusinessRulesValidator**: Must validate business logic (Abstract workflow availability, etc.)

### Integration Points
11. **Model Integration**: The system must integrate with existing `__post_init__` methods in OrderData/OrderItemData
12. **Service Integration**: The system must be usable by OrderFormParser, OrderProcessor, and other services
13. **Error Handling**: The system must support both tuple returns and exception throwing based on usage context

## Non-Goals (Out of Scope)

- **Composite Validators**: No complex validator combination logic (can be added later if needed)
- **Complex Validation Rules**: No advanced validation like cross-field dependencies or async validation
- **Localization**: No multi-language error message support
- **Configuration-Based Validation**: No external config files for validation rules
- **Performance Optimization**: No caching or optimization features in initial implementation
- **UI Validation**: No client-side or real-time validation features

## Design Considerations

### File Structure
```
src/core/validation/
├── __init__.py           # Exports and common validators
├── protocols.py          # Validator protocol and base class
├── messages.py           # Standardized validation message templates
└── validators.py         # Concrete validator implementations
```

### Protocol Design
- Use Python `Protocol` for duck typing support
- Keep interface simple: `validate(data) -> Tuple[bool, str]`
- Provide optional `ValidatorBase` ABC for shared functionality

### Message Standardization
- **Two-tier message system**: User-friendly messages for GUI display, technical messages for business logic
- **Template-based formatting**: Centralized message templates with parameter substitution
- **Message categories**: Required field, invalid format, file errors, business rules, type errors, constraint violations
- **Consistent patterns**: "Please {action} {requirement}" for user messages, "{field} must be {type}" for technical messages

### Integration Pattern
```python
# Models will call validators in __post_init__
def __post_init__(self):
    validator = OrderDataValidator()
    is_valid, error = validator.validate(self)
    if not is_valid:
        raise ValueError(error)

# Services will use direct validation calls
validator = FormDataValidator()
is_valid, error = validator.validate(form_data)
if not is_valid:
    messagebox.showwarning("Validation Error", error)
    return
```

## Technical Considerations

### Dependencies
- Builds on existing `src/core/` structure following established patterns
- Uses same typing patterns as existing codebase (`typing.Protocol`, `ABC`)
- Integrates with existing exception handling in services

### Architecture Alignment
- Follows same pattern as `WorkflowBase` ABC for consistency
- Uses protocol-based design like cloud integration layer
- Maintains existing error handling patterns

### Implementation Strategy
- **Phase 1**: Create protocol and placeholder validators with comprehensive TODO comments
- **Phase 2**: Implement core validators (FormData, ExcelFile, OrderForm) to remove app.py duplication
- **Phase 3**: Integrate with existing services and refactor model validation

### Placeholder Implementation Notes
Each validator will be created as a stub with detailed implementation guidance:

```python
class FormDataValidator(ValidatorBase):
    """Validates GUI form data before processing.
    
    TODO: Implement validation for:
    - Agency selection (not "Select Agency")
    - Order type selection (not "Select Order Type") 
    - Order number format (alphanumeric + hyphens/underscores)
    - File path presence
    - Abstract workflow availability check
    
    Current logic location: app.py lines 24-56
    Message format: Use ValidationMessages.format_message() with USER_FRIENDLY type
    """
    
    def validate(self, form_data: Dict[str, Any]) -> Tuple[bool, str]:
        # TODO: Move validation logic from app.py process_order()
        # TODO: Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, ...)
        return True, ""

class ValidationMessages:
    """Centralized validation message templates.
    
    TODO: Implement message templates with two categories:
    - USER_FRIENDLY: For GUI display ("Please select an agency")
    - TECHNICAL: For business logic ("order_number must be string")
    
    Template format: Use {field}, {requirement}, {action} parameters
    """
    
    @classmethod
    def format_message(cls, message_type, template_key: str, **kwargs) -> str:
        # TODO: Implement template-based message formatting
        return "TODO: Implement message formatting"
```

## Success Metrics

1. **Code Reduction**: Reduce `app.py` validation logic from ~70 lines to ~10 lines
2. **Duplication Elimination**: Remove duplicate file validation between `app.py` and `OrderFormParser`
3. **Test Coverage**: Achieve 100% test coverage for all validator implementations
4. **Integration Success**: All existing functionality works after migration with no behavior changes
5. **SOLID Compliance**: Each validator has single responsibility, codebase follows Open/Closed principle

## Open Questions

1. **Validation Timing**: Should model validation happen in `__post_init__` or externally?
2. **Performance Impact**: Any performance concerns with adding validation layer to hot paths?
3. **Future Validation Needs**: What other validation types might be needed (API validation, file format validation)?
4. **Message Integration**: How should the message system integrate with future terminal display and logging systems?

---

**Note**: This PRD focuses on creating a solid foundation with placeholder implementations that can be filled in gradually, following the user's preference for avoiding overengineering while maintaining clean, extensible architecture.