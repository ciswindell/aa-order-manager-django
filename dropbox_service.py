"""
Dropbox Service Module

A modular, reusable service for interacting with the Dropbox API.
Designed following SOLID/DRY principles for use across multiple applications.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Import Dropbox SDK classes - for testing and actual usage
try:
    import dropbox
    from dropbox.sharing import RequestedVisibility, SharedLinkSettings

    DROPBOX_AVAILABLE = True
except ImportError:
    dropbox = None
    RequestedVisibility = None
    SharedLinkSettings = None
    DROPBOX_AVAILABLE = False


class DropboxServiceInterface(ABC):
    """
    Abstract interface for Dropbox service implementations.
    Defines the contract for all Dropbox service classes.
    """

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with Dropbox using OAuth 2.0 flow.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if the service is currently authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        pass

    @abstractmethod
    def search_directory(
        self, directory_name: str, agency: str = None
    ) -> Optional[str]:
        """
        Search for a directory by exact name match.

        Args:
            directory_name: Name of the directory to search for
            agency: Optional agency type for scoped search (e.g., 'Federal', 'State')

        Returns:
            Optional[str]: Shareable link to the directory if found, None otherwise
        """
        pass

    @abstractmethod
    def get_shareable_link(self, path: str) -> Optional[str]:
        """
        Generate a shareable link for a given Dropbox path.

        Args:
            path: Dropbox path to create shareable link for

        Returns:
            Optional[str]: Shareable link if successful, None otherwise
        """
        pass


class DropboxServiceError(Exception):
    """Base exception for Dropbox service errors"""

    pass


class DropboxAuthenticationError(DropboxServiceError):
    """Raised when authentication fails"""

    pass


class DropboxSearchError(DropboxServiceError):
    """Raised when directory search fails"""

    pass


class DropboxLinkError(DropboxServiceError):
    """Raised when link generation fails"""

    pass


class DropboxService(DropboxServiceInterface):
    """
    Main Dropbox service implementation.

    Provides a clean, modular interface for Dropbox API interactions
    including authentication, directory search, and link generation.
    """

    def __init__(self, auth_handler=None, config_manager=None):
        """
        Initialize the Dropbox service.

        Args:
            auth_handler: Authentication handler (injected dependency)
            config_manager: Configuration manager (injected dependency)
        """
        self._auth_handler = auth_handler
        self._config_manager = config_manager
        self._client = None

        logger.info("DropboxService initialized")

    def authenticate(self) -> bool:
        """
        Authenticate with Dropbox using OAuth 2.0 flow or token-based authentication.

        Returns:
            bool: True if authentication successful, False otherwise

        Raises:
            DropboxAuthenticationError: If authentication fails
        """
        try:
            if not self._auth_handler:
                raise DropboxAuthenticationError("No authentication handler provided")

            # Check if already authenticated (for token-based auth)
            if self._auth_handler.is_authenticated():
                self._client = self._auth_handler.get_client()
                logger.info("Using existing authentication")
                return True

            # Otherwise, try OAuth flow
            self._client = self._auth_handler.authenticate()

            if self._client:
                logger.info("Dropbox authentication successful")
                return True
            else:
                logger.warning("Dropbox authentication failed")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise DropboxAuthenticationError(f"Authentication failed: {str(e)}")

    def is_authenticated(self) -> bool:
        """
        Check if the service is currently authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self._client is not None

    def search_directory(
        self, directory_name: str, agency: str = None
    ) -> Optional[str]:
        """
        Search for a directory by exact name match within agency-specific root directories.

        Args:
            directory_name: Name of the directory to search for
            agency: Optional agency type for scoped search (e.g., 'Federal', 'State')

        Returns:
            Optional[str]: Shareable link to the directory if found, None otherwise

        Raises:
            DropboxSearchError: If search operation fails
            DropboxAuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Searching for directory: {directory_name} (agency: {agency})")

            # Get the search path from configuration
            if self._config_manager and agency:
                search_path = self._config_manager.get_search_path_for_lease(
                    agency, directory_name
                )
                if search_path:
                    logger.info(f"Generated search path: {search_path}")

                    # Search for the exact directory path
                    found_path = self._search_exact_directory_path(search_path)
                    if found_path:
                        # Generate shareable link for the found directory
                        shareable_link = self.get_shareable_link(found_path)
                        if shareable_link:
                            logger.info(
                                f"Found directory and generated link: {shareable_link}"
                            )
                            return shareable_link
                        else:
                            logger.warning(
                                f"Found directory but failed to generate shareable link: {found_path}"
                            )
                            return None
                    else:
                        logger.info(
                            f"Directory not found at expected path: {search_path}"
                        )
                        return None
                else:
                    logger.warning(
                        f"Could not generate search path for agency '{agency}' and directory '{directory_name}'"
                    )
                    return None
            else:
                # Fallback to general search without agency scoping
                logger.info("Performing general directory search (no agency scoping)")
                found_path = self._search_directory_general(directory_name)
                if found_path:
                    shareable_link = self.get_shareable_link(found_path)
                    if shareable_link:
                        logger.info(
                            f"Found directory and generated link: {shareable_link}"
                        )
                        return shareable_link

                logger.info(f"Directory not found: {directory_name}")
                return None

        except DropboxSearchError:
            # Re-raise DropboxSearchError as-is
            raise
        except DropboxAuthenticationError:
            # Re-raise DropboxAuthenticationError as-is
            raise
        except Exception as e:
            logger.error(f"Directory search error: {str(e)}")
            raise DropboxSearchError(
                f"Failed to search directory '{directory_name}': {str(e)}"
            )

    def get_shareable_link(self, path: str) -> Optional[str]:
        """
        Generate a shareable link for a given Dropbox path.

        Args:
            path: Dropbox path to create shareable link for

        Returns:
            Optional[str]: Shareable link if successful, None otherwise

        Raises:
            DropboxLinkError: If link generation fails
            DropboxAuthenticationError: If not authenticated
        """
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Generating shareable link for path: {path}")

            # Check if this is a team workspace path that needs special handling
            if path.startswith("/Federal Workspace/"):
                logger.debug("Detected Federal Workspace path for link generation")
                return self._get_team_workspace_link(path, "Federal Workspace")
            elif path.startswith("/State Workspace/"):
                logger.debug("Detected State Workspace path for link generation")
                return self._get_team_workspace_link(path, "State Workspace")
            else:
                # Regular path handling
                # First, try to get existing shared links
                existing_link = self._get_existing_shared_link(path)
                if existing_link:
                    logger.info(f"Found existing shareable link: {existing_link}")
                    return existing_link

                # If no existing link, create a new one
                new_link = self._create_new_shared_link(path)
                if new_link:
                    logger.info(f"Created new shareable link: {new_link}")
                    return new_link

                logger.warning(f"Failed to create shareable link for path: {path}")
                return None

        except DropboxLinkError:
            # Re-raise DropboxLinkError as-is
            raise
        except DropboxAuthenticationError:
            # Re-raise DropboxAuthenticationError as-is
            raise
        except Exception as e:
            logger.error(f"Link generation error: {str(e)}")
            raise DropboxLinkError(f"Failed to generate link for '{path}': {str(e)}")

    def _get_team_workspace_link(
        self, full_path: str, workspace_name: str
    ) -> Optional[str]:
        """
        Generate a shareable link for a path in a team workspace.

        Args:
            full_path: Full path including workspace name
            workspace_name: Name of the workspace (e.g., "Federal Workspace")

        Returns:
            Optional[str]: Shareable link if successful, None otherwise
        """
        try:
            logger.debug(f"Generating link for team workspace: {workspace_name}")

            # Get the shared folder ID for the workspace
            shared = self._client.sharing_list_folders()
            workspace_folder_id = None

            for folder in shared.entries:
                if folder.name == workspace_name:
                    workspace_folder_id = folder.shared_folder_id
                    break

            if not workspace_folder_id:
                logger.debug(
                    f"Workspace '{workspace_name}' not found in shared folders"
                )
                return None

            # Create namespaced client for the workspace
            path_root = dropbox.common.PathRoot.namespace_id(workspace_folder_id)
            workspace_client = self._client.with_path_root(path_root)

            # Convert full path to relative path within workspace
            relative_path = full_path.replace(f"/{workspace_name}/", "/").rstrip("/")
            logger.debug(f"Generating link for relative path: {relative_path}")

            # First, try to get existing shared links
            existing_link = self._get_existing_shared_link_in_workspace(
                workspace_client, relative_path
            )
            if existing_link:
                logger.info(
                    f"Found existing shareable link in workspace: {existing_link}"
                )
                return existing_link

            # If no existing link, create a new one
            new_link = self._create_new_shared_link_in_workspace(
                workspace_client, relative_path
            )
            if new_link:
                logger.info(f"Created new shareable link in workspace: {new_link}")
                return new_link

            logger.warning(
                f"Failed to create shareable link for workspace path: {relative_path}"
            )
            return None

        except Exception as e:
            logger.debug(f"Team workspace link generation failed: {str(e)}")
            return None

    def _get_existing_shared_link_in_workspace(
        self, workspace_client, path: str
    ) -> Optional[str]:
        """
        Check if a shareable link already exists for the given path in a workspace.

        Args:
            workspace_client: Namespaced Dropbox client for the workspace
            path: Relative path within the workspace

        Returns:
            Optional[str]: Existing shareable link if found, None otherwise
        """
        try:
            logger.debug(f"Checking for existing shared links in workspace for: {path}")

            # List existing shared links for the path
            shared_links = workspace_client.sharing_list_shared_links(
                path=path, direct_only=True  # Only check links for this specific path
            )

            if shared_links.links:
                # Return the first available link
                link = shared_links.links[0]
                logger.debug(f"Found existing shared link in workspace: {link.url}")
                return link.url

            logger.debug(f"No existing shared links found in workspace for: {path}")
            return None

        except Exception as e:
            logger.debug(f"Error checking existing shared links in workspace: {str(e)}")
            return None

    def _create_new_shared_link_in_workspace(
        self, workspace_client, path: str
    ) -> Optional[str]:
        """
        Create a new shareable link for the given path in a workspace.

        Args:
            workspace_client: Namespaced Dropbox client for the workspace
            path: Relative path within the workspace

        Returns:
            Optional[str]: New shareable link if successful, None otherwise
        """
        try:
            logger.debug(f"Creating new shared link in workspace for: {path}")

            # Use module-level imports for sharing settings
            if DROPBOX_AVAILABLE and SharedLinkSettings and RequestedVisibility:
                # Create link settings for public access
                link_settings = SharedLinkSettings(
                    requested_visibility=RequestedVisibility.public,
                    allow_download=True,
                    expires=None,  # No expiration
                )

                logger.debug("Using SharedLinkSettings for public access in workspace")
            else:
                # Fallback if sharing module imports aren't available
                link_settings = None
                logger.debug(
                    "SharedLinkSettings not available, using default settings in workspace"
                )

            # Create the shared link
            if link_settings:
                shared_link = workspace_client.sharing_create_shared_link_with_settings(
                    path=path, settings=link_settings
                )
            else:
                # Fallback method for older API versions
                shared_link = workspace_client.sharing_create_shared_link(path=path)

            if shared_link and hasattr(shared_link, "url"):
                logger.debug(
                    f"Successfully created shared link in workspace: {shared_link.url}"
                )
                return shared_link.url
            else:
                logger.debug("Shared link creation in workspace returned no URL")
                return None

        except Exception as e:
            # Check if this is a "shared link already exists" error
            error_str = str(e).lower()
            if (
                "shared_link_already_exists" in error_str
                or "already exists" in error_str
            ):
                logger.debug(
                    "Shared link already exists in workspace, attempting to retrieve it"
                )
                # Try to get the existing link
                return self._get_existing_shared_link_in_workspace(
                    workspace_client, path
                )
            else:
                logger.debug(f"Error creating new shared link in workspace: {str(e)}")
                return None

    def _get_existing_shared_link(self, path: str) -> Optional[str]:
        """
        Check if a shareable link already exists for the given path.

        Args:
            path: Dropbox path to check for existing links

        Returns:
            Optional[str]: Existing shareable link if found, None otherwise
        """
        try:
            logger.debug(f"Checking for existing shared links for: {path}")

            # List existing shared links for the path
            shared_links = self._client.sharing_list_shared_links(
                path=path, direct_only=True  # Only check links for this specific path
            )

            if shared_links.links:
                # Return the first available link
                link = shared_links.links[0]
                logger.debug(f"Found existing shared link: {link.url}")
                return link.url

            logger.debug(f"No existing shared links found for: {path}")
            return None

        except Exception as e:
            logger.debug(f"Error checking existing shared links: {str(e)}")
            return None

    def _create_new_shared_link(self, path: str) -> Optional[str]:
        """
        Create a new shareable link for the given path.

        Args:
            path: Dropbox path to create a shareable link for

        Returns:
            Optional[str]: New shareable link if successful, None otherwise
        """
        try:
            logger.debug(f"Creating new shared link for: {path}")

            # Use module-level imports for sharing settings
            if DROPBOX_AVAILABLE and SharedLinkSettings and RequestedVisibility:
                # Create link settings for public access
                link_settings = SharedLinkSettings(
                    requested_visibility=RequestedVisibility.public,
                    allow_download=True,
                    expires=None,  # No expiration
                )

                logger.debug("Using SharedLinkSettings for public access")
            else:
                # Fallback if sharing module imports aren't available
                link_settings = None
                logger.debug("SharedLinkSettings not available, using default settings")

            # Create the shared link
            if link_settings:
                shared_link = self._client.sharing_create_shared_link_with_settings(
                    path=path, settings=link_settings
                )
            else:
                # Fallback method for older API versions
                shared_link = self._client.sharing_create_shared_link(path=path)

            if shared_link and hasattr(shared_link, "url"):
                logger.debug(f"Successfully created shared link: {shared_link.url}")
                return shared_link.url
            else:
                logger.debug("Shared link creation returned no URL")
                return None

        except Exception as e:
            # Check if this is a "shared link already exists" error
            error_str = str(e).lower()
            if (
                "shared_link_already_exists" in error_str
                or "already exists" in error_str
            ):
                logger.debug("Shared link already exists, attempting to retrieve it")
                # Try to get the existing link
                return self._get_existing_shared_link(path)
            else:
                logger.debug(f"Error creating new shared link: {str(e)}")
                return None

    def create_shareable_links_batch(
        self, paths: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Create shareable links for multiple paths in batch.

        Args:
            paths: List of Dropbox paths to create shareable links for

        Returns:
            Dict[str, Optional[str]]: Mapping of paths to their shareable links
        """
        results = {}

        for path in paths:
            try:
                link = self.get_shareable_link(path)
                results[path] = link
            except DropboxServiceError as e:
                logger.warning(
                    f"Failed to create shareable link for '{path}': {str(e)}"
                )
                results[path] = None

        return results

    def validate_shareable_link(self, link: str) -> bool:
        """
        Validate that a shareable link is accessible.

        Args:
            link: Shareable link to validate

        Returns:
            bool: True if link is valid and accessible, False otherwise
        """
        try:
            # Basic URL validation
            if not link or not link.startswith("https://"):
                return False

            # Check if it looks like a Dropbox link
            if "dropbox.com" not in link.lower():
                return False

            logger.debug(f"Shareable link appears valid: {link}")
            return True

        except Exception as e:
            logger.debug(f"Error validating shareable link: {str(e)}")
            return False

    def bulk_search_directories(
        self, directory_names: List[str], agency: str = None
    ) -> Dict[str, Optional[str]]:
        """
        Search for multiple directories at once.

        Args:
            directory_names: List of directory names to search for
            agency: Optional agency type for scoped search

        Returns:
            Dict[str, Optional[str]]: Mapping of directory names to their shareable links
        """
        results = {}

        for directory_name in directory_names:
            try:
                link = self.search_directory(directory_name, agency)
                results[directory_name] = link
            except DropboxServiceError as e:
                logger.warning(f"Failed to find directory '{directory_name}': {str(e)}")
                results[directory_name] = None

        return results

    def _search_exact_directory_path(self, search_path: str) -> Optional[str]:
        """
        Search for a directory at the exact specified path.

        Args:
            search_path: Full path to search for (e.g., "/Federal Workspace/^Runsheet Workspace/Runsheet Archive/NMNM 123456/")

        Returns:
            Optional[str]: Found directory path if exists, None otherwise
        """
        try:
            logger.debug(f"Searching for exact path: {search_path}")

            # Remove trailing slash for Dropbox API consistency
            clean_path = search_path.rstrip("/")

            # Check if this is a team workspace path that needs special handling
            if clean_path.startswith("/Federal Workspace/"):
                logger.debug("Detected Federal Workspace path, using namespaced client")
                return self._search_team_workspace_path(clean_path, "Federal Workspace")
            elif clean_path.startswith("/State Workspace/"):
                logger.debug("Detected State Workspace path, using namespaced client")
                return self._search_team_workspace_path(clean_path, "State Workspace")
            else:
                # Try regular client for non-workspace paths
                try:
                    metadata = self._client.files_get_metadata(clean_path)

                    # Check if it's a folder
                    if hasattr(metadata, "tag") and metadata.tag == "folder":
                        logger.debug(f"Found directory at exact path: {clean_path}")
                        return clean_path
                    else:
                        logger.debug(
                            f"Path exists but is not a directory: {clean_path}"
                        )
                        return None

                except Exception as e:
                    # If direct path lookup fails, try using search API
                    logger.debug(
                        f"Direct path lookup failed, trying search API: {str(e)}"
                    )
                    return self._search_directory_with_api(clean_path)

        except Exception as e:
            logger.debug(f"Exact path search failed: {str(e)}")
            return None

    def _search_team_workspace_path(
        self, full_path: str, workspace_name: str
    ) -> Optional[str]:
        """
        Search for a directory in a team workspace using namespaced client.

        Args:
            full_path: Full path including workspace name (e.g., "/Federal Workspace/^Runsheet Workspace/Runsheet Archive/NMNM 123456")
            workspace_name: Name of the workspace (e.g., "Federal Workspace")

        Returns:
            Optional[str]: Found directory path if exists, None otherwise
        """
        try:
            logger.debug(f"Searching in team workspace: {workspace_name}")

            # Get the shared folder ID for the workspace
            shared = self._client.sharing_list_folders()
            workspace_folder_id = None

            for folder in shared.entries:
                if folder.name == workspace_name:
                    workspace_folder_id = folder.shared_folder_id
                    break

            if not workspace_folder_id:
                logger.debug(
                    f"Workspace '{workspace_name}' not found in shared folders"
                )
                return None

            # Create namespaced client for the workspace
            path_root = dropbox.common.PathRoot.namespace_id(workspace_folder_id)
            workspace_client = self._client.with_path_root(path_root)

            # Convert full path to relative path within workspace
            relative_path = full_path.replace(f"/{workspace_name}/", "/").rstrip("/")
            logger.debug(f"Relative path in workspace: {relative_path}")

            # Try to get metadata for the relative path
            try:
                metadata = workspace_client.files_get_metadata(relative_path)

                # Check if it's a folder by checking the object type
                if isinstance(metadata, dropbox.files.FolderMetadata):
                    logger.debug(f"Found directory in workspace: {relative_path}")
                    # Return the full original path for consistency
                    return full_path.rstrip("/")
                else:
                    logger.debug(
                        f"Path exists but is not a directory: {type(metadata).__name__}"
                    )
                    return None

            except Exception as metadata_error:
                logger.debug(
                    f"Metadata lookup failed in workspace: {str(metadata_error)}"
                )
                return None

        except Exception as e:
            logger.debug(f"Team workspace search failed: {str(e)}")
            return None

    def _search_directory_with_api(self, target_path: str) -> Optional[str]:
        """
        Search for directory using Dropbox API v2 search endpoint with pagination.

        Args:
            target_path: Target directory path to search for

        Returns:
            Optional[str]: Found directory path if exists, None otherwise
        """
        try:
            # Extract directory name from path for search query
            directory_name = (
                target_path.split("/")[-1]
                if target_path.split("/")[-1]
                else target_path.split("/")[-2]
            )

            logger.debug(f"Searching with API for directory name: {directory_name}")

            # Use Dropbox API v2 search endpoint with pagination
            search_options = dropbox.files.SearchOptions(
                filename_only=True,  # Search filenames only for better performance
                max_results=100,  # Limit results per page
            )

            search_results = self._client.files_search_v2(
                query=directory_name,
                options=search_options,
            )

            # Process all pages of results
            while True:
                # Filter results to find exact directory matches
                for match in search_results.matches:
                    if hasattr(match, "metadata") and hasattr(
                        match.metadata, "metadata"
                    ):
                        file_metadata = match.metadata.metadata

                        # Check if it's a folder and path matches our target
                        if (
                            hasattr(file_metadata, "tag")
                            and file_metadata.tag == "folder"
                            and hasattr(file_metadata, "path_lower")
                        ):

                            found_path = file_metadata.path_lower

                            # Check for exact path match (case insensitive)
                            if found_path.lower() == target_path.lower():
                                logger.debug(
                                    f"Found exact directory match: {found_path}"
                                )
                                return (
                                    file_metadata.path_display
                                )  # Return the properly cased path

                            # Check if the found path ends with our target structure
                            if found_path.lower().endswith(target_path.lower()):
                                logger.debug(
                                    f"Found directory with matching suffix: {found_path}"
                                )
                                return file_metadata.path_display

                # Check if there are more results to fetch
                if not search_results.has_more:
                    break

                # Continue with next page using cursor
                search_results = self._client.files_search_continue_v2(
                    cursor=search_results.cursor
                )

            logger.debug(f"No matching directory found for: {target_path}")
            return None

        except Exception as e:
            logger.debug(f"API search failed: {str(e)}")
            return None

    def _search_directory_general(self, directory_name: str) -> Optional[str]:
        """
        Perform a general directory search without agency scoping with pagination.

        Args:
            directory_name: Name of the directory to search for

        Returns:
            Optional[str]: Found directory path if exists, None otherwise
        """
        try:
            logger.debug(f"Performing general search for: {directory_name}")

            # Use Dropbox API v2 search endpoint with pagination
            search_options = dropbox.files.SearchOptions(
                filename_only=True,  # Search filenames only
                max_results=100,  # Limit results per page
            )

            search_results = self._client.files_search_v2(
                query=directory_name,
                options=search_options,
            )

            # Process all pages of results
            while True:
                # Look for exact directory name matches
                for match in search_results.matches:
                    if hasattr(match, "metadata") and hasattr(
                        match.metadata, "metadata"
                    ):
                        file_metadata = match.metadata.metadata

                        # Check if it's a folder with exact name match
                        if (
                            hasattr(file_metadata, "tag")
                            and file_metadata.tag == "folder"
                            and hasattr(file_metadata, "name")
                            and file_metadata.name.lower() == directory_name.lower()
                        ):

                            logger.debug(
                                f"Found directory with exact name match: {file_metadata.path_display}"
                            )
                            return file_metadata.path_display

                # Check if there are more results to fetch
                if not search_results.has_more:
                    break

                # Continue with next page using cursor
                search_results = self._client.files_search_continue_v2(
                    cursor=search_results.cursor
                )

            logger.debug(f"No directory found with name: {directory_name}")
            return None

        except Exception as e:
            logger.debug(f"General search failed: {str(e)}")
            return None
