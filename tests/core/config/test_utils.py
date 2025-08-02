"""
Test utilities for configuration testing.

Simple mock configurations for testing purposes.
"""

from src.core.config.models import AgencyStaticConfig, AgencyBehaviorConfig


def create_mock_static_config(agency_name: str = "TestAgency") -> AgencyStaticConfig:
    """
    Create a mock static configuration for testing.
    
    Args:
        agency_name: Name for the agency (default: "TestAgency")
        
    Returns:
        AgencyStaticConfig instance with test data
    """
    return AgencyStaticConfig(
        column_widths={
            "Agency": 15,
            "Order Type": 20,
            "Order Number": 15,
            "Order Date": 15,
            "Lease": 15,
            "Requested Legal": 25,
            "Report Start Date": 20,
            "Test Column": 12,
        },
        folder_structure=["^Document Archive", "Test Folder", "Runsheets"],
        dropbox_agency_name=agency_name
    )


def create_mock_behavioral_config() -> AgencyBehaviorConfig:
    """
    Create a mock behavioral configuration for testing.
    
    Returns:
        AgencyBehaviorConfig instance with test data
    """
    def mock_search_func(data):
        return f"search_result_{data}"
    
    return AgencyBehaviorConfig(
        search_mappings={
            "Test Search": mock_search_func,
            "Another Search": mock_search_func,
        },
        blank_columns=[
            "Test Column",
            "Another Column",
            "Documents",
            "Link",
        ]
    )


def create_mock_agency_config(agency_name: str = "TestAgency") -> dict:
    """
    Create a complete mock agency configuration for testing.
    
    Args:
        agency_name: Name for the agency (default: "TestAgency")
        
    Returns:
        Dictionary with 'static' and 'behavioral' configurations
    """
    return {
        "static": create_mock_static_config(agency_name),
        "behavioral": create_mock_behavioral_config()
    }


def create_minimal_static_config() -> AgencyStaticConfig:
    """
    Create a minimal static configuration for testing edge cases.
    
    Returns:
        AgencyStaticConfig instance with minimal data
    """
    return AgencyStaticConfig(
        column_widths={"Test": 10},
        folder_structure=["Test Folder"],
        dropbox_agency_name="MinimalAgency"
    )


def create_minimal_behavioral_config() -> AgencyBehaviorConfig:
    """
    Create a minimal behavioral configuration for testing edge cases.
    
    Returns:
        AgencyBehaviorConfig instance with minimal data
    """
    def minimal_search_func(data):
        return "minimal_result"
    
    return AgencyBehaviorConfig(
        search_mappings={"Minimal Search": minimal_search_func},
        blank_columns=["Minimal Column"]
    ) 