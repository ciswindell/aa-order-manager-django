"""
Unit tests for Order Worksheet Exporter Service with Strategy Pattern.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import tempfile

from src.core.services.order_worksheet_exporter import (
    OrderWorksheetExporterService,
    LegacyFormatStrategy,
    MinimalFormatStrategy,
    export_order_items_to_worksheet,
    export_order_items_legacy_format,
    export_order_items_minimal_format,
)
from src.core.models import OrderItemData, AgencyType


@pytest.fixture
def sample_order_items():
    """Create sample OrderItemData for testing."""
    return [
        OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="T1N R1E S1",
            notes="Test notes",
            report_directory_link="https://example.com/12345",
            previous_report_found=True,
            documents_links=["https://example.com/doc1", "https://example.com/doc2"],
            lease_index_links=["https://example.com/index1"],
        ),
        OrderItemData(
            agency=AgencyType.BLM,
            lease_number="67890",
            legal_description="T2N R2E S2",
            previous_report_found=False,
        ),
    ]


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestLegacyFormatStrategy:
    """Test cases for LegacyFormatStrategy."""

    def test_convert_to_dataframe(self, sample_order_items):
        """Test converting OrderItemData to DataFrame with legacy format."""
        strategy = LegacyFormatStrategy()
        df = strategy.convert_to_dataframe(sample_order_items)

        # Check basic columns
        assert "Agency" in df.columns
        assert "Lease" in df.columns
        assert "Legal Description" in df.columns
        assert "Previous Report Found" in df.columns
        assert "Link" in df.columns

        # Check values
        assert df.iloc[0]["Agency"] == "NMSLO"
        assert df.iloc[0]["Lease"] == "12345"
        assert df.iloc[0]["Previous Report Found"] == True  # Boolean for legacy
        assert df.iloc[1]["Previous Report Found"] == False

    @patch("src.core.services.order_worksheet_exporter.ParsedColumnGenerator")
    @patch("src.core.services.order_worksheet_exporter.ColumnManager")
    def test_add_agency_columns_nmslo(
        self, mock_column_manager, mock_parsed_generator, sample_order_items
    ):
        """Test adding NMSLO agency-specific columns."""
        strategy = LegacyFormatStrategy()
        df = pd.DataFrame({"test": [1, 2]})

        mock_column_manager.add_metadata_columns.return_value = df
        mock_parsed_generator.add_nmslo_search_columns.return_value = df

        result = strategy.add_agency_columns(df, AgencyType.NMSLO)

        mock_column_manager.add_metadata_columns.assert_called_once()
        mock_parsed_generator.add_nmslo_search_columns.assert_called_once_with(df)
        mock_parsed_generator.add_federal_search_columns.assert_not_called()

    @patch("src.core.services.order_worksheet_exporter.ParsedColumnGenerator")
    @patch("src.core.services.order_worksheet_exporter.ColumnManager")
    def test_add_agency_columns_blm(
        self, mock_column_manager, mock_parsed_generator, sample_order_items
    ):
        """Test adding BLM agency-specific columns."""
        strategy = LegacyFormatStrategy()
        df = pd.DataFrame({"test": [1, 2]})

        mock_column_manager.add_metadata_columns.return_value = df
        mock_parsed_generator.add_federal_search_columns.return_value = df

        result = strategy.add_agency_columns(df, AgencyType.BLM)

        mock_column_manager.add_metadata_columns.assert_called_once()
        mock_parsed_generator.add_federal_search_columns.assert_called_once_with(df)
        mock_parsed_generator.add_nmslo_search_columns.assert_not_called()

    def test_get_column_widths(self):
        """Test column width calculation for legacy format."""
        strategy = LegacyFormatStrategy()
        df = pd.DataFrame(
            {
                "Link": ["test"],
                "Legal Description": ["test"],
                "Agency": ["test"],
                "Other": ["test"],
            }
        )

        widths = strategy.get_column_widths(df)

        assert widths["Link"] == 50
        assert widths["Legal Description"] == 40
        assert widths["Agency"] == 15
        assert widths["Other"] == 20


class TestMinimalFormatStrategy:
    """Test cases for MinimalFormatStrategy."""

    def test_convert_to_dataframe(self, sample_order_items):
        """Test converting OrderItemData to DataFrame with minimal format."""
        strategy = MinimalFormatStrategy()
        df = strategy.convert_to_dataframe(sample_order_items)

        # Check basic columns
        assert "Agency" in df.columns
        assert "Lease" in df.columns
        assert "Legal Description" in df.columns
        assert "Previous Report Found" in df.columns

        # Check boolean to Yes/No conversion
        assert df.iloc[0]["Previous Report Found"] == "Yes"
        assert df.iloc[1]["Previous Report Found"] == "No"

    @patch("src.core.services.order_worksheet_exporter.ColumnManager")
    def test_add_agency_columns_minimal(self, mock_column_manager, sample_order_items):
        """Test adding minimal agency-specific columns (no parsed columns)."""
        strategy = MinimalFormatStrategy()
        df = pd.DataFrame({"test": [1, 2]})

        mock_column_manager.add_metadata_columns.return_value = df

        result = strategy.add_agency_columns(df, AgencyType.NMSLO)

        mock_column_manager.add_metadata_columns.assert_called_once()
        # Should not call any parsed column generators

    def test_get_column_widths(self):
        """Test column width calculation for minimal format."""
        strategy = MinimalFormatStrategy()
        df = pd.DataFrame(
            {
                "Report Directory Link": ["test"],
                "Legal Description": ["test"],
                "Agency": ["test"],
                "Other": ["test"],
            }
        )

        widths = strategy.get_column_widths(df)

        assert widths["Report Directory Link"] == 50
        assert widths["Legal Description"] == 40
        assert widths["Agency"] == 15
        assert widths["Other"] == 20


class TestOrderWorksheetExporterService:
    """Test cases for OrderWorksheetExporterService."""

    def test_init(self):
        """Test service initialization with strategy."""
        strategy = LegacyFormatStrategy()
        service = OrderWorksheetExporterService(strategy)
        assert service.strategy == strategy

    @patch("src.core.services.order_worksheet_exporter.ExcelWriter")
    @patch("src.core.services.order_worksheet_exporter.FilenameGenerator")
    def test_export_order_items_success(
        self, mock_filename_gen, mock_excel_writer, sample_order_items, temp_output_dir
    ):
        """Test successful export using strategy."""
        # Setup mocks
        mock_filename_gen.generate_order_filename.return_value = "test_output.xlsx"
        mock_excel_writer.save_with_formatting.return_value = str(
            temp_output_dir / "test_output.xlsx"
        )

        # Create service with mock strategy
        mock_strategy = Mock()
        mock_strategy.convert_to_dataframe.return_value = pd.DataFrame({"test": [1, 2]})
        mock_strategy.add_agency_columns.return_value = pd.DataFrame({"test": [1, 2]})
        mock_strategy.get_column_widths.return_value = {"test": 20}

        service = OrderWorksheetExporterService(mock_strategy)

        # Execute
        result = service.export_order_items(
            sample_order_items, AgencyType.NMSLO, temp_output_dir, "123", "Test"
        )

        # Verify strategy methods called
        mock_strategy.convert_to_dataframe.assert_called_once_with(sample_order_items)
        mock_strategy.add_agency_columns.assert_called_once()
        mock_strategy.get_column_widths.assert_called_once()

        # Verify file operations
        mock_filename_gen.generate_order_filename.assert_called_once()
        mock_excel_writer.save_with_formatting.assert_called_once()

    def test_export_empty_order_items(self, temp_output_dir):
        """Test error handling for empty order items."""
        strategy = LegacyFormatStrategy()
        service = OrderWorksheetExporterService(strategy)

        with pytest.raises(ValueError, match="order_items cannot be empty"):
            service.export_order_items([], AgencyType.NMSLO, temp_output_dir)

    def test_export_invalid_directory(self, sample_order_items):
        """Test error handling for invalid directory."""
        strategy = LegacyFormatStrategy()
        service = OrderWorksheetExporterService(strategy)

        with pytest.raises(ValueError, match="output_directory must be a Path object"):
            service.export_order_items(
                sample_order_items, AgencyType.NMSLO, "not_a_path"
            )


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @patch("src.core.services.order_worksheet_exporter.OrderWorksheetExporterService")
    def test_export_order_items_to_worksheet_legacy(
        self, mock_service_class, sample_order_items, temp_output_dir
    ):
        """Test convenience function with legacy format."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        export_order_items_to_worksheet(
            sample_order_items,
            AgencyType.NMSLO,
            temp_output_dir,
            use_legacy_format=True,
        )

        # Verify LegacyFormatStrategy was used
        args, kwargs = mock_service_class.call_args
        assert isinstance(args[0], LegacyFormatStrategy)

    @patch("src.core.services.order_worksheet_exporter.OrderWorksheetExporterService")
    def test_export_order_items_to_worksheet_minimal(
        self, mock_service_class, sample_order_items, temp_output_dir
    ):
        """Test convenience function with minimal format."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        export_order_items_to_worksheet(
            sample_order_items,
            AgencyType.NMSLO,
            temp_output_dir,
            use_legacy_format=False,
        )

        # Verify MinimalFormatStrategy was used
        args, kwargs = mock_service_class.call_args
        assert isinstance(args[0], MinimalFormatStrategy)

    @patch("src.core.services.order_worksheet_exporter.OrderWorksheetExporterService")
    def test_export_order_items_legacy_format(
        self, mock_service_class, sample_order_items, temp_output_dir
    ):
        """Test legacy format convenience function."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        export_order_items_legacy_format(
            sample_order_items, AgencyType.NMSLO, temp_output_dir
        )

        # Verify LegacyFormatStrategy was used
        args, kwargs = mock_service_class.call_args
        assert isinstance(args[0], LegacyFormatStrategy)

    @patch("src.core.services.order_worksheet_exporter.OrderWorksheetExporterService")
    def test_export_order_items_minimal_format(
        self, mock_service_class, sample_order_items, temp_output_dir
    ):
        """Test minimal format convenience function."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        export_order_items_minimal_format(
            sample_order_items, AgencyType.NMSLO, temp_output_dir
        )

        # Verify MinimalFormatStrategy was used
        args, kwargs = mock_service_class.call_args
        assert isinstance(args[0], MinimalFormatStrategy)
