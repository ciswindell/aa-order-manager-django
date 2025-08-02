"""
Unit tests for base workflow classes.

Tests the foundational workflow components: WorkflowConfig, WorkflowIdentity, and WorkflowBase.
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

from src.core.workflows.base import WorkflowConfig, WorkflowIdentity, WorkflowBase


class TestWorkflowConfig:
    """Test WorkflowConfig class."""
    
    def test_default_initialization(self):
        """Test WorkflowConfig initializes with empty settings."""
        config = WorkflowConfig()
        assert config.settings == {}
    
    def test_initialization_with_settings(self):
        """Test WorkflowConfig initializes with provided settings."""
        settings = {"timeout": 30, "retry": 3}
        config = WorkflowConfig(settings=settings)
        assert config.settings == settings
    
    def test_none_settings_converts_to_empty_dict(self):
        """Test that None settings gets converted to empty dict."""
        config = WorkflowConfig(settings=None)
        assert config.settings == {}


class TestWorkflowIdentity:
    """Test WorkflowIdentity class."""
    
    def test_initialization_with_all_fields(self):
        """Test WorkflowIdentity initializes with all provided fields."""
        identity = WorkflowIdentity(
            workflow_type="test_workflow",
            workflow_name="Test Workflow",
            workflow_id="test_123"
        )
        assert identity.workflow_type == "test_workflow"
        assert identity.workflow_name == "Test Workflow"
        assert identity.workflow_id == "test_123"
    
    def test_auto_id_generation(self):
        """Test that workflow_id is auto-generated when not provided."""
        with patch('time.time', return_value=1234567890):
            identity = WorkflowIdentity(
                workflow_type="test_workflow",
                workflow_name="Test Workflow"
            )
            assert identity.workflow_id == "test_workflow_1234567890"
    
    def test_empty_id_gets_generated(self):
        """Test that empty workflow_id gets auto-generated."""
        with patch('time.time', return_value=9876543210):
            identity = WorkflowIdentity(
                workflow_type="another_workflow",
                workflow_name="Another Workflow",
                workflow_id=""
            )
            assert identity.workflow_id == "another_workflow_9876543210"


class ConcreteWorkflow(WorkflowBase):
    """Concrete implementation of WorkflowBase for testing."""
    
    def _create_default_identity(self) -> WorkflowIdentity:
        return WorkflowIdentity(
            workflow_type="test_workflow",
            workflow_name="Test Workflow"
        )
    
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        if not input_data:
            return False, "Input data is required"
        if "required_field" not in input_data:
            return False, "required_field is missing"
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if input_data.get("should_fail"):
            raise ValueError("Simulated execution failure")
        
        return {
            "success": True,
            "result": f"Processed {input_data.get('data', 'default')}"
        }


class TestWorkflowBase:
    """Test WorkflowBase abstract class."""
    
    def test_initialization_with_default_config(self):
        """Test WorkflowBase initializes with default config."""
        workflow = ConcreteWorkflow()
        assert isinstance(workflow.config, WorkflowConfig)
        assert workflow.config.settings == {}
        assert isinstance(workflow.identity, WorkflowIdentity)
        assert workflow.identity.workflow_type == "test_workflow"
    
    def test_initialization_with_custom_config(self):
        """Test WorkflowBase initializes with provided config."""
        config = WorkflowConfig(settings={"custom": "value"})
        workflow = ConcreteWorkflow(config=config)
        assert workflow.config == config
        assert workflow.config.settings == {"custom": "value"}
    
    def test_validate_inputs_success(self):
        """Test validate_inputs returns True for valid input."""
        workflow = ConcreteWorkflow()
        input_data = {"required_field": "value", "other": "data"}
        
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_inputs_empty_data(self):
        """Test validate_inputs returns False for empty input."""
        workflow = ConcreteWorkflow()
        
        is_valid, error = workflow.validate_inputs({})
        assert is_valid is False
        assert error == "Input data is required"
    
    def test_validate_inputs_missing_required_field(self):
        """Test validate_inputs returns False for missing required field."""
        workflow = ConcreteWorkflow()
        input_data = {"other": "data"}
        
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert error == "required_field is missing"
    
    def test_execute_success(self):
        """Test execute returns success result."""
        workflow = ConcreteWorkflow()
        input_data = {"required_field": "value", "data": "test"}
        
        result = workflow.execute(input_data)
        assert result["success"] is True
        assert result["result"] == "Processed test"
    
    def test_execute_with_default_data(self):
        """Test execute with default data processing."""
        workflow = ConcreteWorkflow()
        input_data = {"required_field": "value"}
        
        result = workflow.execute(input_data)
        assert result["success"] is True
        assert result["result"] == "Processed default"
    
    def test_handle_errors_basic(self):
        """Test handle_errors creates proper error result."""
        workflow = ConcreteWorkflow()
        error = ValueError("Test error")
        
        result = workflow.handle_errors(error)
        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["error_type"] == "ValueError"
        assert result["workflow_id"] == workflow.identity.workflow_id
    
    def test_handle_errors_with_context(self):
        """Test handle_errors includes context in result."""
        workflow = ConcreteWorkflow()
        error = RuntimeError("Context error")
        context = {"step": "validation", "input": "test"}
        
        result = workflow.handle_errors(error, context)
        assert result["success"] is False
        assert result["error"] == "Context error"
        assert result["error_type"] == "RuntimeError"
        assert result["context"] == context
    
    def test_handle_errors_logs_error(self):
        """Test handle_errors logs the error properly."""
        workflow = ConcreteWorkflow()
        error = Exception("Logged error")
        
        with patch.object(workflow.logger, 'error') as mock_error:
            result = workflow.handle_errors(error)
            
            # Verify that the workflow's logger was called
            mock_error.assert_called_once()
            call_args = mock_error.call_args
            assert "Workflow failed: Logged error" in call_args[0][0]
            assert call_args[1]["exc_info"] is True


class TestWorkflowIntegration:
    """Integration tests for workflow components working together."""
    
    def test_full_workflow_lifecycle_success(self):
        """Test complete workflow lifecycle with successful execution."""
        config = WorkflowConfig(settings={"test": "setting"})
        workflow = ConcreteWorkflow(config=config)
        input_data = {"required_field": "value", "data": "integration_test"}
        
        # Validate inputs
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is True
        
        # Execute workflow
        result = workflow.execute(input_data)
        assert result["success"] is True
        assert result["result"] == "Processed integration_test"
    
    def test_full_workflow_lifecycle_validation_failure(self):
        """Test workflow lifecycle with validation failure."""
        workflow = ConcreteWorkflow()
        input_data = {"wrong_field": "value"}
        
        # Validate inputs
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert error == "required_field is missing"
        
        # Would not proceed to execution in real scenario
    
    def test_full_workflow_lifecycle_execution_failure(self):
        """Test workflow lifecycle with execution failure."""
        workflow = ConcreteWorkflow()
        input_data = {"required_field": "value", "should_fail": True}
        
        # Validate inputs
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is True
        
        # Execute workflow (should fail)
        with pytest.raises(ValueError, match="Simulated execution failure"):
            workflow.execute(input_data)
        
        # Handle the error
        error = ValueError("Simulated execution failure")
        result = workflow.handle_errors(error)
        assert result["success"] is False
        assert result["error"] == "Simulated execution failure"