"""
Data Processing Utilities Module

Contains utility classes for data cleaning and transformation operations
that are shared across different order processors.
"""

from datetime import datetime
from typing import Any, List, Optional, Union

import pandas as pd


class DataCleaner:
    """Utility class for cleaning and processing data in DataFrames."""

    @classmethod
    def clean_date_column(cls, data: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """
        Clean date column - keep only actual dates, make everything else blank.

        This method extracts the date cleaning logic that was duplicated between
        NMSLOOrderProcessor and FederalOrderProcessor. It handles:
        - Excel serial dates (converts to datetime)
        - String date formats (parses to datetime)
        - Text values like "Inception" (sets to None)
        - Existing datetime objects (preserves them)

        Args:
            data: pandas DataFrame containing the column to clean
            column_name: Name of the column to clean

        Returns:
            DataFrame with the specified column cleaned

        Raises:
            ValueError: If data is not a DataFrame or column_name doesn't exist
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")

        if column_name not in data.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame")

        def clean_date(value: Any) -> Optional[datetime]:
            """Clean individual date value - extracted from existing processors."""
            if pd.isna(value) or value == "":
                return None

            # If it's a string, check if it contains only letters (like "Inception")
            if isinstance(value, str):
                # If it's all letters or contains words like "inception", make it blank
                if value.isalpha() or "inception" in value.lower():
                    return None
                # Try to parse date strings
                try:
                    return pd.to_datetime(value, errors="raise")
                except:
                    return None

            # If it's a number, try to convert (could be Excel serial date)
            if isinstance(value, (int, float)):
                try:
                    # Convert Excel serial number to date
                    return pd.to_datetime("1899-12-30") + pd.Timedelta(days=value)
                except:
                    return None

            # If it's already a datetime, keep it
            if isinstance(value, (pd.Timestamp, datetime)):
                return value

            return None

            # Apply the cleaning function to the specified column

        data_copy = data.copy()
        data_copy[column_name] = data_copy[column_name].apply(clean_date)

        return data_copy


class ColumnManager:
    """Utility class for managing DataFrame columns and metadata."""

    @classmethod
    def add_metadata_columns(
        cls,
        data: pd.DataFrame,
        agency: Optional[str] = None,
        order_type: Optional[str] = None,
        order_date: Optional[Union[str, datetime]] = None,
        order_number: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Add Agency, Order Type, Order Number, Order Date columns to beginning of DataFrame.

        This method extracts the metadata column addition logic that was duplicated
        between NMSLOOrderProcessor and FederalOrderProcessor. It:
        - Adds ["Agency", "Order Type", "Order Number", "Order Date"] columns at the beginning
        - Only adds columns that don't already exist
        - Populates columns with provided metadata values
        - Maintains existing column order for new additions

        Args:
            data: pandas DataFrame to modify
            agency: Agency value to populate in Agency column
            order_type: Order type value to populate in Order Type column
            order_date: Order date value to populate in Order Date column
            order_number: Order number value to populate in Order Number column

        Returns:
            DataFrame with metadata columns added and populated

        Raises:
            ValueError: If data is not a DataFrame
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")

        # Add new columns if they don't exist, placing them at the beginning
        new_columns = ["Agency", "Order Type", "Order Number", "Order Date"]
        existing_columns = data.columns.tolist()

        data_copy = data.copy()

        # Create empty columns for the new fields
        for col in reversed(
            new_columns
        ):  # Reverse to maintain order when inserting at front
            if col not in existing_columns:
                data_copy.insert(0, col, "")

        # Prefill columns based on provided values
        if agency:
            data_copy["Agency"] = agency
        if order_type:
            data_copy["Order Type"] = order_type
        if order_date:
            data_copy["Order Date"] = order_date
        if order_number:
            data_copy["Order Number"] = order_number

        return data_copy


class BlankColumnManager:
    """Utility class for adding blank columns to DataFrames."""

    @classmethod
    def add_blank_columns(
        cls, data: pd.DataFrame, column_names: List[str]
    ) -> pd.DataFrame:
        """
        Add empty columns with specified names to the end of the DataFrame.

        This method extracts the blank column addition logic that was duplicated
        between NMSLOOrderProcessor and FederalOrderProcessor. It creates a new
        DataFrame with empty columns and concatenates it with the existing data.

        Args:
            data: pandas DataFrame to modify
            column_names: List of column names to add as empty columns

        Returns:
            DataFrame with blank columns added to the end

        Raises:
            ValueError: If data is not a DataFrame or column_names is not a list
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")

        if not isinstance(column_names, list):
            raise ValueError("column_names must be a list")

        # Create blank DataFrame with specified columns and same index as original data
        blank_columns = pd.DataFrame(
            columns=column_names,
            index=data.index,
        )

        # Concatenate original data with blank columns
        data_copy = data.copy()
        result = pd.concat([data_copy, blank_columns], axis=1)

        return result
