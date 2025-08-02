"""
Unit tests for order processors.

Simple tests for processors using configuration instead of hard-coded values.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.core.processors import NMSLOOrderProcessor, FederalOrderProcessor
from tests.core.config.test_utils import create_mock_static_config, create_mock_behavioral_config


class TestNMSLOOrderProcessor:
    """Test NMSLOOrderProcessor with configuration integration."""

    @patch('pandas.read_excel')
    def test_processor_initialization_with_config(self, mock_read_excel):
        """Test that processor initializes correctly with configuration."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Lease': ['B-1234-5'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01']
        })
        mock_read_excel.return_value = mock_data
        
        # Create mock configurations
        static_config = create_mock_static_config("NMSLO")
        behavioral_config = create_mock_behavioral_config()
        
        # Create mock order form data
        mock_order_form = Mock()
        
        processor = NMSLOOrderProcessor(
            order_form=mock_order_form,
            agency="NMSLO",
            order_type="Test Order",
            order_date="2024-01-01",
            order_number="12345",
            static_config=static_config,
            behavioral_config=behavioral_config
        )
        
        assert processor.agency == "NMSLO"
        assert processor.order_type == "Test Order"
        assert processor.static_config == static_config
        assert processor.behavioral_config == behavioral_config

    @patch('pandas.read_excel')
    def test_processor_uses_default_config_when_none_provided(self, mock_read_excel):
        """Test that processor uses default configuration when none provided."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Lease': ['B-1234-5'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01']
        })
        mock_read_excel.return_value = mock_data
        
        mock_order_form = Mock()
        
        processor = NMSLOOrderProcessor(
            order_form=mock_order_form,
            agency="NMSLO"
        )
        
        # Should have default NMSLO configuration
        assert processor.static_config is not None
        assert processor.behavioral_config is not None
        assert processor.static_config.dropbox_agency_name == "NMSLO"

    @patch('pandas.read_excel')
    def test_read_order_form(self, mock_read_excel):
        """Test read_order_form method."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Lease': ['B-1234-5', 'B-6789-0'],
            'Requested Legal': ['Legal 1', 'Legal 2'],
            'Report Start Date': ['2024-01-01', '2024-01-02']
        })
        mock_read_excel.return_value = mock_data
        
        mock_order_form = Mock()
        processor = NMSLOOrderProcessor(
            order_form=mock_order_form,
            agency="NMSLO"
        )
        
        # Should call pandas.read_excel
        mock_read_excel.assert_called_once_with(mock_order_form)
        assert len(processor.data) == 2

    @patch('pandas.read_excel')
    def test_process_data_adds_metadata_columns(self, mock_read_excel):
        """Test that process_data adds metadata columns."""
        # Create test data
        test_data = pd.DataFrame({
            'Lease': ['B-1234-5'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01']
        })
        mock_read_excel.return_value = test_data
        
        mock_order_form = Mock()
        processor = NMSLOOrderProcessor(
            order_form=mock_order_form,
            agency="NMSLO",
            order_type="Test Order",
            order_date="2024-01-01",
            order_number="12345"
        )
        
        # Process data
        result = processor.process_data()
        
        # Check metadata columns were added
        assert 'Agency' in result.columns
        assert 'Order Type' in result.columns
        assert 'Order Number' in result.columns
        assert 'Order Date' in result.columns
        assert result['Agency'].iloc[0] == "NMSLO"
        assert result['Order Type'].iloc[0] == "Test Order"

    @patch('pandas.read_excel')
    def test_process_data_uses_behavioral_config(self, mock_read_excel):
        """Test that process_data uses behavioral configuration."""
        # Create mock behavioral config
        def mock_search_func(data):
            return f"search_{data}"
        
        behavioral_config = create_mock_behavioral_config()
        behavioral_config.search_mappings = {"Test Search": mock_search_func}
        
        # Create test data
        test_data = pd.DataFrame({
            'Lease': ['B-1234-5'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01']
        })
        mock_read_excel.return_value = test_data
        
        mock_order_form = Mock()
        processor = NMSLOOrderProcessor(
            order_form=mock_order_form,
            agency="NMSLO",
            behavioral_config=behavioral_config
        )
        
        # Process data
        result = processor.process_data()
        
        # Check search columns were added using behavioral config
        assert 'Test Search' in result.columns
        assert result['Test Search'].iloc[0] == "search_B-1234-5"


class TestFederalOrderProcessor:
    """Test FederalOrderProcessor with configuration integration."""

    @patch('pandas.read_excel')
    def test_processor_initialization_with_config(self, mock_read_excel):
        """Test that processor initializes correctly with configuration."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Lease': ['NMNM 12345A'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01'],
            'Notes': ['Note 1']
        })
        mock_read_excel.return_value = mock_data
        
        # Create mock configurations
        static_config = create_mock_static_config("Federal")
        behavioral_config = create_mock_behavioral_config()
        
        # Create mock order form data
        mock_order_form = Mock()
        
        processor = FederalOrderProcessor(
            order_form=mock_order_form,
            agency="Federal",
            order_type="Test Order",
            order_date="2024-01-01",
            order_number="12345",
            static_config=static_config,
            behavioral_config=behavioral_config
        )
        
        assert processor.agency == "Federal"
        assert processor.order_type == "Test Order"
        assert processor.static_config == static_config
        assert processor.behavioral_config == behavioral_config

    @patch('pandas.read_excel')
    def test_processor_uses_default_config_when_none_provided(self, mock_read_excel):
        """Test that processor uses default configuration when none provided."""
        # Create mock data
        mock_data = pd.DataFrame({
            'Lease': ['NMNM 12345A'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01'],
            'Notes': ['Note 1']
        })
        mock_read_excel.return_value = mock_data
        
        mock_order_form = Mock()
        
        processor = FederalOrderProcessor(
            order_form=mock_order_form,
            agency="Federal"
        )
        
        # Should have default Federal configuration
        assert processor.static_config is not None
        assert processor.behavioral_config is not None
        assert processor.static_config.dropbox_agency_name == "Federal"

    @patch('pandas.read_excel')
    def test_read_order_form_includes_notes_column(self, mock_read_excel):
        """Test read_order_form method includes Notes column for Federal."""
        # Create mock data with Notes column
        mock_data = pd.DataFrame({
            'Lease': ['NMNM 12345A'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01'],
            'Notes': ['Note 1']  # Federal-specific column
        })
        mock_read_excel.return_value = mock_data
        
        mock_order_form = Mock()
        processor = FederalOrderProcessor(
            order_form=mock_order_form,
            agency="Federal"
        )
        
        # Should call pandas.read_excel
        mock_read_excel.assert_called_once_with(mock_order_form)
        assert len(processor.data) == 1
        assert 'Notes' in processor.data.columns

    @patch('pandas.read_excel')
    def test_process_data_adds_federal_specific_columns(self, mock_read_excel):
        """Test that process_data adds Federal-specific columns."""
        # Create test data with Notes column
        test_data = pd.DataFrame({
            'Lease': ['NMNM 12345A'],
            'Requested Legal': ['Legal 1'],
            'Report Start Date': ['2024-01-01'],
            'Notes': ['Note 1']
        })
        mock_read_excel.return_value = test_data
        
        mock_order_form = Mock()
        processor = FederalOrderProcessor(
            order_form=mock_order_form,
            agency="Federal",
            order_type="Test Order",
            order_date="2024-01-01",
            order_number="12345"
        )
        
        # Process data
        result = processor.process_data()
        
        # Check metadata columns were added
        assert 'Agency' in result.columns
        assert 'Order Type' in result.columns
        assert 'Order Number' in result.columns
        assert 'Order Date' in result.columns
        assert result['Agency'].iloc[0] == "Federal"
        
        # Check Notes column is preserved (Federal-specific)
        assert 'Notes' in result.columns
        assert result['Notes'].iloc[0] == "Note 1" 