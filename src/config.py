"""
Simple Configuration System

Everything in one place: env loading, directory paths, column widths.
"""

import os
from typing import Dict, List
from dataclasses import dataclass


def load_environment():
    """Load environment variables from .env file if it exists."""
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Environment loaded")
        except (OSError, IOError) as e:
            print(f"⚠️ Could not load .env: {e}")


@dataclass
class AgencyConfig:
    """Simple agency configuration."""

    runsheet_report_directory_path: str
    lease_file_directory_path: str
    column_widths: Dict[str, int]
    folder_structure: List[str]


# All configuration in one place
AGENCY_CONFIGS = {
    "NMSLO": AgencyConfig(
        runsheet_report_directory_path="/State Workspace/^Runsheet Workspace/Runsheet Report Archive - New Format/",
        lease_file_directory_path="/NMSLO/",
        column_widths={
            "Agency": 15,
            "Order Type": 15,
            "Order Number": 15,
            "Order Date": 15,
            "Lease": 15,
            "Legal Description": 25,
            "Report Start Date": 20,
            "Report End Date": 20,
            "Report Notes": 30,
            "Report Directory Link": 30,
            "Previous Report Found": 20,
            "Tractstar Needed": 12,
            "Documents Needed": 12,
            "Misc Index Needed": 12,
            # "Documents Links": 30,
            "Misc Index Links": 30,
            "Documents": 12,
            "Search Notes": 30,
        },
        folder_structure=["^Document Archive", "^MI Index", "Runsheets"],
    ),
    "Federal": AgencyConfig(
        runsheet_report_directory_path="/Federal Workspace/^Runsheet Workspace/Runsheet Archive/",
        lease_file_directory_path="/Federal/",
        column_widths={
            "Agency": 15,
            "Order Type": 15,
            "Order Number": 15,
            "Order Date": 15,
            "Lease": 15,
            "Legal Description": 25,
            "Report Start Date": 20,
            "Report End Date": 20,
            "Report Notes": 30,
            "Report Directory Link": 30,
            "Previous Report Found": 20,
            "Tractstar Needed": 12,
            # "Documents Links": 30,
            "Documents Needed": 12,
            "Search Notes": 30,
        },
        folder_structure=["^Document Archive", "Runsheets"],
    ),
}

# Create BLM as alias for Federal config
AGENCY_CONFIGS["BLM"] = AGENCY_CONFIGS["Federal"]


# Simple accessors
def get_agency_config(agency: str) -> AgencyConfig:
    """Get configuration for an agency."""
    return AGENCY_CONFIGS.get(agency, AGENCY_CONFIGS["NMSLO"])


def get_runsheet_directory_path(agency: str) -> str:
    """Get runsheet report directory path for an agency."""
    return get_agency_config(agency).runsheet_report_directory_path


def get_lease_file_directory_path(agency: str) -> str:
    """Get lease file directory path for an agency."""
    return get_agency_config(agency).lease_file_directory_path


def get_column_widths(agency: str) -> Dict[str, int]:
    """Get column widths for an agency."""
    return get_agency_config(agency).column_widths


def get_column_order(agency: str) -> List[str]:
    """Get column order for an agency based on column_widths keys."""
    return list(get_agency_config(agency).column_widths.keys())


# Cloud provider configuration
def get_cloud_provider() -> str:
    """Get configured cloud provider from environment."""
    return os.getenv("CLOUD_PROVIDER", "dropbox")


def get_dropbox_auth_type() -> str:
    """Get Dropbox authentication type from environment."""
    return os.getenv("DROPBOX_AUTH_TYPE", "token")


def get_dropbox_access_token() -> str:
    """Get Dropbox access token from environment."""
    return os.getenv("DROPBOX_ACCESS_TOKEN", "")


# Load environment once when module is imported
load_environment()
