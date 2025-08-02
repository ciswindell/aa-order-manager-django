"""
Unit tests for dropbox_config.py module.

Tests configuration management, agency directory mappings,
file loading/saving, and environment variable handling.
"""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

# Import the classes we're testing
try:
    from src.integrations.dropbox.config import (
        DropboxConfig,
        DropboxConfigError,
        get_config,
        reset_config,
    )
except ImportError:
    # Handle case where modules aren't available
    DropboxConfig = None
    DropboxConfigError = Exception


class TestDropboxConfigInitialization(unittest.TestCase):
    """Test DropboxConfig initialization and setup."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        reset_config()  # Reset global config for other tests

    @patch("src.integrations.dropbox.config.logger")
    def test_initialization_success(self, mock_logger):
        """Test successful initialization with default settings."""
        with patch.object(DropboxConfig, "_load_configuration"):
            config = DropboxConfig()

        self.assertEqual(
            config._agency_directories, DropboxConfig.DEFAULT_AGENCY_DIRECTORIES
        )
        mock_logger.info.assert_called_with("DropboxConfig initialized")

    @patch("src.integrations.dropbox.config.logger")
    def test_initialization_with_custom_file_path(self, mock_logger):
        """Test initialization with custom config file path."""
        with patch.object(DropboxConfig, "_load_configuration"):
            config = DropboxConfig(config_file_path=self.config_file)

        self.assertEqual(config.config_file_path, self.config_file)
        mock_logger.info.assert_called_with("DropboxConfig initialized")

    def test_default_agency_directories(self):
        """Test that default agency directories are properly set."""
        with patch.object(DropboxConfig, "_load_configuration"):
            config = DropboxConfig()

        expected_defaults = {
            "Federal": "/Federal/",
            "NMSLO": "/NMSLO/",
        }
        self.assertEqual(config._agency_directories, expected_defaults)


class TestDropboxConfigFileLoading(unittest.TestCase):
    """Test configuration file loading functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        reset_config()

    @patch("src.integrations.dropbox.config.logger")
    def test_load_from_valid_json_file(self, mock_logger):
        """Test loading configuration from valid JSON file."""
        test_config = {
            "app_key": "test_key",
            "app_secret": "test_secret",
            "agency_directories": {"Federal": "/MyFederal/", "NMSLO": "/MyNMSLO/"},
        }

        with open(self.config_file, "w") as f:
            json.dump(test_config, f)

        config = DropboxConfig(config_file_path=self.config_file)

        self.assertEqual(config.get_app_key(), "test_key")
        self.assertEqual(config.get_app_secret(), "test_secret")
        self.assertEqual(config.get_agency_directory("Federal"), "/MyFederal/")
        mock_logger.info.assert_any_call(
            f"Configuration loaded from: {self.config_file}"
        )

    @patch("src.integrations.dropbox.config.logger")
    def test_load_from_invalid_json_file(self, mock_logger):
        """Test loading configuration from invalid JSON file."""
        with open(self.config_file, "w") as f:
            f.write("invalid json content")

        with self.assertRaises(DropboxConfigError) as context:
            DropboxConfig(config_file_path=self.config_file)

        self.assertIn("Invalid configuration file", str(context.exception))
        mock_logger.error.assert_called()

    @patch("src.integrations.dropbox.config.logger")
    def test_load_from_nonexistent_file(self, mock_logger):
        """Test loading configuration when file doesn't exist."""
        config = DropboxConfig(config_file_path="/nonexistent/config.json")

        # Should use defaults when file doesn't exist
        self.assertEqual(config.get_agency_directory("Federal"), "/Federal/")
        mock_logger.info.assert_any_call("No configuration file found, using defaults")


