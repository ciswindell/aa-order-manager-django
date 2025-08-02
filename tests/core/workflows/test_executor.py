"""
Unit tests for workflow executor.

Tests the WorkflowExecutor class including execution, error handling, and progress tracking.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.workflows.executor import WorkflowExecutor
from src.core.workflows.base import WorkflowBase, WorkflowConfig, WorkflowIdentity


class MockWorkflow(WorkflowBase):
    """Mock workflow for testing purposes."""
    
    def __init__(self, config: WorkflowConfig = None, should_fail_validation=False, should_fail_execution=False):
        super().__init__(config)
        self.should_fail_validation = should_fail_validation
        self.should_fail_execution = should_fail_execution
        self.execute_called = False
        self.validate_called = False
    
    def _create_default_identity(self) -> WorkflowIdentity:
        return WorkflowIdentity(
            workflow_type="mock_workflow",
            workflow_name="Mock Workflow"
        )
    
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        self.validate_called = True
        if self.should_fail_validation:
            return False, "Mock validation failure"
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.execute_called = True
        if self.should_fail_execution:
            raise RuntimeError("Mock execution failure")
        
        return {
            "success": True,
            "processed_data": input_data.get("data", "default"),
            "mock_result": "executed successfully"
        }


class TestWorkflowExecutor:
    """Test WorkflowExecutor class."""
    
    def test_initialization(self):
        """Test WorkflowExecutor initializes correctly."""
        executor = WorkflowExecutor()
        assert executor._progress_callbacks == []
        assert hasattr(executor, 'logger')
    
    def test_add_progress_callback(self):
        """Test adding progress callbacks."""
        executor = WorkflowExecutor()
        callback1 = Mock()
        callback2 = Mock()
        
        executor.add_progress_callback(callback1)
        executor.add_progress_callback(callback2)
        
        assert len(executor._progress_callbacks) == 2
        assert callback1 in executor._progress_callbacks
        assert callback2 in executor._progress_callbacks
    
    def test_execute_workflow_success(self):
        """Test successful workflow execution."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow()
        input_data = {"data": "test_input"}
        
        with patch('time.time', side_effect=[1000.0, 1002.5]):  # 2.5 seconds execution
            result = executor.execute_workflow(workflow, input_data)
        
        # Verify workflow methods were called
        assert workflow.validate_called is True
        assert workflow.execute_called is True
        
        # Verify result structure
        assert result["success"] is True
        assert result["workflow_id"] == workflow.identity.workflow_id
        assert result["workflow_type"] == "mock_workflow"
        assert result["execution_time_seconds"] == 2.5
        assert result["error"] is None
        assert isinstance(result["timestamp"], datetime)
        
        # Verify data was passed through
        assert result["data"]["processed_data"] == "test_input"
        assert result["data"]["mock_result"] == "executed successfully"
        
        # Verify executor metadata
        assert result["executor_metadata"]["executed_by"] == "WorkflowExecutor"
        assert result["executor_metadata"]["execution_mode"] == "single_workflow"
    
    def test_execute_workflow_validation_failure(self):
        """Test workflow execution with validation failure."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow(should_fail_validation=True)
        input_data = {"invalid": "data"}
        
        with patch('time.time', side_effect=[1000.0, 1000.1, 1000.1]):  # Provide extra values
            result = executor.execute_workflow(workflow, input_data)
        
        # Verify workflow validation was called but execution was not
        assert workflow.validate_called is True
        assert workflow.execute_called is False
        
        # Verify error result structure
        assert result["success"] is False
        assert result["workflow_id"] == workflow.identity.workflow_id
        assert result["workflow_type"] == "mock_workflow"
        assert abs(result["execution_time_seconds"] - 0.1) < 0.001  # Allow for floating point precision
        assert "Validation failed: Mock validation failure" in result["error"]
        assert result["error_type"] == "ValidationError"
        assert result["data"] is None
    
    def test_execute_workflow_execution_failure(self):
        """Test workflow execution with runtime failure."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow(should_fail_execution=True)
        input_data = {"data": "test_input"}
        
        with patch('time.time', side_effect=[1000.0, 1001.0, 1001.0, 1001.0]):  # Provide extra values for logging
            result = executor.execute_workflow(workflow, input_data)
        
        # Verify both validation and execution were attempted
        assert workflow.validate_called is True
        assert workflow.execute_called is True
        
        # Verify error result structure
        assert result["success"] is False
        assert result["workflow_id"] == workflow.identity.workflow_id
        assert result["execution_time_seconds"] == 1.0
        assert "Mock execution failure" in result["error"]
        assert result["error_type"] == "RuntimeError"
    
    def test_progress_tracking_success(self):
        """Test progress callbacks are called during successful execution."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow()
        input_data = {"data": "test"}
        
        # Add progress callbacks
        callback1 = Mock()
        callback2 = Mock()
        executor.add_progress_callback(callback1)
        executor.add_progress_callback(callback2)
        
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify callbacks were called with correct parameters
        expected_calls = [
            (workflow.identity.workflow_id, "started"),
            (workflow.identity.workflow_id, "completed")
        ]
        
        assert callback1.call_count == 2
        assert callback2.call_count == 2
        assert callback1.call_args_list == [((call[0], call[1]),) for call in expected_calls]
        assert callback2.call_args_list == [((call[0], call[1]),) for call in expected_calls]
    
    def test_progress_tracking_failure(self):
        """Test progress callbacks are called during failed execution."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow(should_fail_execution=True)
        input_data = {"data": "test"}
        
        callback = Mock()
        executor.add_progress_callback(callback)
        
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify callbacks were called with correct parameters
        expected_calls = [
            (workflow.identity.workflow_id, "started"),
            (workflow.identity.workflow_id, "failed")
        ]
        
        assert callback.call_count == 2
        assert callback.call_args_list == [((call[0], call[1]),) for call in expected_calls]
    
    def test_progress_callback_exception_handling(self):
        """Test that callback exceptions don't stop workflow execution."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow()
        input_data = {"data": "test"}
        
        # Add a callback that raises an exception
        failing_callback = Mock(side_effect=Exception("Callback failed"))
        working_callback = Mock()
        
        executor.add_progress_callback(failing_callback)
        executor.add_progress_callback(working_callback)
        
        with patch.object(executor.logger, 'warning') as mock_warning:
            result = executor.execute_workflow(workflow, input_data)
        
        # Verify workflow still completed successfully
        assert result["success"] is True
        
        # Verify working callback was still called
        assert working_callback.call_count == 2
        
        # Verify warning was logged for failing callback
        assert mock_warning.call_count == 2  # Called for both started and completed events
    
    def test_create_success_result(self):
        """Test _create_success_result method."""
        executor = WorkflowExecutor()
        
        data = {"result": "test_data"}
        result = executor._create_success_result(
            workflow_id="test_123",
            workflow_type="test_workflow",
            data=data,
            execution_time=1.5
        )
        
        assert result["success"] is True
        assert result["workflow_id"] == "test_123"
        assert result["workflow_type"] == "test_workflow"
        assert result["data"] == data
        assert result["error"] is None
        assert result["execution_time_seconds"] == 1.5
        assert isinstance(result["timestamp"], datetime)
        assert result["executor_metadata"]["executed_by"] == "WorkflowExecutor"
    
    def test_create_error_result(self):
        """Test _create_error_result method."""
        executor = WorkflowExecutor()
        
        result = executor._create_error_result(
            workflow_id="test_456",
            workflow_type="test_workflow",
            error="Test error message",
            error_type="TestError",
            execution_time=0.5
        )
        
        assert result["success"] is False
        assert result["workflow_id"] == "test_456"
        assert result["workflow_type"] == "test_workflow"
        assert result["data"] is None
        assert result["error"] == "Test error message"
        assert result["error_type"] == "TestError"
        assert result["execution_time_seconds"] == 0.5
        assert isinstance(result["timestamp"], datetime)
    
    def test_get_executor_info(self):
        """Test get_executor_info method."""
        executor = WorkflowExecutor()
        
        # Add some callbacks
        executor.add_progress_callback(Mock())
        executor.add_progress_callback(Mock())
        
        info = executor.get_executor_info()
        
        assert info["executor_type"] == "WorkflowExecutor"
        assert info["version"] == "1.0.0"
        assert "single_workflow_execution" in info["capabilities"]
        assert "input_validation" in info["capabilities"]
        assert "error_handling" in info["capabilities"]
        assert "progress_tracking" in info["capabilities"]
        assert "timing_metadata" in info["capabilities"]
        assert info["registered_callbacks"] == 2
    
    def test_logging_during_execution(self):
        """Test that appropriate logging occurs during execution."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow()
        input_data = {"data": "test"}
        
        with patch.object(executor.logger, 'info') as mock_info:
            result = executor.execute_workflow(workflow, input_data)
            
            # Verify executor logger was called
            assert mock_info.call_count >= 2  # Start and completion logs
            
            # Check log messages
            log_calls = mock_info.call_args_list
            start_log = log_calls[0][0][0]
            completion_log = log_calls[-1][0][0]
            
            assert "Starting workflow execution" in start_log
            assert workflow.identity.workflow_name in start_log
            assert "Workflow completed successfully" in completion_log
    
    def test_error_logging_during_failure(self):
        """Test that errors are properly logged during failure."""
        executor = WorkflowExecutor()
        workflow = MockWorkflow(should_fail_execution=True)
        input_data = {"data": "test"}
        
        with patch.object(executor.logger, 'error') as mock_error:
            result = executor.execute_workflow(workflow, input_data)
            
            # Verify error was logged
            mock_error.assert_called_once()
            error_call = mock_error.call_args
            assert "Workflow execution failed" in error_call[0][0]
            assert error_call[1]["exc_info"] is True


