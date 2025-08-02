"""
Unit tests for dropbox_service.py module.

Tests the service module structure, interfaces, error handling,
and core functionality of the DropboxService class.
"""

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

# Import the classes we're testing
from src.integrations.dropbox.service import (
    DropboxAuthenticationError,
    DropboxLinkError,
    DropboxSearchError,
    DropboxService,
    DropboxServiceError,
    DropboxServiceInterface,
)


class TestDropboxServiceInterface(unittest.TestCase):
    """Test the abstract DropboxServiceInterface."""

    def test_interface_is_abstract(self):
        """Test that DropboxServiceInterface cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            DropboxServiceInterface()

    def test_interface_has_required_methods(self):
        """Test that the interface defines all required abstract methods."""
        required_methods = [
            "authenticate",
            "is_authenticated",
            "search_directory",
            "get_shareable_link",
        ]

        for method_name in required_methods:
            self.assertTrue(hasattr(DropboxServiceInterface, method_name))
            method = getattr(DropboxServiceInterface, method_name)
            self.assertTrue(hasattr(method, "__isabstractmethod__"))


class TestDropboxServiceExceptions(unittest.TestCase):
    """Test the custom exception hierarchy."""

    def test_dropbox_service_error_inheritance(self):
        """Test that DropboxServiceError inherits from Exception."""
        error = DropboxServiceError("test error")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "test error")

    def test_authentication_error_inheritance(self):
        """Test that DropboxAuthenticationError inherits from DropboxServiceError."""
        error = DropboxAuthenticationError("auth error")
        self.assertIsInstance(error, DropboxServiceError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "auth error")

    def test_search_error_inheritance(self):
        """Test that DropboxSearchError inherits from DropboxServiceError."""
        error = DropboxSearchError("search error")
        self.assertIsInstance(error, DropboxServiceError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "search error")

    def test_link_error_inheritance(self):
        """Test that DropboxLinkError inherits from DropboxServiceError."""
        error = DropboxLinkError("link error")
        self.assertIsInstance(error, DropboxServiceError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "link error")


class TestDropboxService(unittest.TestCase):
    """Test the main DropboxService implementation."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )

    def test_service_implements_interface(self):
        """Test that DropboxService implements DropboxServiceInterface."""
        self.assertIsInstance(self.service, DropboxServiceInterface)

    def test_initialization(self):
        """Test proper initialization of DropboxService."""
        self.assertEqual(self.service._auth_handler, self.mock_auth_handler)
        self.assertEqual(self.service._config_manager, self.mock_config_manager)
        self.assertIsNone(self.service._client)

    def test_initialization_without_dependencies(self):
        """Test initialization without dependency injection."""
        service = DropboxService()
        self.assertIsNone(service._auth_handler)
        self.assertIsNone(service._config_manager)
        self.assertIsNone(service._client)

    @patch("src.integrations.dropbox.service.logger")
    def test_initialization_logging(self, mock_logger):
        """Test that initialization logs properly."""
        DropboxService()
        mock_logger.info.assert_called_with("DropboxService initialized")


