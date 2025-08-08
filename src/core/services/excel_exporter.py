"""
Excel Exporter Service for OrderItemData export functionality.
"""

from pathlib import Path
from typing import List, Dict
import pandas as pd

from src.core.models import OrderItemData, AgencyType
from src.core.utils import (
    DataCleaner,
    ColumnManager,
    BlankColumnManager,
    ExcelWriter,
    FilenameGenerator,
)


class ExcelExporterService:
    """Service for exporting OrderItemData to Excel files with proper formatting."""

    def export_order_items(
        self,
        order_items: List[OrderItemData],
        agency: AgencyType,
        output_directory: Path,
        order_number: str = None,
        order_type: str = None,
    ) -> str:
        """
        Export list of OrderItemData to formatted Excel file.

        Args:
            order_items: List of OrderItemData instances to export
            agency: Agency type for agency-specific formatting
            output_directory: Directory where Excel file will be saved
            order_number: Optional order number for filename
            order_type: Optional order type for filename

        Returns:
            str: Path to created Excel file

        Raises:
            ValueError: If order_items is empty or invalid parameters
            IOError: If file cannot be written
        """
        if not order_items:
            raise ValueError("order_items cannot be empty")
        if not isinstance(output_directory, Path):
            raise ValueError("output_directory must be a Path object")
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame
        df = self._convert_to_dataframe(order_items)

        # Add agency-specific columns
        df = self._add_agency_columns(df, agency)

        # Clean data
        df = DataCleaner.clean_order_data(df)

        # Generate filename and output path
        filename = FilenameGenerator.generate_order_filename(
            order_number=order_number,
            agency=agency.value,
            order_type=order_type,
        )
        output_path = output_directory / filename

        # Get column widths for formatting
        column_widths = self._get_column_widths(df)

        # Export with formatting
        return ExcelWriter.save_with_formatting(df, output_path, column_widths)

    def _convert_to_dataframe(self, order_items: List[OrderItemData]) -> pd.DataFrame:
        """Convert OrderItemData list to pandas DataFrame."""
        data = []
        for item in order_items:
            row = {
                "Agency": item.agency.value,
                "Lease": item.lease_number,
                "Legal Description": item.legal_description,
                "Start Date": item.start_date,
                "End Date": item.end_date,
                "Notes": item.notes,
                "Report Directory Link": item.report_directory_link,
                "Report Directory Path": item.report_directory_path,
                "Previous Report Found": item.previous_report_found,
            }
            # Add document links and lease index links as comma-separated strings
            row["Documents Links"] = (
                ", ".join(item.documents_links) if item.documents_links else ""
            )
            row["Lease Index Links"] = (
                ", ".join(item.lease_index_links) if item.lease_index_links else ""
            )
            data.append(row)

        return pd.DataFrame(data)

    def _add_agency_columns(self, df: pd.DataFrame, agency: AgencyType) -> pd.DataFrame:
        """Add agency-specific blank columns using existing utilities."""
        # Add standard columns using ColumnManager
        df = ColumnManager.add_standard_columns(df)

        # Add agency-specific blank columns using BlankColumnManager
        df = BlankColumnManager.add_agency_columns(df, agency.value)

        return df

    def _get_column_widths(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get appropriate column widths for Excel formatting."""
        widths = {}
        for column in df.columns:
            if "Link" in column or "Path" in column:
                widths[column] = 50  # Wider for URLs/paths
            elif column in ["Legal Description", "Notes"]:
                widths[column] = 40  # Wider for text content
            elif column in ["Agency", "Lease"]:
                widths[column] = 15  # Standard width
            else:
                widths[column] = 20  # Default width

        return widths


def export_order_items_to_excel(
    order_items: List[OrderItemData],
    agency: AgencyType,
    output_directory: Path,
    order_number: str = None,
    order_type: str = None,
) -> str:
    """
    Convenience function for exporting OrderItemData to Excel.

    Args:
        order_items: List of OrderItemData instances to export
        agency: Agency type for agency-specific formatting
        output_directory: Directory where Excel file will be saved
        order_number: Optional order number for filename
        order_type: Optional order type for filename

    Returns:
        str: Path to created Excel file
    """
    exporter = ExcelExporterService()
    return exporter.export_order_items(
        order_items, agency, output_directory, order_number, order_type
    )
