"""
Unit tests for data_utils module.

Tests DataCleaner, ColumnManager, and BlankColumnManager utility classes.
"""

import unittest
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.core.utils.data_utils import BlankColumnManager, ColumnManager, DataCleaner


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner utility class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {
                "Lease": ["NMLC 123456", "NMLC 789012"],
                "Report Start Date": [
                    datetime(2023, 5, 15),  # Already datetime
                    "Inception",  # Text to be cleaned
                ],
                "Other Column": ["Value1", "Value2"],
            }
        )

    def test_clean_date_column_with_datetime_objects(self):
        """Test cleaning column with existing datetime objects."""
        data = pd.DataFrame(
            {
                "Date Column": [
                    datetime(2023, 1, 15),
                    datetime(2023, 2, 20),
                    pd.Timestamp("2023-3-25"),
                ]
            }
        )

        result = DataCleaner.clean_date_column(data, "Date Column")

        # Should preserve existing datetime objects
        self.assertIsInstance(result.iloc[0]["Date Column"], (datetime, pd.Timestamp))
        self.assertIsInstance(result.iloc[1]["Date Column"], (datetime, pd.Timestamp))
        self.assertIsInstance(result.iloc[2]["Date Column"], (datetime, pd.Timestamp))

    def test_clean_date_column_with_text_values(self):
        """Test cleaning column with text values like 'Inception'."""
        data = pd.DataFrame(
            {"Date Column": ["Inception", "PENDING", "TBD", "inception"]}
        )

        result = DataCleaner.clean_date_column(data, "Date Column")

        # All text values should become None
        self.assertTrue(result["Date Column"].isna().all())

    def test_clean_date_column_with_excel_serial_dates(self):
        """Test cleaning column with Excel serial date numbers."""
        data = pd.DataFrame(
            {"Date Column": [44927, 44958, 44989]}  # Excel serial dates
        )

        result = DataCleaner.clean_date_column(data, "Date Column")

        # Should convert to datetime objects
        for date_val in result["Date Column"]:
            self.assertIsInstance(date_val, (datetime, pd.Timestamp))

    def test_clean_date_column_with_date_strings(self):
        """Test cleaning column with parseable date strings."""
        data = pd.DataFrame({"Date Column": ["2023-01-15", "01/15/2023", "2023-12-25"]})

        result = DataCleaner.clean_date_column(data, "Date Column")

        # Should parse to datetime objects
        for date_val in result["Date Column"]:
            self.assertIsInstance(date_val, (datetime, pd.Timestamp))

    def test_clean_date_column_with_empty_values(self):
        """Test cleaning column with empty/NaN values."""
        data = pd.DataFrame({"Date Column": [None, pd.NaT, "", float("nan")]})

        result = DataCleaner.clean_date_column(data, "Date Column")

        # All should remain as None/NaN
        self.assertTrue(result["Date Column"].isna().all())

    def test_clean_date_column_mixed_values(self):
        """Test cleaning column with mixed value types."""
        data = pd.DataFrame(
            {
                "Date Column": [
                    datetime(2023, 1, 15),  # Datetime
                    "Inception",  # Text
                    44927,  # Excel serial
                    "2023-05-15",  # Date string
                    None,  # Empty
                    "Invalid Date",  # Invalid string
                ]
            }
        )

        result = DataCleaner.clean_date_column(data, "Date Column")

        # First should remain datetime
        self.assertIsInstance(result.iloc[0]["Date Column"], (datetime, pd.Timestamp))
        # Second should be None (text)
        self.assertTrue(pd.isna(result.iloc[1]["Date Column"]))
        # Third should be datetime (converted from serial)
        self.assertIsInstance(result.iloc[2]["Date Column"], (datetime, pd.Timestamp))
        # Fourth should be datetime (parsed string)
        self.assertIsInstance(result.iloc[3]["Date Column"], (datetime, pd.Timestamp))
        # Fifth should remain None
        self.assertTrue(pd.isna(result.iloc[4]["Date Column"]))
        # Sixth should be None (invalid string)
        self.assertTrue(pd.isna(result.iloc[5]["Date Column"]))

    def test_clean_date_column_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError):
            DataCleaner.clean_date_column("not a dataframe", "Date Column")

    def test_clean_date_column_missing_column(self):
        """Test error handling with missing column."""
        data = pd.DataFrame({"Other Column": [1, 2, 3]})

        with self.assertRaises(ValueError):
            DataCleaner.clean_date_column(data, "Missing Column")

    def test_clean_date_column_returns_copy(self):
        """Test that method returns a copy and doesn't modify original."""
        original_data = pd.DataFrame({"Date Column": ["Inception", "2023-01-15"]})
        original_copy = original_data.copy()

        result = DataCleaner.clean_date_column(original_data, "Date Column")

        # Original should be unchanged
        pd.testing.assert_frame_equal(original_data, original_copy)
        # Result should be different
        self.assertFalse(result.equals(original_data))


