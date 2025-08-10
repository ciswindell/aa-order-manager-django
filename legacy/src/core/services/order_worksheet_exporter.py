"""
Simplified Order Worksheet Exporter Service for OrderItemData export functionality.

This exporter uses config as the single source of truth for all column operations.
"""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from src.core.models import OrderItemData, AgencyType
from src.core.utils import (
    ColumnManager,
    ExcelWriter,
    FilenameGenerator,
)
from src import config


class ColumnMapper:
    """Centralized column mapping using config as single source of truth."""

    @staticmethod
    def map_item_to_row(item: OrderItemData, agency: AgencyType) -> Dict[str, Any]:
        """
        Map OrderItemData to row dict with only configured columns for the agency.

        This is the single source of truth for field-to-column mapping.
        Only creates columns that exist in the agency's configuration.
        """
        configured_columns = set(config.get_column_order(agency.value))
        row = {}

        # Map each configured column to its value
        for column in configured_columns:
            if column == "Agency":
                row[column] = item.agency.value
            elif column == "Lease":
                row[column] = item.lease_number
            elif column == "Legal Description":
                row[column] = item.legal_description
            elif column == "Report Start Date":
                row[column] = item.start_date
            elif column == "Report End Date":
                row[column] = item.end_date
            elif column == "Report Notes":
                row[column] = item.report_notes or ""
            elif column == "Report Directory Link":
                row[column] = item.report_directory_link or ""
            elif column == "Previous Report Found":
                row[column] = (
                    "Yes"
                    if item.previous_report_found
                    else "No" if item.previous_report_found is not None else ""
                )
            elif column == "Tractstar Needed" or column == "Tractstar":
                row[column] = (
                    "Yes"
                    if item.tractstar_needed
                    else "No" if item.tractstar_needed is not None else ""
                )
            elif column == "Documents Needed":
                row[column] = (
                    "Yes"
                    if item.documents_needed
                    else "No" if item.documents_needed is not None else ""
                )
            elif column == "Misc Index Needed":
                row[column] = (
                    "Yes"
                    if item.misc_index_needed
                    else "No" if item.misc_index_needed is not None else ""
                )
            elif column == "Documents Links":
                row[column] = (
                    ", ".join(item.documents_links) if item.documents_links else ""
                )
            elif column == "Misc Index Links":
                row[column] = (
                    ", ".join(item.misc_index_links) if item.misc_index_links else ""
                )
            else:
                # For any other configured columns, set as blank
                row[column] = ""

        return row


class WorksheetExporter:
    """Simplified worksheet exporter that dynamically handles columns based on config."""

    def convert_to_dataframe(
        self, order_items: List[OrderItemData], agency: AgencyType
    ) -> pd.DataFrame:
        """
        Convert OrderItemData list to DataFrame with only configured columns.

        Uses ColumnMapper as single source of truth for column handling.
        """
        if not order_items:
            raise ValueError("order_items cannot be empty")

        # Convert each item using centralized mapper
        data = [ColumnMapper.map_item_to_row(item, agency) for item in order_items]

        # Create DataFrame with exact column order from config
        column_order = config.get_column_order(agency.value)
        df = pd.DataFrame(data, columns=column_order)

        return df

    def add_metadata_columns(
        self,
        df: pd.DataFrame,
        agency: AgencyType,
        order_number: str = "",
        order_type: str = "",
        order_date=None,
    ) -> pd.DataFrame:
        """Add metadata columns (Order Type, Order Number, Order Date) to the DataFrame."""
        return ColumnManager.add_metadata_columns(
            df,
            agency=agency.value,
            order_type=order_type,
            order_date=order_date,
            order_number=order_number,
        )

    def get_column_widths(self, df: pd.DataFrame, agency: AgencyType) -> Dict[str, int]:
        """Get column widths from config - all columns should be configured."""
        return config.get_column_widths(agency.value)

    def export_order_items(
        self,
        order_items: List[OrderItemData],
        agency: AgencyType,
        output_directory: Path,
        order_number: str = None,
        order_type: str = None,
        order_date=None,
    ) -> str:
        """
        Export OrderItemData to worksheet using dynamic column generation.

        Args:
            order_items: List of OrderItemData instances to export
            agency: Agency type for agency-specific formatting
            output_directory: Directory where order worksheet file will be saved
            order_number: Optional order number for filename and metadata
            order_type: Optional order type for filename and metadata
            order_date: Optional order date for metadata

        Returns:
            str: Path to created order worksheet file

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

        # Step 1: Convert to DataFrame with all configured columns
        df = self.convert_to_dataframe(order_items, agency)

        # Step 2: Add metadata columns
        df = self.add_metadata_columns(df, agency, order_number, order_type, order_date)

        # No need to reorder - DataFrame already has correct columns in correct order

        # Step 3: Generate filename and output path
        filename = FilenameGenerator.generate_order_filename(
            order_number=order_number,
            agency=agency.value,
            order_type=order_type,
        )
        output_path = output_directory / filename

        # Step 4: Get column widths from config
        column_widths = self.get_column_widths(df, agency)

        # Step 5: Export with formatting
        return ExcelWriter.save_with_formatting(df, output_path, column_widths)


def export_order_items_to_worksheet(
    order_items: List[OrderItemData],
    agency: AgencyType,
    output_directory: Path,
    order_number: str = None,
    order_type: str = None,
    order_date=None,
) -> str:
    """
    Convenience function for exporting OrderItemData to order worksheet.

    Args:
        order_items: List of OrderItemData instances to export
        agency: Agency type for agency-specific formatting
        output_directory: Directory where order worksheet file will be saved
        order_number: Optional order number for filename and metadata
        order_type: Optional order type for filename and metadata
        order_date: Optional order date for metadata

    Returns:
        str: Path to created order worksheet file
    """
    exporter = WorksheetExporter()
    return exporter.export_order_items(
        order_items, agency, output_directory, order_number, order_type, order_date
    )