class TestDropboxConfigEnvironmentVariables(unittest.TestCase):
    """Test environment variable configuration loading."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        reset_config()

    @patch("src.integrations.dropbox.config.logger")
    def test_load_from_environment_variables(self, mock_logger):
        """Test loading configuration from environment variables."""
        # Set test environment variables
        os.environ["DROPBOX_APP_KEY"] = "env_test_key"
        os.environ["DROPBOX_APP_SECRET"] = "env_test_secret"
        os.environ["DROPBOX_FEDERAL_DIR"] = "/EnvFederal/"
        os.environ["DROPBOX_NMSLO_DIR"] = "/EnvNMSLO/"

        with patch.object(DropboxConfig, "_find_config_file", return_value=None):
            config = DropboxConfig()

        self.assertEqual(config.get_app_key(), "env_test_key")
        self.assertEqual(config.get_app_secret(), "env_test_secret")
        self.assertEqual(config.get_agency_directory("Federal"), "/EnvFederal/")
        self.assertEqual(config.get_agency_directory("NMSLO"), "/EnvNMSLO/")

    def test_environment_variables_override_file(self):
        """Test that environment variables override file configuration."""
        # Create config file
        temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(temp_dir, "config.json")

        file_config = {
            "app_key": "file_key",
            "agency_directories": {"Federal": "/FileFederal/"},
        }

        with open(config_file, "w") as f:
            json.dump(file_config, f)

        # Set environment variable that should override
        os.environ["DROPBOX_APP_KEY"] = "env_override_key"
        os.environ["DROPBOX_FEDERAL_DIR"] = "/EnvOverrideFederal/"

        try:
            config = DropboxConfig(config_file_path=config_file)

            # Environment should override file
            self.assertEqual(config.get_app_key(), "env_override_key")
            self.assertEqual(
                config.get_agency_directory("Federal"), "/EnvOverrideFederal/"
            )
        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestDropboxConfigAgencyDirectories(unittest.TestCase):
    """Test agency directory management functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch.object(DropboxConfig, "_load_configuration"):
            self.config = DropboxConfig()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_config()

    def test_get_agency_directory_exists(self):
        """Test getting existing agency directory."""
        result = self.config.get_agency_directory("Federal")
        self.assertEqual(result, "/Federal/")

    def test_get_agency_directory_not_exists(self):
        """Test getting non-existent agency directory."""
        result = self.config.get_agency_directory("NonExistent")
        self.assertIsNone(result)

    def test_set_agency_directory_with_slashes(self):
        """Test setting agency directory with proper slash handling."""
        self.config.set_agency_directory("TestAgency", "/Test/Path/")
        result = self.config.get_agency_directory("TestAgency")
        self.assertEqual(result, "/Test/Path/")

    def test_set_agency_directory_without_slashes(self):
        """Test setting agency directory with automatic slash addition."""
        self.config.set_agency_directory("TestAgency", "Test/Path")
        result = self.config.get_agency_directory("TestAgency")
        self.assertEqual(result, "/Test/Path/")

    def test_get_all_agency_directories(self):
        """Test getting all agency directory mappings."""
        result = self.config.get_all_agency_directories()

        # Should be a copy, not the original
        self.assertIsNot(result, self.config._agency_directories)
        self.assertEqual(result, self.config._agency_directories)

    def test_get_search_path_for_lease(self):
        """Test generating search path for lease."""
        result = self.config.get_search_path_for_lease("Federal", "NMLC 123456")
        self.assertEqual(result, "/Federal/NMLC 123456/")

    def test_get_search_path_for_lease_unknown_agency(self):
        """Test generating search path for unknown agency."""
        result = self.config.get_search_path_for_lease("Unknown", "NMLC 123456")
        self.assertIsNone(result)

    def test_get_search_path_for_lease_strips_slashes(self):
        """Test that lease name slashes are properly handled."""
        result = self.config.get_search_path_for_lease("Federal", "/NMLC 123456/")
        self.assertEqual(result, "/Federal/NMLC 123456/")


class TestDropboxConfigCredentials(unittest.TestCase):
    """Test app credentials management."""

    def setUp(self):
        """Set up test fixtures."""
        with patch.object(DropboxConfig, "_load_configuration"):
            self.config = DropboxConfig()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_config()

    def test_set_and_get_app_credentials(self):
        """Test setting and getting app credentials."""
        self.config.set_app_credentials("test_key", "test_secret")

        self.assertEqual(self.config.get_app_key(), "test_key")
        self.assertEqual(self.config.get_app_secret(), "test_secret")

    def test_is_configured_true(self):
        """Test is_configured when credentials are set."""
        self.config.set_app_credentials("test_key", "test_secret")
        self.assertTrue(self.config.is_configured())

    def test_is_configured_false(self):
        """Test is_configured when credentials are not set."""
        self.assertFalse(self.config.is_configured())

    def test_get_configuration_summary(self):
        """Test getting configuration summary."""
        self.config.set_app_credentials("test_key", "test_secret")

        summary = self.config.get_configuration_summary()

        expected_keys = [
            "app_key_configured",
            "app_secret_configured",
            "agency_directories",
            "config_file_path",
            "is_configured",
        ]

        for key in expected_keys:
            self.assertIn(key, summary)

        self.assertTrue(summary["app_key_configured"])
        self.assertTrue(summary["app_secret_configured"])
        self.assertTrue(summary["is_configured"])


