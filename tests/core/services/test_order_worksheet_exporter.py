"""
Unit tests for Simplified Order Worksheet Exporter Service.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import tempfile
from datetime import datetime

from src.core.services.order_worksheet_exporter import (
    WorksheetExporter,
    export_order_items_to_worksheet,
)
from src.core.models import OrderItemData, AgencyType


@pytest.fixture
def sample_order_items():
    """Create sample OrderItemData for testing."""
    return [
        OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="12345",
            legal_description="Section 1, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            report_notes="Test notes",
            report_directory_link="https://example.com/link1",
            previous_report_found=True,
            documents_links=["https://example.com/doc1"],
            misc_index_links=["https://example.com/index1"],
            tractstar_needed=True,
            documents_needed=False,
            misc_index_needed=True,
        ),
        OrderItemData(
            agency=AgencyType.BLM,
            lease_number="67890",
            legal_description="Section 2, Township 3N, Range 4E",
            previous_report_found=False,
        ),
    ]


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestWorksheetExporter:
    """Test cases for WorksheetExporter."""

    def test_map_order_item_to_columns(self, sample_order_items):
        """Test mapping OrderItemData to worksheet columns."""
        exporter = WorksheetExporter()
        item = sample_order_items[0]

        columns = exporter._map_order_item_to_columns(item)

        # Check basic fields
        assert columns["Agency"] == "NMSLO"
        assert columns["Lease"] == "12345"
        assert columns["Legal Description"] == "Section 1, Township 2N, Range 3E"
        assert columns["Report Notes"] == "Test notes"
        assert columns["Report Directory Link"] == "https://example.com/link1"

        # Check boolean fields
        assert columns["Previous Report Found"] == "Yes"
        assert columns["Tractstar Needed"] == "Yes"
        assert columns["Documents Needed"] == "No"
        assert columns["Misc Index Needed"] == "Yes"

        # Check list fields
        assert columns["Documents Links"] == "https://example.com/doc1"
        assert columns["Misc Index Links"] == "https://example.com/index1"

    def test_convert_to_dataframe(self, sample_order_items):
        """Test converting OrderItemData to DataFrame with all configured columns."""
        exporter = WorksheetExporter()
        df = exporter.convert_to_dataframe(sample_order_items, AgencyType.NMSLO)

        # Check that all configured columns are present
        expected_columns = [
            "Agency",
            "Order Type",
            "Order Number",
            "Order Date",
            "Lease",
            "Legal Description",
            "Report Start Date",
            "Report End Date",
            "Report Notes",
            "Report Directory Link",
            "Previous Report Found",
            "Tractstar Needed",
            "Documents Needed",
            "Misc Index Needed",
            "Documents Links",
            "Misc Index Links",
            "Documents",
            "Search Notes",
        ]

        for col in expected_columns:
            assert col in df.columns, f"Column {col} not found in DataFrame"

        # Check values
        assert df.iloc[0]["Agency"] == "NMSLO"
        assert df.iloc[0]["Lease"] == "12345"
        assert df.iloc[0]["Previous Report Found"] == "Yes"
        assert df.iloc[0]["Tractstar Needed"] == "Yes"
        assert df.iloc[0]["Documents Needed"] == "No"
        assert df.iloc[0]["Misc Index Needed"] == "Yes"

        # Check that BLM item has correct values
        assert df.iloc[1]["Agency"] == "BLM"
        assert df.iloc[1]["Previous Report Found"] == "No"

    def test_convert_to_dataframe_with_blank_columns(self, sample_order_items):
        """Test that missing columns are added as blank."""
        exporter = WorksheetExporter()
        df = exporter.convert_to_dataframe(sample_order_items, AgencyType.NMSLO)

        # Check that blank columns are added
        assert "Documents" in df.columns
        assert "Search Notes" in df.columns

        # Check that blank columns are empty
        assert df.iloc[0]["Documents"] == ""
        assert df.iloc[0]["Search Notes"] == ""

    @patch("src.core.services.order_worksheet_exporter.ColumnManager")
    def test_add_metadata_columns(self, mock_column_manager, sample_order_items):
        """Test adding metadata columns."""
        exporter = WorksheetExporter()
        df = pd.DataFrame({"test": [1, 2]})

        mock_column_manager.add_metadata_columns.return_value = df

        result = exporter.add_metadata_columns(
            df, AgencyType.NMSLO, "test-123", "Runsheet", datetime.now().date()
        )

        mock_column_manager.add_metadata_columns.assert_called_once()
        assert result is df

    def test_get_column_widths(self, sample_order_items):
        """Test getting column widths from config."""
        exporter = WorksheetExporter()
        df = exporter.convert_to_dataframe(sample_order_items, AgencyType.NMSLO)
        widths = exporter.get_column_widths(df, AgencyType.NMSLO)

        # Check that widths are retrieved from config
        assert widths["Agency"] == 15
        assert widths["Lease"] == 15
        assert widths["Legal Description"] == 25
        assert widths["Report Notes"] == 30

        # Check fallback widths for columns not in config
        assert "test" not in widths  # This shouldn't be in the DataFrame anyway

    @patch("src.core.services.order_worksheet_exporter.ExcelWriter")
    @patch("src.core.services.order_worksheet_exporter.FilenameGenerator")
    def test_export_order_items_success(
        self, mock_filename_gen, mock_excel_writer, sample_order_items, temp_output_dir
    ):
        """Test successful export of order items."""
        exporter = WorksheetExporter()

        # Mock the dependencies
        mock_filename_gen.generate_order_filename.return_value = "test_order.xlsx"
        mock_excel_writer.save_with_formatting.return_value = str(
            temp_output_dir / "test_order.xlsx"
        )

        result = exporter.export_order_items(
            sample_order_items,
            AgencyType.NMSLO,
            temp_output_dir,
            "test-123",
            "Runsheet",
            datetime.now().date(),
        )

        # Verify the result
        assert result == str(temp_output_dir / "test_order.xlsx")
        mock_filename_gen.generate_order_filename.assert_called_once()
        mock_excel_writer.save_with_formatting.assert_called_once()

    def test_export_empty_order_items(self, temp_output_dir):
        """Test that empty order items raises an error."""
        exporter = WorksheetExporter()

        with pytest.raises(ValueError, match="order_items cannot be empty"):
            exporter.export_order_items([], AgencyType.NMSLO, temp_output_dir)

    def test_export_invalid_directory(self, sample_order_items):
        """Test that invalid directory raises an error."""
        exporter = WorksheetExporter()

        with pytest.raises(ValueError, match="output_directory must be a Path object"):
            exporter.export_order_items(
                sample_order_items, AgencyType.NMSLO, "not_a_path"
            )


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    @patch("src.core.services.order_worksheet_exporter.WorksheetExporter")
    def test_export_order_items_to_worksheet(
        self, mock_exporter_class, sample_order_items, temp_output_dir
    ):
        """Test the convenience function."""
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter
        mock_exporter.export_order_items.return_value = str(
            temp_output_dir / "test.xlsx"
        )

        result = export_order_items_to_worksheet(
            sample_order_items,
            AgencyType.NMSLO,
            temp_output_dir,
            "test-123",
            "Runsheet",
            datetime.now().date(),
        )

        assert result == str(temp_output_dir / "test.xlsx")
        mock_exporter.export_order_items.assert_called_once()
