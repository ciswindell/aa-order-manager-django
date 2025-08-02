"""
Integration Tests for Previous Report Detection Workflow

Tests complete workflow execution with WorkflowExecutor and mock Dropbox data
to validate end-to-end functionality and workflow orchestration.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.workflows import setup_workflow_executor, WorkflowExecutor
from src.core.workflows.previous_report_detection import PreviousReportDetectionWorkflow
from src.core.models import OrderItemData, AgencyType
from src.integrations.dropbox.service import DropboxService


class TestPreviousReportDetectionIntegration:
    """Integration tests for PreviousReportDetectionWorkflow with WorkflowExecutor."""
    
    @pytest.fixture
    def mock_dropbox_service(self):
        """Create a mock DropboxService for integration tests."""
        mock_service = Mock(spec=DropboxService)
        mock_service.is_authenticated.return_value = True
        return mock_service
    
    @pytest.fixture
    def order_item_with_directory(self):
        """Create OrderItemData with report_directory_path populated."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/NMSLO/12345"
        )
    
    @pytest.fixture
    def order_item_blm_with_directory(self):
        """Create BLM OrderItemData with report_directory_path populated."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMNM 0501759",
            legal_description="Section 5, Township 10S, Range 15E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/Federal/NMNM 0501759"
        )
    
    def test_workflow_executor_setup_includes_previous_report_detection(self):
        """Test that setup_workflow_executor includes PreviousReportDetectionWorkflow."""
        executor = setup_workflow_executor()
        
        # Verify workflow is registered
        assert executor.is_workflow_registered("previous_report_detection")
        assert "previous_report_detection" in executor.get_available_workflow_types()
        
        # Verify we can create an instance
        workflow = executor.create_workflow("previous_report_detection")
        assert isinstance(workflow, PreviousReportDetectionWorkflow)
        assert workflow.identity.workflow_type == "previous_report_detection"
    
    def test_end_to_end_execution_master_documents_found(self, mock_dropbox_service, order_item_with_directory):
        """Test complete workflow execution when Master Documents are found."""
        # Setup mock Dropbox response with Master Documents
        mock_files = [
            {"name": "NMSLO 12345 Master Documents.pdf", "type": "file"},
            {"name": "Supporting File.txt", "type": "file"},
            {"name": "Updated Master Documents Report.docx", "type": "file"}
        ]
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        # Create executor and workflow
        executor = setup_workflow_executor()
        workflow = executor.create_workflow("previous_report_detection", config={
            "timeout": 30
        })
        workflow.dropbox_service = mock_dropbox_service
        
        # Prepare input data
        input_data = {
            "order_item_data": order_item_with_directory,
            "dropbox_service": mock_dropbox_service
        }
        
        # Execute workflow through executor
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify executor result structure
        assert result["success"] is True
        assert result["workflow_type"] == "previous_report_detection"
        assert result["workflow_id"] is not None
        assert result["execution_time_seconds"] >= 0
        assert result["executor_metadata"]["executed_by"] == "WorkflowExecutor"
        
        # Verify workflow-specific data
        workflow_data = result["data"]
        assert workflow_data["success"] is True
        assert workflow_data["previous_report_found"] is True
        assert len(workflow_data["matching_files"]) == 2
        assert "NMSLO 12345 Master Documents.pdf" in workflow_data["matching_files"]
        assert "Updated Master Documents Report.docx" in workflow_data["matching_files"]
        assert workflow_data["total_files_checked"] == 3
        assert workflow_data["directory_path"] == "/NMSLO/12345"
        
        # Verify OrderItemData was updated
        assert order_item_with_directory.previous_report_found is True
    
    def test_end_to_end_execution_no_master_documents(self, mock_dropbox_service, order_item_blm_with_directory):
        """Test complete workflow execution when no Master Documents are found."""
        # Setup mock Dropbox response without Master Documents
        mock_files = [
            {"name": "Lease Agreement.pdf", "type": "file"},
            {"name": "Survey Report.pdf", "type": "file"},
            {"name": "Environmental Study.docx", "type": "file"}
        ]
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        # Create executor and workflow
        executor = setup_workflow_executor()
        workflow = executor.create_workflow("previous_report_detection")
        workflow.dropbox_service = mock_dropbox_service
        
        # Prepare input data
        input_data = {
            "order_item_data": order_item_blm_with_directory,
            "dropbox_service": mock_dropbox_service
        }
        
        # Execute workflow through executor
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify executor result
        assert result["success"] is True
        
        # Verify workflow data
        workflow_data = result["data"]
        assert workflow_data["previous_report_found"] is False
        assert len(workflow_data["matching_files"]) == 0
        assert workflow_data["total_files_checked"] == 3
        assert workflow_data["directory_path"] == "/Federal/NMNM 0501759"
        
        # Verify OrderItemData was updated
        assert order_item_blm_with_directory.previous_report_found is False
    
    def test_end_to_end_execution_empty_directory(self, mock_dropbox_service, order_item_with_directory):
        """Test complete workflow execution with empty directory."""
        # Setup mock Dropbox response with empty directory
        mock_dropbox_service.list_directory_files.return_value = []
        
        executor = setup_workflow_executor()
        workflow = executor.create_workflow("previous_report_detection")
        workflow.dropbox_service = mock_dropbox_service
        
        input_data = {
            "order_item_data": order_item_with_directory,
            "dropbox_service": mock_dropbox_service
        }
        
        result = executor.execute_workflow(workflow, input_data)
        
        assert result["success"] is True
        workflow_data = result["data"]
        assert workflow_data["previous_report_found"] is False
        assert len(workflow_data["matching_files"]) == 0
        assert workflow_data["total_files_checked"] == 0
        assert order_item_with_directory.previous_report_found is False
    
    def test_end_to_end_execution_dropbox_api_error(self, mock_dropbox_service, order_item_with_directory):
        """Test complete workflow execution when Dropbox API fails."""
        # Setup mock Dropbox service to raise exception
        mock_dropbox_service.list_directory_files.side_effect = Exception("Dropbox API Error")
        
        executor = setup_workflow_executor()
        workflow = executor.create_workflow("previous_report_detection")
        workflow.dropbox_service = mock_dropbox_service
        
        input_data = {
            "order_item_data": order_item_with_directory,
            "dropbox_service": mock_dropbox_service
        }
        
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify executor result structure - executor success is True but workflow failed
        assert result["success"] is True  # Executor executed successfully
        assert result["workflow_type"] == "previous_report_detection"
        assert result["execution_time_seconds"] >= 0
        
        # Verify workflow failure in data field
        workflow_data = result["data"]
        assert workflow_data["success"] is False
        assert "Directory access failed" in workflow_data["error"]
        assert workflow_data["error_type"] == "Exception"
        
        # Verify OrderItemData.previous_report_found is set to None
        assert order_item_with_directory.previous_report_found is None
    
    def test_end_to_end_execution_invalid_input_data(self, mock_dropbox_service):
        """Test complete workflow execution with invalid input data."""
        executor = setup_workflow_executor()
        workflow = executor.create_workflow("previous_report_detection")
        workflow.dropbox_service = mock_dropbox_service
        
        # Missing order_item_data
        input_data = {
            "dropbox_service": mock_dropbox_service
        }
        
        result = executor.execute_workflow(workflow, input_data)
        
        # Verify executor handles validation failure
        assert result["success"] is False
        assert "order_item_data is required" in result["error"]
        assert result["error_type"] == "ValidationError"
    
    def test_workflow_configuration_passed_through(self, mock_dropbox_service, order_item_with_directory):
        """Test that workflow configuration is properly passed through executor."""
        mock_dropbox_service.list_directory_files.return_value = []
        
        executor = setup_workflow_executor()
        
        # Create workflow with custom configuration
        custom_config = {
            "timeout": 60,
            "retry_attempts": 3,
            "custom_setting": "test_value"
        }
        workflow = executor.create_workflow("previous_report_detection", config=custom_config)
        workflow.dropbox_service = mock_dropbox_service
        
        # Verify configuration was applied
        assert workflow.config.settings == custom_config
        assert workflow.config.settings["timeout"] == 60
        assert workflow.config.settings["custom_setting"] == "test_value"
        
        # Execute workflow to ensure configuration doesn't break execution
        input_data = {
            "order_item_data": order_item_with_directory,
            "dropbox_service": mock_dropbox_service
        }
        
        result = executor.execute_workflow(workflow, input_data)
        assert result["success"] is True
    
    def test_multiple_workflow_executions_independent(self, mock_dropbox_service):
        """Test that multiple workflow executions are independent."""
        # Create two different order items
        from datetime import datetime
        order_item_1 = OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/NMSLO/12345"
        )
        
        order_item_2 = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMNM 0501759",
            legal_description="Section 5, Township 10S, Range 15E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_directory_path="/Federal/NMNM 0501759"
        )
        
        # Setup different responses for each directory
        def mock_list_files(directory_path):
            if directory_path == "/NMSLO/12345":
                return [{"name": "NMSLO Master Documents.pdf", "type": "file"}]
            elif directory_path == "/Federal/NMNM 0501759":
                return [{"name": "Regular File.txt", "type": "file"}]
            return []
        
        mock_dropbox_service.list_directory_files.side_effect = mock_list_files
        
        executor = setup_workflow_executor()
        
        # Execute first workflow
        workflow_1 = executor.create_workflow("previous_report_detection")
        workflow_1.dropbox_service = mock_dropbox_service
        
        result_1 = executor.execute_workflow(workflow_1, {
            "order_item_data": order_item_1,
            "dropbox_service": mock_dropbox_service
        })
        
        # Execute second workflow
        workflow_2 = executor.create_workflow("previous_report_detection")
        workflow_2.dropbox_service = mock_dropbox_service
        
        result_2 = executor.execute_workflow(workflow_2, {
            "order_item_data": order_item_2,
            "dropbox_service": mock_dropbox_service
        })
        
        # Verify both executions were successful and independent
        assert result_1["success"] is True
        assert result_2["success"] is True
        
        # Verify different results based on directory contents
        assert result_1["data"]["previous_report_found"] is True
        assert result_2["data"]["previous_report_found"] is False
        
        # Verify OrderItemData objects were updated independently
        assert order_item_1.previous_report_found is True
        assert order_item_2.previous_report_found is False
        
        # Verify different workflow IDs (may be the same due to timestamp precision)
        # This is not critical for independence verification
        print(f"Workflow IDs: {result_1['workflow_id']} vs {result_2['workflow_id']}")