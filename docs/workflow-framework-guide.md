# Workflow Framework Developer Guide

## Overview

The Workflow Framework provides a flexible, extensible architecture for implementing data collection and automation workflows. Built on SOLID principles, it enables modular development of business logic while maintaining consistency and testability.

## Architecture Principles

### 1. **Separation of Concerns**
- **Workflows**: Business logic implementation
- **Executor**: Orchestration and lifecycle management  
- **Configuration**: External settings and behavior
- **Results**: Structured output handling

### 2. **Dependency Injection**
All external dependencies (DropboxService, configurations) are injected, enabling:
- Easy testing with mocks
- Runtime behavior modification
- Service swapping without code changes

### 3. **Abstract Base Classes**
`WorkflowBase` defines the contract all workflows must implement:
- `validate_inputs()`: Input validation
- `execute()`: Main business logic
- `_create_default_identity()`: Workflow identification

### 4. **Fail-Safe Design**
- Errors are contained within workflows
- Structured error results prevent crashes
- Graceful degradation when services are unavailable

## Core Components

### WorkflowBase
Abstract base class providing the fundamental workflow contract.

```python
from src.core.workflows.base import WorkflowBase, WorkflowConfig, WorkflowIdentity

class MyWorkflow(WorkflowBase):
    def _create_default_identity(self) -> WorkflowIdentity:
        return WorkflowIdentity(
            workflow_type="my_workflow",
            workflow_name="My Custom Workflow"
        )
    
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        # Implement validation logic
        if "required_field" not in input_data:
            return False, "required_field is missing"
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement main workflow logic
        result = self.do_work(input_data)
        return {
            "success": True,
            "data": result,
            "message": "Workflow completed successfully"
        }
```

### WorkflowExecutor
Manages workflow lifecycle, registration, and execution.

```python
from src.core.workflows import WorkflowExecutor, MyWorkflow

# Create executor
executor = WorkflowExecutor()

# Register workflow types
executor.register_workflow_type("my_workflow", MyWorkflow)

# Create workflow instance
workflow = executor.create_workflow("my_workflow")

# Execute workflow
input_data = {"required_field": "value"}
result = executor.execute_workflow(workflow, input_data)
```

## Usage Examples

### Example 1: Simple Data Processing Workflow

```python
from typing import Dict, Any, Optional
from src.core.workflows.base import WorkflowBase, WorkflowIdentity

class DataValidationWorkflow(WorkflowBase):
    """Validates data against business rules."""
    
    def _create_default_identity(self) -> WorkflowIdentity:
        return WorkflowIdentity(
            workflow_type="data_validation",
            workflow_name="Data Validation Workflow"
        )
    
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if "data" not in input_data:
            return False, "data field is required"
        if not isinstance(input_data["data"], dict):
            return False, "data must be a dictionary"
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        data = input_data["data"]
        
        validation_results = {
            "valid_fields": [],
            "invalid_fields": [],
            "warnings": []
        }
        
        # Perform validation logic
        for field, value in data.items():
            if self._is_valid_field(field, value):
                validation_results["valid_fields"].append(field)
            else:
                validation_results["invalid_fields"].append(field)
        
        return {
            "success": True,
            "validation_results": validation_results,
            "total_fields": len(data),
            "valid_count": len(validation_results["valid_fields"])
        }
    
    def _is_valid_field(self, field: str, value: Any) -> bool:
        # Implement field validation logic
        return value is not None and str(value).strip() != ""
```

### Example 2: External Service Integration Workflow

```python
class FileProcessingWorkflow(WorkflowBase):
    """Processes files with external service integration."""
    
    def __init__(self, config: WorkflowConfig = None, file_service=None):
        super().__init__(config)
        self.file_service = file_service
    
    def _create_default_identity(self) -> WorkflowIdentity:
        return WorkflowIdentity(
            workflow_type="file_processing",
            workflow_name="File Processing Workflow"
        )
    
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if not self.file_service:
            return False, "File service not configured"
        
        if "file_path" not in input_data:
            return False, "file_path is required"
        
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        file_path = input_data["file_path"]
        
        try:
            # Process file using external service
            processed_data = self.file_service.process_file(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "processed_data": processed_data,
                "processing_time": processed_data.get("processing_time", 0)
            }
            
        except Exception as e:
            # Let executor handle the error
            raise e
```

