"""
Integration tests for real order processing workflows.

Simple tests that simulate real order processing workflows using the configuration system.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.core.processors import NMSLOOrderProcessor, FederalOrderProcessor
from src.core.config.factory import get_agency_config, get_static_config, get_behavioral_config


class TestWorkflowIntegration:
    """Test real order processing workflows with configuration system."""

    def test_nmslo_workflow_with_configuration(self):
        """Test complete NMSLO order processing workflow with configuration."""
        # Create realistic test data
        test_data = pd.DataFrame({
            'Lease': ['B-1234-5', 'B-6789-0', 'B-1111-2'],
            'Requested Legal': ['Legal Description 1', 'Legal Description 2', 'Legal Description 3'],
            'Report Start Date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        # Mock the Excel file reading
        with patch('pandas.read_excel', return_value=test_data):
            # Create processor with configuration
            processor = NMSLOOrderProcessor(
                order_form="test_file.xlsx",
                agency="NMSLO",
                order_type="Runsheet",
                order_date="2024-01-01",
                order_number="12345"
            )
            
            # Process the data
            processed_data = processor.process_data()
            
            # Verify the workflow worked correctly
            assert len(processed_data) == 3
            
            # Check metadata columns were added
            assert 'Agency' in processed_data.columns
            assert 'Order Type' in processed_data.columns
            assert 'Order Number' in processed_data.columns
            assert 'Order Date' in processed_data.columns
            
            # Check data columns are preserved
            assert 'Lease' in processed_data.columns
            assert 'Requested Legal' in processed_data.columns
            assert 'Report Start Date' in processed_data.columns
            
            # Check search columns were added (from behavioral config)
            assert 'Full Search' in processed_data.columns
            assert 'Partial Search' in processed_data.columns
            
            # Check blank columns were added (from behavioral config)
            assert 'New Format' in processed_data.columns
            assert 'Tractstar' in processed_data.columns
            assert 'Old Format' in processed_data.columns
            assert 'MI Index' in processed_data.columns
            assert 'Documents' in processed_data.columns
            assert 'Search Notes' in processed_data.columns
            assert 'Link' in processed_data.columns
            
            # Verify data values
            assert processed_data['Agency'].iloc[0] == "NMSLO"
            assert processed_data['Order Type'].iloc[0] == "Runsheet"
            assert processed_data['Order Number'].iloc[0] == "12345"
            assert processed_data['Lease'].iloc[0] == "B-1234-5"

    def test_federal_workflow_with_configuration(self):
        """Test complete Federal order processing workflow with configuration."""
        # Create realistic test data with Notes column
        test_data = pd.DataFrame({
            'Lease': ['NMNM 12345A', 'NMNM 67890B', 'NMNM 11111C'],
            'Requested Legal': ['Federal Legal 1', 'Federal Legal 2', 'Federal Legal 3'],
            'Report Start Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Notes': ['Note 1', 'Note 2', 'Note 3']
        })
        
        # Mock the Excel file reading
        with patch('pandas.read_excel', return_value=test_data):
            # Create processor with configuration
            processor = FederalOrderProcessor(
                order_form="test_file.xlsx",
                agency="Federal",
                order_type="Runsheet",
                order_date="2024-01-01",
                order_number="54321"
            )
            
            # Process the data
            processed_data = processor.process_data()
            
            # Verify the workflow worked correctly
            assert len(processed_data) == 3
            
            # Check metadata columns were added
            assert 'Agency' in processed_data.columns
            assert 'Order Type' in processed_data.columns
            assert 'Order Number' in processed_data.columns
            assert 'Order Date' in processed_data.columns
            
            # Check data columns are preserved
            assert 'Lease' in processed_data.columns
            assert 'Requested Legal' in processed_data.columns
            assert 'Report Start Date' in processed_data.columns
            assert 'Notes' in processed_data.columns  # Federal-specific
            
            # Check search columns were added (from behavioral config)
            assert 'Files Search' in processed_data.columns
            assert 'Tractstar Search' in processed_data.columns
            
            # Check blank columns were added (from behavioral config)
            assert 'New Format' in processed_data.columns
            assert 'Tractstar' in processed_data.columns
            assert 'Documents' in processed_data.columns
            assert 'Search Notes' in processed_data.columns
            assert 'Link' in processed_data.columns
            
            # Verify data values
            assert processed_data['Agency'].iloc[0] == "Federal"
            assert processed_data['Order Type'].iloc[0] == "Runsheet"
            assert processed_data['Order Number'].iloc[0] == "54321"
            assert processed_data['Lease'].iloc[0] == "NMNM 12345A"
            assert processed_data['Notes'].iloc[0] == "Note 1"

    def test_configuration_integration_in_workflow(self):
        """Test that configuration is properly integrated throughout the workflow."""
        # Get configurations
        nmslo_config = get_agency_config("NMSLO")
        federal_config = get_agency_config("Federal")
        
        # Verify configurations are available
        assert nmslo_config is not None
        assert federal_config is not None
        
        # Test static configuration integration
        nmslo_static = get_static_config("NMSLO")
        federal_static = get_static_config("Federal")
        
        assert nmslo_static.dropbox_agency_name == "NMSLO"
        assert federal_static.dropbox_agency_name == "Federal"
        
        # Test behavioral configuration integration
        nmslo_behavioral = get_behavioral_config("NMSLO")
        federal_behavioral = get_behavioral_config("Federal")
        
        assert "Full Search" in nmslo_behavioral.search_mappings
        assert "Files Search" in federal_behavioral.search_mappings
        
        # Test column generation integration
        nmslo_columns = nmslo_behavioral.get_search_columns()
        federal_columns = federal_behavioral.get_search_columns()
        
        assert "Full Search" in nmslo_columns
        assert "Files Search" in federal_columns

    def test_workflow_with_custom_configuration(self):
        """Test workflow with custom injected configuration."""
        # Create custom configurations
        from tests.core.config.test_utils import create_mock_static_config, create_mock_behavioral_config
        
        custom_static = create_mock_static_config("CustomAgency")
        custom_behavioral = create_mock_behavioral_config()
        
        # Create test data
        test_data = pd.DataFrame({
            'Lease': ['CUSTOM-123'],
            'Requested Legal': ['Custom Legal'],
            'Report Start Date': ['2024-01-01']
        })
        
        # Mock the Excel file reading
        with patch('pandas.read_excel', return_value=test_data):
            # Create processor with custom configuration
            processor = NMSLOOrderProcessor(
                order_form="test_file.xlsx",
                agency="CustomAgency",
                order_type="Custom Order",
                order_date="2024-01-01",
                order_number="99999",
                static_config=custom_static,
                behavioral_config=custom_behavioral
            )
            
            # Process the data
            processed_data = processor.process_data()
            
            # Verify custom configuration was used
            assert len(processed_data) == 1
            assert processed_data['Agency'].iloc[0] == "CustomAgency"
            assert processed_data['Order Type'].iloc[0] == "Custom Order"
            
            # Check that custom behavioral config was used
            assert 'Test Search' in processed_data.columns
            assert 'Another Search' in processed_data.columns 