class TestColumnManager(unittest.TestCase):
    """Test cases for ColumnManager utility class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {
                "Lease": ["NMLC 123456", "NMLC 789012"],
                "Requested Legal": ["Legal1", "Legal2"],
            }
        )

    def test_add_metadata_columns_new_columns(self):
        """Test adding metadata columns to DataFrame without existing metadata."""
        result = ColumnManager.add_metadata_columns(
            self.test_data,
            agency="Federal",
            order_type="Runsheet",
            order_date="2023-01-15",
            order_number="12345",
        )

        # Should have new columns at the beginning
        expected_columns = [
            "Agency",
            "Order Type",
            "Order Number",
            "Order Date",
            "Lease",
            "Requested Legal",
        ]
        self.assertEqual(list(result.columns), expected_columns)

        # Check values are populated
        self.assertEqual(result["Agency"].iloc[0], "Federal")
        self.assertEqual(result["Order Type"].iloc[0], "Runsheet")
        self.assertEqual(result["Order Number"].iloc[0], "12345")
        self.assertEqual(result["Order Date"].iloc[0], "2023-01-15")

    def test_add_metadata_columns_existing_columns(self):
        """Test adding metadata columns when some already exist."""
        data_with_agency = pd.DataFrame(
            {"Agency": ["NMSLO", "NMSLO"], "Lease": ["NMLC 123456", "NMLC 789012"]}
        )

        result = ColumnManager.add_metadata_columns(
            data_with_agency, agency="Federal", order_type="Runsheet"
        )

        # Should not duplicate Agency column
        agency_count = list(result.columns).count("Agency")
        self.assertEqual(agency_count, 1)

        # Should have new columns added
        self.assertIn("Order Type", result.columns)
        self.assertIn("Order Number", result.columns)
        self.assertIn("Order Date", result.columns)

    def test_add_metadata_columns_partial_metadata(self):
        """Test adding metadata columns with only some values provided."""
        result = ColumnManager.add_metadata_columns(
            self.test_data, agency="Federal", order_type=None, order_number="12345"
        )

        # Agency and Order Number should be populated
        self.assertEqual(result["Agency"].iloc[0], "Federal")
        self.assertEqual(result["Order Number"].iloc[0], "12345")

        # Order Type and Order Date should be empty strings
        self.assertEqual(result["Order Type"].iloc[0], "")
        self.assertEqual(result["Order Date"].iloc[0], "")

    def test_add_metadata_columns_no_metadata(self):
        """Test adding metadata columns with no values provided."""
        result = ColumnManager.add_metadata_columns(self.test_data)

        # Should have all metadata columns
        metadata_columns = ["Agency", "Order Type", "Order Number", "Order Date"]
        for col in metadata_columns:
            self.assertIn(col, result.columns)
            # Should be empty strings
            self.assertEqual(result[col].iloc[0], "")

    def test_add_metadata_columns_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError):
            ColumnManager.add_metadata_columns("not a dataframe")

    def test_add_metadata_columns_returns_copy(self):
        """Test that method returns a copy and doesn't modify original."""
        original_data = self.test_data.copy()

        result = ColumnManager.add_metadata_columns(self.test_data, agency="Federal")

        # Original should be unchanged
        pd.testing.assert_frame_equal(self.test_data, original_data)
        # Result should have more columns
        self.assertGreater(len(result.columns), len(original_data.columns))


class TestBlankColumnManager(unittest.TestCase):
    """Test cases for BlankColumnManager utility class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {"Lease": ["NMLC 123456", "NMLC 789012"], "Agency": ["Federal", "NMSLO"]}
        )

    def test_add_blank_columns_basic(self):
        """Test adding blank columns to DataFrame."""
        column_names = ["New Format", "Tractstar", "Documents"]

        result = BlankColumnManager.add_blank_columns(self.test_data, column_names)

        # Should have original columns plus new blank columns
        expected_columns = ["Lease", "Agency", "New Format", "Tractstar", "Documents"]
        self.assertEqual(list(result.columns), expected_columns)

        # New columns should be empty/NaN
        for col in column_names:
            self.assertTrue(result[col].isna().all())

    def test_add_blank_columns_empty_list(self):
        """Test adding blank columns with empty column list."""
        result = BlankColumnManager.add_blank_columns(self.test_data, [])

        # Should be identical to original
        pd.testing.assert_frame_equal(result, self.test_data)

    def test_add_blank_columns_single_column(self):
        """Test adding single blank column."""
        result = BlankColumnManager.add_blank_columns(self.test_data, ["Notes"])

        # Should have original columns plus Notes
        self.assertIn("Notes", result.columns)
        self.assertTrue(result["Notes"].isna().all())

    def test_add_blank_columns_preserve_index(self):
        """Test that blank columns preserve DataFrame index."""
        # Create data with custom index
        indexed_data = self.test_data.copy()
        indexed_data.index = [10, 20]

        result = BlankColumnManager.add_blank_columns(indexed_data, ["Notes"])

        # Index should be preserved
        self.assertEqual(list(result.index), [10, 20])
        self.assertTrue(result["Notes"].isna().all())

    def test_add_blank_columns_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError):
            BlankColumnManager.add_blank_columns("not a dataframe", ["Col1"])

    def test_add_blank_columns_invalid_column_names(self):
        """Test error handling with invalid column names."""
        with self.assertRaises(ValueError):
            BlankColumnManager.add_blank_columns(self.test_data, "not a list")

    def test_add_blank_columns_returns_copy(self):
        """Test that method returns a copy and doesn't modify original."""
        original_data = self.test_data.copy()

        result = BlankColumnManager.add_blank_columns(self.test_data, ["Notes"])

        # Original should be unchanged
        pd.testing.assert_frame_equal(self.test_data, original_data)
        # Result should have more columns
        self.assertGreater(len(result.columns), len(original_data.columns))


if __name__ == "__main__":
    unittest.main()
