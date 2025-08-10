"""
Workflow Orchestrator Service

Simple service to execute workflows in sequence for order items.
"""

from typing import List

from src.core.models import OrderItemData, ReportType
from src.core.workflows import (
    LeaseDirectorySearchWorkflow,
    PreviousReportDetectionWorkflow,
)
from src.integrations.cloud.protocols import CloudOperations


class WorkflowOrchestrator:
    """Orchestrates workflow execution for order items with minimal logic."""

    def __init__(self, cloud_service: CloudOperations):
        self.cloud_service = cloud_service

    def execute_workflows_for_order_item(
        self, order_item: OrderItemData, order_type: ReportType
    ) -> OrderItemData:
        """Execute workflows for a single order item based on order type."""
        from ..validation import BusinessRulesValidator

        # Validate order type is supported using centralized validation
        validator = BusinessRulesValidator()
        is_valid, error = validator.validate_order_type_support(order_type)
        if not is_valid:
            raise ValueError(error)

        if order_type == ReportType.RUNSHEET:
            self._execute_runsheet_workflows(order_item)
        elif order_type in [
            ReportType.BASE_ABSTRACT,
            ReportType.SUPPLEMENTAL_ABSTRACT,
            ReportType.DOL_ABSTRACT,
        ]:
            self._execute_abstract_workflows(order_item)

        return order_item

    def _execute_runsheet_workflows(self, order_item: OrderItemData):
        """Execute Runsheet-specific workflows."""
        # Execute lease directory search first
        lease_workflow = LeaseDirectorySearchWorkflow(cloud_service=self.cloud_service)
        lease_workflow.execute({"order_item_data": order_item})

        # Execute previous report detection - workflow handles validation internally
        report_workflow = PreviousReportDetectionWorkflow(
            cloud_service=self.cloud_service
        )
        report_workflow.execute({"order_item_data": order_item})

    def _execute_abstract_workflows(self, order_item: OrderItemData):
        """Execute Abstract-specific workflows (placeholder for future implementation)."""
        # TODO: Implement Abstract workflows when requirements are defined
        pass

    def execute_workflows_for_order_items(
        self, order_items: List[OrderItemData], order_type: ReportType
    ) -> List[OrderItemData]:
        """Execute workflows for multiple order items."""
        for order_item in order_items:
            try:
                self.execute_workflows_for_order_item(order_item, order_type)
            except Exception:
                # Continue with other items if one fails
                continue

        return order_items
