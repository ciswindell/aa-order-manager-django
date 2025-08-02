"""
Unit tests for configuration models.

Simple tests for AgencyStaticConfig and AgencyBehaviorConfig classes.
"""

import pytest

from src.core.config.exceptions import ConfigurationError
from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig


class TestAgencyStaticConfig:
    """Test AgencyStaticConfig dataclass validation and methods."""

    def test_valid_configuration(self):
        """Test that valid configuration initializes correctly."""
        config = AgencyStaticConfig(
            column_widths={"Agency": 15, "Order Type": 20},
            folder_structure=["^Document Archive", "Runsheets"],
            dropbox_agency_name="NMSLO"
        )
        
        assert config.column_widths == {"Agency": 15, "Order Type": 20}
        assert config.folder_structure == ["^Document Archive", "Runsheets"]
        assert config.dropbox_agency_name == "NMSLO"

    def test_empty_column_widths_raises_error(self):
        """Test that empty column_widths raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="column_widths cannot be empty"):
            AgencyStaticConfig(
                column_widths={},
                folder_structure=["^Document Archive"],
                dropbox_agency_name="NMSLO"
            )

    def test_empty_folder_structure_raises_error(self):
        """Test that empty folder_structure raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="folder_structure cannot be empty"):
            AgencyStaticConfig(
                column_widths={"Agency": 15},
                folder_structure=[],
                dropbox_agency_name="NMSLO"
            )

    def test_empty_dropbox_agency_name_raises_error(self):
        """Test that empty dropbox_agency_name raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="dropbox_agency_name cannot be empty"):
            AgencyStaticConfig(
                column_widths={"Agency": 15},
                folder_structure=["^Document Archive"],
                dropbox_agency_name=""
            )

    def test_invalid_column_width_type_raises_error(self):
        """Test that non-integer column width raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be an integer"):
            AgencyStaticConfig(
                column_widths={"Agency": "15"},  # String instead of int
                folder_structure=["^Document Archive"],
                dropbox_agency_name="NMSLO"
            )

    def test_negative_column_width_raises_error(self):
        """Test that negative column width raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be positive"):
            AgencyStaticConfig(
                column_widths={"Agency": -5},
                folder_structure=["^Document Archive"],
                dropbox_agency_name="NMSLO"
            )

    def test_get_column_width_existing(self):
        """Test get_column_width returns correct width for existing column."""
        config = AgencyStaticConfig(
            column_widths={"Agency": 15, "Order Type": 20},
            folder_structure=["^Document Archive"],
            dropbox_agency_name="NMSLO"
        )
        
        assert config.get_column_width("Agency") == 15
        assert config.get_column_width("Order Type") == 20

    def test_get_column_width_default(self):
        """Test get_column_width returns default for non-existing column."""
        config = AgencyStaticConfig(
            column_widths={"Agency": 15},
            folder_structure=["^Document Archive"],
            dropbox_agency_name="NMSLO"
        )
        
        assert config.get_column_width("NonExistent") == 12  # Default
        assert config.get_column_width("NonExistent", 25) == 25  # Custom default


class TestAgencyBehaviorConfig:
    """Test AgencyBehaviorConfig class validation and methods."""

    def test_valid_configuration(self):
        """Test that valid configuration initializes correctly."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Full Search": mock_search_func},
            blank_columns=["New Format", "Documents"]
        )
        
        assert len(config.search_mappings) == 1
        assert len(config.blank_columns) == 2
        assert "Full Search" in config.search_mappings

    def test_empty_search_mappings_raises_error(self):
        """Test that empty search_mappings raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="search_mappings cannot be empty"):
            AgencyBehaviorConfig(
                search_mappings={},
                blank_columns=["New Format"]
            )

    def test_empty_blank_columns_raises_error(self):
        """Test that empty blank_columns raises ConfigurationError."""
        def mock_search_func(data):
            return f"search_{data}"
        
        with pytest.raises(ConfigurationError, match="blank_columns cannot be empty"):
            AgencyBehaviorConfig(
                search_mappings={"Full Search": mock_search_func},
                blank_columns=[]
            )

    def test_get_search_columns(self):
        """Test get_search_columns returns correct list."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Full Search": mock_search_func, "Partial Search": mock_search_func},
            blank_columns=["New Format"]
        )
        
        search_columns = config.get_search_columns()
        assert "Full Search" in search_columns
        assert "Partial Search" in search_columns
        assert len(search_columns) == 2

    def test_get_blank_columns(self):
        """Test get_blank_columns returns correct list."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Full Search": mock_search_func},
            blank_columns=["New Format", "Documents", "Link"]
        )
        
        blank_columns = config.get_blank_columns()
        assert "New Format" in blank_columns
        assert "Documents" in blank_columns
        assert "Link" in blank_columns
        assert len(blank_columns) == 3

    def test_non_callable_search_mapping_raises_error(self):
        """Test that non-callable search mapping raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be callable"):
            AgencyBehaviorConfig(
                search_mappings={"Full Search": "not_callable"},  # String instead of function
                blank_columns=["New Format"]
            )

    def test_empty_blank_column_raises_error(self):
        """Test that empty blank column raises ConfigurationError."""
        def mock_search_func(data):
            return f"search_{data}"
        
        with pytest.raises(ConfigurationError, match="cannot be empty or whitespace"):
            AgencyBehaviorConfig(
                search_mappings={"Full Search": mock_search_func},
                blank_columns=["New Format", "", "Documents"]  # Empty string in middle
            )

    def test_validate_with_sample_data_success(self):
        """Test validate_with_sample_data works with valid sample data."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Full Search": mock_search_func},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        result = config.validate_with_sample_data("TEST-123")
        assert result is True

    def test_validate_with_sample_data_empty_string_raises_error(self):
        """Test validate_with_sample_data raises error with empty sample data."""
        def mock_search_func(data):
            return f"search_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Full Search": mock_search_func},
            blank_columns=["New Format"]
        )
        
        with pytest.raises(ConfigurationError, match="must be a non-empty string"):
            config.validate_with_sample_data("")

    def test_callable_validation_with_lambda(self):
        """Test that lambda functions are accepted as callables."""
        config = AgencyBehaviorConfig(
            search_mappings={"Lambda Search": lambda x: f"lambda_{x}"},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Lambda Search" in config.search_mappings
        assert callable(config.search_mappings["Lambda Search"])

    def test_callable_validation_with_function_reference(self):
        """Test that function references are accepted as callables."""
        def test_search_func(data):
            return f"func_{data}"
        
        config = AgencyBehaviorConfig(
            search_mappings={"Function Search": test_search_func},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Function Search" in config.search_mappings
        assert callable(config.search_mappings["Function Search"])

    def test_callable_validation_with_method(self):
        """Test that methods are accepted as callables."""
        class TestSearchClass:
            def search_method(self, data):
                return f"method_{data}"
        
        search_instance = TestSearchClass()
        
        config = AgencyBehaviorConfig(
            search_mappings={"Method Search": search_instance.search_method},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Method Search" in config.search_mappings
        assert callable(config.search_mappings["Method Search"])

    def test_callable_validation_with_builtin_function(self):
        """Test that builtin functions are accepted as callables."""
        config = AgencyBehaviorConfig(
            search_mappings={"Builtin Search": str.upper},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Builtin Search" in config.search_mappings
        assert callable(config.search_mappings["Builtin Search"])

    def test_callable_validation_with_class_constructor(self):
        """Test that class constructors are accepted as callables."""
        config = AgencyBehaviorConfig(
            search_mappings={"Constructor Search": str},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Constructor Search" in config.search_mappings
        assert callable(config.search_mappings["Constructor Search"])

    def test_callable_validation_with_partial_function(self):
        """Test that partial functions are accepted as callables."""
        from functools import partial
        
        def base_search_func(data, prefix):
            return f"{prefix}_{data}"
        
        partial_func = partial(base_search_func, prefix="partial")
        
        config = AgencyBehaviorConfig(
            search_mappings={"Partial Search": partial_func},
            blank_columns=["New Format"]
        )
        
        # Should not raise any error
        assert "Partial Search" in config.search_mappings
        assert callable(config.search_mappings["Partial Search"])

    def test_callable_validation_with_non_callable_raises_error(self):
        """Test that non-callable values raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be callable"):
            AgencyBehaviorConfig(
                search_mappings={"Invalid Search": "not_callable"},
                blank_columns=["New Format"]
            )

    def test_callable_validation_with_none_raises_error(self):
        """Test that None values raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be callable"):
            AgencyBehaviorConfig(
                search_mappings={"Invalid Search": None},
                blank_columns=["New Format"]
            )

    def test_callable_validation_with_integer_raises_error(self):
        """Test that integer values raise ConfigurationError."""
        with pytest.raises(ConfigurationError, match="must be callable"):
            AgencyBehaviorConfig(
                search_mappings={"Invalid Search": 123},
                blank_columns=["New Format"]
            ) 