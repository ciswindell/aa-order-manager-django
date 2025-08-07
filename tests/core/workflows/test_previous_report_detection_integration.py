"""
Integration test for previous report detection with real Dropbox authentication.

Tests the complete workflow using real Dropbox API to detect Master Documents
in the known lease directory "NMLC 0028446A".
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

from src.core.workflows.previous_report_detection import PreviousReportDetectionWorkflow
from src.core.models import OrderItemData, AgencyType
from src.integrations.cloud.factory import get_cloud_service


class TestPreviousReportDetectionIntegration:
    """Integration test using real Dropbox authentication."""

    def test_blm_nmlc_previous_report_detection(self):
        """Test detecting Master Documents in the known lease directory 'NMLC 0028446A'."""
        # Create cloud service using factory
        cloud_service = get_cloud_service()

        # Authenticate
        cloud_service.authenticate()  # Raises exception on failure
        assert cloud_service.is_authenticated(), "Service should be authenticated"

        # Create workflow with service
        workflow = PreviousReportDetectionWorkflow(cloud_service=cloud_service)

        # Create test order item with known lease directory
        order_item = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMLC 0028446A",
            legal_description="Test legal description",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/Federal Workspace/^Runsheet Workspace/Runsheet Archive/NMLC 0028446A",
        )

        # Execute workflow
        result = workflow.execute({"order_item_data": order_item})

        # Verify results
        assert (
            result["success"] is True
        ), f"Workflow should succeed: {result.get('message', '')}"
        assert (
            "previous_report_found" in result
        ), "Result should contain previous_report_found"
        assert (
            "total_files_checked" in result
        ), "Result should contain total_files_checked"
        assert "directory_path" in result, "Result should contain directory_path"
        assert result["directory_path"] == order_item.report_directory_path

        # Check if Master Documents were found
        previous_report_found = result.get("previous_report_found")
        assert (
            previous_report_found is not None
        ), "previous_report_found should not be None"

        total_files = result.get("total_files_checked", 0)
        assert total_files >= 0, "total_files_checked should be non-negative"

        print(f"✅ Directory checked: {result.get('directory_path')}")
        print(f"✅ Files checked: {total_files}")
        print(f"✅ Master Documents found: {previous_report_found}")

        if result.get("matching_files"):
            print(f"✅ Matching files: {result.get('matching_files')}")

        # Verify order item was updated
        assert order_item.previous_report_found == previous_report_found


if __name__ == "__main__":
    test = TestPreviousReportDetectionIntegration()
    test.test_blm_nmlc_previous_report_detection()
    print("✅ Integration test completed successfully!")
