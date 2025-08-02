"""
Unit tests for LeaseDirectorySearchWorkflow.

Tests the workflow logic with mock Dropbox operations to ensure proper functionality
without requiring real Dropbox authentication.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

from src.core.workflows.lease_directory_search import LeaseDirectorySearchWorkflow
from src.core.workflows.base import WorkflowConfig
from src.core.models import OrderItemData, AgencyType
from src.integrations.dropbox.service import DropboxService, DropboxAuthenticationError


class TestLeaseDirectorySearchWorkflow:
    """Test LeaseDirectorySearchWorkflow class."""
    
    def test_initialization_default(self):
        """Test workflow initializes with default parameters."""
        workflow = LeaseDirectorySearchWorkflow()
        
        assert workflow.dropbox_service is None
        assert isinstance(workflow.config, WorkflowConfig)
        assert workflow.identity.workflow_type == "lease_directory_search"
        assert workflow.identity.workflow_name == "Lease Directory Search"
    
    def test_initialization_with_dropbox_service(self):
        """Test workflow initializes with DropboxService."""
        mock_service = Mock(spec=DropboxService)
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        
        assert workflow.dropbox_service == mock_service
    
    def test_initialization_with_config(self):
        """Test workflow initializes with custom config."""
        config = WorkflowConfig(settings={"timeout": 60})
        workflow = LeaseDirectorySearchWorkflow(config=config)
        
        assert workflow.config == config
        assert workflow.config.settings["timeout"] == 60
    
    def test_set_dropbox_service(self):
        """Test setting DropboxService after initialization."""
        workflow = LeaseDirectorySearchWorkflow()
        mock_service = Mock(spec=DropboxService)
        
        workflow.set_dropbox_service(mock_service)
        
        assert workflow.dropbox_service == mock_service


class TestWorkflowValidation:
    """Test input validation for LeaseDirectorySearchWorkflow."""
    
    def test_validate_inputs_missing_order_item_data(self):
        """Test validation fails when order_item_data is missing."""
        workflow = LeaseDirectorySearchWorkflow()
        
        is_valid, error = workflow.validate_inputs({})
        
        assert is_valid is False
        assert error == "order_item_data is required"
    
    def test_validate_inputs_invalid_order_item_data_type(self):
        """Test validation fails when order_item_data is wrong type."""
        workflow = LeaseDirectorySearchWorkflow()
        
        is_valid, error = workflow.validate_inputs({"order_item_data": "not_an_object"})
        
        assert is_valid is False
        assert error == "order_item_data must be an OrderItemData instance"
    
    def test_validate_inputs_missing_agency(self):
        """Test validation fails when agency is missing."""
        workflow = LeaseDirectorySearchWorkflow()
        
        # Test that OrderItemData itself prevents None agency
        with pytest.raises(ValueError, match="agency must be an AgencyType enum value"):
            OrderItemData(
                agency=None,  # Missing agency
                lease_number="12345",
                legal_description="Test",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
    
    def test_validate_inputs_empty_lease_number(self):
        """Test validation fails when lease_number is empty."""
        workflow = LeaseDirectorySearchWorkflow()
        
        # Test that OrderItemData itself prevents empty lease number
        with pytest.raises(ValueError, match="lease_number cannot be empty"):
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="",  # Empty lease number
                legal_description="Test", 
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
    
    def test_validate_inputs_missing_dropbox_service(self):
        """Test validation fails when DropboxService is not provided."""
        workflow = LeaseDirectorySearchWorkflow()  # No DropboxService
        order_item = OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Test",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        is_valid, error = workflow.validate_inputs({"order_item_data": order_item})
        
        assert is_valid is False
        assert error == "DropboxService is required for directory search"
    
    def test_validate_inputs_success(self):
        """Test validation succeeds with valid inputs."""
        mock_service = Mock(spec=DropboxService)
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Test",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        
        is_valid, error = workflow.validate_inputs({"order_item_data": order_item})
        
        assert is_valid is True
        assert error is None


class TestAgencyMapping:
    """Test agency type mapping functionality."""
    
    def test_map_agency_type_nmslo(self):
        """Test NMSLO agency mapping."""
        workflow = LeaseDirectorySearchWorkflow()
        
        result = workflow._map_agency_type_to_string(AgencyType.NMSLO)
        
        assert result == "NMSLO"
    
    def test_map_agency_type_blm(self):
        """Test BLM agency mapping to Federal."""
        workflow = LeaseDirectorySearchWorkflow()
        
        result = workflow._map_agency_type_to_string(AgencyType.BLM)
        
        assert result == "Federal"
    
    def test_map_agency_type_invalid(self):
        """Test mapping invalid agency type raises error."""
        workflow = LeaseDirectorySearchWorkflow()
        
        with pytest.raises(ValueError, match="Unsupported agency type"):
            workflow._map_agency_type_to_string("INVALID_AGENCY")


class TestWorkflowExecution:
    """Test workflow execution scenarios."""
    
    def create_test_order_item(self, agency=AgencyType.NMSLO, lease_number="12345"):
        """Helper to create test OrderItemData."""
        return OrderItemData(
            agency=agency,
            lease_number=lease_number,
            legal_description="Test legal description",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
    
    def test_execute_success_nmslo_directory_found(self):
        """Test successful execution with NMSLO agency - directory found."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.return_value = {
            "path": "/NMSLO/12345",
            "shareable_link": "https://dropbox.com/share/nmslo12345"
        }
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item(AgencyType.NMSLO, "12345")
        input_data = {"order_item_data": order_item}
        
        result = workflow.execute(input_data)
        
        # Verify DropboxService was called with the resolved path (SOLID principle)
        mock_service.search_directory_with_metadata.assert_called_once_with("/NMSLO/12345")
        
        # Verify result
        assert result["success"] is True
        assert result["shareable_link"] == "https://dropbox.com/share/nmslo12345"
        assert result["directory_path"] == "/NMSLO/12345"
        assert result["agency"] == "NMSLO"
        assert result["lease_number"] == "12345"
        assert "Successfully found directory" in result["message"]
        
        # Verify OrderItemData was updated
        assert order_item.report_directory_link == "https://dropbox.com/share/nmslo12345"
        assert order_item.report_directory_path == "/NMSLO/12345"
    
    def test_execute_success_blm_directory_found(self):
        """Test successful execution with BLM agency - directory found."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.return_value = {
            "path": "/Federal/NMNM 0501759",
            "shareable_link": "https://dropbox.com/share/federal67890"
        }
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item(AgencyType.BLM, "NMNM 0501759")
        input_data = {"order_item_data": order_item}
        
        result = workflow.execute(input_data)
        
        # Verify DropboxService was called with the resolved path (SOLID principle)
        mock_service.search_directory_with_metadata.assert_called_once_with("/Federal/NMNM 0501759")
        
        # Verify result
        assert result["success"] is True
        assert result["shareable_link"] == "https://dropbox.com/share/federal67890"
        assert result["directory_path"] == "/Federal/NMNM 0501759"
        assert result["agency"] == "Federal"
        assert result["lease_number"] == "NMNM 0501759"
        
        # Verify OrderItemData was updated
        assert order_item.report_directory_link == "https://dropbox.com/share/federal67890"
        assert order_item.report_directory_path == "/Federal/NMNM 0501759"
    
    def test_execute_success_directory_not_found(self):
        """Test successful execution - directory not found."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.return_value = {
            "path": None,
            "shareable_link": None
        }  # Directory not found
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item(AgencyType.NMSLO, "NOTFOUND")
        input_data = {"order_item_data": order_item}
        
        result = workflow.execute(input_data)
        
        # Verify DropboxService was called with the resolved path
        mock_service.search_directory_with_metadata.assert_called_once_with("/NMSLO/NOTFOUND")
        
        # Verify result
        assert result["success"] is True
        assert result["shareable_link"] is None
        assert result["directory_path"] is None
        assert result["agency"] == "NMSLO"
        assert result["lease_number"] == "NOTFOUND"
        assert "No directory found" in result["message"]
        
        # Verify OrderItemData was not updated
        assert order_item.report_directory_link is None
        assert order_item.report_directory_path is None
    
    def test_execute_handles_whitespace_in_lease_number(self):
        """Test execution handles whitespace in lease number."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.return_value = {
            "path": "/NMSLO/12345",
            "shareable_link": "https://dropbox.com/share/test"
        }
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item(AgencyType.NMSLO, "  12345  ")  # With whitespace
        input_data = {"order_item_data": order_item}
        
        result = workflow.execute(input_data)
        
        # Verify whitespace was stripped in path building
        mock_service.search_directory_with_metadata.assert_called_once_with("/NMSLO/12345")
        
        assert result["lease_number"] == "12345"  # Should be stripped in result too
    
    def test_execute_dropbox_authentication_error(self):
        """Test execution handles DropboxAuthenticationError."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.side_effect = DropboxAuthenticationError("Not authenticated")
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item()
        input_data = {"order_item_data": order_item}
        
        # Should raise the error (handled by executor)
        with pytest.raises(DropboxAuthenticationError):
            workflow.execute(input_data)
    
    def test_execute_generic_error(self):
        """Test execution handles generic errors."""
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.side_effect = Exception("Network error")
        
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        order_item = self.create_test_order_item()
        input_data = {"order_item_data": order_item}
        
        # Should raise the error (handled by executor)
        with pytest.raises(Exception, match="Network error"):
            workflow.execute(input_data)


