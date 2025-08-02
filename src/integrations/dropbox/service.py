"""
DROPBOX BUSINESS TEAM WORKSPACE SERVICE
=======================================
This service is designed EXCLUSIVELY for Dropbox Business team workspaces.
All methods assume team workspace paths and use namespaced clients.

❌ THESE DON'T WORK (for team workspaces):
- client.files_search_v2() - doesn't search team workspaces
- client.files_get_metadata("/workspace/path") - wrong namespace  
- client.files_list_folder("/workspace/path") - wrong namespace

✅ THIS SERVICE USES (automatically):
1. Get workspace namespace: client.sharing_list_folders()
2. Create namespaced client: client.with_path_root(PathRoot.namespace_id(workspace_id))
3. Use relative paths: workspace_client.files_get_metadata("/relative/path")

Example usage:
    service.search_directory("NMNM 0501759", agency="Federal")
    service.list_directory_files("/Federal Workspace/^Runsheet Workspace/Archive")

All paths must contain a workspace (e.g., "Federal Workspace", "State Workspace").
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Import Dropbox SDK
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
    """Abstract interface for Dropbox service implementations."""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with Dropbox."""
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        pass

    @abstractmethod
    def search_directory(self, directory_name: str, agency: str = None) -> Optional[str]:
        """Search for directory (legacy method)."""
        pass

    @abstractmethod
    def search_directory_with_metadata(self, directory_path: str) -> Dict[str, Optional[str]]:
        """Search for directory by path and return metadata."""
        pass

    @abstractmethod
    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """List files in directory."""
        pass

    @abstractmethod
    def get_shareable_link(self, path: str) -> Optional[str]:
        """Generate shareable link."""
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


class DropboxListError(DropboxServiceError):
    """Raised when file listing fails"""
    pass


