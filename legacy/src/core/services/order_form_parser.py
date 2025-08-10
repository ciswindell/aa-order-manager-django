"""
Order Form Parser Service

Service to parse order form files into OrderItemData instances using SOLID principles.
"""

from typing import List

import pandas as pd

from src.core.models import OrderItemData, AgencyType
from src.core.utils.data_utils import DataCleaner
from src.core.validation import ExcelFileValidator, OrderFormStructureValidator


class OrderFormParser:
    """Parser for order form files with single-responsibility methods."""

    def __init__(self, file_path: str, agency: AgencyType):
        self.file_path = file_path
        self.agency = agency

    def _validate_file(self) -> None:
        """Validate file exists and is accessible using centralized validation service."""
        validator = ExcelFileValidator()
        is_valid, error = validator.validate(self.file_path)
        if not is_valid:
            # Convert user-friendly message to FileNotFoundError for consistency
            raise FileNotFoundError(error)

    def _load_data(self) -> pd.DataFrame:
        """Load data from Excel file."""
        return pd.read_excel(self.file_path)

    def _validate_columns(self, data: pd.DataFrame) -> None:
        """Validate required columns exist using centralized validation service."""
        validator = OrderFormStructureValidator()
        is_valid, error = validator.validate(data)
        if not is_valid:
            raise ValueError(error)

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean data using existing utilities."""
        if "Report Start Date" in data.columns:
            data = DataCleaner.clean_date_column(data, "Report Start Date")
        return data

    def _convert_to_order_items(self, data: pd.DataFrame) -> List[OrderItemData]:
        """Convert DataFrame rows to OrderItemData instances."""
        order_items = []
        for _, row in data.iterrows():
            start_date = (
                row.get("Report Start Date")
                if pd.notna(row.get("Report Start Date"))
                else None
            )
            end_date = (
                row.get("Report End Date")
                if pd.notna(row.get("Report End Date"))
                else None
            )

            order_item = OrderItemData(
                agency=self.agency,
                lease_number=str(row.get("Lease", "")),
                legal_description=str(row.get("Requested Legal", "")),
                start_date=start_date,
                end_date=end_date,
                report_notes=(
                    str(row.get("Notes", "")) if pd.notna(row.get("Notes")) else None
                ),
            )
            order_items.append(order_item)
        return order_items

    def parse(self) -> List[OrderItemData]:
        """Parse order form file into OrderItemData instances."""
        self._validate_file()
        data = self._load_data()
        self._validate_columns(data)
        data = self._clean_data(data)
        return self._convert_to_order_items(data)


def parse_order_form_to_order_items(
    file_path: str, agency: AgencyType
) -> List[OrderItemData]:
    """Convenience function for parsing order forms."""
    parser = OrderFormParser(file_path, agency)
    return parser.parse()
