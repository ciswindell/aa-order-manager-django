"""
Unit Tests for Previous Report Detection Workflow

Tests the PreviousReportDetectionWorkflow with mocked DropboxService and various file scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.workflows.previous_report_detection import PreviousReportDetectionWorkflow
from src.core.workflows.base import WorkflowConfig
from src.core.models import OrderItemData, AgencyType, ReportType
from src.integrations.dropbox.service import DropboxService


class TestPreviousReportDetectionWorkflow:
    """Test cases for PreviousReportDetectionWorkflow."""
    
    @pytest.fixture
    def workflow_config(self):
        """Create a basic workflow configuration."""
        return WorkflowConfig(settings={})
    
    @pytest.fixture
    def mock_dropbox_service(self):
        """Create a mock DropboxService."""
        mock_service = Mock(spec=DropboxService)
        mock_service.is_authenticated.return_value = True
        return mock_service
    
    @pytest.fixture
    def workflow(self, workflow_config, mock_dropbox_service):
        """Create a PreviousReportDetectionWorkflow instance."""
        return PreviousReportDetectionWorkflow(
            config=workflow_config,
            dropbox_service=mock_dropbox_service
        )
    
    @pytest.fixture
    def valid_order_item_data(self):
        """Create valid OrderItemData with report_directory_path."""
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
    def order_item_without_directory(self):
        """Create OrderItemData without report_directory_path."""
        from datetime import datetime
        return OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
    
    def test_workflow_identity(self, workflow):
        """Test workflow identity creation."""
        identity = workflow.identity
        assert identity.workflow_type == "previous_report_detection"
        assert identity.workflow_name == "Previous Report Detection"
        assert identity.workflow_id is not None
    
    def test_validate_inputs_success(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test successful input validation."""
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        is_valid, error_message = workflow.validate_inputs(input_data)
        assert is_valid is True
        assert error_message is None
    
    def test_validate_inputs_missing_order_item_data(self, workflow):
        """Test validation failure when order_item_data is missing."""
        input_data = {}
        
        is_valid, error_message = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert "order_item_data is required" in error_message
    
    def test_validate_inputs_invalid_order_item_data_type(self, workflow):
        """Test validation failure when order_item_data is wrong type."""
        input_data = {
            "order_item_data": "not_an_order_item"
        }
        
        is_valid, error_message = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert "must be an OrderItemData instance" in error_message
    
    def test_validate_inputs_missing_directory_path(self, workflow, order_item_without_directory):
        """Test validation failure when report_directory_path is missing."""
        input_data = {
            "order_item_data": order_item_without_directory
        }
        
        is_valid, error_message = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert "report_directory_path is required" in error_message
    
    def test_validate_inputs_missing_dropbox_service(self, workflow, valid_order_item_data):
        """Test validation failure when DropboxService is missing."""
        # Create workflow without dropbox_service
        workflow_no_service = PreviousReportDetectionWorkflow()
        input_data = {
            "order_item_data": valid_order_item_data
        }
        
        is_valid, error_message = workflow_no_service.validate_inputs(input_data)
        assert is_valid is False
        assert "dropbox_service is required" in error_message
    
    def test_validate_inputs_unauthenticated_dropbox_service(self, workflow, valid_order_item_data):
        """Test validation failure when DropboxService is not authenticated."""
        mock_service = Mock(spec=DropboxService)
        mock_service.is_authenticated.return_value = False
        
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_service
        }
        
        is_valid, error_message = workflow.validate_inputs(input_data)
        assert is_valid is False
        assert "must be authenticated" in error_message
    
    def test_execute_master_documents_found(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test successful execution when Master Documents are found."""
        # Mock file listing with Master Documents
        mock_files = [
            {"name": "NMSLO 12345 Master Documents.pdf", "type": "file"},
            {"name": "Other File.txt", "type": "file"},
            {"name": "Another master documents file.docx", "type": "file"}
        ]
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        result = workflow.execute(input_data)
        
        # Verify result
        assert result["success"] is True
        assert result["previous_report_found"] is True
        assert len(result["matching_files"]) == 2
        assert "NMSLO 12345 Master Documents.pdf" in result["matching_files"]
        assert "Another master documents file.docx" in result["matching_files"]
        assert result["total_files_checked"] == 3
        assert result["directory_path"] == "/NMSLO/12345"
        
        # Verify OrderItemData was updated
        assert valid_order_item_data.previous_report_found is True
    
    def test_execute_no_master_documents_found(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test successful execution when no Master Documents are found."""
        # Mock file listing without Master Documents
        mock_files = [
            {"name": "Regular File.pdf", "type": "file"},
            {"name": "Another File.txt", "type": "file"}
        ]
        mock_dropbox_service.list_directory_files.return_value = mock_files
        
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        result = workflow.execute(input_data)
        
        # Verify result
        assert result["success"] is True
        assert result["previous_report_found"] is False
        assert len(result["matching_files"]) == 0
        assert result["total_files_checked"] == 2
        
        # Verify OrderItemData was updated
        assert valid_order_item_data.previous_report_found is False
    
    def test_execute_empty_directory(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test execution with empty directory."""
        mock_dropbox_service.list_directory_files.return_value = []
        
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        result = workflow.execute(input_data)
        
        assert result["success"] is True
        assert result["previous_report_found"] is False
        assert len(result["matching_files"]) == 0
        assert result["total_files_checked"] == 0
        assert valid_order_item_data.previous_report_found is False
    
    def test_execute_validation_failure(self, workflow):
        """Test execution with invalid inputs."""
        input_data = {}  # Missing required data
        
        result = workflow.execute(input_data)
        
        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "ValidationError"
    
    def test_execute_dropbox_api_error(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test execution when Dropbox API fails."""
        # Mock Dropbox service to raise an exception
        mock_dropbox_service.list_directory_files.side_effect = Exception("API Error")
        
        input_data = {
            "order_item_data": valid_order_item_data,
            "dropbox_service": mock_dropbox_service
        }
        
        result = workflow.execute(input_data)
        
        # Verify error handling
        assert result["success"] is False
        assert "Directory access failed" in result["error"]
        assert result["error_type"] == "Exception"
        assert result["directory_path"] == "/NMSLO/12345"
        
        # Verify OrderItemData.previous_report_found is set to None
        assert valid_order_item_data.previous_report_found is None
    
    def test_execute_unexpected_error(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test execution with unexpected error."""
        # Mock validation to raise an unexpected error
        with patch.object(workflow, 'validate_inputs', side_effect=RuntimeError("Unexpected error")):
            input_data = {
                "order_item_data": valid_order_item_data,
                "dropbox_service": mock_dropbox_service
            }
            
            result = workflow.execute(input_data)
            
            assert result["success"] is False
            assert "error" in result
            assert result["error_type"] == "RuntimeError"
            assert valid_order_item_data.previous_report_found is None
    
    def test_pattern_matching_case_variations(self, workflow, valid_order_item_data, mock_dropbox_service):
        """Test pattern matching with various case combinations."""
        # Test files with different case variations
        test_files = [
            {"name": "Master Documents.pdf", "should_match": True},
            {"name": "master documents.pdf", "should_match": True},
            {"name": "MASTER DOCUMENTS.pdf", "should_match": True},
            {"name": "Master documents report.pdf", "should_match": True},
            {"name": "Prefix Master Documents Suffix.pdf", "should_match": True},
            {"name": "MasterDocuments.pdf", "should_match": False},  # Missing space
            {"name": "Master Document.pdf", "should_match": False},  # Missing 's'
            {"name": "Documents Master.pdf", "should_match": False},  # Wrong order
        ]
        
        for test_file in test_files:
            mock_dropbox_service.list_directory_files.return_value = [test_file]
            
            # Reset the order item data
            valid_order_item_data.previous_report_found = None
            
            input_data = {
                "order_item_data": valid_order_item_data,
                "dropbox_service": mock_dropbox_service
            }
            
            result = workflow.execute(input_data)
            
            if test_file["should_match"]:
                assert result["previous_report_found"] is True, f"Should match: {test_file['name']}"
                assert len(result["matching_files"]) == 1
            else:
                assert result["previous_report_found"] is False, f"Should not match: {test_file['name']}"
                assert len(result["matching_files"]) == 0