class TestWorkflowRegistration:
    """Test workflow registration system."""
    
    def test_register_workflow_type(self):
        """Test registering a workflow type."""
        executor = WorkflowExecutor()
        
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        assert executor.is_workflow_registered("mock_workflow")
        assert "mock_workflow" in executor.get_available_workflow_types()
    
    def test_register_duplicate_workflow_type_fails(self):
        """Test that registering duplicate workflow type fails."""
        executor = WorkflowExecutor()
        
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        with pytest.raises(ValueError, match="already registered"):
            executor.register_workflow_type("mock_workflow", MockWorkflow)
    
    def test_register_empty_workflow_type_fails(self):
        """Test that registering empty workflow type fails."""
        executor = WorkflowExecutor()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            executor.register_workflow_type("", MockWorkflow)
    
    def test_register_invalid_workflow_class_fails(self):
        """Test that registering non-WorkflowBase class fails."""
        executor = WorkflowExecutor()
        
        class NotAWorkflow:
            pass
        
        with pytest.raises(ValueError, match="must inherit from WorkflowBase"):
            executor.register_workflow_type("invalid", NotAWorkflow)
    
    def test_create_workflow_success(self):
        """Test creating a workflow instance."""
        executor = WorkflowExecutor()
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        workflow = executor.create_workflow("mock_workflow")
        
        assert isinstance(workflow, MockWorkflow)
        assert workflow.identity.workflow_type == "mock_workflow"
    
    def test_create_workflow_with_config(self):
        """Test creating a workflow instance with configuration."""
        executor = WorkflowExecutor()
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        config = {"timeout": 60, "custom_setting": "value"}
        workflow = executor.create_workflow("mock_workflow", config)
        
        assert isinstance(workflow, MockWorkflow)
        assert workflow.config.settings == config
    
    def test_create_unregistered_workflow_fails(self):
        """Test that creating unregistered workflow fails."""
        executor = WorkflowExecutor()
        
        with pytest.raises(ValueError, match="Unknown workflow type"):
            executor.create_workflow("nonexistent")
    
    def test_get_available_workflow_types(self):
        """Test getting available workflow types."""
        executor = WorkflowExecutor()
        
        # Initially empty
        assert executor.get_available_workflow_types() == []
        
        # Register some workflows
        executor.register_workflow_type("workflow_a", MockWorkflow)
        executor.register_workflow_type("workflow_b", MockWorkflow)
        
        available = executor.get_available_workflow_types()
        assert "workflow_a" in available
        assert "workflow_b" in available
        assert len(available) == 2
    
    def test_is_workflow_registered(self):
        """Test checking if workflow is registered."""
        executor = WorkflowExecutor()
        
        assert not executor.is_workflow_registered("mock_workflow")
        
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        assert executor.is_workflow_registered("mock_workflow")
        assert not executor.is_workflow_registered("other_workflow")
    
    def test_unregister_workflow_type(self):
        """Test unregistering a workflow type."""
        executor = WorkflowExecutor()
        
        # Register and verify
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        assert executor.is_workflow_registered("mock_workflow")
        
        # Unregister and verify
        result = executor.unregister_workflow_type("mock_workflow")
        assert result is True
        assert not executor.is_workflow_registered("mock_workflow")
        
        # Try unregistering again
        result = executor.unregister_workflow_type("mock_workflow")
        assert result is False
    
    def test_executor_info_includes_registry(self):
        """Test that executor info includes registry information."""
        executor = WorkflowExecutor()
        
        # Initially empty
        info = executor.get_executor_info()
        assert "workflow_registration" in info["capabilities"]
        assert "workflow_creation" in info["capabilities"]
        assert info["registered_workflows"] == []
        assert info["workflow_count"] == 0
        
        # Register workflows
        executor.register_workflow_type("workflow_a", MockWorkflow)
        executor.register_workflow_type("workflow_b", MockWorkflow)
        
        info = executor.get_executor_info()
        assert len(info["registered_workflows"]) == 2
        assert info["workflow_count"] == 2
        assert "workflow_a" in info["registered_workflows"]
        assert "workflow_b" in info["registered_workflows"]


