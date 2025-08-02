"""
Unit tests for parsing_utils module.

Tests LeaseNumberParser and ParsedColumnGenerator utility classes.
"""

import unittest

import pandas as pd

from src.core.utils.parsing_utils import LeaseNumberParser, ParsedColumnGenerator


class TestLeaseNumberParser(unittest.TestCase):
    """Test cases for LeaseNumberParser utility class."""

    def test_search_file_basic_number(self):
        """Test search_file with basic lease number."""
        parser = LeaseNumberParser("NMLC 123456")
        result = parser.search_file()
        expected = "*123456*"
        self.assertEqual(result, expected)

    def test_search_file_with_letters(self):
        """Test search_file filtering out letters."""
        parser = LeaseNumberParser("NMLC ABC123DEF")
        result = parser.search_file()
        expected = "*123*"
        self.assertEqual(result, expected)

    def test_search_file_with_zeros(self):
        """Test search_file including zeros."""
        parser = LeaseNumberParser("NMLC 102030")
        result = parser.search_file()
        expected = "*102030*"
        self.assertEqual(result, expected)

    def test_search_file_no_digits(self):
        """Test search_file with no digits."""
        parser = LeaseNumberParser("NMLC ABCDEF")
        result = parser.search_file()
        expected = "Error"
        self.assertEqual(result, expected)

    def test_search_file_empty_string(self):
        """Test search_file with empty string."""
        parser = LeaseNumberParser("")
        result = parser.search_file()
        expected = "Error"
        self.assertEqual(result, expected)

    def test_search_tractstar_basic(self):
        """Test search_tractstar with basic lease format."""
        parser = LeaseNumberParser("NMLC 123456A")
        result = parser.search_tractstar()
        expected = "123456-A"
        self.assertEqual(result, expected)

    def test_search_tractstar_no_alpha(self):
        """Test search_tractstar with no alpha characters."""
        parser = LeaseNumberParser("NMLC 123456")
        result = parser.search_tractstar()
        expected = "123456"
        self.assertEqual(result, expected)

    def test_search_tractstar_multiple_spaces(self):
        """Test search_tractstar with multiple space-separated parts."""
        parser = LeaseNumberParser("NMLC 123 456B")
        result = parser.search_tractstar()
        expected = "123456-B"
        self.assertEqual(result, expected)

    def test_search_tractstar_no_digits(self):
        """Test search_tractstar with no digits."""
        parser = LeaseNumberParser("NMLC ABCDEF")
        result = parser.search_tractstar()
        expected = "Error"
        self.assertEqual(result, expected)

    def test_search_full_basic(self):
        """Test search_full with basic lease number."""
        parser = LeaseNumberParser("NMLC-123456-A")
        result = parser.search_full()
        expected = "*NMLC*123456*A*"
        self.assertEqual(result, expected)

    def test_search_full_no_dashes(self):
        """Test search_full with no dashes."""
        parser = LeaseNumberParser("NMLC 123456 A")
        result = parser.search_full()
        expected = "*NMLC 123456 A*"
        self.assertEqual(result, expected)

    def test_search_full_multiple_dashes(self):
        """Test search_full with multiple dashes."""
        parser = LeaseNumberParser("NMLC-123-456-A")
        result = parser.search_full()
        expected = "*NMLC*123*456*A*"
        self.assertEqual(result, expected)

    def test_search_partial_basic(self):
        """Test search_partial with basic lease number."""
        parser = LeaseNumberParser("NMLC-123456-A-B")
        result = parser.search_partial()
        expected = "*NMLC*123456*"
        self.assertEqual(result, expected)

    def test_search_partial_single_part(self):
        """Test search_partial with single part."""
        parser = LeaseNumberParser("NMLC")
        result = parser.search_partial()
        expected = "*NMLC*"
        self.assertEqual(result, expected)

    def test_search_partial_two_parts(self):
        """Test search_partial with exactly two parts."""
        parser = LeaseNumberParser("NMLC-123456")
        result = parser.search_partial()
        expected = "*NMLC*123456*"
        self.assertEqual(result, expected)

    def test_search_partial_no_dashes(self):
        """Test search_partial with no dashes."""
        parser = LeaseNumberParser("NMLC 123456")
        result = parser.search_partial()
        expected = "*NMLC 123456*"
        self.assertEqual(result, expected)

    def test_real_world_lease_numbers(self):
        """Test with realistic lease number formats."""
        # Federal lease format - search_tractstar doesn't extract alpha from dash-separated parts
        parser1 = LeaseNumberParser("NM-12345-A")
        self.assertEqual(parser1.search_file(), "*12345*")
        self.assertEqual(
            parser1.search_tractstar(), "12345"
        )  # No alpha extracted from dash format
        self.assertEqual(parser1.search_full(), "*NM*12345*A*")
        self.assertEqual(parser1.search_partial(), "*NM*12345*")

        # NMSLO lease format - search_tractstar extracts alpha when space-separated
        parser2 = LeaseNumberParser("NMLC 987654")
        self.assertEqual(parser2.search_file(), "*987654*")
        self.assertEqual(parser2.search_tractstar(), "987654")
        self.assertEqual(parser2.search_full(), "*NMLC 987654*")
        self.assertEqual(parser2.search_partial(), "*NMLC 987654*")

    def test_edge_cases(self):
        """Test edge cases and unusual inputs."""
        # Only numbers
        parser1 = LeaseNumberParser("123456")
        self.assertEqual(parser1.search_file(), "*123456*")
        self.assertEqual(parser1.search_tractstar(), "123456")

        # Special characters
        parser2 = LeaseNumberParser("NM@123#456")
        self.assertEqual(parser2.search_file(), "*123456*")

        # Mixed case
        parser3 = LeaseNumberParser("nmlc 123456A")
        self.assertEqual(parser3.search_tractstar(), "123456-A")


