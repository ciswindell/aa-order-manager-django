"""
Dropbox Configuration Management

Manages app credentials and agency-specific directory path mappings
for the Dropbox integration system. Supports flexible configuration
through environment variables, config files, and runtime settings.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dropbox_service import DropboxServiceError

# Configure logging
logger = logging.getLogger(__name__)


class DropboxConfigError(DropboxServiceError):
    """Raised when configuration errors occur"""

    pass


class DropboxConfig:
    """
    Manages Dropbox application configuration and agency-specific settings.

    Handles app credentials, directory path mappings, and other configuration
    options with support for multiple configuration sources.
    """

    # Default agency directory mappings (can be overridden)
    DEFAULT_AGENCY_DIRECTORIES = {
        "Federal": "/Federal/",
        "NMState": "/NMState/",
        "State": "/NMState/",  # Alias for NMState
    }

    # Default configuration file locations
    DEFAULT_CONFIG_PATHS = [
        "dropbox_config.json",  # Current directory
        "~/.dropbox_auth/config.json",  # User home directory
        "/etc/dropbox/config.json",  # System-wide (Linux)
    ]

    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file_path: Optional path to configuration file
        """
        self.config_file_path = config_file_path
        self._config = {}
        self._agency_directories = self.DEFAULT_AGENCY_DIRECTORIES.copy()

        # Load configuration from various sources
        self._load_configuration()

        logger.info("DropboxConfig initialized")

    def _load_configuration(self) -> None:
        """Load configuration from various sources in priority order."""
        try:
            # 1. Load from config file
            self._load_from_file()

            # 2. Override with environment variables
            self._load_from_environment()

            # 3. Validate required settings
            self._validate_configuration()

            logger.info("Configuration loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise DropboxConfigError(f"Configuration error: {str(e)}")

    def _load_from_file(self) -> None:
        """Load configuration from JSON file."""
        config_path = self._find_config_file()

        if not config_path:
            logger.info("No configuration file found, using defaults")
            return

        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)

            self._config.update(file_config)

            # Load agency directories if specified
            if "agency_directories" in file_config:
                self._agency_directories.update(file_config["agency_directories"])

            logger.info(f"Configuration loaded from: {config_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {str(e)}")
            raise DropboxConfigError(f"Invalid configuration file: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {str(e)}")
            raise DropboxConfigError(f"Could not load configuration: {str(e)}")

    def _find_config_file(self) -> Optional[str]:
        """Find the first available configuration file."""
        paths_to_check = []

        # Check user-specified path first
        if self.config_file_path:
            paths_to_check.append(self.config_file_path)

        # Add default paths
        paths_to_check.extend(self.DEFAULT_CONFIG_PATHS)

        for path in paths_to_check:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                return expanded_path

        return None

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "DROPBOX_APP_KEY": "app_key",
            "DROPBOX_APP_SECRET": "app_secret",
            "DROPBOX_FEDERAL_DIR": ("agency_directories", "Federal"),
            "DROPBOX_NMSTATE_DIR": ("agency_directories", "NMState"),
            "DROPBOX_STATE_DIR": ("agency_directories", "State"),
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if isinstance(config_key, tuple):
                    # Nested configuration (e.g., agency_directories.Federal)
                    section, key = config_key
                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][key] = value

                    # Also update our agency directories
                    if section == "agency_directories":
                        self._agency_directories[key] = value
                else:
                    # Simple configuration
                    self._config[config_key] = value

                logger.debug(f"Loaded {config_key} from environment variable {env_var}")

    def _validate_configuration(self) -> None:
        """Validate that required configuration is present."""
        # Check for app credentials (optional for token-based auth)
        if not self.get_app_key():
            logger.debug(
                "No Dropbox app key configured (not required for token-based auth)"
            )

        if not self.get_app_secret():
            logger.debug(
                "No Dropbox app secret configured (not required for token-based auth)"
            )

        # Validate agency directories
        for agency, directory in self._agency_directories.items():
            if not directory.startswith("/"):
                logger.warning(
                    f"Agency directory for {agency} should start with '/': {directory}"
                )
            if not directory.endswith("/"):
                logger.warning(
                    f"Agency directory for {agency} should end with '/': {directory}"
                )

    def get_app_key(self) -> Optional[str]:
        """
        Get the Dropbox app key.

        Returns:
            Optional[str]: App key if configured, None otherwise
        """
        return self._config.get("app_key")

    def get_app_secret(self) -> Optional[str]:
        """
        Get the Dropbox app secret.

        Returns:
            Optional[str]: App secret if configured, None otherwise
        """
        return self._config.get("app_secret")

    def get_agency_directory(self, agency: str) -> Optional[str]:
        """
        Get the root directory path for a specific agency.

        Args:
            agency: Agency name (e.g., 'Federal', 'NMState', 'State')

        Returns:
            Optional[str]: Directory path if configured, None otherwise
        """
        return self._agency_directories.get(agency)

    def get_all_agency_directories(self) -> Dict[str, str]:
        """
        Get all configured agency directory mappings.

        Returns:
            Dict[str, str]: Mapping of agency names to directory paths
        """
        return self._agency_directories.copy()

    def set_agency_directory(self, agency: str, directory_path: str) -> None:
        """
        Set the root directory path for a specific agency.

        Args:
            agency: Agency name (e.g., 'Federal', 'NMState')
            directory_path: Root directory path (e.g., '/Federal/')
        """
        if not directory_path.startswith("/"):
            directory_path = "/" + directory_path
        if not directory_path.endswith("/"):
            directory_path = directory_path + "/"

        self._agency_directories[agency] = directory_path
        logger.info(f"Set agency directory for {agency}: {directory_path}")

    def set_app_credentials(self, app_key: str, app_secret: str) -> None:
        """
        Set Dropbox app credentials.

        Args:
            app_key: Dropbox app key
            app_secret: Dropbox app secret
        """
        self._config["app_key"] = app_key
        self._config["app_secret"] = app_secret
        logger.info("App credentials updated")

    def save_configuration(self, file_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.

        Args:
            file_path: Optional path to save configuration file
        """
        if not file_path:
            file_path = self.config_file_path or self.DEFAULT_CONFIG_PATHS[0]

        try:
            # Expand user home directory
            file_path = os.path.expanduser(file_path)

            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Prepare configuration data
            config_data = self._config.copy()
            config_data["agency_directories"] = self._agency_directories

            # Write configuration file
            with open(file_path, "w") as f:
                json.dump(config_data, f, indent=2)

            # Set restrictive permissions
            os.chmod(file_path, 0o600)

            logger.info(f"Configuration saved to: {file_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise DropboxConfigError(f"Could not save configuration: {str(e)}")

    def get_search_path_for_lease(self, agency: str, lease_name: str) -> Optional[str]:
        """
        Get the full Dropbox search path for a specific lease.

        Args:
            agency: Agency name (e.g., 'Federal', 'NMState')
            lease_name: Lease name (e.g., 'NMLC 123456')

        Returns:
            Optional[str]: Full search path if agency is configured, None otherwise

        Example:
            get_search_path_for_lease('Federal', 'NMLC 123456') -> '/Federal/NMLC 123456/'
        """
        agency_dir = self.get_agency_directory(agency)
        if not agency_dir:
            logger.warning(f"No directory configured for agency: {agency}")
            return None

        # Ensure lease name doesn't have leading/trailing slashes
        lease_name = lease_name.strip("/")

        # Construct full path
        full_path = f"{agency_dir}{lease_name}/"

        logger.debug(f"Generated search path for {agency}/{lease_name}: {full_path}")
        return full_path

    def is_configured(self) -> bool:
        """
        Check if the minimum required configuration is present.

        Returns:
            bool: True if app credentials are configured, False otherwise
        """
        return bool(self.get_app_key() and self.get_app_secret())

    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration (excluding secrets).

        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            "app_key_configured": bool(self.get_app_key()),
            "app_secret_configured": bool(self.get_app_secret()),
            "agency_directories": self.get_all_agency_directories(),
            "config_file_path": self.config_file_path,
            "is_configured": self.is_configured(),
        }

    def create_sample_config_file(self, file_path: str) -> None:
        """
        Create a sample configuration file with placeholders.

        Args:
            file_path: Path where to create the sample config file
        """
        sample_config = {
            "app_key": "YOUR_DROPBOX_APP_KEY_HERE",
            "app_secret": "YOUR_DROPBOX_APP_SECRET_HERE",
            "agency_directories": {
                "Federal": "/Federal/",
                "NMState": "/NMState/",
                "State": "/NMState/",
            },
        }

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as f:
                json.dump(sample_config, f, indent=2)

            os.chmod(file_path, 0o600)

            logger.info(f"Sample configuration file created: {file_path}")
            print(f"Sample configuration file created at: {file_path}")
            print(
                "Please edit this file with your actual Dropbox app credentials and directory paths."
            )

        except Exception as e:
            logger.error(f"Failed to create sample config: {str(e)}")
            raise DropboxConfigError(f"Could not create sample config: {str(e)}")


# Global configuration instance for easy access
_global_config = None


def get_config(config_file_path: Optional[str] = None) -> DropboxConfig:
    """
    Get the global configuration instance.

    Args:
        config_file_path: Optional path to configuration file

    Returns:
        DropboxConfig: Global configuration instance
    """
    global _global_config

    if _global_config is None:
        _global_config = DropboxConfig(config_file_path)

    return _global_config


def reset_config() -> None:
    """Reset the global configuration instance (mainly for testing)."""
    global _global_config
    _global_config = None


if __name__ == "__main__":
    # Command-line utility for configuration management
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create-sample":
        # Create sample configuration file
        config_path = sys.argv[2] if len(sys.argv) > 2 else "dropbox_config.json"
        config = DropboxConfig()
        config.create_sample_config_file(config_path)
    else:
        # Display current configuration
        config = get_config()
        summary = config.get_configuration_summary()

        print("Dropbox Configuration Summary:")
        print(f"  App Key Configured: {summary['app_key_configured']}")
        print(f"  App Secret Configured: {summary['app_secret_configured']}")
        print(f"  Is Fully Configured: {summary['is_configured']}")
        print(f"  Config File Path: {summary['config_file_path']}")
        print("  Agency Directories:")
        for agency, directory in summary["agency_directories"].items():
            print(f"    {agency}: {directory}")

        if not summary["is_configured"]:
            print("\nTo get started, run:")
            print(f"  python3 {sys.argv[0]} create-sample dropbox_config.json")