class DropboxService(DropboxServiceInterface):
    """Simplified Dropbox service with only essential functionality."""

    def __init__(self, auth_handler=None, config_manager=None):
        self._auth_handler = auth_handler
        self._config_manager = config_manager
        self._client = None
        logger.info("DropboxService initialized")

    def authenticate(self) -> bool:
        """Authenticate with Dropbox."""
        try:
            if not self._auth_handler:
                raise DropboxAuthenticationError("No authentication handler provided")

            if self._auth_handler.is_authenticated():
                self._client = self._auth_handler.get_client()
                logger.info("Using existing authentication")
                return True

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
        """Check if authenticated."""
        return self._client is not None

    def search_directory(self, directory_name: str, agency: str = None) -> Optional[str]:
        """Search for directory (legacy method for processors.py)."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Searching for directory: {directory_name} (agency: {agency})")

            # Use the working method: config manager + team workspace search
            if self._config_manager and agency:
                search_path = self._config_manager.get_search_path_for_lease(agency, directory_name)
                if search_path:
                    logger.info(f"Config generated search path: {search_path}")
                    found_path = self._search_exact_directory_path(search_path)
                    if found_path:
                        return self.get_shareable_link(found_path)

            logger.info(f"Directory not found: {directory_name}")
            return None

        except DropboxAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Directory search error: {str(e)}")
            raise DropboxSearchError(f"Failed to search directory '{directory_name}': {str(e)}")

    def search_directory_with_metadata(self, directory_path: str) -> Dict[str, Optional[str]]:
        """Search for directory by path and return both path and shareable link."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Searching for directory with metadata at path: {directory_path}")
            
            # Extract directory name from path (e.g., "/Federal/NMNM 0501759" -> "NMNM 0501759")
            directory_name = directory_path.rstrip("/").split("/")[-1]
            
            # Extract agency from path (e.g., "/Federal/NMNM 0501759" -> "Federal")  
            agency = None
            if "/" in directory_path.strip("/"):
                agency = directory_path.strip("/").split("/")[0]
            
            # Use the working method: config manager + team workspace search
            if self._config_manager and agency and directory_name:
                search_path = self._config_manager.get_search_path_for_lease(agency, directory_name)
                if search_path:
                    logger.info(f"Config generated search path: {search_path}")
                    found_path = self._search_exact_directory_path(search_path)
                    
                    if found_path:
                        shareable_link = self.get_shareable_link(found_path)
                        logger.info(f"Found directory: {found_path}")
                        return {
                            "path": found_path,
                            "shareable_link": shareable_link
                        }
            
            logger.info(f"Directory not found for path: {directory_path}")
            return {
                "path": None,
                "shareable_link": None
            }

        except DropboxAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Directory search with metadata error: {str(e)}")
            raise DropboxSearchError(f"Failed to search directory at path '{directory_path}': {str(e)}")

    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """List all files in a directory using team workspace namespaced client."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Listing files in directory: {directory_path}")
            
            clean_path = directory_path.rstrip("/")
            workspace_name = self._extract_workspace_name(clean_path)
            
            if not workspace_name:
                raise DropboxListError(f"Path does not contain a workspace: {directory_path}")
            
            return self._list_team_workspace_files(clean_path, workspace_name)

        except DropboxAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Failed to list directory files: {str(e)}")
            raise DropboxListError(f"Could not list files in directory '{directory_path}': {str(e)}")

    def _extract_workspace_name(self, path: str) -> Optional[str]:
        """Extract workspace name from path if it's a workspace path."""
        if not path.startswith("/"):
            return None
        
        # Split path and check if it could be a workspace
        parts = path.strip("/").split("/")
        if len(parts) >= 1:
            # Check if this matches workspace naming pattern (contains "Workspace")
            potential_workspace = parts[0]
            if "Workspace" in potential_workspace:
                return potential_workspace
        
        return None

    def _list_team_workspace_files(self, full_path: str, workspace_name: str) -> List[Dict[str, Any]]:
        """List files in team workspace directory using namespaced client."""
        # Get workspace namespace ID
        shared = self._client.sharing_list_folders()
        workspace_folder_id = None
        
        for folder in shared.entries:
            if folder.name == workspace_name:
                workspace_folder_id = folder.shared_folder_id
                break
        
        if not workspace_folder_id:
            raise DropboxListError(f"Workspace '{workspace_name}' not found")
        
        # Create namespaced client
        path_root = dropbox.common.PathRoot.namespace_id(workspace_folder_id)
        workspace_client = self._client.with_path_root(path_root)
        
        # Convert to relative path within workspace
        relative_path = full_path.replace(f"/{workspace_name}", "")
        if not relative_path:
            relative_path = ""
        
        logger.debug(f"Listing workspace files: {relative_path} (namespace: {workspace_folder_id})")
        
        # List files using namespaced client
        result = workspace_client.files_list_folder(relative_path)
        
        files = []
        for entry in result.entries:
            if hasattr(entry, 'name'):
                file_data = {
                    'name': entry.name,
                    'path': f"{full_path}/{entry.name}",  # Use full workspace path
                    'is_file': hasattr(entry, 'size'),
                }
                if hasattr(entry, 'size'):
                    file_data['size'] = entry.size
                if hasattr(entry, 'client_modified'):
                    file_data['modified'] = entry.client_modified.isoformat()
                
                files.append(file_data)
        
        # Handle pagination
        while result.has_more:
            result = workspace_client.files_list_folder_continue(result.cursor)
            for entry in result.entries:
                if hasattr(entry, 'name'):
                    file_data = {
                        'name': entry.name,
                        'path': f"{full_path}/{entry.name}",
                        'is_file': hasattr(entry, 'size'),
                    }
                    if hasattr(entry, 'size'):
                        file_data['size'] = entry.size
                    if hasattr(entry, 'client_modified'):
                        file_data['modified'] = entry.client_modified.isoformat()
                    
                    files.append(file_data)
        
        logger.info(f"Found {len(files)} files in workspace directory: {full_path}")
        return files

    def get_shareable_link(self, path: str) -> Optional[str]:
        """Generate a shareable link for a path."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            logger.info(f"Generating shareable link for: {path}")
            
            # Try to get existing shared link first
            try:
                links = self._client.sharing_list_shared_links(path=path, direct_only=True)
                if links.links:
                    logger.info("Found existing shareable link")
                    return links.links[0].url
            except:
                pass  # No existing link found, create new one
            
            # Create new shared link
            settings = SharedLinkSettings(
                requested_visibility=RequestedVisibility.public,
                allow_download=True
            )
            link = self._client.sharing_create_shared_link_with_settings(path, settings)
            logger.info("Created new shareable link")
            return link.url

        except Exception as e:
            logger.error(f"Failed to generate shareable link: {str(e)}")
            return None

    def _search_exact_directory_path(self, search_path: str) -> Optional[str]:
        """Search for exact directory path using team workspace namespaced client."""
        try:
            logger.debug(f"Searching for exact path: {search_path}")
            
            # Remove trailing slash for Dropbox API consistency
            clean_path = search_path.rstrip("/")
            
            # Extract workspace name - all paths should be workspace paths
            workspace_name = self._extract_workspace_name(clean_path)
            if not workspace_name:
                logger.debug(f"Path does not contain a workspace: {clean_path}")
                return None
            
            logger.debug(f"Searching in team workspace: {workspace_name}")
            return self._search_team_workspace_path(clean_path, workspace_name)
                    
        except Exception as e:
            logger.debug(f"Exact path search failed: {str(e)}")
            return None

    def _search_team_workspace_path(self, full_path: str, workspace_name: str) -> Optional[str]:
        """Search for a directory in a team workspace using namespaced client."""
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
                logger.debug(f"Workspace '{workspace_name}' not found in shared folders")
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
                    logger.debug(f"Path exists but is not a directory: {type(metadata).__name__}")
                    return None
                    
            except Exception as metadata_error:
                logger.debug(f"Metadata lookup failed in workspace: {str(metadata_error)}")
                return None
                
        except Exception as e:
            logger.debug(f"Team workspace search failed: {str(e)}")
            return None

