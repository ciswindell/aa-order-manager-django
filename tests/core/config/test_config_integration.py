"""
Integration tests for configuration validation and error handling.

Simple tests that verify the configuration system works end-to-end.
"""

import pytest

from src.core.config.exceptions import InvalidAgencyError, ConfigurationError
from src.core.config.factory import (
    get_agency_config,
    get_static_config,
    get_behavioral_config,
    get_all_columns,
    validate_agency_type
)
from src.core.config.registry import AGENCY_CONFIGS


class TestConfigurationIntegration:
    """Integration tests for configuration system."""

    def test_full_configuration_retrieval_nmslo(self):
        """Test complete configuration retrieval for NMSLO agency."""
        # Get full configuration
        config = get_agency_config("NMSLO")
        
        # Verify structure
        assert "static" in config
        assert "behavioral" in config
        
        # Verify static config
        static_config = config["static"]
        assert static_config.column_widths is not None
        assert static_config.folder_structure is not None
        assert static_config.dropbox_agency_name == "NMSLO"
        
        # Verify behavioral config
        behavioral_config = config["behavioral"]
        assert behavioral_config.search_mappings is not None
        assert behavioral_config.blank_columns is not None

    def test_full_configuration_retrieval_federal(self):
        """Test complete configuration retrieval for Federal agency."""
        # Get full configuration
        config = get_agency_config("Federal")
        
        # Verify structure
        assert "static" in config
        assert "behavioral" in config
        
        # Verify static config
        static_config = config["static"]
        assert static_config.column_widths is not None
        assert static_config.folder_structure is not None
        assert static_config.dropbox_agency_name == "Federal"
        
        # Verify behavioral config
        behavioral_config = config["behavioral"]
        assert behavioral_config.search_mappings is not None
        assert behavioral_config.blank_columns is not None

    def test_static_configuration_integration(self):
        """Test static configuration integration."""
        # Test NMSLO static config
        nmslo_static = get_static_config("NMSLO")
        assert nmslo_static.dropbox_agency_name == "NMSLO"
        assert "Agency" in nmslo_static.column_widths
        assert "^Document Archive" in nmslo_static.folder_structure
        
        # Test Federal static config
        federal_static = get_static_config("Federal")
        assert federal_static.dropbox_agency_name == "Federal"
        assert "Agency" in federal_static.column_widths
        assert "^Document Archive" in federal_static.folder_structure

    def test_behavioral_configuration_integration(self):
        """Test behavioral configuration integration."""
        # Test NMSLO behavioral config
        nmslo_behavioral = get_behavioral_config("NMSLO")
        assert "Full Search" in nmslo_behavioral.search_mappings
        assert "Partial Search" in nmslo_behavioral.search_mappings
        assert "New Format" in nmslo_behavioral.blank_columns
        
        # Test Federal behavioral config
        federal_behavioral = get_behavioral_config("Federal")
        assert "Files Search" in federal_behavioral.search_mappings
        assert "Tractstar Search" in federal_behavioral.search_mappings
        assert "New Format" in federal_behavioral.blank_columns

    def test_column_generation_integration(self):
        """Test column generation integration."""
        # Test NMSLO columns
        nmslo_columns = get_all_columns("NMSLO")
        assert "Agency" in nmslo_columns
        assert "Full Search" in nmslo_columns
        assert "Partial Search" in nmslo_columns
        assert "New Format" in nmslo_columns
        
        # Test Federal columns
        federal_columns = get_all_columns("Federal")
        assert "Agency" in federal_columns
        assert "Notes" in federal_columns  # Federal-specific
        assert "Files Search" in federal_columns
        assert "Tractstar Search" in federal_columns
        assert "New Format" in federal_columns

    def test_agency_validation_integration(self):
        """Test agency validation integration."""
        # Valid agencies
        assert validate_agency_type("NMSLO") is True
        assert validate_agency_type("Federal") is True
        
        # Invalid agencies
        assert validate_agency_type("InvalidAgency") is False
        assert validate_agency_type("") is False
        assert validate_agency_type("   ") is False

    def test_error_handling_integration(self):
        """Test error handling integration."""
        # Test invalid agency type
        with pytest.raises(InvalidAgencyError):
            get_agency_config("InvalidAgency")
        
        # Test invalid input type
        with pytest.raises(InvalidAgencyError):
            get_agency_config(123)
        
        # Test empty string
        with pytest.raises(InvalidAgencyError):
            get_agency_config("")

    def test_configuration_consistency(self):
        """Test that configurations are consistent across the system."""
        # Get configurations through different methods
        full_config = get_agency_config("NMSLO")
        static_config = get_static_config("NMSLO")
        behavioral_config = get_behavioral_config("NMSLO")
        
        # Verify consistency
        assert full_config["static"] == static_config
        assert full_config["behavioral"] == behavioral_config
        
        # Verify column widths are consistent
        assert static_config.column_widths["Agency"] == 15
        assert static_config.column_widths["Order Type"] == 15

    def test_search_function_integration(self):
        """Test that search functions work correctly."""
        behavioral_config = get_behavioral_config("NMSLO")
        
        # Test search functions with sample data
        sample_lease = "B-1234-5"
        
        for search_name, search_func in behavioral_config.search_mappings.items():
            result = search_func(sample_lease)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_registry_integration(self):
        """Test that registry contains expected agencies."""
        # Verify registry has expected agencies
        assert "NMSLO" in AGENCY_CONFIGS
        assert "Federal" in AGENCY_CONFIGS
        assert len(AGENCY_CONFIGS) == 2
        
        # Verify registry structure
        for agency_name, config in AGENCY_CONFIGS.items():
            assert "static" in config
            assert "behavioral" in config
            assert config["static"].dropbox_agency_name == agency_name 