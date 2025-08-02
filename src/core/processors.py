from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

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
    def __init__(
        self,
        order_form,
        agency=None,
        order_type=None,
        order_date=None,
        order_number=None,
        dropbox_service=None,
    ):
        super().__init__(order_form, agency, order_type, order_date, order_number)
        self.dropbox_service = dropbox_service

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

        # Add search columns using ParsedColumnGenerator utility
        data = ParsedColumnGenerator.add_state_search_columns(data)

        # Add blank columns using BlankColumnManager utility
        blank_column_names = [
            "New Format",
            "Tractstar",
            "Old Format",
            "MI Index",
            "Documents",
            "Search Notes",
            "Link",
        ]
        data = BlankColumnManager.add_blank_columns(data, blank_column_names)

        return data

    def create_order_worksheet(self):
        data = self.process_data()

        # Populate Dropbox links if service is available
        if self.dropbox_service:
            try:
                print("🔍 Populating Dropbox links for State agency...")
                for index, row in data.iterrows():
                    lease_name = row.get("Lease", "")
                    if lease_name and pd.notna(lease_name):
                        try:
                            # Search for directory using State agency
                            shareable_link = self.dropbox_service.search_directory(
                                str(lease_name), agency="NMSLO"
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

        column_widths = {
            "Agency": 15,
            "Order Type": 15,
            "Order Number": 15,
            "Order Date": 15,
            "Lease": 15,
            "Requested Legal": 25,
            "Report Start Date": 20,
            "Full Search": 14,
            "Partial Search": 14,
            "New Format": 12,
            "Tractstar": 12,
            "Old Format": 12,
            "MI Index": 12,
            "Documents": 12,
            "Search Notes": 30,
            "Link": 30,
        }

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = ["^Document Archive", "^MI Index", "Runsheets"]

        for lease in self.data["Lease"]:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


class FederalOrderProcessor(OrderProcessor):
    def __init__(
        self,
        order_form,
        agency=None,
        order_type=None,
        order_date=None,
        order_number=None,
        dropbox_service=None,
    ):
        super().__init__(order_form, agency, order_type, order_date, order_number)
        self.dropbox_service = dropbox_service

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

        # Add search columns using ParsedColumnGenerator utility
        data = ParsedColumnGenerator.add_federal_search_columns(data)

        # Add blank columns using BlankColumnManager utility
        blank_column_names = [
            "New Format",
            "Tractstar",
            "Documents",
            "Search Notes",
            "Link",
        ]
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
                            # Search for directory using Federal agency
                            shareable_link = self.dropbox_service.search_directory(
                                str(lease_name), agency="Federal"
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

        column_widths = {
            "Agency": 15,
            "Order Type": 15,
            "Order Number": 15,
            "Order Date": 15,
            "Lease": 15,
            "Requested Legal": 25,
            "Report Start Date": 20,
            "Notes": 30,
            "Files Search": 14,
            "Tractstar Search": 14,
            "New Format": 12,
            "Tractstar": 12,
            "Documents": 12,
            "Search Notes": 30,
            "Link": 30,
        }

        ExcelWriter.save_with_formatting(data, output_path, column_widths)

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = ["^Document Archive", "Runsheets"]

        for lease in self.data["Lease"]:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


if __name__ == "__main__":
    state_order_form_path = "sample_data/order_state.xlsx"
    federal_order_form_path = "sample_data/order_fed.xlsx"
    order_processor = NMSLOOrderProcessor(state_order_form_path)
    # order_processor = FederalOrderProcessor(federal_order_form_path)
    order_processor.create_order_worksheet()