### Example 3: Using WorkflowExecutor Factory Pattern

```python
from src.core.workflows import WorkflowExecutor

def setup_workflow_system():
    """Initialize the workflow system with all available workflows."""
    executor = WorkflowExecutor()
    
    # Register all workflow types
    executor.register_workflow_type("lease_directory_search", LeaseDirectorySearchWorkflow)
    executor.register_workflow_type("data_validation", DataValidationWorkflow)
    executor.register_workflow_type("file_processing", FileProcessingWorkflow)
    
    return executor

def process_order_workflow(executor: WorkflowExecutor, order_data):
    """Example of processing an order through multiple workflows."""
    
    # Step 1: Validate order data
    validation_workflow = executor.create_workflow("data_validation")
    validation_result = executor.execute_workflow(
        validation_workflow, 
        {"data": order_data}
    )
    
    if not validation_result["success"]:
        return {"error": "Order validation failed", "details": validation_result}
    
    # Step 2: Search for lease directory
    search_workflow = executor.create_workflow("lease_directory_search")
    # Configure with DropboxService
    search_workflow.set_dropbox_service(dropbox_service)
    
    search_result = executor.execute_workflow(
        search_workflow,
        {"order_item_data": order_data}
    )
    
    return {
        "validation": validation_result,
        "directory_search": search_result,
        "overall_success": validation_result["success"] and search_result["success"]
    }
```

## Configuration Management

### Workflow-Specific Settings

```python
from src.core.workflows.base import WorkflowConfig

# Create configuration
config = WorkflowConfig(settings={
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "enable_caching": True,
    "validation_rules": {
        "required_fields": ["agency", "lease_number"],
        "max_lease_length": 50
    }
})

# Use in workflow
workflow = MyWorkflow(config=config)

# Access settings in workflow
class MyWorkflow(WorkflowBase):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        timeout = self.config.get_setting("timeout_seconds", 60)
        retry_attempts = self.config.get_setting("retry_attempts", 1)
        
        # Use configuration in logic
        return self.process_with_config(input_data, timeout, retry_attempts)
```

## Error Handling Patterns

### Workflow-Level Error Handling

```python
class RobustWorkflow(WorkflowBase):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Main workflow logic
            result = self.do_complex_operation(input_data)
            
            return {
                "success": True,
                "data": result
            }
            
        except AuthenticationError as e:
            # Re-raise authentication errors for executor to handle
            raise e
            
        except ValidationError as e:
            # Handle validation errors gracefully
            self.logger.warning(f"Validation failed: {e}")
            return {
                "success": False,
                "error": "Data validation failed",
                "details": str(e)
            }
            
        except Exception as e:
            # Let executor handle unexpected errors
            raise e
```

### Executor Error Handling

The `WorkflowExecutor` automatically handles errors and returns structured results:

```python
result = executor.execute_workflow(workflow, input_data)

# Result structure for successful execution:
{
    "success": True,
    "workflow_id": "lease_directory_search_a1b2c3d4e5",
    "workflow_type": "lease_directory_search",
    "data": { /* workflow-specific results */ },
    "execution_time_seconds": 2.34,
    "timestamp": "2024-01-15T10:30:45.123456"
}

# Result structure for failed execution:
{
    "success": False,
    "workflow_id": "lease_directory_search_a1b2c3d4e5",
    "workflow_type": "lease_directory_search",
    "data": None,
    "error": "Authentication failed",
    "error_type": "DropboxAuthenticationError",
    "context": { /* error context */ },
    "timestamp": "2024-01-15T10:30:45.123456"
}
```

## Testing Strategies

### Unit Testing Workflows

```python
import pytest
from unittest.mock import Mock, patch
from src.core.workflows.my_workflow import MyWorkflow

class TestMyWorkflow:
    def test_successful_execution(self):
        workflow = MyWorkflow()
        input_data = {"required_field": "test_value"}
        
        result = workflow.execute(input_data)
        
        assert result["success"] is True
        assert "data" in result
    
    def test_validation_failure(self):
        workflow = MyWorkflow()
        
        is_valid, error = workflow.validate_inputs({})
        
        assert is_valid is False
        assert "required_field" in error
    
    @patch('src.integrations.external_service.ExternalService')
    def test_with_mocked_service(self, mock_service):
        mock_service.do_something.return_value = "mocked_result"
        
        workflow = MyWorkflow(external_service=mock_service)
        result = workflow.execute({"required_field": "value"})
        
        assert result["success"] is True
        mock_service.do_something.assert_called_once()
```

