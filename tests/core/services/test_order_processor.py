"""
Integration tests for OrderProcessorService end-to-end functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import pandas as pd
from datetime import datetime

from src.core.services.order_processor import OrderProcessorService
from src.core.models import OrderData, AgencyType, ReportType


@pytest.fixture
def sample_order_data():
    """Create sample OrderData for testing."""
    return OrderData(
        order_number="TEST-001",
        order_date=datetime.now().date(),
        order_type=ReportType.RUNSHEET,
    )


@pytest.fixture
def sample_order_form():
    """Create a sample order form Excel file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
        # Create sample data
        data = {
            "Lease": ["12345", "67890"],
            "Legal Description": ["T1N R1E S1", "T2N R2E S2"],
            "Notes": ["Test note 1", "Test note 2"],
        }
        df = pd.DataFrame(data)
        df.to_excel(temp_file.name, index=False)
        yield Path(temp_file.name)
        # Cleanup handled by pytest


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_cloud_service():
    """Create a mock cloud service for testing."""
    mock_service = Mock()
    return mock_service


@pytest.fixture
def mock_progress_callback():
    """Create a mock progress callback for testing."""
    mock_callback = Mock()
    return mock_callback


class TestOrderProcessorServiceIntegration:
    """Integration tests for OrderProcessorService."""

    def test_initialization(self, mock_cloud_service, mock_progress_callback):
        """Test OrderProcessorService initialization."""
        processor = OrderProcessorService(mock_cloud_service, mock_progress_callback)
        assert processor.cloud_service == mock_cloud_service
        assert processor.progress_callback == mock_progress_callback
        assert processor.workflow_orchestrator is not None

    @patch("src.core.services.order_processor.parse_order_form_to_order_items")
    @patch("src.core.services.order_processor.export_order_items_to_worksheet")
    def test_process_order_minimal_format(
        self,
        mock_export,
        mock_parse,
        sample_order_data,
        sample_order_form,
        temp_output_dir,
        mock_cloud_service,
        mock_progress_callback,
    ):
        """Test end-to-end order processing with minimal format."""
        # Setup mocks
        mock_parse.return_value = [
            Mock(
                agency=AgencyType.NMSLO,
                lease_number="12345",
                legal_description="T1N R1E S1",
            )
        ]
        mock_export.return_value = str(temp_output_dir / "test_output.xlsx")

        # Create processor
        processor = OrderProcessorService(mock_cloud_service, mock_progress_callback)

        # Mock workflow orchestrator
        with patch.object(
            processor.workflow_orchestrator, "execute_workflows_for_order_item"
        ) as mock_workflow:
            # Execute
            result = processor.process_order(
                order_data=sample_order_data,
                order_form_path=sample_order_form,
                output_directory=temp_output_dir,
                agency=AgencyType.NMSLO,
            )

            # Verify calls
            mock_parse.assert_called_once_with(str(sample_order_form), AgencyType.NMSLO)
            mock_workflow.assert_called_once()
            mock_export.assert_called_once()

            # Verify progress updates
            assert mock_progress_callback.update_progress.call_count >= 3
            progress_calls = [
                call[0][0]
                for call in mock_progress_callback.update_progress.call_args_list
            ]
            assert "Starting order processing..." in progress_calls
            assert "Order processing complete!" in progress_calls

            # Verify result
            assert result == str(temp_output_dir / "test_output.xlsx")

    @patch("src.core.services.order_processor.parse_order_form_to_order_items")
    @patch("src.core.services.order_processor.export_order_items_to_worksheet")
    def test_process_order_legacy_format(
        self,
        mock_export,
        mock_parse,
        sample_order_data,
        sample_order_form,
        temp_output_dir,
        mock_cloud_service,
        mock_progress_callback,
    ):
        """Test end-to-end order processing with legacy format."""
        # Setup mocks
        mock_parse.return_value = [
            Mock(
                agency=AgencyType.BLM,
                lease_number="67890",
                legal_description="T2N R2E S2",
            )
        ]
        mock_export.return_value = str(temp_output_dir / "test_legacy.xlsx")

        # Create processor
        processor = OrderProcessorService(mock_cloud_service, mock_progress_callback)

        # Mock workflow orchestrator
        with patch.object(
            processor.workflow_orchestrator, "execute_workflows_for_order_item"
        ) as mock_workflow:
            # Execute
            result = processor.process_order(
                order_data=sample_order_data,
                order_form_path=sample_order_form,
                output_directory=temp_output_dir,
                agency=AgencyType.BLM,
            )

            # Verify legacy export was called
            mock_export.assert_called_once()
            assert result == str(temp_output_dir / "test_legacy.xlsx")

    def test_process_order_with_workflow_error(
        self,
        sample_order_data,
        sample_order_form,
        temp_output_dir,
        mock_cloud_service,
        mock_progress_callback,
    ):
        """Test error handling during workflow execution."""
        processor = OrderProcessorService(mock_cloud_service, mock_progress_callback)

        # Mock workflow to raise exception
        with patch.object(
            processor.workflow_orchestrator, "execute_workflows_for_order_item"
        ) as mock_workflow:
            mock_workflow.side_effect = RuntimeError("Workflow error")

            # Should continue processing despite workflow error
            with patch(
                "src.core.services.order_processor.parse_order_form_to_order_items"
            ) as mock_parse:
                with patch(
                    "src.core.services.order_processor.export_order_items_to_worksheet"
                ) as mock_export:
                    mock_parse.return_value = [Mock()]
                    mock_export.return_value = str(temp_output_dir / "output.xlsx")

                    # Should not raise exception
                    result = processor.process_order(
                        order_data=sample_order_data,
                        order_form_path=sample_order_form,
                        output_directory=temp_output_dir,
                        agency=AgencyType.NMSLO,
                    )

                    # Should still complete and export
                    assert result is not None


class TestGUIIntegration:
    """Test GUI integration aspects."""

    def test_report_type_conversion(self):
        """Test converting GUI report type strings to ReportType enum."""
        test_cases = [
            ("Runsheet", ReportType.RUNSHEET),
            ("Abstract", ReportType.BASE_ABSTRACT),
        ]

        for gui_value, expected_enum in test_cases:
            report_type = (
                ReportType.RUNSHEET
                if gui_value == "Runsheet"
                else ReportType.BASE_ABSTRACT
            )
            assert report_type == expected_enum
