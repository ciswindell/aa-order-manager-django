"""
Unit tests for WorkflowOrchestrator service.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.services.workflow_orchestrator import WorkflowOrchestrator
from src.core.models import OrderItemData, ReportType, AgencyType
from src.integrations.cloud.protocols import CloudOperations


@pytest.fixture
def mock_cloud_service():
    """Create a mock cloud service for testing."""
    mock_service = Mock()
    return mock_service


@pytest.fixture
def orchestrator(mock_cloud_service):
    """Create a WorkflowOrchestrator instance for testing."""
    return WorkflowOrchestrator(mock_cloud_service)


@pytest.fixture
def sample_order_item():
    """Create a sample OrderItemData for testing."""
    return OrderItemData(
        agency=AgencyType.NMSLO, lease_number="12345", legal_description="T1N R1E S1"
    )


class TestWorkflowOrchestrator:
    """Test cases for WorkflowOrchestrator class."""

    def test_init(self, mock_cloud_service):
        """Test WorkflowOrchestrator initialization."""
        orchestrator = WorkflowOrchestrator(mock_cloud_service)
        assert orchestrator.cloud_service == mock_cloud_service

    @patch("src.core.services.workflow_orchestrator.LeaseDirectorySearchWorkflow")
    @patch("src.core.services.workflow_orchestrator.PreviousReportDetectionWorkflow")
    def test_execute_runsheet_workflows(
        self, mock_prev_workflow, mock_lease_workflow, orchestrator, sample_order_item
    ):
        """Test execution of Runsheet workflows."""
        # Setup mocks
        mock_lease_instance = Mock()
        mock_prev_instance = Mock()
        mock_lease_workflow.return_value = mock_lease_instance
        mock_prev_workflow.return_value = mock_prev_instance

        # Execute
        result = orchestrator.execute_workflows_for_order_item(
            sample_order_item, ReportType.RUNSHEET
        )

        # Verify workflows were created with cloud service
        mock_lease_workflow.assert_called_once_with(
            cloud_service=orchestrator.cloud_service
        )
        mock_prev_workflow.assert_called_once_with(
            cloud_service=orchestrator.cloud_service
        )

        # Verify workflows were executed with order item data
        mock_lease_instance.execute.assert_called_once_with(
            {"order_item_data": sample_order_item}
        )
        mock_prev_instance.execute.assert_called_once_with(
            {"order_item_data": sample_order_item}
        )

        # Verify original order item is returned
        assert result == sample_order_item

    def test_execute_abstract_workflows(self, orchestrator, sample_order_item):
        """Test execution of Abstract workflows (placeholder)."""
        # Test all abstract types
        abstract_types = [
            ReportType.BASE_ABSTRACT,
            ReportType.SUPPLEMENTAL_ABSTRACT,
            ReportType.DOL_ABSTRACT,
        ]

        for report_type in abstract_types:
            result = orchestrator.execute_workflows_for_order_item(
                sample_order_item, report_type
            )
            assert result == sample_order_item

    def test_unsupported_order_type(self, orchestrator, sample_order_item):
        """Test handling of unsupported order types."""
        # Create a mock unsupported report type
        with patch("src.core.models.ReportType") as mock_report_type:
            mock_report_type.UNSUPPORTED = "UNSUPPORTED"

            with pytest.raises(ValueError, match="Unsupported order type"):
                orchestrator.execute_workflows_for_order_item(
                    sample_order_item, "UNSUPPORTED"
                )

    def test_execute_workflows_for_order_items_success(self, orchestrator):
        """Test successful execution for multiple order items."""
        order_items = [
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="12345",
                legal_description="T1N R1E S1",
            ),
            OrderItemData(
                agency=AgencyType.BLM,
                lease_number="67890",
                legal_description="T2N R2E S2",
            ),
        ]

        with patch.object(
            orchestrator, "execute_workflows_for_order_item"
        ) as mock_execute:
            mock_execute.return_value = order_items[0]  # Mock return value

            result = orchestrator.execute_workflows_for_order_items(
                order_items, ReportType.RUNSHEET
            )

            # Verify execute was called for each item
            assert mock_execute.call_count == 2
            assert result == order_items  # Returns the original list

    def test_execute_workflows_for_order_items_with_error(self, orchestrator):
        """Test error handling when processing multiple order items."""
        order_items = [
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="12345",
                legal_description="T1N R1E S1",
            ),
            OrderItemData(
                agency=AgencyType.BLM,
                lease_number="67890",
                legal_description="T2N R2E S2",
            ),
        ]

        with patch.object(
            orchestrator, "execute_workflows_for_order_item"
        ) as mock_execute:
            # First call raises exception, second succeeds
            mock_execute.side_effect = [Exception("Test error"), order_items[1]]

            result = orchestrator.execute_workflows_for_order_items(
                order_items, ReportType.RUNSHEET
            )

            # Verify both items were attempted despite first error
            assert mock_execute.call_count == 2
            assert result == order_items  # Returns the original list
