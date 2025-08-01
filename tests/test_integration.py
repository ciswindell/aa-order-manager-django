"""
Integration Tests for Dropbox-Enabled Order Processors

Tests the complete end-to-end workflow of order processing with Dropbox link integration,
including both Federal and State processors with various scenarios.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from processors import FederalOrderProcessor, NMStateOrderProcessor


class TestDropboxIntegration(unittest.TestCase):
    """Test end-to-end integration of order processors with Dropbox service."""

    def setUp(self):
        """Set up test fixtures with sample data and mock Dropbox service."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Sample order data for testing
        self.sample_data = pd.DataFrame(
            {
                "Lease": ["NMLC 123456", "NMLC 789012", "NMLC 345678"],
                "Requested Legal": ["Legal desc 1", "Legal desc 2", "Legal desc 3"],
                "Report Start Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            }
        )

        # Create sample Excel file
        self.test_excel_file = self.temp_path / "test_order.xlsx"
        self.sample_data.to_excel(self.test_excel_file, index=False)

        # Mock Dropbox service
        self.mock_dropbox_service = Mock()
        self.mock_dropbox_service.search_directory.return_value = (
            "https://dropbox.com/s/abc123/NMLC%20123456"
        )

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_federal_processor_with_dropbox_service(self):
        """Test FederalOrderProcessor with Dropbox service integration."""
        # Create processor with Dropbox service
        processor = FederalOrderProcessor(
            order_form=str(self.test_excel_file),
            agency="Federal",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="12345",
            dropbox_service=self.mock_dropbox_service,
        )

        # Mock successful Dropbox responses for each lease
        def mock_search_directory(lease_name, agency):
            return f"https://dropbox.com/s/mock123/{lease_name.replace(' ', '%20')}"

        self.mock_dropbox_service.search_directory.side_effect = mock_search_directory

        # Execute order worksheet creation
        with patch("builtins.print"):  # Suppress print output during test
            processor.create_order_worksheet()

        # Verify Dropbox service was called correctly
        self.assertEqual(self.mock_dropbox_service.search_directory.call_count, 3)

        # Verify calls were made with correct parameters
        call_args_list = self.mock_dropbox_service.search_directory.call_args_list
        for i, call_args in enumerate(call_args_list):
            lease_name = self.sample_data.iloc[i]["Lease"]
            self.assertEqual(call_args[0][0], lease_name)  # First argument: lease name
            self.assertEqual(
                call_args[1]["agency"], "Federal"
            )  # Keyword argument: agency

        # Verify output file was created
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify the output file contains the expected data with Link column
        output_file = output_files[0]
        result_data = pd.read_excel(output_file)

        # Check that Link column exists and has values
        self.assertIn("Link", result_data.columns)

        # Check that links were populated for all leases
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 3)  # All 3 leases should have links

    def test_state_processor_with_dropbox_service(self):
        """Test NMStateOrderProcessor with Dropbox service integration."""
        # Create processor with Dropbox service
        processor = NMStateOrderProcessor(
            order_form=str(self.test_excel_file),
            agency="State",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="67890",
            dropbox_service=self.mock_dropbox_service,
        )

        # Mock successful Dropbox responses
        def mock_search_directory(lease_name, agency):
            return f"https://dropbox.com/s/state456/{lease_name.replace(' ', '%20')}"

        self.mock_dropbox_service.search_directory.side_effect = mock_search_directory

        # Execute order worksheet creation
        with patch("builtins.print"):  # Suppress print output during test
            processor.create_order_worksheet()

        # Verify Dropbox service was called with State agency
        call_args_list = self.mock_dropbox_service.search_directory.call_args_list
        for call_args in call_args_list:
            self.assertEqual(call_args[1]["agency"], "NMState")

        # Verify output file was created with populated links
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        result_data = pd.read_excel(output_files[0])
        self.assertIn("Link", result_data.columns)

        # Verify all links were populated
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 3)

    def test_processor_without_dropbox_service(self):
        """Test that processors work normally without Dropbox service."""
        # Create processor without Dropbox service (None)
        processor = FederalOrderProcessor(
            order_form=str(self.test_excel_file),
            agency="Federal",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="11111",
            # dropbox_service=None (default)
        )

        # Execute order worksheet creation
        processor.create_order_worksheet()

        # Verify output file was created
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify Link column exists but is empty (no Dropbox integration)
        result_data = pd.read_excel(output_files[0])
        self.assertIn("Link", result_data.columns)

        # All links should be NaN/empty when no Dropbox service
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 0)

    def test_dropbox_service_with_partial_failures(self):
        """Test graceful handling when some Dropbox searches fail."""
        processor = FederalOrderProcessor(
            order_form=str(self.test_excel_file),
            agency="Federal",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="22222",
            dropbox_service=self.mock_dropbox_service,
        )

        # Mock mixed success/failure responses
        def mock_search_with_failures(lease_name, agency):
            if "123456" in lease_name:
                return "https://dropbox.com/s/success/NMLC%20123456"
            elif "789012" in lease_name:
                raise Exception("Network error")
            else:
                return None  # Directory not found

        self.mock_dropbox_service.search_directory.side_effect = (
            mock_search_with_failures
        )

        # Execute order worksheet creation (should not fail)
        with patch("builtins.print"):  # Suppress print output during test
            processor.create_order_worksheet()

        # Verify output file was still created despite partial failures
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify that successful link was populated, others are empty
        result_data = pd.read_excel(output_files[0])
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 1)  # Only one successful link

    def test_dropbox_service_complete_failure(self):
        """Test graceful handling when Dropbox service fails completely."""
        processor = NMStateOrderProcessor(
            order_form=str(self.test_excel_file),
            agency="State",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="33333",
            dropbox_service=self.mock_dropbox_service,
        )

        # Mock complete Dropbox failure
        self.mock_dropbox_service.search_directory.side_effect = Exception(
            "Dropbox API unavailable"
        )

        # Execute order worksheet creation (should not fail)
        with patch("builtins.print"):  # Suppress print output during test
            processor.create_order_worksheet()

        # Verify output file was still created despite Dropbox failure
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify Link column exists but is empty due to service failure
        result_data = pd.read_excel(output_files[0])
        self.assertIn("Link", result_data.columns)
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 0)  # No links due to complete failure

    def test_empty_lease_names_handling(self):
        """Test handling of empty or invalid lease names."""
        # Create data with some empty lease names
        test_data = pd.DataFrame(
            {
                "Lease": ["NMLC 123456", "", "NMLC 789012", None, "NMLC 345678"],
                "Requested Legal": [
                    "Legal 1",
                    "Legal 2",
                    "Legal 3",
                    "Legal 4",
                    "Legal 5",
                ],
                "Report Start Date": [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ],
            }
        )

        test_file = self.temp_path / "test_empty_leases.xlsx"
        test_data.to_excel(test_file, index=False)

        processor = FederalOrderProcessor(
            order_form=str(test_file),
            agency="Federal",
            order_type="Runsheet",
            order_date="2024-01-01",
            order_number="44444",
            dropbox_service=self.mock_dropbox_service,
        )

        # Mock Dropbox service to return links for valid leases
        def mock_search_valid_only(lease_name, agency):
            if lease_name and lease_name.strip():
                return f"https://dropbox.com/s/valid/{lease_name.replace(' ', '%20')}"
            return None

        self.mock_dropbox_service.search_directory.side_effect = mock_search_valid_only

        # Execute order worksheet creation
        with patch("builtins.print"):
            processor.create_order_worksheet()

        # Verify only valid leases were processed
        # Should have called search_directory for 3 valid leases (not for empty/None ones)
        valid_calls = [
            call
            for call in self.mock_dropbox_service.search_directory.call_args_list
            if call[0][0] and call[0][0].strip()
        ]
        self.assertEqual(len(valid_calls), 3)

        # Verify output file was created
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)


