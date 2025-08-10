"""
Unit tests for OrderFormParser.

Simple tests for the SOLID-compliant order form parser.
"""

import os
import tempfile
import pytest
import pandas as pd

from src.core.models import AgencyType
from src.core.services.order_form_parser import (
    OrderFormParser,
    parse_order_form_to_order_items,
)


def test_parse_valid_order_form():
    """Test parsing a valid order form with all columns."""
    # Create test Excel file
    test_data = {
        "Lease": ["NMNM 123456", "NMNM 789012"],
        "Requested Legal": ["Section 1, Township 2N", "Section 2, Township 3N"],
        "Notes": ["Test note 1", "Test note 2"],
    }
    df = pd.DataFrame(test_data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        # Test class method
        parser = OrderFormParser(tmp_path, AgencyType.NMSLO)
        order_items = parser.parse()

        assert len(order_items) == 2
        assert order_items[0].lease_number == "NMNM 123456"
        assert order_items[0].agency == AgencyType.NMSLO
        assert order_items[0].report_notes == "Test note 1"

        # Test convenience function
        order_items2 = parse_order_form_to_order_items(tmp_path, AgencyType.BLM)
        assert len(order_items2) == 2
        assert order_items2[0].agency == AgencyType.BLM

    finally:
        os.unlink(tmp_path)


def test_missing_file():
    """Test error handling for missing file."""
    parser = OrderFormParser("nonexistent.xlsx", AgencyType.NMSLO)

    with pytest.raises(FileNotFoundError):
        parser.parse()


def test_missing_required_columns():
    """Test error handling for missing required columns."""
    # Create Excel file without required columns
    test_data = {"Wrong Column": ["data1", "data2"]}
    df = pd.DataFrame(test_data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        parser = OrderFormParser(tmp_path, AgencyType.NMSLO)

        with pytest.raises(ValueError, match="must contain 'Lease' column"):
            parser.parse()

    finally:
        os.unlink(tmp_path)


def test_minimal_order_form():
    """Test parsing order form with only required columns."""
    test_data = {
        "Lease": ["NMNM 123456"],
        "Requested Legal": ["Section 1, Township 2N"],
    }
    df = pd.DataFrame(test_data)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        order_items = parse_order_form_to_order_items(tmp_path, AgencyType.NMSLO)

        assert len(order_items) == 1
        assert order_items[0].lease_number == "NMNM 123456"
        assert order_items[0].start_date is None
        assert order_items[0].end_date is None
        assert order_items[0].report_notes is None

    finally:
        os.unlink(tmp_path)