class TestDropboxServiceAuthentication(unittest.TestCase):
    """Test authentication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )

    @patch("src.integrations.dropbox.service.logger")
    def test_authenticate_success(self, mock_logger):
        """Test successful authentication."""
        mock_client = Mock()
        self.mock_auth_handler.authenticate.return_value = mock_client

        result = self.service.authenticate()

        self.assertTrue(result)
        self.assertEqual(self.service._client, mock_client)
        self.mock_auth_handler.authenticate.assert_called_once()
        mock_logger.info.assert_called_with("Dropbox authentication successful")

    @patch("src.integrations.dropbox.service.logger")
    def test_authenticate_failure(self, mock_logger):
        """Test authentication failure."""
        self.mock_auth_handler.authenticate.return_value = None

        result = self.service.authenticate()

        self.assertFalse(result)
        self.assertIsNone(self.service._client)
        mock_logger.warning.assert_called_with("Dropbox authentication failed")

    def test_authenticate_no_auth_handler(self):
        """Test authentication without auth handler."""
        service = DropboxService()

        with self.assertRaises(DropboxAuthenticationError) as context:
            service.authenticate()

        self.assertIn("No authentication handler provided", str(context.exception))

    @patch("src.integrations.dropbox.service.logger")
    def test_authenticate_exception(self, mock_logger):
        """Test authentication when auth handler raises exception."""
        self.mock_auth_handler.authenticate.side_effect = Exception("Auth failed")

        with self.assertRaises(DropboxAuthenticationError) as context:
            self.service.authenticate()

        self.assertIn("Authentication failed: Auth failed", str(context.exception))
        mock_logger.error.assert_called_with("Authentication error: Auth failed")

    def test_is_authenticated_true(self):
        """Test is_authenticated when client is set."""
        self.service._client = Mock()
        self.assertTrue(self.service.is_authenticated())

    def test_is_authenticated_false(self):
        """Test is_authenticated when client is None."""
        self.service._client = None
        self.assertFalse(self.service.is_authenticated())


class TestDropboxServiceDirectorySearch(unittest.TestCase):
    """Test directory search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_search_directory_authenticated(self, mock_logger):
        """Test directory search when authenticated."""
        result = self.service.search_directory("NMLC 123456", "Federal")

        # Currently returns None as placeholder
        self.assertIsNone(result)
        mock_logger.info.assert_any_call(
            "Searching for directory: NMLC 123456 (agency: Federal)"
        )
        mock_logger.info.assert_any_call("Directory search completed for: NMLC 123456")

    def test_search_directory_not_authenticated(self):
        """Test directory search when not authenticated."""
        self.service._client = None

        with self.assertRaises(DropboxAuthenticationError) as context:
            self.service.search_directory("NMLC 123456", "Federal")

        self.assertIn("Service not authenticated", str(context.exception))

    @patch("src.integrations.dropbox.service.logger")
    def test_search_directory_exception(self, mock_logger):
        """Test directory search when exception occurs."""
        # Mock an exception during search (will be implemented in future tasks)
        with patch.object(self.service, "search_directory") as mock_search:
            mock_search.side_effect = Exception("Search failed")

            with self.assertRaises(Exception):
                self.service.search_directory("NMLC 123456", "Federal")


class TestDropboxServiceLinkGeneration(unittest.TestCase):
    """Test link generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_get_shareable_link_authenticated(self, mock_logger):
        """Test shareable link generation when authenticated."""
        result = self.service.get_shareable_link("/Federal/NMLC 123456/")

        # Currently returns None as placeholder
        self.assertIsNone(result)
        mock_logger.info.assert_any_call(
            "Generating shareable link for path: /Federal/NMLC 123456/"
        )
        mock_logger.info.assert_any_call(
            "Shareable link generation completed for: /Federal/NMLC 123456/"
        )

    def test_get_shareable_link_not_authenticated(self):
        """Test link generation when not authenticated."""
        self.service._client = None

        with self.assertRaises(DropboxAuthenticationError) as context:
            self.service.get_shareable_link("/Federal/NMLC 123456/")

        self.assertIn("Service not authenticated", str(context.exception))


class TestDropboxServiceBulkOperations(unittest.TestCase):
    """Test bulk operations functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_bulk_search_directories_success(self, mock_logger):
        """Test bulk directory search with successful results."""
        directory_names = ["NMLC 123456", "NMLC 789012"]

        # Mock search_directory to return None (placeholder)
        with patch.object(self.service, "search_directory", return_value=None):
            results = self.service.bulk_search_directories(directory_names, "Federal")

        expected_results = {"NMLC 123456": None, "NMLC 789012": None}
        self.assertEqual(results, expected_results)

    @patch("src.integrations.dropbox.service.logger")
    def test_bulk_search_directories_with_errors(self, mock_logger):
        """Test bulk directory search with some errors."""
        directory_names = ["NMLC 123456", "NMLC 789012"]

        def mock_search(name, agency):
            if name == "NMLC 123456":
                return "https://dropbox.com/link1"
            else:
                raise DropboxSearchError("Not found")

        with patch.object(self.service, "search_directory", side_effect=mock_search):
            results = self.service.bulk_search_directories(directory_names, "Federal")

        expected_results = {
            "NMLC 123456": "https://dropbox.com/link1",
            "NMLC 789012": None,
        }
        self.assertEqual(results, expected_results)
        mock_logger.warning.assert_called_with(
            "Failed to find directory 'NMLC 789012': Not found"
        )


