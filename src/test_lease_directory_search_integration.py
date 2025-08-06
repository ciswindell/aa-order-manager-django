"""
Integration test for lease directory search with real Dropbox authentication.

Tests the complete workflow using real Dropbox API to find the known lease "NMLC 0028446A".
"""

from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.workflows.lease_directory_search import LeaseDirectorySearchWorkflow
from src.core.models import OrderItemData, AgencyType
from src.integrations.cloud.factory import get_cloud_service


class TestLeaseDirectorySearchIntegration:
    """Integration test using real Dropbox authentication."""
    
    def test_blm_nmlc_lease_directory(self):
        """Test finding the known lease directory 'NMLC 0028446A'."""
        # Create cloud service using factory
        cloud_service = get_cloud_service()
        
        # Authenticate
        assert cloud_service.authenticate(), "Failed to authenticate with cloud service"
        assert cloud_service.is_authenticated(), "Service should be authenticated"
        
        # Create workflow with service
        workflow = LeaseDirectorySearchWorkflow(cloud_service=cloud_service)
        
        # Create test order item with known lease
        order_item = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMLC 0028446A",
            legal_description="Test legal description",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        # Execute workflow
        result = workflow.execute({"order_item_data": order_item})
        
        # Verify results
        assert result["success"] is True, f"Workflow should succeed: {result.get('message', '')}"
        assert result["lease_number"] == "NMLC 0028446A"
        assert result["agency"] == "Federal"
        
        # Check if directory was found (either path or link should be present)
        directory_found = result.get("directory_path") or result.get("shareable_link")
        assert directory_found, f"Directory should be found for known lease: {result}"
        
        print(f"✅ Found directory: {result.get('directory_path')}")
        print(f"✅ Shareable link: {result.get('shareable_link')}")
        
        # Verify order item was updated
        assert order_item.report_directory_path == result.get("directory_path")
        assert order_item.report_directory_link == result.get("shareable_link")


if __name__ == "__main__":
    test = TestLeaseDirectorySearchIntegration()
    test.test_blm_nmlc_lease_directory()
    print("✅ Integration test completed successfully!") 