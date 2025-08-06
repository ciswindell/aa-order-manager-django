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
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ Environment loaded")
        except Exception as e:
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
        },
        folder_structure=["^Document Archive", "^MI Index", "Runsheets"]
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
        },
        folder_structure=["^Document Archive", "Runsheets"]
    )
}

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

# Dropbox configuration accessors
def get_dropbox_access_token() -> str:
    """Get Dropbox access token from environment."""
    return os.getenv("DROPBOX_ACCESS_TOKEN", "")

def get_dropbox_app_key() -> str:
    """Get Dropbox app key from environment."""
    return os.getenv("DROPBOX_APP_KEY", "")

def get_dropbox_app_secret() -> str:
    """Get Dropbox app secret from environment."""
    return os.getenv("DROPBOX_APP_SECRET", "")

def get_dropbox_auth_type() -> str:
    """
    Get Dropbox authentication type from environment.
    
    Returns:
        str: Authentication type - 'user', 'team', or 'oauth'
             Defaults to 'team' (for current business setup)
    
    Auth Types:
        - 'user': Regular individual user authentication (for real users)
        - 'team': Business team token with member selection (for services)  
        - 'oauth': OAuth browser flow (future implementation)
    """
    return os.getenv("DROPBOX_AUTH_TYPE", "team")

# Load environment once when module is imported
load_environment()