class TestDropboxServiceLogging(unittest.TestCase):
    """Test logging functionality throughout the service."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.service = DropboxService(auth_handler=self.mock_auth_handler)

    @patch("src.integrations.dropbox.service.logger")
    def test_logger_configuration(self, mock_logger):
        """Test that logger is properly configured."""
        # Logger should be configured at module level
        from src.integrations.dropbox.service import logger

        self.assertEqual(logger.name, "dropbox_service")


class TestDropboxServiceDirectorySearchEnhanced(unittest.TestCase):
    """Test enhanced directory search functionality with agency-specific scoping."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_search_directory_with_agency_scoping_success(self, mock_logger):
        """Test successful directory search with agency scoping."""
        # Mock config manager to return search path
        self.mock_config_manager.get_search_path_for_lease.return_value = (
            "/Federal/NMLC 123456/"
        )

        # Mock successful exact path search
        with patch.object(
            self.service,
            "_search_exact_directory_path",
            return_value="/Federal/NMLC 123456",
        ), patch.object(
            self.service, "get_shareable_link", return_value="https://dropbox.com/link"
        ):

            result = self.service.search_directory("NMLC 123456", "Federal")

        self.assertEqual(result, "https://dropbox.com/link")
        self.mock_config_manager.get_search_path_for_lease.assert_called_with(
            "Federal", "NMLC 123456"
        )
        mock_logger.info.assert_any_call("Generated search path: /Federal/NMLC 123456/")

    @patch("src.integrations.dropbox.service.logger")
    def test_search_directory_with_agency_no_search_path(self, mock_logger):
        """Test directory search when config manager can't generate search path."""
        # Mock config manager to return None
        self.mock_config_manager.get_search_path_for_lease.return_value = None

        result = self.service.search_directory("NMLC 123456", "Federal")

        self.assertIsNone(result)
        mock_logger.warning.assert_called_with(
            "Could not generate search path for agency 'Federal' and directory 'NMLC 123456'"
        )

    @patch("src.integrations.dropbox.service.logger")
    def test_search_directory_fallback_to_general_search(self, mock_logger):
        """Test fallback to general search when no agency specified."""
        with patch.object(
            self.service,
            "_search_directory_general",
            return_value="/General/NMLC 123456",
        ), patch.object(
            self.service, "get_shareable_link", return_value="https://dropbox.com/link"
        ):

            result = self.service.search_directory("NMLC 123456", agency=None)

        self.assertEqual(result, "https://dropbox.com/link")
        mock_logger.info.assert_any_call(
            "Performing general directory search (no agency scoping)"
        )

    def test_search_exact_directory_path_success(self):
        """Test successful exact directory path search."""
        mock_metadata = Mock()
        mock_metadata.tag = "folder"
        self.service._client.files_get_metadata.return_value = mock_metadata

        result = self.service._search_exact_directory_path("/Federal/NMLC 123456/")

        self.assertEqual(result, "/Federal/NMLC 123456")
        self.service._client.files_get_metadata.assert_called_with(
            "/Federal/NMLC 123456"
        )

    def test_search_exact_directory_path_not_folder(self):
        """Test exact path search when path exists but is not a folder."""
        mock_metadata = Mock()
        mock_metadata.tag = "file"
        self.service._client.files_get_metadata.return_value = mock_metadata

        result = self.service._search_exact_directory_path("/Federal/NMLC 123456/")

        self.assertIsNone(result)

    def test_search_exact_directory_path_fallback_to_api(self):
        """Test fallback to API search when direct path lookup fails."""
        self.service._client.files_get_metadata.side_effect = Exception("Not found")

        with patch.object(
            self.service,
            "_search_directory_with_api",
            return_value="/Federal/NMLC 123456",
        ):
            result = self.service._search_exact_directory_path("/Federal/NMLC 123456/")

        self.assertEqual(result, "/Federal/NMLC 123456")

    def test_search_directory_with_api_success(self):
        """Test successful API-based directory search."""
        # Mock search results
        mock_match = Mock()
        mock_metadata = Mock()
        mock_metadata.tag = "folder"
        mock_metadata.path_lower = "/federal/nmlc 123456"
        mock_metadata.path_display = "/Federal/NMLC 123456"
        mock_match.metadata.metadata = mock_metadata

        mock_search_results = Mock()
        mock_search_results.matches = [mock_match]
        self.service._client.files_search_v2.return_value = mock_search_results

        result = self.service._search_directory_with_api("/Federal/NMLC 123456")

        self.assertEqual(result, "/Federal/NMLC 123456")

    def test_search_directory_general_exact_name_match(self):
        """Test general directory search with exact name match."""
        # Mock search results
        mock_match = Mock()
        mock_metadata = Mock()
        mock_metadata.tag = "folder"
        mock_metadata.name = "NMLC 123456"
        mock_metadata.path_display = "/SomeFolder/NMLC 123456"
        mock_match.metadata.metadata = mock_metadata

        mock_search_results = Mock()
        mock_search_results.matches = [mock_match]
        self.service._client.files_search_v2.return_value = mock_search_results

        result = self.service._search_directory_general("NMLC 123456")

        self.assertEqual(result, "/SomeFolder/NMLC 123456")


