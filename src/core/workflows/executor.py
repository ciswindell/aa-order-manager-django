"""
Workflow Executor

Simple workflow execution framework with setup, teardown, and basic progress tracking.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .base import WorkflowBase


logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """
    Simple workflow executor for running individual workflows.
    
    Provides workflow execution with proper setup, teardown, timing,
    basic progress tracking, and workflow registration.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._progress_callbacks: list[Callable] = []
        self._workflow_registry: Dict[str, type] = {}
    
    def add_progress_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Add a callback function for progress updates.
        
        Args:
            callback: Function that takes (workflow_id, status) parameters
                     Status will be: 'started', 'completed', 'failed'
        """
        self._progress_callbacks.append(callback)
    
    def execute_workflow(self, workflow: WorkflowBase, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow with proper setup and teardown.
        
        Args:
            workflow: The workflow instance to execute
            input_data: Input data for the workflow
            
        Returns:
            Dict containing execution results with metadata
        """
        workflow_id = workflow.identity.workflow_id
        workflow_type = workflow.identity.workflow_type
        start_time = time.time()
        
        # Setup: Log start and notify progress callbacks
        self.logger.info(f"Starting workflow execution: {workflow.identity.workflow_name} ({workflow_id})")
        self._notify_progress(workflow_id, "started")
        
        try:
            # Validate inputs before execution
            is_valid, validation_error = workflow.validate_inputs(input_data)
            if not is_valid:
                self.logger.warning(f"Workflow validation failed: {validation_error}")
                error_result = self._create_error_result(
                    workflow_id=workflow_id,
                    workflow_type=workflow_type,
                    error=f"Validation failed: {validation_error}",
                    error_type="ValidationError",
                    execution_time=time.time() - start_time
                )
                self._notify_progress(workflow_id, "failed")
                return error_result
            
            # Execute the workflow
            self.logger.info(f"Executing workflow: {workflow_id}")
            result = workflow.execute(input_data)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create success result with metadata
            success_result = self._create_success_result(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                data=result,
                execution_time=execution_time
            )
            
            # Teardown: Log success and notify progress callbacks
            self.logger.info(f"Workflow completed successfully: {workflow_id} ({execution_time:.2f}s)")
            self._notify_progress(workflow_id, "completed")
            
            return success_result
            
        except Exception as error:
            # Handle any errors during execution
            execution_time = time.time() - start_time
            
            self.logger.error(f"Workflow execution failed: {workflow_id}", exc_info=True)
            
            # Use workflow's error handling
            error_result = workflow.handle_errors(error, {
                "input_data": input_data,
                "execution_time": execution_time
            })
            
            # Add executor metadata to error result
            if isinstance(error_result, dict):
                error_result.update({
                    "execution_time_seconds": execution_time,
                    "timestamp": datetime.now(),
                    "executor_metadata": {
                        "workflow_type": workflow_type,
                        "started_at": datetime.fromtimestamp(start_time),
                        "failed_at": datetime.now()
                    }
                })
            
            # Teardown: Notify progress callbacks of failure
            self._notify_progress(workflow_id, "failed")
            
            return error_result
    
    def register_workflow_type(self, workflow_type: str, workflow_class: type) -> None:
        """
        Register a workflow type with the executor.
        
        Args:
            workflow_type: Unique identifier for the workflow type (e.g., "lease_directory_search")
            workflow_class: The workflow class that inherits from WorkflowBase
            
        Raises:
            ValueError: If workflow_type is already registered or workflow_class is invalid
        """
        if not workflow_type:
            raise ValueError("Workflow type cannot be empty")
        
        if workflow_type in self._workflow_registry:
            raise ValueError(f"Workflow type '{workflow_type}' is already registered")
        
        if not issubclass(workflow_class, WorkflowBase):
            raise ValueError(f"Workflow class must inherit from WorkflowBase")
        
        self._workflow_registry[workflow_type] = workflow_class
        self.logger.info(f"Registered workflow type: {workflow_type}")
    
    def create_workflow(self, workflow_type: str, config: Optional[Dict[str, Any]] = None) -> WorkflowBase:
        """
        Create a workflow instance of the specified type.
        
        Args:
            workflow_type: The type of workflow to create
            config: Optional configuration settings for the workflow
            
        Returns:
            WorkflowBase: Instance of the requested workflow type
            
        Raises:
            ValueError: If workflow_type is not registered
        """
        if workflow_type not in self._workflow_registry:
            available_types = list(self._workflow_registry.keys())
            raise ValueError(f"Unknown workflow type '{workflow_type}'. Available types: {available_types}")
        
        workflow_class = self._workflow_registry[workflow_type]
        
        # Create config if provided
        from .base import WorkflowConfig
        workflow_config = None
        if config:
            workflow_config = WorkflowConfig(settings=config)
        
        workflow = workflow_class(config=workflow_config)
        self.logger.debug(f"Created workflow instance: {workflow_type}")
        return workflow
    
    def get_available_workflow_types(self) -> list[str]:
        """
        Get list of available workflow types.
        
        Returns:
            List of registered workflow type names
        """
        return list(self._workflow_registry.keys())
    
    def is_workflow_registered(self, workflow_type: str) -> bool:
        """
        Check if a workflow type is registered.
        
        Args:
            workflow_type: The workflow type to check
            
        Returns:
            True if the workflow type is registered, False otherwise
        """
        return workflow_type in self._workflow_registry
    
    def unregister_workflow_type(self, workflow_type: str) -> bool:
        """
        Unregister a workflow type.
        
        Args:
            workflow_type: The workflow type to unregister
            
        Returns:
            True if the workflow was unregistered, False if it wasn't registered
        """
        if workflow_type in self._workflow_registry:
            del self._workflow_registry[workflow_type]
            self.logger.info(f"Unregistered workflow type: {workflow_type}")
            return True
        return False
    
    def _create_success_result(self, workflow_id: str, workflow_type: str, 
                             data: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """Create a standardized success result."""
        return {
            "success": True,
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "data": data,
            "error": None,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.now(),
            "executor_metadata": {
                "executed_by": "WorkflowExecutor",
                "execution_mode": "single_workflow"
            }
        }
    
    def _create_error_result(self, workflow_id: str, workflow_type: str,
                           error: str, error_type: str, execution_time: float) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "success": False,
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "data": None,
            "error": error,
            "error_type": error_type,
            "execution_time_seconds": execution_time,
            "timestamp": datetime.now(),
            "executor_metadata": {
                "executed_by": "WorkflowExecutor",
                "execution_mode": "single_workflow"
            }
        }
    
    def _notify_progress(self, workflow_id: str, status: str) -> None:
        """Notify all registered progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(workflow_id, status)
            except Exception as e:
                self.logger.warning(f"Progress callback failed: {e}")
    
    def get_executor_info(self) -> Dict[str, Any]:
        """Get information about the executor."""
        return {
            "executor_type": "WorkflowExecutor",
            "version": "1.0.0",
            "capabilities": [
                "single_workflow_execution",
                "workflow_registration",
                "workflow_creation",
                "input_validation",
                "error_handling",
                "progress_tracking",
                "timing_metadata"
            ],
            "registered_callbacks": len(self._progress_callbacks),
            "registered_workflows": list(self._workflow_registry.keys()),
            "workflow_count": len(self._workflow_registry)
        }