### Integration Testing with Executor

```python
def test_workflow_integration():
    executor = WorkflowExecutor()
    executor.register_workflow_type("my_workflow", MyWorkflow)
    
    workflow = executor.create_workflow("my_workflow")
    input_data = {"required_field": "test_value"}
    
    result = executor.execute_workflow(workflow, input_data)
    
    assert result["success"] is True
    assert result["workflow_type"] == "my_workflow"
    assert "execution_time_seconds" in result
```

## Best Practices

### 1. **Input Validation**
- Always validate inputs thoroughly in `validate_inputs()`
- Return descriptive error messages
- Check for required dependencies (services, configuration)

### 2. **Error Handling**
- Let the executor handle unexpected errors
- Handle known error types gracefully within workflows
- Use structured logging for debugging

### 3. **Configuration**
- Use `WorkflowConfig` for workflow-specific settings
- Provide sensible defaults
- Document all configuration options

### 4. **Dependency Injection**
- Inject all external services through constructor
- Support None values for testing scenarios
- Validate service availability in `validate_inputs()`

### 5. **Result Structure**
- Always return a dictionary with consistent structure
- Include success status, data, and descriptive messages
- Provide enough detail for debugging

### 6. **Logging**
- Use the workflow's logger (`self.logger`)
- Log important operations and state changes
- Include workflow ID in log messages for traceability

## Extension Guidelines

### Adding New Workflows

1. **Create Workflow Class**
   ```python
   class NewWorkflow(WorkflowBase):
       # Implement required methods
   ```

2. **Register with Executor**
   ```python
   executor.register_workflow_type("new_workflow", NewWorkflow)
   ```

3. **Write Tests**
   - Unit tests for workflow logic
   - Integration tests with executor
   - Mock external dependencies

4. **Document Usage**
   - Add examples to this guide
   - Document configuration options
   - Include error scenarios

### Extending Existing Workflows

1. **Inheritance**
   ```python
   class ExtendedLeaseSearchWorkflow(LeaseDirectorySearchWorkflow):
       def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
           # Add pre-processing
           enhanced_input = self.enhance_input(input_data)
           
           # Call parent implementation
           result = super().execute(enhanced_input)
           
           # Add post-processing
           return self.enhance_result(result)
   ```

2. **Configuration Override**
   ```python
   config = WorkflowConfig(settings={
       "enhanced_mode": True,
       "additional_validation": True
   })
   workflow = ExtendedLeaseSearchWorkflow(config=config)
   ```

## Troubleshooting

### Common Issues

1. **Workflow Registration Errors**
   - Ensure workflow class is imported
   - Check that class inherits from `WorkflowBase`
   - Verify all abstract methods are implemented

2. **Validation Failures**
   - Check input data structure
   - Verify required services are available
   - Review workflow-specific requirements

3. **Execution Errors**
   - Check executor logs for detailed error information
   - Verify external service authentication
   - Ensure all dependencies are properly injected

### Debugging Tips

1. **Enable Debug Logging**
   ```python
   import logging
   logging.getLogger('src.core.workflows').setLevel(logging.DEBUG)
   ```

2. **Use Workflow Info**
   ```python
   info = workflow.get_workflow_info()
   print(f"Workflow: {info['identity']['workflow_name']}")
   print(f"Config: {info['config']}")
   ```

3. **Test in Isolation**
   ```python
   # Test validation separately
   is_valid, error = workflow.validate_inputs(test_data)
   
   # Test execution with minimal data
   result = workflow.execute(minimal_valid_data)
   ```

## Future Enhancements

The framework is designed to support future enhancements:

- **Workflow Chaining**: Sequential execution of related workflows
- **Parallel Execution**: Concurrent execution of independent workflows  
- **Workflow Templates**: Pre-configured workflow combinations
- **Event System**: Pub/sub notifications for workflow events
- **Metrics Collection**: Performance and success rate tracking
- **Workflow Scheduling**: Time-based or event-triggered execution

---

*This framework follows the principle of "start simple, grow complex" - begin with basic workflows and gradually add sophistication as requirements evolve.*