class TestWorkflowIntegration(unittest.TestCase):
    """Test complete workflow scenarios similar to GUI usage."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_workflow_simulation_federal_with_dropbox(self):
        """Simulate complete workflow for Federal agency with Dropbox enabled."""
        # Create sample order form
        order_data = pd.DataFrame(
            {
                "Lease": ["NMLC 111111", "NMLC 222222"],
                "Requested Legal": ["Legal description 1", "Legal description 2"],
                "Report Start Date": ["2024-01-01", "2024-01-02"],
            }
        )

        order_file = self.temp_path / "federal_order.xlsx"
        order_data.to_excel(order_file, index=False)

        # Simulate GUI inputs
        selected_agency = "Federal"
        selected_order_type = "Runsheet"
        selected_order_date = "2024-01-15"
        selected_order_number = "FED2024001"
        use_dropbox = True  # Checkbox enabled

        # Mock Dropbox service initialization (simulating app.py behavior)
        mock_dropbox_service = Mock()
        mock_dropbox_service.search_directory.return_value = (
            "https://dropbox.com/s/workflow/NMLC%20111111"
        )

        # Create processor as app.py would
        if selected_agency == "Federal":
            processor = FederalOrderProcessor(
                order_form=str(order_file),
                agency=selected_agency,
                order_type=selected_order_type,
                order_date=selected_order_date,
                order_number=selected_order_number,
                dropbox_service=mock_dropbox_service if use_dropbox else None,
            )

        # Execute workflow
        with patch("builtins.print"):
            processor.create_order_worksheet()

        # Verify results
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify filename includes GUI inputs
        output_filename = output_files[0].name
        self.assertIn("FED2024001", output_filename)
        self.assertIn("Federal", output_filename)
        self.assertIn("Runsheet", output_filename)

        # Verify Dropbox integration worked
        self.assertTrue(mock_dropbox_service.search_directory.called)

    def test_workflow_simulation_state_without_dropbox(self):
        """Simulate complete workflow for State agency with Dropbox disabled."""
        # Create sample order form
        order_data = pd.DataFrame(
            {
                "Lease": ["NMLC 333333", "NMLC 444444"],
                "Requested Legal": ["State legal 1", "State legal 2"],
                "Report Start Date": ["2024-02-01", "2024-02-02"],
            }
        )

        order_file = self.temp_path / "state_order.xlsx"
        order_data.to_excel(order_file, index=False)

        # Simulate GUI inputs with Dropbox disabled
        selected_agency = "State"
        selected_order_type = "Runsheet"
        selected_order_date = "2024-02-15"
        selected_order_number = "STATE2024001"
        use_dropbox = False  # Checkbox disabled

        # Create processor as app.py would
        if selected_agency == "State":
            processor = NMStateOrderProcessor(
                order_form=str(order_file),
                agency=selected_agency,
                order_type=selected_order_type,
                order_date=selected_order_date,
                order_number=selected_order_number,
                dropbox_service=None,  # No Dropbox service when disabled
            )

        # Execute workflow
        processor.create_order_worksheet()

        # Verify results
        output_files = list(self.temp_path.glob("Order_*.xlsx"))
        self.assertEqual(len(output_files), 1)

        # Verify filename includes GUI inputs
        output_filename = output_files[0].name
        self.assertIn("STATE2024001", output_filename)
        self.assertIn("State", output_filename)
        self.assertIn("Runsheet", output_filename)

        # Verify Link column exists but is empty (no Dropbox)
        result_data = pd.read_excel(output_files[0])
        self.assertIn("Link", result_data.columns)
        link_column = result_data["Link"]
        non_null_links = link_column.dropna()
        self.assertEqual(len(non_null_links), 0)


if __name__ == "__main__":
    unittest.main()
