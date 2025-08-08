"""
Order Worksheet Exporter Service for OrderItemData export functionality.
"""

from pathlib import Path
from typing import List, Dict, Protocol
import pandas as pd

from src.core.models import OrderItemData, AgencyType
from src.core.utils import (
    ColumnManager,
    ExcelWriter,
    FilenameGenerator,
    ParsedColumnGenerator,
)


class WorksheetExportStrategy(Protocol):
    """Strategy protocol for different worksheet export formats."""

    def convert_to_dataframe(self, order_items: List[OrderItemData]) -> pd.DataFrame:
        """Convert OrderItemData list to pandas DataFrame with format-specific columns."""
        ...

    def add_agency_columns(self, df: pd.DataFrame, agency: AgencyType) -> pd.DataFrame:
        """Add agency-specific columns based on format requirements."""
        ...

    def get_column_widths(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get column widths appropriate for this format."""
        ...


class LegacyFormatStrategy:
    """Legacy format with all columns including blank search columns and parsed lease columns."""

    def convert_to_dataframe(self, order_items: List[OrderItemData]) -> pd.DataFrame:
        """Convert to DataFrame with legacy column structure."""
        data = []
        for item in order_items:
            row = {
                "Agency": item.agency.value,
                "Lease": item.lease_number,
                "Legal Description": item.legal_description,
                "Report Start Date": item.start_date,
                "Report End Date": item.end_date,
                "Notes": item.notes,
                "Link": item.report_directory_link or "",
                "Previous Report Found": item.previous_report_found,
            }
            # Add document and lease index links
            row["Documents Links"] = (
                ", ".join(item.documents_links) if item.documents_links else ""
            )
            row["Lease Index Links"] = (
                ", ".join(item.lease_index_links) if item.lease_index_links else ""
            )
            data.append(row)

        df = pd.DataFrame(data)

        # No parsed columns here - will be added in add_agency_columns based on agency

        return df

    def add_agency_columns(
        self,
        df: pd.DataFrame,
        agency: AgencyType,
        order_number: str = "",
        order_type: str = "",
        order_date=None,
    ) -> pd.DataFrame:
        """Add legacy agency-specific columns including blank search columns."""
        # Add metadata columns
        df = ColumnManager.add_metadata_columns(
            df,
            agency=agency.value,
            order_type=order_type,
            order_date=order_date,
            order_number=order_number,
        )

        # Add agency-specific parsed columns
        if agency == AgencyType.NMSLO:
            df = ParsedColumnGenerator.add_nmslo_search_columns(df)
        elif agency == AgencyType.BLM:
            df = ParsedColumnGenerator.add_federal_search_columns(df)

        return df

    def get_column_widths(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get legacy column widths."""
        widths = {}
        for column in df.columns:
            if "Link" in column:
                widths[column] = 50
            elif column in ["Legal Description", "Notes"]:
                widths[column] = 40
            elif column in ["Agency", "Lease"]:
                widths[column] = 15
            else:
                widths[column] = 20
        return widths


class MinimalFormatStrategy:
    """Minimal format with only essential columns, no blank search columns."""

    def convert_to_dataframe(self, order_items: List[OrderItemData]) -> pd.DataFrame:
        """Convert to DataFrame with minimal column structure."""
        data = []
        for item in order_items:
            # Convert boolean to Yes/No for Previous Report Found
            previous_report = ""
            if item.previous_report_found is not None:
                previous_report = "Yes" if item.previous_report_found else "No"

            row = {
                "Agency": item.agency.value,
                "Lease": item.lease_number,
                "Legal Description": item.legal_description,
                "Report Start Date": item.start_date,
                "Report End Date": item.end_date,
                "Notes": item.notes,
                "Report Directory Link": item.report_directory_link or "",
                "Previous Report Found": previous_report,
            }
            # Add document and lease index links
            row["Documents Links"] = (
                ", ".join(item.documents_links) if item.documents_links else ""
            )
            row["Lease Index Links"] = (
                ", ".join(item.lease_index_links) if item.lease_index_links else ""
            )
            data.append(row)

        return pd.DataFrame(data)

    def add_agency_columns(
        self,
        df: pd.DataFrame,
        agency: AgencyType,
        order_number: str = "",
        order_type: str = "",
        order_date=None,
    ) -> pd.DataFrame:
        """Add minimal agency-specific columns (no blank search columns)."""
        # Only add metadata columns, no blank search columns
        df = ColumnManager.add_metadata_columns(
            df,
            agency=agency.value,
            order_type=order_type,
            order_date=order_date,
            order_number=order_number,
        )
        return df

    def get_column_widths(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get minimal format column widths."""
        widths = {}
        for column in df.columns:
            if "Link" in column:
                widths[column] = 50
            elif column in ["Legal Description", "Notes"]:
                widths[column] = 40
            elif column in ["Agency", "Lease"]:
                widths[column] = 15
            else:
                widths[column] = 20
        return widths


class OrderWorksheetExporterService:
    """Service for exporting OrderItemData using different format strategies."""

    def __init__(self, strategy: WorksheetExportStrategy):
        """Initialize with a specific export strategy."""
        self.strategy = strategy

    def export_order_items(
        self,
        order_items: List[OrderItemData],
        agency: AgencyType,
        output_directory: Path,
        order_number: str = None,
        order_type: str = None,
        order_date=None,
    ) -> str:
        """Export using the configured strategy."""
        if not order_items:
            raise ValueError("order_items cannot be empty")
        if not isinstance(output_directory, Path):
            raise ValueError("output_directory must be a Path object")
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=True)

        # Use strategy to convert data
        df = self.strategy.convert_to_dataframe(order_items)
        df = self.strategy.add_agency_columns(
            df, agency, order_number, order_type, order_date
        )

        # Clean data (skip data cleaning for now as method doesn't exist)
        # df = DataCleaner.clean_order_data(df)

        # Generate filename and output path
        filename = FilenameGenerator.generate_order_filename(
            order_number=order_number,
            agency=agency.value,
            order_type=order_type,
        )
        output_path = output_directory / filename

        # Get column widths from strategy
        column_widths = self.strategy.get_column_widths(df)

        # Export with formatting
        return ExcelWriter.save_with_formatting(df, output_path, column_widths)


def export_order_items_to_worksheet(
    order_items: List[OrderItemData],
    agency: AgencyType,
    output_directory: Path,
    order_number: str = None,
    order_type: str = None,
    order_date=None,
    use_legacy_format: bool = False,
) -> str:
    """
    Convenience function for exporting OrderItemData to order worksheet.

    Args:
        order_items: List of OrderItemData instances to export
        agency: Agency type for agency-specific formatting
        output_directory: Directory where order worksheet file will be saved
        order_number: Optional order number for filename
        order_type: Optional order type for filename
        use_legacy_format: If True, uses legacy format with all columns

    Returns:
        str: Path to created order worksheet file
    """
    strategy = LegacyFormatStrategy() if use_legacy_format else MinimalFormatStrategy()
    exporter = OrderWorksheetExporterService(strategy)
    return exporter.export_order_items(
        order_items, agency, output_directory, order_number, order_type, order_date
    )


def export_order_items_legacy_format(
    order_items: List[OrderItemData],
    agency: AgencyType,
    output_directory: Path,
    order_number: str = None,
    order_type: str = None,
    order_date=None,
) -> str:
    """
    Convenience function for exporting OrderItemData in legacy format.

    Args:
        order_items: List of OrderItemData instances to export
        agency: Agency type for agency-specific formatting
        output_directory: Directory where order worksheet file will be saved
        order_number: Optional order number for filename
        order_type: Optional order type for filename

    Returns:
        str: Path to created order worksheet file
    """
    strategy = LegacyFormatStrategy()
    exporter = OrderWorksheetExporterService(strategy)
    return exporter.export_order_items(
        order_items, agency, output_directory, order_number, order_type, order_date
    )


def export_order_items_minimal_format(
    order_items: List[OrderItemData],
    agency: AgencyType,
    output_directory: Path,
    order_number: str = None,
    order_type: str = None,
    order_date=None,
) -> str:
    """
    Convenience function for exporting OrderItemData in minimal format.

    Args:
        order_items: List of OrderItemData instances to export
        agency: Agency type for agency-specific formatting
        output_directory: Directory where order worksheet file will be saved
        order_number: Optional order number for filename
        order_type: Optional order type for filename

    Returns:
        str: Path to created order worksheet file
    """
    strategy = MinimalFormatStrategy()
    exporter = OrderWorksheetExporterService(strategy)
    return exporter.export_order_items(
        order_items, agency, output_directory, order_number, order_type, order_date
    )
