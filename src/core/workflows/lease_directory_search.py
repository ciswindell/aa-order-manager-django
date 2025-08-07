"""
Lease Directory Search Workflow

Workflow implementation for finding lease directories in agency-specific Dropbox folders
that exactly match the lease number and generating shareable links.
"""

import logging
from typing import Dict, Any, Optional

from src import config
from src.core.models import OrderItemData, AgencyType
from src.integrations.cloud.protocols import CloudOperations

from .base import WorkflowBase, WorkflowConfig, WorkflowIdentity


logger = logging.getLogger(__name__)


class LeaseDirectorySearchWorkflow(WorkflowBase):
    """
    Workflow for searching lease directories in Dropbox.

    This workflow searches for lease directories in agency-specific Dropbox folders
    that exactly match the lease number, and generates shareable links for found directories.

    Input: OrderItemData with agency and lease_number
    Output: Shareable link if found, None if not found, error details if workflow fails
    """

    def __init__(
        self,
        workflow_config: WorkflowConfig = None,
        cloud_service: CloudOperations = None,
    ):
        """
        Initialize the Lease Directory Search workflow.

        Args:
            workflow_config: Workflow configuration settings
            cloud_service: Optional CloudOperations instance for dependency injection
        """
        super().__init__(workflow_config)
        self.cloud_service = cloud_service

    def _create_default_identity(self) -> WorkflowIdentity:
        """Create default identity for this workflow type."""
        return WorkflowIdentity(
            workflow_type="lease_directory_search",
            workflow_name="Lease Directory Search",
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

        # Check if it's an OrderItemData instance
        if not isinstance(order_item_data, OrderItemData):
            return False, "order_item_data must be an OrderItemData instance"

        # Validate required fields
        if not order_item_data.agency:
            return False, "OrderItemData.agency is required"

        if not order_item_data.lease_number:
            return False, "OrderItemData.lease_number is required"

        if not order_item_data.lease_number.strip():
            return False, "OrderItemData.lease_number cannot be empty"

        # Check if CloudOperations service is available
        if not self.cloud_service:
            return False, "CloudOperations service is required for directory search"

        return True, None

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the lease directory search workflow.

        Args:
            input_data: Dictionary containing OrderItemData

        Returns:
            Dict containing workflow results
        """
        order_item_data = input_data["order_item_data"]

        # Extract agency and lease number
        agency = order_item_data.agency
        lease_number = order_item_data.lease_number.strip()

        # Map AgencyType enum to DropboxService agency string
        agency_name = self._map_agency_type_to_string(agency)

        self.logger.info(
            "Searching for lease directory: %s (agency: %s)", lease_number, agency_name
        )

        try:
            # Build the directory path based on agency mapping
            directory_path = self._build_directory_path(agency_name, lease_number)

            # Use CloudOperations with the resolved path
            # Check if directory exists by listing files
            files = self.cloud_service.list_files(directory_path)

            if files:
                # Directory exists, create share link
                share_link = self.cloud_service.create_share_link(
                    directory_path, is_public=True
                )
                shareable_link = share_link.url if share_link else None
                found_path = directory_path
            else:
                # Directory doesn't exist
                shareable_link = None
                found_path = None

            if shareable_link or found_path:
                self.logger.info(
                    "Found lease directory - Link: %s, Path: %s",
                    shareable_link,
                    found_path,
                )

                # Update the OrderItemData with both results
                order_item_data.report_directory_link = shareable_link
                order_item_data.report_directory_path = found_path

                return {
                    "success": True,
                    "shareable_link": shareable_link,
                    "directory_path": found_path,
                    "agency": agency_name,
                    "lease_number": lease_number,
                    "message": f"Successfully found directory for lease {lease_number}",
                }
            else:
                self.logger.info("No directory found for lease: %s", lease_number)

                return {
                    "success": True,
                    "shareable_link": None,
                    "directory_path": None,
                    "agency": agency_name,
                    "lease_number": lease_number,
                    "message": f"No directory found for lease {lease_number}",
                }

        except Exception as error:
            self.logger.error(
                "Directory search failed for lease %s: %s", lease_number, str(error)
            )

            # Let the base class handle the error
            raise error

    def _map_agency_type_to_string(self, agency: AgencyType) -> str:
        """
        Map AgencyType enum to agency string for directory mapping.

        Args:
            agency: AgencyType enum value

        Returns:
            str: Agency string for directory path construction
        """
        if agency == AgencyType.NMSLO:
            return "NMSLO"
        elif agency == AgencyType.BLM:
            return "Federal"  # BLM uses "Federal" directory structure
        else:
            raise ValueError(f"Unsupported agency type: {agency}")

    def _build_directory_path(self, agency_string: str, lease_number: str) -> str:
        """
        Build the full directory path for a given agency and lease number.

        This method encapsulates the business logic of how agencies map to
        directory structures, keeping DropboxService focused on API operations.

        Args:
            agency_string: Agency identifier ("NMSLO" or "Federal")
            lease_number: Lease number to search for

        Returns:
            str: Full directory path for searching

        Examples:
            _build_directory_path("Federal", "NMNM 0501759") → "/Federal Workspace/^Runsheet Workspace/Runsheet Archive/NMNM 0501759"
            _build_directory_path("NMSLO", "12345") → "/State Workspace/^Runsheet Workspace/Runsheet Report Archive - New Format/12345"
        """
        # Get base directory path from config system
        base_path = config.get_runsheet_directory_path(agency_string)

        # Ensure base path ends with slash for proper path construction
        if not base_path.endswith("/"):
            base_path += "/"

        # Build full path: base_path + lease_number
        return f"{base_path}{lease_number}"

    def set_cloud_service(self, cloud_service: CloudOperations) -> None:
        """
        Set the CloudOperations instance for this workflow.

        Args:
            cloud_service: CloudOperations instance
        """
        self.cloud_service = cloud_service

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get workflow information and current state.

        Returns:
            Dict containing workflow metadata and configuration
        """
        base_info = super().get_workflow_info()
        base_info.update(
            {
                "workflow_specific": {
                    "supported_agencies": ["NMSLO", "BLM"],
                    "cloud_service_available": self.cloud_service is not None,
                    "agency_mappings": {"NMSLO": "NMSLO", "BLM": "Federal"},
                }
            }
        )
        return base_info
