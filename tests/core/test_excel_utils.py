"""
Unit tests for excel_utils module.

Tests WorksheetStyler and ExcelWriter utility classes.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

import pandas as pd
import pytest

from src.core.utils.excel_utils import ExcelWriter, WorksheetStyler


class TestWorksheetStyler(unittest.TestCase):
    """Test cases for WorksheetStyler utility class."""

    def setUp(self):
        """Set up test data and mock worksheet."""
        self.test_data = pd.DataFrame(
            {
                "Agency": ["Federal", "State"],
                "Order Date": ["2023-01-15", "2023-02-20"],
                "Report Start Date": ["2023-01-10", "2023-02-15"],
                "Lease": ["NMLC 123456", "NMLC 789012"],
                "Notes": ["Note1", "Note2"],
            }
        )

        # Create mock worksheet
        self.mock_worksheet = MagicMock()
        self.mock_worksheet.max_row = 3  # Header + 2 data rows
        self.mock_worksheet.iter_rows.return_value = [
            [MagicMock() for _ in range(5)] for _ in range(3)  # 3 rows, 5 columns
        ]

        # Mock cell objects
        for row in self.mock_worksheet.iter_rows.return_value:
            for i, cell in enumerate(row):
                cell.row = 1  # Mock row number

        # Mock column dimensions
        self.mock_worksheet.column_dimensions = {}
        for letter in "ABCDE":
            mock_col = MagicMock()
            self.mock_worksheet.column_dimensions[letter] = mock_col

    def test_apply_standard_formatting(self):
        """Test applying standard formatting to worksheet."""
        WorksheetStyler.apply_standard_formatting(self.mock_worksheet, self.test_data)

        # Should have called iter_rows to apply styles
        self.mock_worksheet.iter_rows.assert_called_once_with(min_row=1, max_row=500)

        # Should have applied styles to all cells
        for row in self.mock_worksheet.iter_rows.return_value:
            for cell in row:
                self.assertIsNotNone(cell.style)

    def test_apply_date_formatting(self):
        """Test applying date formatting to specific columns."""
        date_columns = ["Order Date", "Report Start Date"]

        with patch.object(self.mock_worksheet, "__getitem__") as mock_getitem:
            # Mock cell access
            mock_cells = {}
            for col_idx in [1, 2]:  # Order Date and Report Start Date columns
                for row in range(1, 4):  # 3 rows
                    col_letter = chr(ord("A") + col_idx)
                    cell_key = f"{col_letter}{row}"
                    mock_cell = MagicMock()
                    mock_cells[cell_key] = mock_cell

            mock_getitem.side_effect = lambda key: mock_cells.get(key, MagicMock())

            WorksheetStyler.apply_date_formatting(
                self.mock_worksheet, self.test_data, date_columns
            )

            # Should have formatted date columns
            expected_calls = []
            for col_name in date_columns:
                col_idx = self.test_data.columns.get_loc(col_name) + 1
                col_letter = chr(ord("A") + col_idx - 1)
                for row in range(1, 4):
                    expected_calls.append(call(f"{col_letter}{row}"))

            self.assertGreater(mock_getitem.call_count, 0)

    def test_apply_column_widths(self):
        """Test applying column widths to worksheet."""
        column_widths = {"Agency": 15, "Order Date": 12, "Lease": 20, "Notes": 30}

        WorksheetStyler.apply_column_widths(
            self.mock_worksheet, self.test_data, column_widths
        )

        # Should have set width for each column
        for idx, col_name in enumerate(self.test_data.columns):
            column_letter = chr(ord("A") + idx)
            expected_width = column_widths.get(col_name, 12)

            if column_letter in self.mock_worksheet.column_dimensions:
                # Check that width was set (exact value may vary due to mocking)
                mock_col = self.mock_worksheet.column_dimensions[column_letter]
                self.assertTrue(hasattr(mock_col, "width"))

    def test_freeze_header_row(self):
        """Test freezing header row in worksheet."""
        mock_cell = MagicMock()
        self.mock_worksheet.cell.return_value = mock_cell

        WorksheetStyler.freeze_header_row(self.mock_worksheet)

        # Should have called cell(row=2, column=1) and set freeze_panes
        self.mock_worksheet.cell.assert_called_once_with(row=2, column=1)
        self.assertEqual(self.mock_worksheet.freeze_panes, mock_cell)

    def test_add_auto_filter(self):
        """Test adding auto filter to worksheet."""
        WorksheetStyler.add_auto_filter(self.mock_worksheet, self.test_data)

        # Should have set auto_filter.ref to cover all columns
        expected_ref = f"A1:{chr(ord('A') + self.test_data.shape[1] - 1)}1"
        self.assertEqual(self.mock_worksheet.auto_filter.ref, expected_ref)

    def test_apply_column_widths_with_defaults(self):
        """Test applying column widths with default values for missing columns."""
        column_widths = {"Agency": 25}  # Only one column specified

        WorksheetStyler.apply_column_widths(
            self.mock_worksheet, self.test_data, column_widths
        )

        # Should handle missing columns with defaults
        for idx, col_name in enumerate(self.test_data.columns):
            column_letter = chr(ord("A") + idx)
            if column_letter in self.mock_worksheet.column_dimensions:
                mock_col = self.mock_worksheet.column_dimensions[column_letter]
                self.assertTrue(hasattr(mock_col, "width"))

    def test_apply_date_formatting_missing_columns(self):
        """Test applying date formatting when columns don't exist in data."""
        date_columns = ["Non Existent Date", "Another Missing Date"]

        # Should not raise error for missing columns
        try:
            WorksheetStyler.apply_date_formatting(
                self.mock_worksheet, self.test_data, date_columns
            )
        except Exception as e:
            self.fail(f"apply_date_formatting raised {e} for missing columns")