class TestParsedColumnGenerator(unittest.TestCase):
    """Test cases for ParsedColumnGenerator utility class."""

    def setUp(self):
        """Set up test data."""
        self.test_data = pd.DataFrame(
            {
                "Lease": ["NMLC 123456", "NM-789012-A", "NMLC-555666-B", "XYZ 999888"],
                "Other Column": ["A", "B", "C", "D"],
            }
        )

    def test_add_nmslo_search_columns(self):
        """Test adding NMSLO search columns."""
        result = ParsedColumnGenerator.add_nmslo_search_columns(self.test_data)

        # Should have original columns plus new search columns
        expected_columns = ["Lease", "Other Column", "Full Search", "Partial Search"]
        self.assertEqual(list(result.columns), expected_columns)

        # Check a few values
        self.assertEqual(result.iloc[0]["Full Search"], "*NMLC 123456*")
        self.assertEqual(result.iloc[0]["Partial Search"], "*NMLC 123456*")
        self.assertEqual(result.iloc[1]["Full Search"], "*NM*789012*A*")
        self.assertEqual(result.iloc[1]["Partial Search"], "*NM*789012*")

    def test_add_federal_search_columns(self):
        """Test adding federal search columns."""
        result = ParsedColumnGenerator.add_federal_search_columns(self.test_data)

        # Should have original columns plus new search columns
        expected_columns = ["Lease", "Other Column", "Files Search", "Tractstar Search"]
        self.assertEqual(list(result.columns), expected_columns)

        # Check a few values - search_tractstar behavior depends on space vs dash separation
        self.assertEqual(result.iloc[0]["Files Search"], "*123456*")
        self.assertEqual(
            result.iloc[0]["Tractstar Search"], "123456"
        )  # NMLC 123456 -> space separated, no alpha
        self.assertEqual(result.iloc[1]["Files Search"], "*789012*")
        self.assertEqual(
            result.iloc[1]["Tractstar Search"], "789012"
        )  # NM-789012-A -> dash separated, no alpha extracted

    def test_add_nmslo_search_columns_missing_lease_column(self):
        """Test error handling when Lease column is missing."""
        data_no_lease = pd.DataFrame({"Other Column": ["A", "B", "C"]})

        with self.assertRaises(ValueError) as context:
            ParsedColumnGenerator.add_nmslo_search_columns(data_no_lease)

        self.assertIn("DataFrame must contain a 'Lease' column", str(context.exception))

    def test_add_federal_search_columns_missing_lease_column(self):
        """Test error handling when Lease column is missing."""
        data_no_lease = pd.DataFrame({"Other Column": ["A", "B", "C"]})

        with self.assertRaises(ValueError) as context:
            ParsedColumnGenerator.add_federal_search_columns(data_no_lease)

        self.assertIn("DataFrame must contain a 'Lease' column", str(context.exception))

    def test_add_nmslo_search_columns_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError) as context:
            ParsedColumnGenerator.add_nmslo_search_columns("not a dataframe")

        self.assertIn("data must be a pandas DataFrame", str(context.exception))

    def test_add_federal_search_columns_invalid_dataframe(self):
        """Test error handling with invalid DataFrame."""
        with self.assertRaises(ValueError) as context:
            ParsedColumnGenerator.add_federal_search_columns("not a dataframe")

        self.assertIn("data must be a pandas DataFrame", str(context.exception))

    def test_add_nmslo_search_columns_returns_copy(self):
        """Test that NMSLO search columns method returns a copy."""
        original_data = self.test_data.copy()

        result = ParsedColumnGenerator.add_nmslo_search_columns(self.test_data)

        # Original should be unchanged
        pd.testing.assert_frame_equal(self.test_data, original_data)
        # Result should have more columns
        self.assertGreater(len(result.columns), len(original_data.columns))

    def test_add_federal_search_columns_returns_copy(self):
        """Test that federal search columns method returns a copy."""
        original_data = self.test_data.copy()

        result = ParsedColumnGenerator.add_federal_search_columns(self.test_data)

        # Original should be unchanged
        pd.testing.assert_frame_equal(self.test_data, original_data)
        # Result should have more columns
        self.assertGreater(len(result.columns), len(original_data.columns))

    def test_add_nmslo_search_columns_empty_dataframe(self):
        """Test NMSLO search columns with empty DataFrame."""
        empty_data = pd.DataFrame({"Lease": []})

        result = ParsedColumnGenerator.add_nmslo_search_columns(empty_data)

        # Should have the expected columns even with empty data
        expected_columns = ["Lease", "Full Search", "Partial Search"]
        self.assertEqual(list(result.columns), expected_columns)
        self.assertEqual(len(result), 0)

    def test_add_federal_search_columns_empty_dataframe(self):
        """Test federal search columns with empty DataFrame."""
        empty_data = pd.DataFrame({"Lease": []})

        result = ParsedColumnGenerator.add_federal_search_columns(empty_data)

        # Should have the expected columns even with empty data
        expected_columns = ["Lease", "Files Search", "Tractstar Search"]
        self.assertEqual(list(result.columns), expected_columns)
        self.assertEqual(len(result), 0)

    def test_lease_number_parser_integration(self):
        """Test that ParsedColumnGenerator correctly uses LeaseNumberParser."""
        single_lease_data = pd.DataFrame({"Lease": ["NMLC-123456-A"]})

        # Test NMSLO columns
        nmslo_result = ParsedColumnGenerator.add_nmslo_search_columns(single_lease_data)
        parser = LeaseNumberParser("NMLC-123456-A")

        self.assertEqual(nmslo_result.iloc[0]["Full Search"], parser.search_full())
        self.assertEqual(
            nmslo_result.iloc[0]["Partial Search"], parser.search_partial()
        )

        # Test federal columns
        federal_result = ParsedColumnGenerator.add_federal_search_columns(
            single_lease_data
        )

        self.assertEqual(federal_result.iloc[0]["Files Search"], parser.search_file())
        self.assertEqual(
            federal_result.iloc[0]["Tractstar Search"], parser.search_tractstar()
        )

    def test_real_world_integration(self):
        """Test with realistic data that would come from processors."""
        realistic_data = pd.DataFrame(
            {
                "Agency": ["NMSLO", "Federal", "NMSLO"],
                "Lease": ["NMLC 123456", "NM-789012-A", "NMLC-555666-B"],
                "Requested Legal": ["Legal 1", "Legal 2", "Legal 3"],
            }
        )

        # Test NMSLO processing
        nmslo_result = ParsedColumnGenerator.add_nmslo_search_columns(realistic_data)
        self.assertIn("Full Search", nmslo_result.columns)
        self.assertIn("Partial Search", nmslo_result.columns)
        self.assertEqual(len(nmslo_result), 3)

        # Test federal processing
        federal_result = ParsedColumnGenerator.add_federal_search_columns(
            realistic_data
        )
        self.assertIn("Files Search", federal_result.columns)
        self.assertIn("Tractstar Search", federal_result.columns)
        self.assertEqual(len(federal_result), 3)


if __name__ == "__main__":
    unittest.main()
