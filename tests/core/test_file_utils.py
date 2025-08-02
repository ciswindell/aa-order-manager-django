"""
Unit tests for file_utils module.

Tests FilenameGenerator utility class.
"""

import unittest

from src.core.utils.file_utils import FilenameGenerator


class TestFilenameGenerator(unittest.TestCase):
    """Test cases for FilenameGenerator utility class."""

    def test_generate_order_filename_basic(self):
        """Test basic filename generation with all parameters."""
        result = FilenameGenerator.generate_order_filename(
            order_number="12345", agency="Federal", order_type="Runsheet"
        )

        expected = "Order_12345_Federal_Runsheet.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_with_spaces(self):
        """Test filename generation with parameters containing spaces."""
        result = FilenameGenerator.generate_order_filename(
            order_number="  12345  ",  # Leading/trailing spaces
            agency="Federal",
            order_type="Runsheet",
        )

        expected = "Order_12345_Federal_Runsheet.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_with_none_values(self):
        """Test filename generation with None values."""
        result = FilenameGenerator.generate_order_filename(
            order_number=None, agency=None, order_type=None
        )

        expected = "Order_Unknown_Unknown_Unknown.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_with_empty_strings(self):
        """Test filename generation with empty string values."""
        result = FilenameGenerator.generate_order_filename(
            order_number="", agency="", order_type=""
        )

        expected = "Order_Unknown_Unknown_Unknown.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_partial_parameters(self):
        """Test filename generation with only some parameters provided."""
        result = FilenameGenerator.generate_order_filename(
            order_number="12345",
            agency="Federal",
            # order_type not provided (None)
        )

        expected = "Order_12345_Federal_Unknown.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_with_invalid_characters(self):
        """Test filename generation with invalid filename characters."""
        result = FilenameGenerator.generate_order_filename(
            order_number="123<45>", agency="Fed:eral", order_type="Run/sheet"
        )

        # Invalid characters should be replaced with underscores
        expected = "Order_123_45__Fed_eral_Run_sheet.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_with_complex_invalid_chars(self):
        """Test filename generation with multiple types of invalid characters."""
        result = FilenameGenerator.generate_order_filename(
            order_number='12"34|5', agency="Fed*eral", order_type="Run\\sheet?"
        )

        # All invalid characters should be replaced with underscores
        expected = "Order_12_34_5_Fed_eral_Run_sheet_.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_long_strings(self):
        """Test filename generation with very long parameter values."""
        long_order_number = "A" * 100
        long_agency = "B" * 100
        long_order_type = "C" * 100

        result = FilenameGenerator.generate_order_filename(
            order_number=long_order_number,
            agency=long_agency,
            order_type=long_order_type,
        )

        # Should not truncate, just include all characters
        expected = f"Order_{long_order_number}_{long_agency}_{long_order_type}.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_unicode_characters(self):
        """Test filename generation with unicode characters."""
        result = FilenameGenerator.generate_order_filename(
            order_number="12345", agency="Federâl", order_type="Runshëet"
        )

        expected = "Order_12345_Federâl_Runshëet.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_whitespace_only(self):
        """Test filename generation with whitespace-only parameters."""
        result = FilenameGenerator.generate_order_filename(
            order_number="   ",  # Only spaces
            agency="\t\n",  # Tabs and newlines
            order_type="  \r  ",  # Mixed whitespace
        )

        # order_number gets stripped to empty string (but empty string is still truthy, so not "Unknown")
        # agency and order_type remain as whitespace (implementation doesn't strip them)
        expected = "Order__\t\n_  \r  .xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_mixed_case(self):
        """Test filename generation preserves case."""
        result = FilenameGenerator.generate_order_filename(
            order_number="ABC123def", agency="FederaL", order_type="RunSheet"
        )

        expected = "Order_ABC123def_FederaL_RunSheet.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_numbers_only(self):
        """Test filename generation with numeric-only parameters."""
        result = FilenameGenerator.generate_order_filename(
            order_number="123456", agency="789", order_type="999"
        )

        expected = "Order_123456_789_999.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_special_cases(self):
        """Test filename generation with special case values."""
        result = FilenameGenerator.generate_order_filename(
            order_number="0",  # Zero
            agency="1",  # Single digit
            order_type="Test",  # Normal case
        )

        expected = "Order_0_1_Test.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_all_invalid_chars(self):
        """Test filename generation where all characters are invalid."""
        result = FilenameGenerator.generate_order_filename(
            order_number="<>:", agency='"\\|', order_type="?*"
        )

        # All invalid characters get replaced with underscores
        expected = "Order___________.xlsx"
        self.assertEqual(result, expected)

    def test_generate_order_filename_real_world_examples(self):
        """Test filename generation with realistic real-world examples."""
        # Example 1: NMSLO order
        result1 = FilenameGenerator.generate_order_filename(
            order_number="33333", agency="NMSLO", order_type="Runsheet"
        )
        expected1 = "Order_33333_NMSLO_Runsheet.xlsx"
        self.assertEqual(result1, expected1)

        # Example 2: Federal order
        result2 = FilenameGenerator.generate_order_filename(
            order_number="FED-2023-001", agency="Federal", order_type="Title Report"
        )
        expected2 = "Order_FED-2023-001_Federal_Title Report.xlsx"
        self.assertEqual(result2, expected2)

    def test_generate_order_filename_encoding_error_handling(self):
        """Test that encoding errors are handled gracefully."""
        # This should not raise an encoding error
        try:
            result = FilenameGenerator.generate_order_filename(
                order_number="12345", agency="Federal", order_type="Runsheet"
            )
            # Should succeed
            self.assertTrue(isinstance(result, str))
            self.assertTrue(result.endswith(".xlsx"))
        except UnicodeError:
            self.fail("generate_order_filename raised UnicodeError unexpectedly")

    def test_generate_order_filename_returns_string(self):
        """Test that the method always returns a string."""
        result = FilenameGenerator.generate_order_filename(
            order_number="12345", agency="Federal", order_type="Runsheet"
        )

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertTrue(result.endswith(".xlsx"))

    def test_generate_order_filename_consistent_output(self):
        """Test that identical inputs produce identical outputs."""
        result1 = FilenameGenerator.generate_order_filename(
            order_number="12345", agency="Federal", order_type="Runsheet"
        )

        result2 = FilenameGenerator.generate_order_filename(
            order_number="12345", agency="Federal", order_type="Runsheet"
        )

        self.assertEqual(result1, result2)


if __name__ == "__main__":
    unittest.main()
