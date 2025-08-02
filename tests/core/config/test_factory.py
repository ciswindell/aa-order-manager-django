"""
Unit tests for configuration factory methods.

Simple tests for factory methods with valid and invalid inputs.
"""

import pytest

from src.core.config.exceptions import InvalidAgencyError, ConfigurationError
from src.core.config.factory import (
    get_agency_config,
    get_static_config,
    get_behavioral_config,
    get_supported_agencies,
    validate_agency_type,
    get_all_columns
)


class TestFactoryMethods:
    """Test configuration factory methods with valid and invalid inputs."""

    def test_get_agency_config_valid(self):
        """Test get_agency_config with valid agency types."""
        # Test NMSLO
        config = get_agency_config("NMSLO")
        assert "static" in config
        assert "behavioral" in config
        
        # Test Federal
        config = get_agency_config("Federal")
        assert "static" in config
        assert "behavioral" in config

    def test_get_agency_config_invalid_type(self):
        """Test get_agency_config with invalid input type."""
        with pytest.raises(InvalidAgencyError):
            get_agency_config(123)  # Integer instead of string

    def test_get_agency_config_empty_string(self):
        """Test get_agency_config with empty string."""
        with pytest.raises(InvalidAgencyError):
            get_agency_config("")

    def test_get_agency_config_whitespace(self):
        """Test get_agency_config with whitespace-only string."""
        with pytest.raises(InvalidAgencyError):
            get_agency_config("   ")

    def test_get_agency_config_nonexistent(self):
        """Test get_agency_config with nonexistent agency."""
        with pytest.raises(InvalidAgencyError):
            get_agency_config("NonexistentAgency")

    def test_get_static_config_valid(self):
        """Test get_static_config with valid agency types."""
        # Test NMSLO
        static_config = get_static_config("NMSLO")
        assert static_config.column_widths is not None
        assert static_config.folder_structure is not None
        assert static_config.dropbox_agency_name == "NMSLO"
        
        # Test Federal
        static_config = get_static_config("Federal")
        assert static_config.column_widths is not None
        assert static_config.folder_structure is not None
        assert static_config.dropbox_agency_name == "Federal"

    def test_get_static_config_invalid_agency(self):
        """Test get_static_config with invalid agency."""
        with pytest.raises(InvalidAgencyError):
            get_static_config("InvalidAgency")

    def test_get_behavioral_config_valid(self):
        """Test get_behavioral_config with valid agency types."""
        # Test NMSLO
        behavioral_config = get_behavioral_config("NMSLO")
        assert behavioral_config.search_mappings is not None
        assert behavioral_config.blank_columns is not None
        
        # Test Federal
        behavioral_config = get_behavioral_config("Federal")
        assert behavioral_config.search_mappings is not None
        assert behavioral_config.blank_columns is not None

    def test_get_behavioral_config_invalid_agency(self):
        """Test get_behavioral_config with invalid agency."""
        with pytest.raises(InvalidAgencyError):
            get_behavioral_config("InvalidAgency")

    def test_get_supported_agencies(self):
        """Test get_supported_agencies returns correct list."""
        agencies = get_supported_agencies()
        assert "NMSLO" in agencies
        assert "Federal" in agencies
        assert len(agencies) == 2

    def test_validate_agency_type_valid(self):
        """Test validate_agency_type with valid agency types."""
        assert validate_agency_type("NMSLO") is True
        assert validate_agency_type("Federal") is True

    def test_validate_agency_type_invalid(self):
        """Test validate_agency_type with invalid inputs."""
        assert validate_agency_type("InvalidAgency") is False
        assert validate_agency_type("") is False
        assert validate_agency_type("   ") is False
        assert validate_agency_type(123) is False
        assert validate_agency_type(None) is False

    def test_get_all_columns_nmslo(self):
        """Test get_all_columns for NMSLO agency."""
        columns = get_all_columns("NMSLO")
        
        # Check metadata columns are present
        assert "Agency" in columns
        assert "Order Type" in columns
        assert "Order Number" in columns
        assert "Order Date" in columns
        
        # Check data columns are present
        assert "Lease" in columns
        assert "Requested Legal" in columns
        assert "Report Start Date" in columns
        
        # Check search columns are present
        assert "Full Search" in columns
        assert "Partial Search" in columns
        
        # Check blank columns are present
        assert "New Format" in columns
        assert "Tractstar" in columns
        assert "Old Format" in columns
        assert "MI Index" in columns
        assert "Documents" in columns
        assert "Search Notes" in columns
        assert "Link" in columns

    def test_get_all_columns_federal(self):
        """Test get_all_columns for Federal agency."""
        columns = get_all_columns("Federal")
        
        # Check metadata columns are present
        assert "Agency" in columns
        assert "Order Type" in columns
        assert "Order Number" in columns
        assert "Order Date" in columns
        
        # Check data columns are present
        assert "Lease" in columns
        assert "Requested Legal" in columns
        assert "Report Start Date" in columns
        
        # Check Notes column is present for Federal
        assert "Notes" in columns
        
        # Check search columns are present
        assert "Files Search" in columns
        assert "Tractstar Search" in columns
        
        # Check blank columns are present
        assert "New Format" in columns
        assert "Tractstar" in columns
        assert "Documents" in columns
        assert "Search Notes" in columns
        assert "Link" in columns

    def test_get_all_columns_invalid_agency(self):
        """Test get_all_columns with invalid agency."""
        with pytest.raises(InvalidAgencyError):
            get_all_columns("InvalidAgency") 