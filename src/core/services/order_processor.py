"""
Main Order Processor Service - Coordinates the entire order processing pipeline.
"""

from pathlib import Path
from typing import List, Optional, Protocol

from src.core.models import OrderData, OrderItemData, AgencyType
from src.core.services.order_form_parser import parse_order_form_to_order_items
from src.core.services.workflow_orchestrator import WorkflowOrchestrator
from src.core.services.order_worksheet_exporter import export_order_items_minimal_format
from src.integrations.cloud.protocols import CloudOperations


class ProgressCallback(Protocol):
    """Protocol for progress feedback - allows GUI substitution."""

    def update_progress(self, message: str, percentage: Optional[int] = None) -> None:
        """Update progress with message and optional percentage."""
        ...


class OrderProcessorService:
    """Main coordinator service for the entire order processing pipeline."""

    def __init__(
        self,
        cloud_service: CloudOperations,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """Initialize with cloud service and optional progress callback."""
        self.cloud_service = cloud_service
        self.progress_callback = progress_callback
        self.workflow_orchestrator = WorkflowOrchestrator(cloud_service)

    def process_order(
        self,
        order_data: OrderData,
        order_form_path: Path,
        output_directory: Path,
        agency: AgencyType,
        use_legacy_format: bool = False,
    ) -> str:
        """
        Process complete order from start to finish.

        Args:
            order_data: Basic order information from GUI
            order_form_path: Path to Excel order form file
            output_directory: Directory for output file
            agency: Agency type for parsing order form
            use_legacy_format: If True, exports in legacy format

        Returns:
            str: Path to created output file

        Raises:
            ValueError: If inputs are invalid
            IOError: If files cannot be read/written
        """
        self._update_progress("Starting order processing...", 0)

        # Step 1: Parse order form
        self._update_progress("Parsing order form...", 20)
        order_items = parse_order_form_to_order_items(str(order_form_path), agency)

        # Step 2: Execute workflows for each item
        self._update_progress("Executing workflows...", 40)
        processed_items = self._execute_workflows(order_items, order_data.order_type)

        # Step 3: Export to worksheet
        self._update_progress("Generating output file...", 80)
        output_path = self._export_worksheet(
            processed_items, order_data, output_directory, use_legacy_format
        )

        self._update_progress("Order processing complete!", 100)
        return output_path

    def _execute_workflows(
        self, order_items: List[OrderItemData], report_type
    ) -> List[OrderItemData]:
        """Execute workflows for all order items."""
        total_items = len(order_items)

        for i, order_item in enumerate(order_items):
            try:
                self.workflow_orchestrator.execute_workflows_for_order_item(
                    order_item, report_type
                )
                progress = 40 + int((i + 1) / total_items * 30)  # 40-70% range
                self._update_progress(f"Processed item {i + 1}/{total_items}", progress)
            except Exception as e:
                # Log error but continue with other items
                self._update_progress(f"Error processing item {i + 1}: {str(e)}")
                continue

        return order_items

    def _export_worksheet(
        self,
        order_items: List[OrderItemData],
        order_data: OrderData,
        output_directory: Path,
        use_legacy_format: bool,
    ) -> str:
        """Export processed items to worksheet."""
        if use_legacy_format:
            from src.core.services.order_worksheet_exporter import (
                export_order_items_legacy_format,
            )

            export_func = export_order_items_legacy_format
        else:
            export_func = export_order_items_minimal_format

        # Get agency from first order item (all items should have same agency)
        item_agency = order_items[0].agency if order_items else AgencyType.NMSLO

        return export_func(
            order_items=order_items,
            agency=item_agency,
            output_directory=output_directory,
            order_number=order_data.order_number,
            order_type=order_data.order_type.value,
            order_date=order_data.order_date,
        )

    def _update_progress(self, message: str, percentage: Optional[int] = None) -> None:
        """Update progress if callback is available."""
        if self.progress_callback:
            self.progress_callback.update_progress(message, percentage)


def process_order_end_to_end(
    order_data: OrderData,
    order_form_path: Path,
    output_directory: Path,
    cloud_service: CloudOperations,
    progress_callback: Optional[ProgressCallback] = None,
    use_legacy_format: bool = False,
) -> str:
    """
    Convenience function for end-to-end order processing.

    Args:
        order_data: Basic order information
        order_form_path: Path to Excel order form file
        output_directory: Directory for output file
        cloud_service: Cloud service for workflows
        progress_callback: Optional progress callback
        use_legacy_format: If True, exports in legacy format

    Returns:
        str: Path to created output file
    """
    processor = OrderProcessorService(cloud_service, progress_callback)
    return processor.process_order(
        order_data, order_form_path, output_directory, use_legacy_format
    )
