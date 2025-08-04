"""
Simplified Dropbox Service - Pure API Wrapper

Removes all business logic and serves as a pure API wrapper.
Business logic is handled by the workflow layer.

CRITICAL DROPBOX API QUIRKS:
- Workspace paths work for listing but fail for sharing (need file IDs)
- Regular user tokens have limited sharing permissions  
- Business workspaces require namespace clients for some operations
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import dropbox
from dropbox.common import PathRoot

logger = logging.getLogger(__name__)


class DropboxServiceInterface(ABC):
    """Abstract interface for Dropbox service implementations."""

    @abstractmethod
    def authenticate(self) -> bool: pass

    @abstractmethod
    def is_authenticated(self) -> bool: pass

    @abstractmethod
    def search_directory(self, directory_path: str) -> Optional[str]: pass

    @abstractmethod
    def search_directory_with_metadata(self, directory_path: str) -> Dict[str, Optional[str]]: pass

    @abstractmethod
    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def get_shareable_link(self, path: str, public: bool = True) -> Optional[str]: pass


class DropboxServiceError(Exception): pass
class DropboxAuthenticationError(DropboxServiceError): pass
class DropboxSearchError(DropboxServiceError): pass


class DropboxService(DropboxServiceInterface):
    """
    Simplified Dropbox service - pure API wrapper with essential workspace support.
    
    Service layer = dumb API wrapper (no business logic)
    Workflow layer = handles business logic, path construction
    
    Key Dropbox API Limitations:
    - Sharing APIs require file IDs for workspace paths (not direct paths)
    - Workspace namespacing needed for some operations
    - Regular user auth has limited sharing permissions
    """

    def __init__(self, auth_handler):
        self._auth_handler = auth_handler
        self._client = None

    def authenticate(self) -> bool:
        try:
            if not self._auth_handler:
                raise DropboxAuthenticationError("No authentication handler provided")

            if self._auth_handler.is_authenticated():
                self._client = self._auth_handler.get_client()
                return True

            self._client = self._auth_handler.authenticate()
            return self._client is not None

        except Exception as e:
            raise DropboxAuthenticationError(f"Authentication failed: {str(e)}")

    def is_authenticated(self) -> bool:
        return self._client is not None

    def search_directory(self, directory_path: str) -> Optional[str]:
        """Search for directory by full path and return shareable link."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            found_path = self._find_directory(directory_path)
            return self._create_shareable_link(found_path) if found_path else None
        except Exception as e:
            raise DropboxSearchError(f"Failed to search directory: {str(e)}")

    def search_directory_with_metadata(self, directory_path: str) -> Dict[str, Optional[str]]:
        """Search for directory by path and return both path and shareable link."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            found_path = self._find_directory(directory_path)
            
            if found_path:
                shareable_link = None
                try:
                    shareable_link = self._create_shareable_link(found_path)
                except Exception:
                    pass  # Ignore sharing failures (workspace restrictions)
                
                return {"path": found_path, "shareable_link": shareable_link}
            
            return {"path": None, "shareable_link": None}

        except Exception as e:
            raise DropboxSearchError(f"Failed to search directory: {str(e)}")

    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """List all files in a directory."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            return self._list_files(directory_path)
        except Exception as e:
            raise DropboxSearchError(f"Failed to list files: {str(e)}")

    def get_shareable_link(self, path: str, public: bool = True) -> Optional[str]:
        """
        Generate shareable link for path. 
        
        Args:
            path: File/folder path
            public: If True, creates public link (anyone with link). If False, creates team-only link.
        
        CRITICAL: Workspace paths require file IDs for sharing (not direct paths).
        """
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        try:
            file_metadata = self._get_file_metadata(path)
            if not file_metadata or not hasattr(file_metadata, 'id'):
                return None

            file_id = file_metadata.id
            
            # Check for existing shared link first
            try:
                links = self._client.sharing_list_shared_links(path=file_id, direct_only=True)
                if links.links:
                    return links.links[0].url
            except:
                pass
            
            # Create shareable link with specified visibility
            if public:
                # Public link (anyone with link can access - works outside business)
                settings = dropbox.sharing.SharedLinkSettings(allow_download=True)
            else:
                # Team-only link (only team members can access)
                settings = dropbox.sharing.SharedLinkSettings(
                    requested_visibility=dropbox.sharing.RequestedVisibility.team_only,
                    allow_download=True
                )
            
            result = self._client.sharing_create_shared_link_with_settings(file_id, settings)
            return result.url
        except Exception:
            return None

    # ==========================================
    # CONSOLIDATED PRIVATE HELPER METHODS  
    # ==========================================

    def _find_directory(self, path: str) -> Optional[str]:
        """Find directory by path - handles workspace namespacing."""
        try:
            # Workspace paths need special namespace handling
            if "workspace" in path.lower():
                workspace_name = self._extract_workspace_name(path)
                if workspace_name:
                    return self._search_workspace_path(path, workspace_name)
            
            # Regular path search
            try:
                result = self._client.files_get_metadata(path)
                return path if isinstance(result, dropbox.files.FolderMetadata) else None
            except:
                return None
        except:
            return None

    def _create_shareable_link(self, path: str, public: bool = True) -> Optional[str]:
        """Create shareable link using get_shareable_link."""
        return self.get_shareable_link(path, public)

    def _list_files(self, path: str) -> List[Dict[str, Any]]:
        """List files in directory - handles workspace namespacing."""
        try:
            # Workspace paths need special handling
            if "workspace" in path.lower():
                workspace_name = self._extract_workspace_name(path)
                if workspace_name:
                    return self._list_workspace_files(path, workspace_name)
            
            # Regular directory listing
            result = self._client.files_list_folder(path)
            files = []
            for entry in result.entries:
                files.append({
                    'name': entry.name,
                    'path': f"{path.rstrip('/')}/{entry.name}",
                    'type': 'folder' if isinstance(entry, dropbox.files.FolderMetadata) else 'file',
                    'size': getattr(entry, 'size', 0) if hasattr(entry, 'size') else 0
                })
            return files
        except:
            return []

    def _extract_workspace_name(self, path: str) -> Optional[str]:
        """Extract workspace name from path."""
        try:
            parts = path.strip("/").split("/")
            return parts[0] if parts and "workspace" in parts[0].lower() else None
        except:
            return None

    def _search_workspace_path(self, full_path: str, workspace_name: str) -> Optional[str]:
        """Search within workspace namespace."""
        try:
            namespace_id = self._get_workspace_namespace_id(workspace_name)
            if not namespace_id:
                return None
            
            workspace_client = self._client.with_path_root(PathRoot.namespace_id(namespace_id))
            relative_path = "/".join(full_path.strip("/").split("/")[1:])
            
            try:
                result = workspace_client.files_get_metadata(f"/{relative_path}")
                return full_path if isinstance(result, dropbox.files.FolderMetadata) else None
            except:
                return None
        except:
            return None

    def _list_workspace_files(self, full_path: str, workspace_name: str) -> List[Dict[str, Any]]:
        """List files within workspace namespace."""
        try:
            namespace_id = self._get_workspace_namespace_id(workspace_name)
            if not namespace_id:
                return []
            
            workspace_client = self._client.with_path_root(PathRoot.namespace_id(namespace_id))
            relative_path = "/".join(full_path.strip("/").split("/")[1:])
            
            result = workspace_client.files_list_folder(f"/{relative_path}")
            files = []
            for entry in result.entries:
                files.append({
                    'name': entry.name,
                    'path': f"{full_path.rstrip('/')}/{entry.name}",
                    'type': 'folder' if isinstance(entry, dropbox.files.FolderMetadata) else 'file',
                    'size': getattr(entry, 'size', 0) if hasattr(entry, 'size') else 0
                })
            return files
        except:
            return []

    def _get_file_metadata(self, path: str):
        """Get file metadata including ID for sharing."""
        try:
            if "workspace" in path.lower():
                workspace_name = self._extract_workspace_name(path)
                if workspace_name:
                    return self._get_workspace_metadata(path, workspace_name)
            return self._client.files_get_metadata(path)
        except:
            return None

    def _get_workspace_metadata(self, full_path: str, workspace_name: str):
        """Get metadata within workspace namespace."""
        try:
            namespace_id = self._get_workspace_namespace_id(workspace_name)
            if not namespace_id:
                return None
            
            workspace_client = self._client.with_path_root(PathRoot.namespace_id(namespace_id))
            relative_path = "/".join(full_path.strip("/").split("/")[1:])
            return workspace_client.files_get_metadata(f"/{relative_path}")
        except:
            return None

    def _get_workspace_namespace_id(self, workspace_name: str) -> Optional[str]:
        """Get namespace ID for workspace."""
        try:
            shared_folders = self._client.sharing_list_folders().entries
            for folder in shared_folders:
                if hasattr(folder, 'name') and folder.name == workspace_name:
                    return folder.shared_folder_id
            return None
        except:
            return None