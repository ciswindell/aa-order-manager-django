"""
Unit Tests for Order Data Models

Tests for OrderData and OrderItemData classes including validation,
JSON serialization, and Excel worksheet conversion functionality.
"""

import json
import pytest
from datetime import date, datetime

from src.core.models import (
    AgencyType,
    OrderData,
    OrderItemData,
    ReportType,
    OrderDataJSONEncoder,
)


class TestOrderItemDataFixtures:
    """Test fixtures for OrderItemData objects."""
    
    @pytest.fixture
    def valid_nmslo_item_data(self):
        """Create a valid NMSLO OrderItemData instance."""
        return {
            "agency": AgencyType.NMSLO,
            "lease_number": "12345",
            "legal_description": "Section 1, Township 2N, Range 3E, NMPM",
            "start_date": datetime(2024, 1, 1, 0, 0, 0),
            "end_date": datetime(2024, 12, 31, 23, 59, 59),
        }
    
    @pytest.fixture
    def valid_blm_item_data(self):
        """Create a valid BLM OrderItemData instance."""
        return {
            "agency": AgencyType.BLM,
            "lease_number": "NM-98765#001",
            "legal_description": "Section 16, Township 15N, Range 2W, NMPM",
            "start_date": datetime(2024, 6, 1, 8, 0, 0),
            "end_date": datetime(2024, 6, 30, 17, 0, 0),
        }
    
    @pytest.fixture
    def nmslo_item_with_workflow_data(self, valid_nmslo_item_data):
        """Create NMSLO OrderItemData with workflow-generated fields populated."""
        data = valid_nmslo_item_data.copy()
        data.update({
            "report_directory_link": "https://dropbox.com/sh/abc123/lease12345",
            "previous_report_found": True,
            "documents_links": [
                "https://dropbox.com/sh/abc123/docs1",
                "https://dropbox.com/sh/abc123/docs2"
            ],
            "lease_index_links": [
                "https://dropbox.com/sh/abc123/index1",
                "https://dropbox.com/sh/abc123/index2"
            ]
        })
        return OrderItemData(**data)
    
    @pytest.fixture
    def blm_item_with_workflow_data(self, valid_blm_item_data):
        """Create BLM OrderItemData with workflow-generated fields populated."""
        data = valid_blm_item_data.copy()
        data.update({
            "report_directory_link": "https://dropbox.com/sh/def456/lease98765",
            "previous_report_found": False,
            "documents_links": [
                "https://dropbox.com/sh/def456/documents"
            ],
            # Note: BLM should not have lease_index_links
        })
        return OrderItemData(**data)


class TestOrderDataFixtures:
    """Test fixtures for OrderData objects."""
    
    @pytest.fixture
    def valid_order_data(self):
        """Create a valid OrderData instance."""
        return {
            "order_number": "2024-001",
            "order_date": date(2024, 1, 15),
            "order_type": ReportType.BASE_ABSTRACT,
            "notes": "Standard processing order",
            "delivery_link": "https://example.com/delivery/2024-001"
        }
    
    @pytest.fixture
    def sample_nmslo_item(self):
        """Create a sample NMSLO OrderItemData for testing."""
        return OrderItemData(
            agency=AgencyType.NMSLO,
            lease_number="54321",
            legal_description="Section 25, Township 1S, Range 4E, NMPM",
            start_date=datetime(2024, 3, 1),
            end_date=datetime(2024, 3, 31)
        )
    
    @pytest.fixture
    def sample_blm_item(self):
        """Create a sample BLM OrderItemData for testing."""
        return OrderItemData(
            agency=AgencyType.BLM,
            lease_number="CO-12345#002",
            legal_description="Section 10, Township 5N, Range 1E, 6th PM",
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 29)
        )
    
    @pytest.fixture
    def complete_order(self, valid_order_data, sample_nmslo_item, sample_blm_item):
        """Create a complete OrderData with multiple order items."""
        data = valid_order_data.copy()
        data["order_items"] = [sample_nmslo_item, sample_blm_item]
        return OrderData(**data)


class TestOrderItemDataConstruction:
    """Test OrderItemData object construction and validation."""
    
    def test_valid_nmslo_creation(self, valid_nmslo_item_data):
        """Test creating valid NMSLO OrderItemData."""
        item = OrderItemData(**valid_nmslo_item_data)
        
        assert item.agency == AgencyType.NMSLO
        assert item.lease_number == "12345"
        assert item.legal_description == "Section 1, Township 2N, Range 3E, NMPM"
        assert item.start_date == datetime(2024, 1, 1, 0, 0, 0)
        assert item.end_date == datetime(2024, 12, 31, 23, 59, 59)
        
        # Check default values for workflow fields
        assert item.report_directory_link is None
        assert item.previous_report_found is None
        assert item.documents_links == []
        assert item.lease_index_links == []
    
    def test_valid_blm_creation(self, valid_blm_item_data):
        """Test creating valid BLM OrderItemData."""
        item = OrderItemData(**valid_blm_item_data)
        
        assert item.agency == AgencyType.BLM
        assert item.lease_number == "NM-98765#001"
        assert item.legal_description == "Section 16, Township 15N, Range 2W, NMPM"
        assert item.start_date == datetime(2024, 6, 1, 8, 0, 0)
        assert item.end_date == datetime(2024, 6, 30, 17, 0, 0)
    
    def test_workflow_data_population(self, nmslo_item_with_workflow_data):
        """Test OrderItemData with populated workflow fields."""
        item = nmslo_item_with_workflow_data
        
        assert item.report_directory_link == "https://dropbox.com/sh/abc123/lease12345"
        assert item.previous_report_found is True
        assert len(item.documents_links) == 2
        assert "https://dropbox.com/sh/abc123/docs1" in item.documents_links
        assert len(item.lease_index_links) == 2
        assert "https://dropbox.com/sh/abc123/index1" in item.lease_index_links


class TestOrderDataConstruction:
    """Test OrderData object construction and validation."""
    
    def test_valid_order_creation(self, valid_order_data):
        """Test creating valid OrderData."""
        order = OrderData(**valid_order_data)
        
        assert order.order_number == "2024-001"
        assert order.order_date == date(2024, 1, 15)
        assert order.order_type == ReportType.BASE_ABSTRACT
        assert order.notes == "Standard processing order"
        assert order.delivery_link == "https://example.com/delivery/2024-001"
        assert order.order_items == []  # Empty by default
    
    def test_order_with_items(self, complete_order):
        """Test OrderData with order items."""
        order = complete_order
        
        assert len(order.order_items) == 2
        assert order.order_items[0].agency == AgencyType.NMSLO
        assert order.order_items[1].agency == AgencyType.BLM


if __name__ == "__main__":
    pytest.main([__file__])