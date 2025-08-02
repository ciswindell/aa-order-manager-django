"""
End-to-End Workflow Orchestration Tests

Tests combining LeaseDirectorySearchWorkflow and PreviousReportDetectionWorkflow
to validate complete workflow orchestration scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.workflows import setup_workflow_executor
from src.core.workflows.lease_directory_search import LeaseDirectorySearchWorkflow
from src.core.workflows.previous_report_detection import PreviousReportDetectionWorkflow
from src.core.models import OrderItemData, AgencyType
from src.integrations.dropbox.service import DropboxService


class TestEndToEndWorkflowOrchestration:
    """End-to-end tests combining lease directory search and previous report detection."""
    
    @pytest.fixture
    def mock_dropbox_service(self):
        """Create a mock DropboxService for end-to-end tests."""
        mock_service = Mock(spec=DropboxService)
        mock_service.is_authenticated.return_value = True
        return mock_service
    
    @pytest.fixture
    def nmslo_order_item(self):
        """Create NMSLO OrderItemData without directory path."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
    
    @pytest.fixture
    def blm_order_item(self):
        """Create BLM OrderItemData without directory path."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMNM 0501759",
            legal_description="Section 5, Township 10S, Range 15E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
    
    def test_complete_workflow_chain_master_documents_found(self, mock_dropbox_service, nmslo_order_item):
        """Test complete workflow chain: directory search → Master Documents found."""
        
        # Mock directory search response
        mock_search_result = {
            "entries": [
                {
                    "name": "12345",
                    "path_lower": "/nmslo/12345",
                    ".tag": "folder"
                }
            ]
        }
        
        # Mock file listing response with Master Documents
        mock_files = [
            {"name": "NMSLO 12345 Master Documents.pdf", "type": "file"},
            {"name": "Supporting Documents.txt", "type": "file"},
            {"name": "Another Master Documents Report.docx", "type": "file"}
        ]
        
        # Setup mock responses
        mock_dropbox_service.search_directory_with_metadata.return_value = {
            "path": "/NMSLO/12345",
            "shareable_link": "https://dropbox.com/s/abc123/12345"
        }
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        # Setup executor and workflows
        executor = setup_workflow_executor()
        
        # Step 1: Execute lease directory search
        lease_search_workflow = executor.create_workflow("lease_directory_search")
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        lease_search_input = {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        }
        
        lease_search_result = executor.execute_workflow(lease_search_workflow, lease_search_input)
        
        # Verify lease directory search succeeded
        assert lease_search_result["success"] is True
        assert nmslo_order_item.report_directory_link == "https://dropbox.com/s/abc123/12345"
        assert nmslo_order_item.report_directory_path == "/NMSLO/12345"
        
        # Step 2: Execute previous report detection
        report_detection_workflow = executor.create_workflow("previous_report_detection")
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_input = {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        }
        
        report_detection_result = executor.execute_workflow(report_detection_workflow, report_detection_input)
        
        # Verify previous report detection succeeded
        assert report_detection_result["success"] is True
        report_data = report_detection_result["data"]
        assert report_data["previous_report_found"] is True
        assert len(report_data["matching_files"]) == 2
        assert "NMSLO 12345 Master Documents.pdf" in report_data["matching_files"]
        assert "Another Master Documents Report.docx" in report_data["matching_files"]
        
        # Verify final OrderItemData state
        assert nmslo_order_item.previous_report_found is True
        assert nmslo_order_item.report_directory_link is not None
        assert nmslo_order_item.report_directory_path is not None
    
    def test_complete_workflow_chain_no_master_documents(self, mock_dropbox_service, blm_order_item):
        """Test complete workflow chain: directory search → no Master Documents found."""
        
        # Mock directory search response
        mock_search_result = {
            "entries": [
                {
                    "name": "NMNM 0501759",
                    "path_lower": "/federal/nmnm 0501759",
                    ".tag": "folder"
                }
            ]
        }
        
        # Mock file listing response without Master Documents
        mock_files = [
            {"name": "Lease Agreement.pdf", "type": "file"},
            {"name": "Survey Report.pdf", "type": "file"},
            {"name": "Environmental Assessment.docx", "type": "file"}
        ]
        
        # Setup mock responses
        mock_dropbox_service.search_directory_with_metadata.return_value = {
            "path": "/Federal/NMNM 0501759",
            "shareable_link": "https://dropbox.com/s/def456/NMNM0501759"
        }
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        executor = setup_workflow_executor()
        
        # Step 1: Execute lease directory search
        lease_search_workflow = executor.create_workflow("lease_directory_search")
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        lease_search_result = executor.execute_workflow(lease_search_workflow, {
            "order_item_data": blm_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        assert lease_search_result["success"] is True
        assert blm_order_item.report_directory_path == "/Federal/NMNM 0501759"
        
        # Step 2: Execute previous report detection
        report_detection_workflow = executor.create_workflow("previous_report_detection")
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_result = executor.execute_workflow(report_detection_workflow, {
            "order_item_data": blm_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Verify no Master Documents found
        assert report_detection_result["success"] is True
        report_data = report_detection_result["data"]
        assert report_data["previous_report_found"] is False
        assert len(report_data["matching_files"]) == 0
        assert report_data["total_files_checked"] == 3
        
        # Verify final OrderItemData state
        assert blm_order_item.previous_report_found is False
        assert blm_order_item.report_directory_link is not None
        assert blm_order_item.report_directory_path is not None
    
    def test_workflow_chain_directory_search_fails(self, mock_dropbox_service, nmslo_order_item):
        """Test workflow chain when directory search fails."""
        
        # Mock directory search to return no results (directory not found)
        mock_dropbox_service.search_directory_with_metadata.return_value = {
            "path": None,
            "shareable_link": None
        }
        
        executor = setup_workflow_executor()
        
        # Step 1: Execute lease directory search (should fail)
        lease_search_workflow = executor.create_workflow("lease_directory_search")
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        lease_search_result = executor.execute_workflow(lease_search_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Directory search should succeed but find no directory
        assert lease_search_result["success"] is True
        assert nmslo_order_item.report_directory_link is None
        assert nmslo_order_item.report_directory_path is None
        
        # Step 2: Previous report detection should fail due to missing directory path
        report_detection_workflow = executor.create_workflow("previous_report_detection")
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_result = executor.execute_workflow(report_detection_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Report detection should fail validation
        assert report_detection_result["success"] is False
        assert "report_directory_path is required" in report_detection_result["error"]
        assert nmslo_order_item.previous_report_found is None
    
    def test_workflow_chain_directory_search_api_error(self, mock_dropbox_service, nmslo_order_item):
        """Test workflow chain when directory search encounters API error."""
        
        # Mock directory search to raise an exception
        mock_dropbox_service.search_directory_with_metadata.side_effect = Exception("Dropbox API Error")
        
        executor = setup_workflow_executor()
        
        # Step 1: Execute lease directory search (should fail)
        lease_search_workflow = executor.create_workflow("lease_directory_search")
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        lease_search_result = executor.execute_workflow(lease_search_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Directory search should fail
        assert lease_search_result["success"] is False
        assert "Dropbox API Error" in lease_search_result["error"]
        assert nmslo_order_item.report_directory_path is None
        
        # Step 2: Previous report detection should fail due to missing directory path
        report_detection_workflow = executor.create_workflow("previous_report_detection")
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_result = executor.execute_workflow(report_detection_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        assert report_detection_result["success"] is False
        assert "report_directory_path is required" in report_detection_result["error"]
    
    def test_workflow_chain_report_detection_api_error(self, mock_dropbox_service, nmslo_order_item):
        """Test workflow chain when report detection encounters API error."""
        
        # Mock successful directory search
        mock_dropbox_service.search_directory_with_metadata.return_value = {
            "path": "/NMSLO/12345",
            "shareable_link": "https://dropbox.com/s/abc123/12345"
        }
        
        # Mock file listing to raise an exception
        mock_dropbox_service.list_directory_files.side_effect = Exception("File listing failed")
        
        executor = setup_workflow_executor()
        
        # Step 1: Execute lease directory search (should succeed)
        lease_search_workflow = executor.create_workflow("lease_directory_search")
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        lease_search_result = executor.execute_workflow(lease_search_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        assert lease_search_result["success"] is True
        assert nmslo_order_item.report_directory_path == "/NMSLO/12345"
        
        # Step 2: Previous report detection should fail due to API error
        report_detection_workflow = executor.create_workflow("previous_report_detection")
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_result = executor.execute_workflow(report_detection_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Report detection should fail gracefully
        assert report_detection_result["success"] is True  # Executor succeeded
        workflow_data = report_detection_result["data"]
        assert workflow_data["success"] is False
        assert "Directory access failed" in workflow_data["error"]
        assert nmslo_order_item.previous_report_found is None  # Set to None on error
    
    def test_multiple_order_items_workflow_chain(self, mock_dropbox_service):
        """Test workflow chain with multiple order items."""
        
        # Create multiple order items
        from datetime import datetime
        order_items = [
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="12345",
                legal_description="Section 1, Township 2N, Range 3E",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            ),
            OrderItemData(
                agency=AgencyType.BLM,
                lease_number="NMNM 0501759",
                legal_description="Section 5, Township 10S, Range 15E",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            ),
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="67890",
                legal_description="Section 2, Township 3N, Range 4E",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
        ]
        
        # Setup mock responses based on lease number
        def mock_search_directory_with_metadata(directory_path):
            if "12345" in directory_path:
                return {"path": "/NMSLO/12345", "shareable_link": "https://dropbox.com/s/abc123/12345"}
            elif "NMNM 0501759" in directory_path:
                return {"path": "/Federal/NMNM 0501759", "shareable_link": "https://dropbox.com/s/def456/NMNM0501759"}
            elif "67890" in directory_path:
                return {"path": None, "shareable_link": None}  # Not found
            return {"path": None, "shareable_link": None}
        
        # No longer needed since search_directory_with_metadata returns both path and link
        
        def mock_list_directory_files(directory_path):
            if "/NMSLO/12345" in directory_path:
                return [{"name": "NMSLO 12345 Master Documents.pdf", "type": "file"}]
            elif "/Federal/NMNM 0501759" in directory_path:
                return [{"name": "Regular File.pdf", "type": "file"}]
            return []
        
        mock_dropbox_service.search_directory_with_metadata.side_effect = mock_search_directory_with_metadata
        mock_dropbox_service.list_directory_files.side_effect = mock_list_directory_files
        
        executor = setup_workflow_executor()
        results = []
        
        # Process each order item through both workflows
        for order_item in order_items:
            # Step 1: Directory search
            lease_search_workflow = executor.create_workflow("lease_directory_search")
            lease_search_workflow.dropbox_service = mock_dropbox_service
            
            lease_result = executor.execute_workflow(lease_search_workflow, {
                "order_item_data": order_item,
                "dropbox_service": mock_dropbox_service
            })
            
            # Step 2: Report detection (only if directory was found)
            if order_item.report_directory_path:
                report_detection_workflow = executor.create_workflow("previous_report_detection")
                report_detection_workflow.dropbox_service = mock_dropbox_service
                
                report_result = executor.execute_workflow(report_detection_workflow, {
                    "order_item_data": order_item,
                    "dropbox_service": mock_dropbox_service
                })
                results.append((lease_result, report_result))
            else:
                results.append((lease_result, None))
        
        # Verify results
        # Order item 1 (12345): Directory found, Master Documents found
        assert results[0][0]["success"] is True
        assert results[0][1]["success"] is True
        assert results[0][1]["data"]["previous_report_found"] is True
        assert order_items[0].previous_report_found is True
        
        # Order item 2 (NMNM 0501759): Directory found, no Master Documents
        assert results[1][0]["success"] is True
        assert results[1][1]["success"] is True
        assert results[1][1]["data"]["previous_report_found"] is False
        assert order_items[1].previous_report_found is False
        
        # Order item 3 (67890): Directory not found, no report detection
        assert results[2][0]["success"] is True
        assert results[2][1] is None  # No report detection executed
        assert order_items[2].report_directory_path is None
        assert order_items[2].previous_report_found is None
    
    def test_workflow_orchestration_with_configuration(self, mock_dropbox_service, nmslo_order_item):
        """Test workflow orchestration with custom configurations."""
        
        # Setup mock responses
        mock_files = [{"name": "Master Documents Report.pdf", "type": "file"}]
        
        mock_dropbox_service.search_directory_with_metadata.return_value = {
            "path": "/NMSLO/12345",
            "shareable_link": "https://dropbox.com/s/abc123/12345"
        }
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        executor = setup_workflow_executor()
        
        # Create workflows with custom configurations
        lease_search_config = {"timeout": 30, "retry_attempts": 3}
        report_detection_config = {"pattern_timeout": 10, "max_files": 100}
        
        lease_search_workflow = executor.create_workflow("lease_directory_search", config=lease_search_config)
        lease_search_workflow.dropbox_service = mock_dropbox_service
        
        report_detection_workflow = executor.create_workflow("previous_report_detection", config=report_detection_config)
        report_detection_workflow.dropbox_service = mock_dropbox_service
        
        # Verify configurations were applied
        assert lease_search_workflow.config.settings == lease_search_config
        assert report_detection_workflow.config.settings == report_detection_config
        
        # Execute both workflows
        lease_result = executor.execute_workflow(lease_search_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        report_result = executor.execute_workflow(report_detection_workflow, {
            "order_item_data": nmslo_order_item,
            "dropbox_service": mock_dropbox_service
        })
        
        # Verify both workflows succeeded with configurations
        assert lease_result["success"] is True
        assert report_result["success"] is True
        assert nmslo_order_item.previous_report_found is True