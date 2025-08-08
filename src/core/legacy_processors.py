"""
DEPRECATED - DO NOT DEVELOP FURTHER
===================================

This module is being phased out and should not be used for new development.
The functionality has been moved to the new workflow framework.

For new development, use the workflow system in src/core/workflows/ instead.

Order Processors

Agency-specific order processors that use the unified configuration system.

This module provides concrete implementations of OrderProcessor for different
agency types (NMSLO, Federal). Each processor uses the unified config system
for agency-specific settings like column widths, folder structures, and 
directory paths.

Configuration Integration:
- Uses unified config system (src/config.py) for all agency settings
- Column widths, folder structures, and directory paths loaded per agency
- Configuration can be injected for testing or custom scenarios
- Default configurations are automatically loaded for each agency type

Example:
    # Use default configuration (automatically loads from unified config)
    processor = NMSLOOrderProcessor(order_form="data.xlsx")
    
    # Use custom configuration (for testing)
    custom_agency_config = config.get_agency_config("NMSLO")
    processor = NMSLOOrderProcessor(
        order_form="data.xlsx",
        static_config=custom_agency_config
    )
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

from src import config
from .utils.data_utils import BlankColumnManager, ColumnManager, DataCleaner
from .utils.excel_utils import ExcelWriter
from .utils.file_utils import FilenameGenerator
from .utils.parsing_utils import LeaseNumberParser, ParsedColumnGenerator


class OrderProcessor(ABC):
    def __init__(
        self,
        order_form,
        agency=None,
        order_type=None,
        order_date=None,
        order_number=None,
    ):
        self.order_form = order_form
        self.agency = agency
        self.order_type = order_type
        self.order_date = order_date
        self.order_number = order_number
        self.data = self.read_order_form()

    @abstractmethod
    def read_order_form(self):
        pass

    @abstractmethod
    def create_order_worksheet(self):
        pass

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def create_folders(self):
        pass


class NMSLOOrderProcessor(OrderProcessor):
    """
    NMSLO-specific order processor using externalized configuration.
    
    This processor handles NMSLO agency orders with configuration-driven behavior.
    All agency-specific settings (column widths, folder structures, search functions)
    are loaded from configuration instead of being hard-coded.
    
    Configuration:
    - Uses NMSLO static configuration for column widths and folder structures
    - Uses NMSLO behavioral configuration for search functions and blank columns
    - Supports dependency injection for testing and custom scenarios
    
    Args:
        order_form: Path to the order form Excel file
        agency: Agency name (defaults to "NMSLO")
        order_type: Type of order being processed
        order_date: Date of the order
        order_number: Order number identifier
        dropbox_service: Optional Dropbox service for link generation
        static_config: Optional custom static configuration (for testing/custom use)
        behavioral_config: Optional custom behavioral configuration (for testing/custom use)
    """
    
    def __init__(
        self,
        order_form,
        agency=None,
        order_type=None,
        order_date=None,
        order_number=None,
        dropbox_service=None,
        static_config=None,
        behavioral_config=None,
    ):
        super().__init__(order_form, agency, order_type, order_date, order_number)
        self.dropbox_service = dropbox_service
        # Dependency injection for configuration - allows testing with mock configs
        self.agency_config = static_config or config.get_agency_config("NMSLO")
# behavioral_config removed - using hardcoded agency-specific columns

    def read_order_form(self):
        data = pd.read_excel(self.order_form)

        # Clean Report Start Date column using DataCleaner utility
        if "Report Start Date" in data.columns:
            data = DataCleaner.clean_date_column(data, "Report Start Date")

        return data

    def process_data(self) -> pd.DataFrame:
        data = self.data

        # Add metadata columns using ColumnManager utility
        data = ColumnManager.add_metadata_columns(
            data,
            agency=self.agency,
            order_type=self.order_type,
            order_date=self.order_date,
            order_number=self.order_number,
        )

        # Add blank search columns for NMSLO
        nmslo_search_columns = [
            "Full Search", "Partial Search", "New Format", "Tractstar", 
            "Old Format", "MI Index", "Documents", "Search Notes"
        ]
        data = BlankColumnManager.add_blank_columns(data, nmslo_search_columns)

        return data

    def create_order_worksheet(self):
        data = self.process_data()

        # Populate Dropbox links if service is available
        if self.dropbox_service:
            try:
                print("🔍 Populating Dropbox links for NMSLO agency...")
                for index, row in data.iterrows():
                    lease_name = row.get("Lease", "")
                    if lease_name and pd.notna(lease_name):
                        try:
                            # Search for directory using configured agency name
                            shareable_link = self.dropbox_service.search_directory(
                                str(lease_name),
                                agency="NMSLO",
                            )
                            if shareable_link:
                                data.at[index, "Link"] = shareable_link
                                print(f"✅ Found link for {lease_name}")
                            else:
                                print(f"❌ No directory found for {lease_name}")
                        except Exception as e:
                            print(f"⚠️ Error finding link for {lease_name}: {str(e)}")
                            # Continue with next lease - don't fail the entire process
                            continue
            except Exception as e:
                print(f"⚠️ Dropbox link population failed: {str(e)}")
                # Continue with worksheet creation even if Dropbox fails
                pass

        # Save Excel file with formatting using ExcelWriter utility
        base_path = Path(self.order_form).absolute().parent
        file_name = FilenameGenerator.generate_order_filename(
            order_number=self.order_number,
            agency=self.agency,
            order_type=self.order_type,
        )
        output_path = base_path / file_name

        # Get column widths from static configuration
        column_widths = self.agency_config.column_widths

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = self.agency_config.folder_structure

        for lease in self.data["Lease"]:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


class FederalOrderProcessor(OrderProcessor):
    """
    Federal-specific order processor using externalized configuration.
    
    This processor handles Federal agency orders with configuration-driven behavior.
    All agency-specific settings (column widths, folder structures, search functions)
    are loaded from configuration instead of being hard-coded.
    
    Configuration:
    - Uses Federal static configuration for column widths and folder structures
    - Uses Federal behavioral configuration for search functions and blank columns
    - Supports dependency injection for testing and custom scenarios
    - Includes Federal-specific Notes column handling
    
    Args:
        order_form: Path to the order form Excel file
        agency: Agency name (defaults to "Federal")
        order_type: Type of order being processed
        order_date: Date of the order
        order_number: Order number identifier
        dropbox_service: Optional Dropbox service for link generation
        static_config: Optional custom static configuration (for testing/custom use)
        behavioral_config: Optional custom behavioral configuration (for testing/custom use)
    """
    
    def __init__(
        self,
        order_form,
        agency=None,
        order_type=None,
        order_date=None,
        order_number=None,
        dropbox_service=None,
        static_config=None,
        behavioral_config=None,
    ):
        super().__init__(order_form, agency, order_type, order_date, order_number)
        self.dropbox_service = dropbox_service
        # Dependency injection for configuration - allows testing with mock configs
        self.agency_config = static_config or config.get_agency_config("Federal")
# behavioral_config removed - using hardcoded agency-specific columns

    def read_order_form(self):
        data = pd.read_excel(self.order_form)

        # Clean Report Start Date column using DataCleaner utility
        if "Report Start Date" in data.columns:
            data = DataCleaner.clean_date_column(data, "Report Start Date")

        return data

    def process_data(self) -> pd.DataFrame:
        data = self.data

        # Add metadata columns using ColumnManager utility
        data = ColumnManager.add_metadata_columns(
            data,
            agency=self.agency,
            order_type=self.order_type,
            order_date=self.order_date,
            order_number=self.order_number,
        )

        # Add blank search columns for Federal
        federal_search_columns = [
            "Files Search", "Tractstar Search", "New Format", "Tractstar", 
            "Documents", "Search Notes", "Notes"
        ]
        data = BlankColumnManager.add_blank_columns(data, federal_search_columns)

        return data

    def create_order_worksheet(self):
        data = self.process_data()

        # Populate Dropbox links if service is available
        if self.dropbox_service:
            try:
                print("🔍 Populating Dropbox links for Federal agency...")
                for index, row in data.iterrows():
                    lease_name = row.get("Lease", "")
                    if lease_name and pd.notna(lease_name):
                        try:
                            # Search for directory using configured agency name
                            shareable_link = self.dropbox_service.search_directory(
                                str(lease_name),
                                agency="Federal",
                            )
                            if shareable_link:
                                data.at[index, "Link"] = shareable_link
                                print(f"✅ Found link for {lease_name}")
                            else:
                                print(f"❌ No directory found for {lease_name}")
                        except Exception as e:
                            print(f"⚠️ Error finding link for {lease_name}: {str(e)}")
                            # Continue with next lease - don't fail the entire process
                            continue
            except Exception as e:
                print(f"⚠️ Dropbox link population failed: {str(e)}")
                # Continue with worksheet creation even if Dropbox fails
                pass

        # Save Excel file with formatting using ExcelWriter utility
        base_path = Path(self.order_form).absolute().parent
        file_name = FilenameGenerator.generate_order_filename(
            order_number=self.order_number,
            agency=self.agency,
            order_type=self.order_type,
        )
        output_path = base_path / file_name

        # Get column widths from static configuration
        column_widths = self.agency_config.column_widths

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = self.agency_config.folder_structure

        for lease in self.data["Lease"]:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


if __name__ == "__main__":
    nmslo_order_form_path = "sample_data/order_nmslo.xlsx"
    federal_order_form_path = "sample_data/order_fed.xlsx"
    order_processor = NMSLOOrderProcessor(nmslo_order_form_path)
    # order_processor = FederalOrderProcessor(federal_order_form_path)
    order_processor.create_order_worksheet()