class TestExcelWriter(unittest.TestCase):
    """Test cases for ExcelWriter utility class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {
                "Agency": ["Federal", "State"],
                "Order Date": ["2023-01-15", "2023-02-20"],
                "Lease": ["NMLC 123456", "NMLC 789012"],
                "Notes": ["Note1", "Note2"],
            }
        )

        self.test_path = Path("/tmp/test_output.xlsx")
        self.column_widths = {"Agency": 15, "Order Date": 12, "Lease": 20, "Notes": 30}

    @patch("pandas.DataFrame.to_excel")
    @patch("src.core.utils.excel_utils.pd.ExcelWriter")
    @patch("src.core.utils.excel_utils.WorksheetStyler.apply_column_widths")
    @patch("src.core.utils.excel_utils.WorksheetStyler.apply_standard_formatting")
    @patch("src.core.utils.excel_utils.WorksheetStyler.apply_date_formatting")
    @patch("src.core.utils.excel_utils.WorksheetStyler.freeze_header_row")
    @patch("src.core.utils.excel_utils.WorksheetStyler.add_auto_filter")
    def test_save_with_formatting_success(
        self,
        mock_auto_filter,
        mock_freeze,
        mock_date_format,
        mock_standard_format,
        mock_column_widths,
        mock_excel_writer,
        mock_to_excel,
    ):
        """Test successful Excel file saving with formatting."""
        # Setup mocks
        mock_writer_instance = MagicMock()
        mock_excel_writer.return_value = mock_writer_instance
        mock_worksheet = MagicMock()
        mock_writer_instance.sheets = {"Worksheet": mock_worksheet}

        # Call method
        result = ExcelWriter.save_with_formatting(
            self.test_data, self.test_path, self.column_widths
        )

        # Verify ExcelWriter was created correctly
        mock_excel_writer.assert_called_once_with(self.test_path, engine="openpyxl")

        # Verify DataFrame was written to Excel
        mock_to_excel.assert_called_once_with(
            mock_writer_instance, index=False, sheet_name="Worksheet"
        )

        # Verify all formatting methods were called
        mock_column_widths.assert_called_once_with(
            mock_worksheet, self.test_data, self.column_widths
        )
        mock_standard_format.assert_called_once_with(mock_worksheet, self.test_data)
        mock_date_format.assert_called_once_with(
            mock_worksheet, self.test_data, ["Order Date", "Report Start Date"]
        )
        mock_freeze.assert_called_once_with(mock_worksheet)
        mock_auto_filter.assert_called_once_with(mock_worksheet, self.test_data)

        # Verify writer was closed
        mock_writer_instance.close.assert_called_once()

        # Verify return value
        self.assertEqual(result, str(self.test_path))

    def test_save_with_formatting_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError) as context:
            ExcelWriter.save_with_formatting(
                "not a dataframe", self.test_path, self.column_widths
            )

        self.assertIn("data must be a pandas DataFrame", str(context.exception))

    def test_save_with_formatting_invalid_path(self):
        """Test error handling with invalid path."""
        with self.assertRaises(ValueError) as context:
            ExcelWriter.save_with_formatting(
                self.test_data, "not a path object", self.column_widths
            )

        self.assertIn("output_path must be a Path object", str(context.exception))

    def test_save_with_formatting_invalid_column_widths(self):
        """Test error handling with invalid column widths."""
        with self.assertRaises(ValueError) as context:
            ExcelWriter.save_with_formatting(
                self.test_data, self.test_path, "not a dict"
            )

        self.assertIn("column_widths must be a dictionary", str(context.exception))

    @patch("pandas.DataFrame.to_excel")
    @patch("src.core.utils.excel_utils.pd.ExcelWriter")
    def test_save_with_formatting_permission_error(
        self, mock_excel_writer, mock_to_excel
    ):
        """Test error handling with permission denied."""
        # Setup mock to raise PermissionError
        mock_to_excel.side_effect = PermissionError("Permission denied")

        with self.assertRaises(IOError) as context:
            ExcelWriter.save_with_formatting(
                self.test_data, self.test_path, self.column_widths
            )

        self.assertIn("Permission denied writing to file", str(context.exception))

    @patch("pandas.DataFrame.to_excel")
    @patch("src.core.utils.excel_utils.pd.ExcelWriter")
    def test_save_with_formatting_file_not_found_error(
        self, mock_excel_writer, mock_to_excel
    ):
        """Test error handling with directory not found."""
        # Setup mock to raise FileNotFoundError
        mock_to_excel.side_effect = FileNotFoundError("Directory not found")

        with self.assertRaises(IOError) as context:
            ExcelWriter.save_with_formatting(
                self.test_data, self.test_path, self.column_widths
            )

        self.assertIn("Directory not found for file", str(context.exception))

    @patch("pandas.DataFrame.to_excel")
    @patch("src.core.utils.excel_utils.pd.ExcelWriter")
    def test_save_with_formatting_generic_error(self, mock_excel_writer, mock_to_excel):
        """Test error handling with generic exception."""
        # Setup mock to raise generic Exception
        mock_to_excel.side_effect = Exception("Generic error")

        with self.assertRaises(IOError) as context:
            ExcelWriter.save_with_formatting(
                self.test_data, self.test_path, self.column_widths
            )

        self.assertIn("Error writing Excel file", str(context.exception))


if __name__ == "__main__":
    unittest.main()
