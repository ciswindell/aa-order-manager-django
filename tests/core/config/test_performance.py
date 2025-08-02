"""
Performance tests for configuration system.

Simple tests to ensure configuration access doesn't impact processing speed.
"""

import time
import pytest

from src.core.config.factory import (
    get_agency_config,
    get_static_config,
    get_behavioral_config,
    get_all_columns,
    validate_agency_type
)


class TestConfigurationPerformance:
    """Performance tests for configuration access."""

    def test_get_agency_config_performance(self):
        """Test that get_agency_config is fast."""
        start_time = time.time()
        
        # Call function multiple times
        for _ in range(100):
            config = get_agency_config("NMSLO")
            assert config is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 calls in under 1 second
        assert duration < 1.0, f"get_agency_config took {duration:.3f}s for 100 calls"

    def test_get_static_config_performance(self):
        """Test that get_static_config is fast."""
        start_time = time.time()
        
        # Call function multiple times
        for _ in range(100):
            config = get_static_config("NMSLO")
            assert config is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 calls in under 1 second
        assert duration < 1.0, f"get_static_config took {duration:.3f}s for 100 calls"

    def test_get_behavioral_config_performance(self):
        """Test that get_behavioral_config is fast."""
        start_time = time.time()
        
        # Call function multiple times
        for _ in range(100):
            config = get_behavioral_config("NMSLO")
            assert config is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 calls in under 1 second
        assert duration < 1.0, f"get_behavioral_config took {duration:.3f}s for 100 calls"

    def test_get_all_columns_performance(self):
        """Test that get_all_columns is fast."""
        start_time = time.time()
        
        # Call function multiple times
        for _ in range(100):
            columns = get_all_columns("NMSLO")
            assert len(columns) > 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 calls in under 1 second
        assert duration < 1.0, f"get_all_columns took {duration:.3f}s for 100 calls"

    def test_validate_agency_type_performance(self):
        """Test that validate_agency_type is fast."""
        start_time = time.time()
        
        # Call function multiple times with valid and invalid inputs
        for _ in range(100):
            assert validate_agency_type("NMSLO") is True
            assert validate_agency_type("Federal") is True
            assert validate_agency_type("InvalidAgency") is False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 300 calls in under 1 second
        assert duration < 1.0, f"validate_agency_type took {duration:.3f}s for 300 calls"

    def test_configuration_initialization_performance(self):
        """Test that configuration initialization is fast."""
        from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig
        
        start_time = time.time()
        
        # Create configurations multiple times
        for _ in range(50):
            static_config = AgencyStaticConfig(
                column_widths={"Agency": 15, "Order Type": 20},
                folder_structure=["^Document Archive", "Runsheets"],
                dropbox_agency_name="TestAgency"
            )
            
            def mock_search_func(data):
                return f"search_{data}"
            
            behavioral_config = AgencyBehaviorConfig(
                search_mappings={"Test Search": mock_search_func},
                blank_columns=["New Format", "Documents"]
            )
            
            assert static_config is not None
            assert behavioral_config is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 50 initializations in under 1 second
        assert duration < 1.0, f"Configuration initialization took {duration:.3f}s for 50 instances"

    def test_search_function_performance(self):
        """Test that search functions are fast."""
        from src.core.config.factory import get_behavioral_config
        
        behavioral_config = get_behavioral_config("NMSLO")
        
        start_time = time.time()
        
        # Call search functions multiple times
        test_data = "B-1234-5"
        for _ in range(100):
            for search_name, search_func in behavioral_config.search_mappings.items():
                result = search_func(test_data)
                assert isinstance(result, str)
                assert len(result) > 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 200 search function calls in under 1 second
        assert duration < 1.0, f"Search functions took {duration:.3f}s for 200 calls"

    def test_multiple_agency_performance(self):
        """Test that accessing multiple agencies is fast."""
        start_time = time.time()
        
        # Access both agencies multiple times
        for _ in range(50):
            nmslo_config = get_agency_config("NMSLO")
            federal_config = get_agency_config("Federal")
            
            assert nmslo_config is not None
            assert federal_config is not None
            
            nmslo_columns = get_all_columns("NMSLO")
            federal_columns = get_all_columns("Federal")
            
            assert len(nmslo_columns) > 0
            assert len(federal_columns) > 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 200 operations in under 1 second
        assert duration < 1.0, f"Multiple agency access took {duration:.3f}s for 200 operations" 