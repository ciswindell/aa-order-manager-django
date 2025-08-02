"""
Workflow Architecture Framework

This package provides the foundational workflow architecture for the Order Data
Collection Platform. It includes base classes, interfaces, and orchestration
components for implementing automated data collection workflows.

Key Components:
- WorkflowBase: Abstract base class for all workflows
- WorkflowExecutor: Framework for executing and orchestrating workflows
- WorkflowResult: Structured results and error handling
- LeaseDirectorySearchWorkflow: Implementation for finding lease directories

Example Usage:
    from src.core.workflows import WorkflowExecutor, LeaseDirectorySearchWorkflow
    
    executor = WorkflowExecutor()
    workflow = LeaseDirectorySearchWorkflow(config)
    result = executor.execute_workflow(workflow, input_data)
"""

# Core workflow components
from .base import WorkflowBase, WorkflowConfig, WorkflowIdentity
from .executor import WorkflowExecutor
from .lease_directory_search import LeaseDirectorySearchWorkflow
# from .results import WorkflowResult, WorkflowError  

__version__ = "1.0.0"
__all__ = [
    "WorkflowBase",
    "WorkflowConfig", 
    "WorkflowIdentity",
    "WorkflowExecutor",
    "LeaseDirectorySearchWorkflow"
]