class TestWorkflowExecutorIntegration:
    """Integration tests for WorkflowExecutor with real workflow scenarios."""
    
    def test_full_workflow_lifecycle(self):
        """Test complete workflow lifecycle with all components."""
        # Setup
        config = WorkflowConfig(settings={"timeout": 30})
        workflow = MockWorkflow(config=config)
        executor = WorkflowExecutor()
        
        progress_events = []
        def track_progress(workflow_id, status):
            progress_events.append((workflow_id, status))
        
        executor.add_progress_callback(track_progress)
        
        input_data = {"data": "integration_test", "additional": "info"}
        
        # Execute
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify complete flow
        assert workflow.validate_called is True
        assert workflow.execute_called is True
        assert result["success"] is True
        assert result["data"]["processed_data"] == "integration_test"
        
        # Verify progress tracking
        expected_events = [
            (workflow.identity.workflow_id, "started"),
            (workflow.identity.workflow_id, "completed")
        ]
        assert progress_events == expected_events
        
        # Verify metadata is complete
        assert "execution_time_seconds" in result
        assert "timestamp" in result
        assert "executor_metadata" in result
        assert result["executor_metadata"]["executed_by"] == "WorkflowExecutor"
    
    def test_multiple_workflow_executions(self):
        """Test executor can handle multiple workflow executions."""
        executor = WorkflowExecutor()
        
        # Execute multiple workflows
        results = []
        for i in range(3):
            workflow = MockWorkflow()
            input_data = {"data": f"test_{i}"}
            result = executor.execute_workflow(workflow, input_data)
            results.append(result)
        
        # Verify all executions succeeded
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["data"]["processed_data"] == f"test_{i}"
            assert result["workflow_type"] == "mock_workflow"
    
    def test_registration_and_execution_integration(self):
        """Test workflow registration and execution working together."""
        executor = WorkflowExecutor()
        
        # Register workflow type
        executor.register_workflow_type("mock_workflow", MockWorkflow)
        
        # Create workflow using factory
        workflow = executor.create_workflow("mock_workflow", {"custom": "config"})
        
        # Execute workflow
        result = executor.execute_workflow(workflow, {"data": "registry_test"})
        
        # Verify success
        assert result["success"] is True
        assert result["data"]["processed_data"] == "registry_test"
        assert workflow.config.settings == {"custom": "config"}
        
        # Verify executor info shows registration
        info = executor.get_executor_info()
        assert "mock_workflow" in info["registered_workflows"]
        assert info["workflow_count"] == 1
    
    def test_mixed_success_and_failure_executions(self):
        """Test executor handles mixed success and failure scenarios."""
        executor = WorkflowExecutor()
        
        # Execute mix of successful and failing workflows
        workflows = [
            MockWorkflow(),  # Success
            MockWorkflow(should_fail_validation=True),  # Validation failure
            MockWorkflow(),  # Success
            MockWorkflow(should_fail_execution=True),  # Execution failure
        ]
        
        results = []
        for workflow in workflows:
            result = executor.execute_workflow(workflow, {"data": "test"})
            results.append(result)
        
        # Verify results
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "Validation failed" in results[1]["error"]
        assert results[2]["success"] is True
        assert results[3]["success"] is False
        assert "Mock execution failure" in results[3]["error"]