class TestDropboxConfigFileSaving(unittest.TestCase):
    """Test configuration file saving functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "save_test.json")

        with patch.object(DropboxConfig, "_load_configuration"):
            self.config = DropboxConfig()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        reset_config()

    @patch("src.integrations.dropbox.config.logger")
    def test_save_configuration_success(self, mock_logger):
        """Test successful configuration saving."""
        self.config.set_app_credentials("save_key", "save_secret")
        self.config.set_agency_directory("TestAgency", "/TestPath/")

        self.config.save_configuration(self.config_file)

        # Verify file was created
        self.assertTrue(os.path.exists(self.config_file))

        # Verify file contents
        with open(self.config_file, "r") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["app_key"], "save_key")
        self.assertEqual(saved_data["app_secret"], "save_secret")
        self.assertEqual(saved_data["agency_directories"]["TestAgency"], "/TestPath/")

        # Verify permissions (should be 0o600)
        file_stat = os.stat(self.config_file)
        permissions = file_stat.st_mode & 0o777
        self.assertEqual(permissions, 0o600)

        mock_logger.info.assert_called_with(
            f"Configuration saved to: {self.config_file}"
        )

    def test_save_configuration_creates_directory(self):
        """Test that save_configuration creates parent directories."""
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "config.json")

        self.config.save_configuration(nested_path)

        self.assertTrue(os.path.exists(nested_path))
        self.assertTrue(os.path.isdir(os.path.dirname(nested_path)))

    def test_create_sample_config_file(self):
        """Test creating sample configuration file."""
        sample_file = os.path.join(self.temp_dir, "sample_config.json")

        with patch("builtins.print") as mock_print:
            self.config.create_sample_config_file(sample_file)

        # Verify file was created
        self.assertTrue(os.path.exists(sample_file))

        # Verify file contents
        with open(sample_file, "r") as f:
            sample_data = json.load(f)

        self.assertIn("app_key", sample_data)
        self.assertIn("app_secret", sample_data)
        self.assertIn("agency_directories", sample_data)
        self.assertEqual(sample_data["app_key"], "YOUR_DROPBOX_APP_KEY_HERE")

        # Verify user feedback
        mock_print.assert_any_call(
            f"Sample configuration file created at: {sample_file}"
        )


class TestDropboxConfigValidation(unittest.TestCase):
    """Test configuration validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch.object(DropboxConfig, "_load_configuration"):
            self.config = DropboxConfig()

    def tearDown(self):
        """Clean up test fixtures."""
        reset_config()

    @patch("src.integrations.dropbox.config.logger")
    def test_validate_configuration_missing_credentials(self, mock_logger):
        """Test validation when credentials are missing."""
        self.config._validate_configuration()

        mock_logger.warning.assert_any_call("No Dropbox app key configured")
        mock_logger.warning.assert_any_call("No Dropbox app secret configured")

    @patch("src.integrations.dropbox.config.logger")
    def test_validate_configuration_invalid_directory_paths(self, mock_logger):
        """Test validation of invalid directory paths."""
        self.config.set_agency_directory(
            "BadStart", "Federal/"
        )  # Missing leading slash
        self.config.set_agency_directory("BadEnd", "/Federal")  # Missing trailing slash

        self.config._validate_configuration()

        # Should have warnings about path format
        warning_calls = [call.args[0] for call in mock_logger.warning.call_args_list]
        bad_start_warnings = [
            msg
            for msg in warning_calls
            if "BadStart" in msg and "should start with" in msg
        ]
        bad_end_warnings = [
            msg for msg in warning_calls if "BadEnd" in msg and "should end with" in msg
        ]

        self.assertTrue(len(bad_start_warnings) > 0)
        self.assertTrue(len(bad_end_warnings) > 0)


class TestDropboxConfigGlobalInstance(unittest.TestCase):
    """Test global configuration instance management."""

    def tearDown(self):
        """Clean up test fixtures."""
        reset_config()

    def test_get_config_creates_global_instance(self):
        """Test that get_config creates and returns global instance."""
        with patch.object(DropboxConfig, "_load_configuration"):
            config1 = get_config()
            config2 = get_config()

        # Should return the same instance
        self.assertIs(config1, config2)

    def test_reset_config_clears_global_instance(self):
        """Test that reset_config clears global instance."""
        with patch.object(DropboxConfig, "_load_configuration"):
            config1 = get_config()
            reset_config()
            config2 = get_config()

        # Should be different instances after reset
        self.assertIsNot(config1, config2)


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run the tests
    unittest.main(verbosity=2)
