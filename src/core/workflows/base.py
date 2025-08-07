"""
Base Workflow Classes

Simple foundational classes for the workflow architecture.
Start simple and add complexity as needed.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class WorkflowConfig:
    """Simple configuration for workflows."""
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


@dataclass
class WorkflowIdentity:
    """Simple identity for workflows."""
    workflow_type: str
    workflow_name: str
    workflow_id: str = ""
    
    def __post_init__(self):
        if not self.workflow_id:
            # Simple ID generation
            import time
            self.workflow_id = f"{self.workflow_type}_{int(time.time())}"


class WorkflowBase(ABC):
    """
    Abstract base class for all workflows.
    
    Simple interface with three required methods.
    """
    
    def __init__(self, config: WorkflowConfig = None):
        self.config = config or WorkflowConfig()
        self.identity = self._create_default_identity()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    def _create_default_identity(self) -> WorkflowIdentity:
        """Create default identity for this workflow type."""
        pass
    
    @abstractmethod
    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input data.
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow.
        
        Returns:
            Result dictionary with workflow output
        """
        pass
    
    def handle_errors(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle errors during execution.
        
        Returns:
            Error result dictionary
        """
        context = context or {}
        self.logger.error("Workflow failed: %s", str(error), exc_info=True)
        
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "workflow_id": self.identity.workflow_id
        }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get workflow information and current state."""
        return {
            "identity": {
                "workflow_type": self.identity.workflow_type,
                "workflow_name": self.identity.workflow_name,
                "workflow_id": self.identity.workflow_id,
            },
            "config": self.config.settings,
            "status": "initialized"
        }