class TestWorkflowInfo:
    """Test workflow information and metadata."""
    
    def test_get_workflow_info_without_dropbox(self):
        """Test workflow info when DropboxService is not available."""
        workflow = LeaseDirectorySearchWorkflow()
        
        info = workflow.get_workflow_info()
        
        assert info["identity"]["workflow_type"] == "lease_directory_search"
        assert info["identity"]["workflow_name"] == "Lease Directory Search"
        assert info["workflow_specific"]["supported_agencies"] == ["NMSLO", "BLM"]
        assert info["workflow_specific"]["dropbox_service_available"] is False
        assert info["workflow_specific"]["agency_mappings"]["NMSLO"] == "NMSLO"
        assert info["workflow_specific"]["agency_mappings"]["BLM"] == "Federal"
    
    def test_get_workflow_info_with_dropbox(self):
        """Test workflow info when DropboxService is available."""
        mock_service = Mock(spec=DropboxService)
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        
        info = workflow.get_workflow_info()
        
        assert info["workflow_specific"]["dropbox_service_available"] is True


class TestWorkflowIntegration:
    """Integration tests for complete workflow scenarios."""
    
    def test_full_workflow_lifecycle_success(self):
        """Test complete workflow lifecycle with successful directory search."""
        # Setup
        mock_service = Mock(spec=DropboxService)
        mock_service.search_directory_with_metadata.return_value = {
            "path": "/Federal/NMNM 0501759",
            "shareable_link": "https://dropbox.com/share/success"
        }
        
        config = WorkflowConfig(settings={"timeout": 30})
        workflow = LeaseDirectorySearchWorkflow(config=config, dropbox_service=mock_service)
        
        order_item = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMNM 0501759",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )
        input_data = {"order_item_data": order_item}
        
        # Validate inputs
        is_valid, error = workflow.validate_inputs(input_data)
        assert is_valid is True
        
        # Execute workflow
        result = workflow.execute(input_data)
        
        # Verify complete workflow success
        assert result["success"] is True
        assert result["shareable_link"] == "https://dropbox.com/share/success"
        assert result["directory_path"] == "/Federal/NMNM 0501759"
        assert result["agency"] == "Federal"  # BLM maps to Federal
        assert result["lease_number"] == "NMNM 0501759"
        
        # Verify integration with OrderItemData
        assert order_item.report_directory_link == "https://dropbox.com/share/success"
        assert order_item.report_directory_path == "/Federal/NMNM 0501759"
        
        # Verify DropboxService integration with path-based approach
        mock_service.search_directory_with_metadata.assert_called_once_with("/Federal/NMNM 0501759")
    
    def test_workflow_with_various_lease_formats(self):
        """Test workflow handles various lease number formats."""
        mock_service = Mock(spec=DropboxService)
        workflow = LeaseDirectorySearchWorkflow(dropbox_service=mock_service)
        
        test_cases = [
            ("12345", "NMSLO"),
            ("NMNM 0501759", "Federal"),
            ("NM-123456", "NMSLO"),
            ("  NMNM 98765  ", "Federal"),  # With whitespace
        ]
        
        for lease_number, expected_agency in test_cases:
            mock_service.reset_mock()
            mock_service.search_directory_with_metadata.return_value = {
                "path": f"/{expected_agency}/{lease_number.strip()}",
                "shareable_link": f"https://dropbox.com/share/{lease_number.strip()}"
            }
            
            agency_type = AgencyType.NMSLO if expected_agency == "NMSLO" else AgencyType.BLM
            order_item = OrderItemData(
                agency=agency_type,
                lease_number=lease_number,
                legal_description="Test",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
            
            result = workflow.execute({"order_item_data": order_item})
            
            # Verify correct path building and lease number handling
            expected_path = f"/{expected_agency}/{lease_number.strip()}"
            mock_service.search_directory_with_metadata.assert_called_once_with(expected_path)
            assert result["success"] is True
            assert result["agency"] == expected_agency