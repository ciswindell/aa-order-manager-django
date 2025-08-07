"""
Previous Report Detection Workflow

Workflow implementation for detecting existing Master Documents files within lease directories
to determine if a lease already has a completed report, enabling proper work assignment.
"""

import re
import logging
from typing import Dict, Any, Optional

from src.core.models import OrderItemData
from src.integrations.cloud.protocols import CloudOperations

from .base import WorkflowBase, WorkflowConfig, WorkflowIdentity


logger = logging.getLogger(__name__)


class PreviousReportDetectionWorkflow(WorkflowBase):
    """
    Workflow for detecting existing Master Documents in lease directories.

    This workflow searches for Master Documents files in lease directories using
    pattern matching to determine if a lease already has a completed report.

    Input: OrderItemData with report_directory_path field populated
    Output: Updates OrderItemData.previous_report_found with boolean result
    """

    # Case-insensitive regex pattern for Master Documents detection
    MASTER_DOCUMENTS_PATTERN = re.compile(r".*master documents.*", re.IGNORECASE)

    def __init__(
        self, config: WorkflowConfig = None, cloud_service: CloudOperations = None
    ):
        """
        Initialize the Previous Report Detection workflow.

        Args:
            config: Workflow configuration settings
            cloud_service: Optional CloudOperations instance for dependency injection
        """
        super().__init__(config)
        self.cloud_service = cloud_service

    def _create_default_identity(self) -> WorkflowIdentity:
        """Create default identity for this workflow type."""
        return WorkflowIdentity(
            workflow_type="previous_report_detection",
            workflow_name="Previous Report Detection",
        )

    def validate_inputs(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input data for the workflow.

        Args:
            input_data: Dictionary containing workflow input parameters

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if order_item_data is provided
        if "order_item_data" not in input_data:
            return False, "order_item_data is required"

        order_item_data = input_data["order_item_data"]
        if not isinstance(order_item_data, OrderItemData):
            return False, "order_item_data must be an OrderItemData instance"

        # Check if report_directory_path is available
        if not order_item_data.report_directory_path:
            return False, "report_directory_path is required in order_item_data"

        # Check if CloudOperations service is available
        cloud_service = input_data.get("cloud_service") or self.cloud_service
        if not cloud_service:
            return False, "cloud_service is required"

        if not cloud_service.is_authenticated():
            return False, "cloud_service must be authenticated"

        return True, None

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the Previous Report Detection workflow.

        Args:
            input_data: Dictionary containing workflow input parameters

        Returns:
            Dictionary containing workflow execution results
        """
        try:
            # Validate inputs
            is_valid, error_message = self.validate_inputs(input_data)
            if not is_valid:
                self.logger.error(f"Input validation failed: {error_message}")
                return {
                    "success": False,
                    "error": error_message,
                    "error_type": "ValidationError",
                    "workflow_id": self.identity.workflow_id,
                }

            order_item_data = input_data["order_item_data"]
            cloud_service = input_data.get("cloud_service") or self.cloud_service
            directory_path = order_item_data.report_directory_path

            self.logger.info(
                f"Searching for Master Documents in directory: {directory_path}"
            )

            # List files in the directory
            try:
                cloud_files = cloud_service.list_files(directory_path)
                files = [{"name": file.name, "path": file.path} for file in cloud_files]
                self.logger.debug(f"Found {len(files)} files in directory")

            except Exception as e:
                self.logger.error(f"Failed to list directory files: {str(e)}")
                # Set previous_report_found to None to indicate error
                order_item_data.previous_report_found = None
                return {
                    "success": False,
                    "error": f"Directory access failed: {str(e)}",
                    "error_type": type(e).__name__,
                    "directory_path": directory_path,
                    "workflow_id": self.identity.workflow_id,
                }

            # Search for Master Documents pattern in filenames
            master_documents_found = False
            matching_files = []

            for file_info in files:
                filename = file_info.get("name", "")
                if self.MASTER_DOCUMENTS_PATTERN.match(filename):
                    master_documents_found = True
                    matching_files.append(filename)
                    self.logger.debug(f"Found Master Documents file: {filename}")

            # Update OrderItemData with detection result
            order_item_data.previous_report_found = master_documents_found

            if master_documents_found:
                self.logger.info(
                    f"Master Documents detected. Found {len(matching_files)} matching files."
                )
            else:
                self.logger.info("No Master Documents files found in directory.")

            return {
                "success": True,
                "previous_report_found": master_documents_found,
                "matching_files": matching_files,
                "total_files_checked": len(files),
                "directory_path": directory_path,
                "workflow_id": self.identity.workflow_id,
            }

        except Exception as e:
            # Handle unexpected errors
            self.logger.error(
                f"Unexpected error in workflow execution: {str(e)}", exc_info=True
            )
            # Set previous_report_found to None to indicate error
            if "order_item_data" in input_data:
                input_data["order_item_data"].previous_report_found = None

            return self.handle_errors(
                e,
                {
                    "directory_path": (
                        input_data.get("order_item_data", {}).report_directory_path
                        if "order_item_data" in input_data
                        else None
                    )
                },
            )
