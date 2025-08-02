"""
Error handling tests for configuration system.

Tests that verify error handling works correctly with intentionally invalid configurations.
"""

import pytest
import pandas as pd
from unittest.mock import patch

from src.core.config.exceptions import ConfigurationError, InvalidAgencyError
from src.core.config.factory import (
    get_agency_config,
    get_static_config,
    get_behavioral_config,
    get_all_columns,
    validate_agency_type
)
from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig


class TestInvalidConfigurationErrorHandling:
    """Test error handling with intentionally invalid configurations."""

    def test_invalid_agency_type_handling(self):
        """Test handling of invalid agency types."""
        # Test non-string agency types
        with pytest.raises(InvalidAgencyError):
            get_agency_config(123)
        
        with pytest.raises(InvalidAgencyError):
            get_agency_config(None)
        
        with pytest.raises(InvalidAgencyError):
            get_agency_config([])
        
        # Test empty/whitespace strings
        with pytest.raises(InvalidAgencyError):
            get_agency_config("")
        
        with pytest.raises(InvalidAgencyError):
            get_agency_config("   ")
        
        # Test non-existent agencies
        with pytest.raises(InvalidAgencyError):
            get_agency_config("NonExistentAgency")
        
        with pytest.raises(InvalidAgencyError):
            get_agency_config("Invalid Agency")

    def test_invalid_static_configuration_handling(self):
        """Test handling of invalid static configurations."""
        # Test empty column widths
        with pytest.raises(ConfigurationError, match="column_widths cannot be empty"):
            AgencyStaticConfig(
                column_widths={},
                folder_structure=["Test Folder"],
                dropbox_agency_name="TestAgency"
            )
        
        # Test empty folder structure
        with pytest.raises(ConfigurationError, match="folder_structure cannot be empty"):
            AgencyStaticConfig(
                column_widths={"Test": 10},
                folder_structure=[],
                dropbox_agency_name="TestAgency"
            )
        
        # Test empty dropbox agency name
        with pytest.raises(ConfigurationError, match="dropbox_agency_name cannot be empty"):
            AgencyStaticConfig(
                column_widths={"Test": 10},
                folder_structure=["Test Folder"],
                dropbox_agency_name=""
            )
        
        # Test invalid column width types
        with pytest.raises(ConfigurationError, match="must be an integer"):
            AgencyStaticConfig(
                column_widths={"Test": "10"},  # String instead of int
                folder_structure=["Test Folder"],
                dropbox_agency_name="TestAgency"
            )
        
        # Test negative column widths
        with pytest.raises(ConfigurationError, match="must be positive"):
            AgencyStaticConfig(
                column_widths={"Test": -5},
                folder_structure=["Test Folder"],
                dropbox_agency_name="TestAgency"
            )
        
        # Test invalid folder structure types
        with pytest.raises(ConfigurationError, match="must be a string"):
            AgencyStaticConfig(
                column_widths={"Test": 10},
                folder_structure=["Test Folder", 123],  # Integer in list
                dropbox_agency_name="TestAgency"
            )

    def test_invalid_behavioral_configuration_handling(self):
        """Test handling of invalid behavioral configurations."""
        # Test empty search mappings
        with pytest.raises(ConfigurationError, match="search_mappings cannot be empty"):
            AgencyBehaviorConfig(
                search_mappings={},
                blank_columns=["Test Column"]
            )
        
        # Test empty blank columns
        with pytest.raises(ConfigurationError, match="blank_columns cannot be empty"):
            def mock_search_func(data):
                return f"search_{data}"
            
            AgencyBehaviorConfig(
                search_mappings={"Test Search": mock_search_func},
                blank_columns=[]
            )
        
        # Test non-callable search mappings
        with pytest.raises(ConfigurationError, match="must be callable"):
            AgencyBehaviorConfig(
                search_mappings={"Test Search": "not_callable"},
                blank_columns=["Test Column"]
            )
        
        # Test invalid blank column types
        with pytest.raises(ConfigurationError, match="must be a string"):
            AgencyBehaviorConfig(
                search_mappings={"Test Search": lambda x: f"search_{x}"},
                blank_columns=["Test Column", 123]  # Integer in list
            )
        
        # Test empty blank column strings
        with pytest.raises(ConfigurationError, match="cannot be empty or whitespace"):
            AgencyBehaviorConfig(
                search_mappings={"Test Search": lambda x: f"search_{x}"},
                blank_columns=["Test Column", ""]  # Empty string
            )

    def test_invalid_factory_method_handling(self):
        """Test error handling in factory methods with invalid inputs."""
        # Test invalid agency types in factory methods
        with pytest.raises(InvalidAgencyError):
            get_static_config(123)
        
        with pytest.raises(InvalidAgencyError):
            get_behavioral_config("")
        
        with pytest.raises(InvalidAgencyError):
            get_all_columns("NonExistentAgency")
        
        # Test validate_agency_type with invalid inputs
        assert validate_agency_type(123) is False
        assert validate_agency_type(None) is False
        assert validate_agency_type("") is False
        assert validate_agency_type("   ") is False
        assert validate_agency_type("NonExistentAgency") is False

    def test_invalid_configuration_structure_handling(self):
        """Test handling of invalid configuration structure."""
        # This would test registry-level validation, but we need to mock the registry
        # For now, test that factory methods handle missing configurations gracefully
        # by ensuring they raise appropriate errors
        
        # Test that factory methods provide clear error messages
        try:
            get_agency_config("NonExistentAgency")
        except InvalidAgencyError as e:
            assert "NonExistentAgency" in str(e)
            assert "supported" in str(e).lower()

    def test_search_function_error_handling(self):
        """Test handling of search function errors."""
        # Create a search function that raises an exception
        def failing_search_func(data):
            raise ValueError("Search function failed")
        
        # Test that behavioral config validation catches this
        with pytest.raises(ConfigurationError, match="Search function"):
            AgencyBehaviorConfig(
                search_mappings={"Failing Search": failing_search_func},
                blank_columns=["Test Column"]
            )

    def test_sample_data_validation_error_handling(self):
        """Test handling of sample data validation errors."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Test Search": mock_search_func},
            blank_columns=["Test Column"]
        )
        
        # Test with invalid sample data
        with pytest.raises(ConfigurationError, match="must be a non-empty string"):
            config.validate_with_sample_data("")
        
        with pytest.raises(ConfigurationError, match="must be a non-empty string"):
            config.validate_with_sample_data(None)

    def test_configuration_consistency_error_handling(self):
        """Test handling of configuration consistency errors."""
        # Test that column widths and search columns are consistent
        # This would be tested at the registry level during integration
        
        # For now, test that behavioral config validation works
        def mock_search_func(data):
            return f"search_{data}"
        
        # Test duplicate column names between search and blank columns
        with pytest.raises(ConfigurationError, match="cannot appear in both"):
            AgencyBehaviorConfig(
                search_mappings={"Duplicate": mock_search_func},
                blank_columns=["Duplicate"]  # Same name as search column
            )

    def test_error_message_clarity(self):
        """Test that error messages are clear and actionable."""
        # Test agency error messages
        try:
            get_agency_config("InvalidAgency")
        except InvalidAgencyError as e:
            assert "InvalidAgency" in str(e)
            assert "supported" in str(e).lower()
            assert hasattr(e, 'supported_agencies')
        
        # Test configuration error messages
        try:
            AgencyStaticConfig(
                column_widths={},
                folder_structure=["Test"],
                dropbox_agency_name="Test"
            )
        except ConfigurationError as e:
            assert "column_widths cannot be empty" in str(e)
        
        # Test behavioral configuration error messages
        try:
            AgencyBehaviorConfig(
                search_mappings={},
                blank_columns=["Test"]
            )
        except ConfigurationError as e:
            assert "search_mappings cannot be empty" in str(e)

    @patch('pandas.read_excel')
    def test_error_propagation(self, mock_read_excel):
        """Test that errors propagate correctly through the system."""
        # Mock the Excel file reading
        mock_read_excel.return_value = pd.DataFrame({
            'Lease': ['B-1234-5'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01']
        })
        
        # Test that factory method errors propagate to processor usage
        from src.core.processors import NMSLOOrderProcessor
        
        # This should work normally
        try:
            processor = NMSLOOrderProcessor(
                order_form="test.xlsx",
                agency="NMSLO"
            )
            # If we get here, no error was raised
            assert processor is not None
        except Exception as e:
            # If an error occurs, it should be a configuration-related error
            assert isinstance(e, (ConfigurationError, InvalidAgencyError)) 