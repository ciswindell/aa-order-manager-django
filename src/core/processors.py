"""
Order Processors

Agency-specific order processors that use externalized configuration.

This module provides concrete implementations of OrderProcessor for different
agency types (NMSLO, Federal). Each processor uses configuration-driven
behavior instead of hard-coded values, making it easy to add new agency
types by simply adding configuration entries.

Configuration Integration:
- Static configuration provides column widths, folder structures, and agency names
- Behavioral configuration provides search function mappings and blank column definitions
- Configuration can be injected for testing or custom scenarios
- Default configurations are automatically loaded for each agency type

Example:
    # Use default configuration
    processor = NMSLOOrderProcessor(order_form="data.xlsx")
    
    # Use custom configuration
    custom_static = AgencyStaticConfig(...)
    custom_behavioral = AgencyBehaviorConfig(...)
    processor = NMSLOOrderProcessor(
        order_form="data.xlsx",
        static_config=custom_static,
        behavioral_config=custom_behavioral
    )
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

from .config import get_behavioral_config, get_static_config
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
        self.static_config = static_config or get_static_config("NMSLO")
        self.behavioral_config = behavioral_config or get_behavioral_config("NMSLO")

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

        # Add search columns using behavioral configuration
        search_data = self.behavioral_config.create_search_data(data["Lease"])
        for column_name, column_data in search_data.items():
            data[column_name] = column_data

        # Add blank columns using BlankColumnManager utility
        blank_column_names = self.behavioral_config.get_blank_columns()
        data = BlankColumnManager.add_blank_columns(data, blank_column_names)

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
                                agency=self.static_config.dropbox_agency_name,
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
        column_widths = self.static_config.column_widths

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = self.static_config.folder_structure

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
        self.static_config = static_config or get_static_config("Federal")
        self.behavioral_config = behavioral_config or get_behavioral_config("Federal")

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

        # Add search columns using behavioral configuration
        search_data = self.behavioral_config.create_search_data(data["Lease"])
        for column_name, column_data in search_data.items():
            data[column_name] = column_data

        # Add blank columns using BlankColumnManager utility
        blank_column_names = self.behavioral_config.get_blank_columns()
        data = BlankColumnManager.add_blank_columns(data, blank_column_names)

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
                                agency=self.static_config.dropbox_agency_name,
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
        column_widths = self.static_config.column_widths

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = self.static_config.folder_structure

        for lease in self.data["Lease"]:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


if __name__ == "__main__":
    nmslo_order_form_path = "sample_data/order_nmslo.xlsx"
    federal_order_form_path = "sample_data/order_fed.xlsx"
    order_processor = NMSLOOrderProcessor(nmslo_order_form_path)
    # order_processor = FederalOrderProcessor(federal_order_form_path)
    order_processor.create_order_worksheet()
