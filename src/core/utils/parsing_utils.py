"""
Parsing Utilities Module

Contains utility classes for lease number parsing and parsed column generation
that are shared across different order processors.
"""

from typing import Dict

import pandas as pd


class LeaseNumberParser:
    """
    Utility class for parsing lease numbers and generating search strings.

    This class was moved from processors.py to provide reusable lease number
    parsing functionality across different order processors.
    """

    def __init__(self, lease_number):
        self.lease_number = lease_number

    def search_file(self) -> str:
        """Generate file search string by extracting digits."""
        try:
            number_string = "".join(
                [x for x in self.lease_number if x.isdigit() or x == "0"]
            )
            number = int(number_string)
            search_string = "*" + str(number) + "*"
        except ValueError:
            return "Error"

        return search_string

    def search_tractstar(self) -> str:
        """Generate Tractstar search string with number and alpha components."""
        try:
            base_number = "".join(self.lease_number.split(" ")[1:])
            number_string = "".join(
                [x for x in self.lease_number if x.isdigit() or x == "0"]
            )
            alpha_string = "".join([x for x in base_number if x.isalpha()])
            number = int(number_string)
            if alpha_string:
                search_string = str(number) + "-" + alpha_string
            else:
                search_string = str(number)
        except ValueError:
            return "Error"

        return search_string

    def search_full(self) -> str:
        """Generate full search string by replacing dashes with wildcards."""
        try:
            search = "*" + self.lease_number.replace("-", "*") + "*"
        except ValueError:
            return "Error"
        return search

    def search_partial(self) -> str:
        """Generate partial search string using first two components."""
        try:
            search_split = self.lease_number.split("-")[:2]
            search = "*" + ("*".join(search_split)) + "*"
        except ValueError:
            return "Error"
        return search


class ParsedColumnGenerator:
    """Utility class for generating parsed lease number columns in DataFrames."""

    @classmethod
    def add_state_search_columns(cls, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add "Full Search" and "Partial Search" columns for State agency processing.

        This method extracts the parsed column generation logic that was
        duplicated in the NMSLOOrderProcessor. It uses LeaseNumberParser
        to generate parsed search terms from the "Lease" column.

        Args:
            data: pandas DataFrame containing a "Lease" column

        Returns:
            DataFrame with "Full Search" and "Partial Search" columns added

        Raises:
            ValueError: If data is not a DataFrame or "Lease" column is missing
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
        if "Lease" not in data.columns:
            raise ValueError("DataFrame must contain a 'Lease' column")

        data_copy = data.copy()

        # Add State agency search columns - extracted from existing processor
        data_copy["Full Search"] = data_copy["Lease"].apply(
            lambda x: LeaseNumberParser(x).search_full()
        )
        data_copy["Partial Search"] = data_copy["Lease"].apply(
            lambda x: LeaseNumberParser(x).search_partial()
        )

        return data_copy

    @classmethod
    def add_federal_search_columns(cls, data: pd.DataFrame) -> pd.DataFrame:
        """
        Add "Files Search" and "Tractstar Search" columns for Federal agency processing.

        This method extracts the parsed column generation logic that was
        duplicated in the FederalOrderProcessor. It uses LeaseNumberParser
        to generate parsed search terms from the "Lease" column.

        Args:
            data: pandas DataFrame containing a "Lease" column

        Returns:
            DataFrame with "Files Search" and "Tractstar Search" columns added

        Raises:
            ValueError: If data is not a DataFrame or "Lease" column is missing
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
        if "Lease" not in data.columns:
            raise ValueError("DataFrame must contain a 'Lease' column")

        data_copy = data.copy()

        # Add Federal agency search columns - extracted from existing processor
        data_copy["Files Search"] = data_copy["Lease"].apply(
            lambda x: LeaseNumberParser(x).search_file()
        )
        data_copy["Tractstar Search"] = data_copy["Lease"].apply(
            lambda x: LeaseNumberParser(x).search_tractstar()
        )

        return data_copy
