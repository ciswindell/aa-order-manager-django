"""
Main Order Processor Service - Coordinates the entire order processing pipeline.
"""

from pathlib import Path
from typing import List, Optional, Protocol, Dict, Any, Tuple

from src.core.models import OrderData, OrderItemData, AgencyType, ReportType
from src.core.services.order_form_parser import parse_order_form_to_order_items
from src.core.services.order_worksheet_exporter import export_order_items_to_worksheet
from src.core.services.workflow_orchestrator import WorkflowOrchestrator
from src.integrations.cloud.protocols import CloudOperations
from src.integrations.cloud.factory import CloudServiceFactory


class ProgressCallback(Protocol):
    """Protocol for progress feedback - allows GUI substitution."""

    def update_progress(self, message: str, percentage: Optional[int] = None) -> None:
        """Update progress with message and optional percentage."""
        raise NotImplementedError


class OrderProcessorService:
    """Main coordinator service for the entire order processing pipeline."""

    def __init__(
        self,
        cloud_service: Optional[CloudOperations] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """Initialize with optional cloud service and progress callback."""
        self.cloud_service = cloud_service
        self.progress_callback = progress_callback
        if cloud_service:
            self.workflow_orchestrator = WorkflowOrchestrator(cloud_service)

    def process_order(
        self,
        order_data: OrderData,
        order_form_path: Path,
        output_directory: Path,
        agency: AgencyType,
    ) -> str:
        """
        Process complete order from start to finish.

        Args:
            order_data: Basic order information from GUI
            order_form_path: Path to Excel order form file
            output_directory: Directory for output file
            agency: Agency type for parsing order form

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
            processed_items, order_data, output_directory
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
            except (ValueError, IOError, RuntimeError) as e:
                # Log error but continue with other items
                self._update_progress(f"Error processing item {i + 1}: {str(e)}")
                continue

        return order_items

    def _export_worksheet(
        self,
        order_items: List[OrderItemData],
        order_data: OrderData,
        output_directory: Path,
    ) -> str:
        """Export processed items to worksheet."""
        # Get agency from first order item (all items should have same agency)
        item_agency = order_items[0].agency if order_items else AgencyType.NMSLO

        return export_order_items_to_worksheet(
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

    @staticmethod
    def create_order_data_from_form(form_data: Dict[str, Any]) -> OrderData:
        """
        Convert GUI form data to OrderData business object.

        Args:
            form_data: Dictionary with keys: agency, order_type, order_date,
                      order_number, file_path

        Returns:
            OrderData: Business domain object

        Raises:
            ValueError: If form data is invalid
        """
        # Convert GUI strings to business enums
        report_type = OrderProcessorService._map_order_type(form_data["order_type"])

        return OrderData(
            order_number=form_data["order_number"] or "Unknown",
            order_date=form_data["order_date"],
            order_type=report_type,
        )

    @staticmethod
    def map_agency_type(agency_str: str) -> AgencyType:
        """
        Convert GUI agency string to AgencyType enum using centralized validation.

        Args:
            agency_str: Agency string from GUI ("NMSLO", "Federal", etc.)

        Returns:
            AgencyType: Corresponding enum value

        Raises:
            ValueError: If agency string is invalid
        """
        from ..validation import FormDataValidator

        # Validate agency using centralized validator
        validator = FormDataValidator()
        is_valid, error = validator.validate_agency(agency_str)
        if not is_valid:
            raise ValueError(error)

        # Convert to enum after validation
        agency_mapping = {
            "NMSLO": AgencyType.NMSLO,
            "Federal": AgencyType.BLM,  # "Federal" in GUI maps to BLM in business
        }
        return agency_mapping[agency_str]

    @staticmethod
    def _map_order_type(order_type_str: str) -> ReportType:
        """
        Convert GUI order type string to ReportType enum.

        Args:
            order_type_str: Order type string from GUI

        Returns:
            ReportType: Corresponding enum value

        Raises:
            ValueError: If order type string is invalid
        """
        type_mapping = {
            "Runsheet": ReportType.RUNSHEET,
            "Abstract": ReportType.BASE_ABSTRACT,
        }

        if order_type_str not in type_mapping:
            raise ValueError(f"Unknown order type: {order_type_str}")

        return type_mapping[order_type_str]

    def process_order_from_gui(
        self, form_data: Dict[str, Any]
    ) -> Tuple[bool, str, str]:
        """
        Process order from GUI form data with centralized error handling.

        Args:
            form_data: Dictionary with GUI form data including file_path, agency, etc.

        Returns:
            Tuple[bool, str, str]: (success, output_path_or_user_message, technical_details)
        """
        from ..validation import ApplicationErrorHandler

        error_handler = ApplicationErrorHandler()

        try:
            self._update_progress("Initializing cloud service...", 0)

            # Initialize and authenticate cloud service
            self.cloud_service = CloudServiceFactory.create_service("dropbox")
            self.cloud_service.authenticate()
            self.workflow_orchestrator = WorkflowOrchestrator(self.cloud_service)

            # Create OrderData from form
            order_data = self.create_order_data_from_form(form_data)

            # Convert GUI agency to enum
            agency_enum = self.map_agency_type(form_data["agency"])

            # Setup paths
            input_file_path = Path(form_data["file_path"])
            output_directory = input_file_path.parent

            # Process the order
            output_path = self.process_order(
                order_data=order_data,
                order_form_path=input_file_path,
                output_directory=output_directory,
                agency=agency_enum,
            )

            return True, output_path, ""

        except Exception as e:
            user_message, technical_details = error_handler.handle_exception(
                e, "OrderProcessorService.process_order_from_gui"
            )
            return False, user_message, technical_details