class TestDropboxServiceLinkGenerationEnhanced(unittest.TestCase):
    """Test enhanced shareable link generation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_get_shareable_link_existing_link_found(self, mock_logger):
        """Test shareable link generation when existing link is found."""
        with patch.object(
            self.service,
            "_get_existing_shared_link",
            return_value="https://existing.link",
        ):
            result = self.service.get_shareable_link("/Federal/NMLC 123456")

        self.assertEqual(result, "https://existing.link")
        mock_logger.info.assert_any_call(
            "Found existing shareable link: https://existing.link"
        )

    @patch("src.integrations.dropbox.service.logger")
    def test_get_shareable_link_create_new_link(self, mock_logger):
        """Test creating new shareable link when none exists."""
        with patch.object(
            self.service, "_get_existing_shared_link", return_value=None
        ), patch.object(
            self.service, "_create_new_shared_link", return_value="https://new.link"
        ):

            result = self.service.get_shareable_link("/Federal/NMLC 123456")

        self.assertEqual(result, "https://new.link")
        mock_logger.info.assert_any_call("Created new shareable link: https://new.link")

    @patch("src.integrations.dropbox.service.logger")
    def test_get_shareable_link_creation_fails(self, mock_logger):
        """Test shareable link generation when both existing and new creation fail."""
        with patch.object(
            self.service, "_get_existing_shared_link", return_value=None
        ), patch.object(self.service, "_create_new_shared_link", return_value=None):

            result = self.service.get_shareable_link("/Federal/NMLC 123456")

        self.assertIsNone(result)
        mock_logger.warning.assert_called_with(
            "Failed to create shareable link for path: /Federal/NMLC 123456"
        )

    def test_get_existing_shared_link_found(self):
        """Test finding existing shared link."""
        mock_link = Mock()
        mock_link.url = "https://existing.link"

        mock_shared_links = Mock()
        mock_shared_links.links = [mock_link]
        self.service._client.sharing_list_shared_links.return_value = mock_shared_links

        result = self.service._get_existing_shared_link("/Federal/NMLC 123456")

        self.assertEqual(result, "https://existing.link")
        self.service._client.sharing_list_shared_links.assert_called_with(
            path="/Federal/NMLC 123456", direct_only=True
        )

    def test_get_existing_shared_link_none_found(self):
        """Test when no existing shared links are found."""
        mock_shared_links = Mock()
        mock_shared_links.links = []
        self.service._client.sharing_list_shared_links.return_value = mock_shared_links

        result = self.service._get_existing_shared_link("/Federal/NMLC 123456")

        self.assertIsNone(result)

    @patch("src.integrations.dropbox.service.SharedLinkSettings")
    @patch("src.integrations.dropbox.service.RequestedVisibility")
    def test_create_new_shared_link_with_settings(self, mock_visibility, mock_settings):
        """Test creating new shared link with settings."""
        # Mock the sharing settings
        mock_settings_instance = Mock()
        mock_settings.return_value = mock_settings_instance
        mock_visibility.public = "public"

        mock_shared_link = Mock()
        mock_shared_link.url = "https://new.link"
        self.service._client.sharing_create_shared_link_with_settings.return_value = (
            mock_shared_link
        )

        # Mock the import to be successful
        with patch(
            "src.integrations.dropbox.service.SharedLinkSettings", mock_settings
        ), patch(
            "src.integrations.dropbox.service.RequestedVisibility", mock_visibility
        ):

            result = self.service._create_new_shared_link("/Federal/NMLC 123456")

        self.assertEqual(result, "https://new.link")

    def test_create_new_shared_link_already_exists_error(self):
        """Test handling 'shared link already exists' error."""
        self.service._client.sharing_create_shared_link.side_effect = Exception(
            "shared_link_already_exists"
        )

        with patch.object(
            self.service,
            "_get_existing_shared_link",
            return_value="https://existing.link",
        ):
            result = self.service._create_new_shared_link("/Federal/NMLC 123456")

        self.assertEqual(result, "https://existing.link")

    def test_create_shareable_links_batch_success(self):
        """Test batch creation of shareable links."""
        paths = ["/Federal/NMLC 123456", "/Federal/NMLC 789012"]

        def mock_get_link(path):
            if "123456" in path:
                return "https://link1.com"
            elif "789012" in path:
                return "https://link2.com"
            return None

        with patch.object(
            self.service, "get_shareable_link", side_effect=mock_get_link
        ):
            results = self.service.create_shareable_links_batch(paths)

        expected = {
            "/Federal/NMLC 123456": "https://link1.com",
            "/Federal/NMLC 789012": "https://link2.com",
        }
        self.assertEqual(results, expected)

    @patch("src.integrations.dropbox.service.logger")
    def test_create_shareable_links_batch_with_errors(self, mock_logger):
        """Test batch creation with some errors."""
        paths = ["/Federal/NMLC 123456", "/Federal/NMLC 789012"]

        def mock_get_link(path):
            if "123456" in path:
                return "https://link1.com"
            else:
                raise DropboxLinkError("Failed to create link")

        with patch.object(
            self.service, "get_shareable_link", side_effect=mock_get_link
        ):
            results = self.service.create_shareable_links_batch(paths)

        expected = {
            "/Federal/NMLC 123456": "https://link1.com",
            "/Federal/NMLC 789012": None,
        }
        self.assertEqual(results, expected)
        mock_logger.warning.assert_called()

    def test_validate_shareable_link_valid(self):
        """Test validation of valid shareable link."""
        valid_link = "https://dropbox.com/s/abc123/folder"
        result = self.service.validate_shareable_link(valid_link)
        self.assertTrue(result)

    def test_validate_shareable_link_invalid_protocol(self):
        """Test validation of link with invalid protocol."""
        invalid_link = "http://dropbox.com/s/abc123/folder"
        result = self.service.validate_shareable_link(invalid_link)
        self.assertFalse(result)

    def test_validate_shareable_link_not_dropbox(self):
        """Test validation of non-Dropbox link."""
        invalid_link = "https://google.com/some/path"
        result = self.service.validate_shareable_link(invalid_link)
        self.assertFalse(result)

    def test_validate_shareable_link_empty(self):
        """Test validation of empty link."""
        result = self.service.validate_shareable_link("")
        self.assertFalse(result)

        result = self.service.validate_shareable_link(None)
        self.assertFalse(result)


class TestDropboxServiceIntegration(unittest.TestCase):
    """Test integration between search and link generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_auth_handler = Mock()
        self.mock_config_manager = Mock()
        self.service = DropboxService(
            auth_handler=self.mock_auth_handler, config_manager=self.mock_config_manager
        )
        self.service._client = Mock()  # Set as authenticated

    @patch("src.integrations.dropbox.service.logger")
    def test_end_to_end_search_and_link_generation(self, mock_logger):
        """Test complete workflow from search to link generation."""
        # Setup the complete chain
        self.mock_config_manager.get_search_path_for_lease.return_value = (
            "/Federal/NMLC 123456/"
        )

        # Mock metadata response for exact path search
        mock_metadata = Mock()
        mock_metadata.tag = "folder"
        self.service._client.files_get_metadata.return_value = mock_metadata

        # Mock no existing shared links
        mock_shared_links = Mock()
        mock_shared_links.links = []
        self.service._client.sharing_list_shared_links.return_value = mock_shared_links

        # Mock successful link creation
        mock_shared_link = Mock()
        mock_shared_link.url = "https://dropbox.com/s/abc123/NMLC%20123456"
        self.service._client.sharing_create_shared_link.return_value = mock_shared_link

        # Execute the search
        result = self.service.search_directory("NMLC 123456", "Federal")

        # Verify the complete chain worked
        self.assertEqual(result, "https://dropbox.com/s/abc123/NMLC%20123456")

        # Verify calls were made in the right order
        self.mock_config_manager.get_search_path_for_lease.assert_called_with(
            "Federal", "NMLC 123456"
        )
        self.service._client.files_get_metadata.assert_called_with(
            "/Federal/NMLC 123456"
        )
        self.service._client.sharing_list_shared_links.assert_called_with(
            path="/Federal/NMLC 123456", direct_only=True
        )
        self.service._client.sharing_create_shared_link.assert_called_with(
            path="/Federal/NMLC 123456"
        )


if __name__ == "__main__":
    # Configure logging for tests
    logging.basicConfig(level=logging.DEBUG)

    # Run the tests
    unittest.main(verbosity=2)
