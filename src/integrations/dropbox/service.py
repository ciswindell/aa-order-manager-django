"""
Clean Dropbox Service - Minimal with Essential Workspace Support

Only includes the absolute minimum needed for workspace paths to work.
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
    def get_directory_link(self, directory_path: str) -> Optional[str]: pass

    @abstractmethod
    def get_directory_details(self, directory_path: str) -> Dict[str, Optional[str]]: pass

    @abstractmethod
    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def get_shareable_link(self, path: str, public: bool = True) -> Optional[str]: pass


class DropboxServiceError(Exception): pass
class DropboxAuthenticationError(DropboxServiceError): pass
class DropboxSearchError(DropboxServiceError): pass


class DropboxService(DropboxServiceInterface):
    """Clean Dropbox service - minimal complexity with essential workspace support."""

    def __init__(self, auth_handler):
        self._auth_handler = auth_handler
        self._client = None

    def authenticate(self) -> bool:
        if not self._auth_handler:
            raise DropboxAuthenticationError("No authentication handler provided")

        if self._auth_handler.is_authenticated():
            self._client = self._auth_handler.get_client()
            return True

        self._client = self._auth_handler.authenticate()
        return self._client is not None

    def is_authenticated(self) -> bool:
        return self._client is not None

    def get_directory_link(self, directory_path: str) -> Optional[str]:
        """Get shareable link for directory."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        found_path = self._find_directory(directory_path)
        return self.get_shareable_link(found_path) if found_path else None

    def get_directory_details(self, directory_path: str) -> Dict[str, Optional[str]]:
        """Get directory path and shareable link."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        found_path = self._find_directory(directory_path)
        
        if found_path:
            shareable_link = self.get_shareable_link(found_path)
            return {"path": found_path, "shareable_link": shareable_link}
        
        return {"path": None, "shareable_link": None}

    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """List files in directory."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        return self._list_files(directory_path)

    def get_shareable_link(self, path: str, public: bool = True) -> Optional[str]:
        """Generate shareable link for path."""
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")

        # Get file metadata (includes ID needed for sharing)
        file_metadata = self._get_file_metadata(path)
        if not file_metadata or not hasattr(file_metadata, 'id'):
            return None

        file_id = file_metadata.id
        
        # Check for existing link first
        links = self._client.sharing_list_shared_links(path=file_id, direct_only=True)
        if links.links:
            return links.links[0].url
        
        # Create new link
        if public:
            settings = dropbox.sharing.SharedLinkSettings(allow_download=True)
        else:
            settings = dropbox.sharing.SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.team_only,
                allow_download=True
            )
        
        result = self._client.sharing_create_shared_link_with_settings(file_id, settings)
        return result.url

    # ==========================================
    # MINIMAL HELPERS WITH ESSENTIAL WORKSPACE SUPPORT
    # ==========================================

    def _find_directory(self, path: str) -> Optional[str]:
        """Find directory - handles workspace paths if needed."""
        # Try direct path first (works for non-workspace paths)
        try:
            result = self._client.files_get_metadata(path)
            if isinstance(result, dropbox.files.FolderMetadata):
                return path
        except:
            pass
        
        # If direct path fails and it's a workspace path, try workspace client
        if "workspace" in path.lower():
            client = self._get_workspace_client(path)
            if client:
                relative_path = self._get_relative_path(path)
                try:
                    result = client.files_get_metadata(relative_path)
                    if isinstance(result, dropbox.files.FolderMetadata):
                        return path  # Return original path
                except:
                    pass
        
        return None

    def _list_files(self, path: str) -> List[Dict[str, Any]]:
        """List files in directory."""
        # Try direct listing first
        try:
            result = self._client.files_list_folder(path)
        except:
            # If direct fails and it's workspace, try workspace client
            if "workspace" in path.lower():
                client = self._get_workspace_client(path)
                if client:
                    relative_path = self._get_relative_path(path)
                    result = client.files_list_folder(relative_path)
                else:
                    return []
            else:
                return []
        
        files = []
        for entry in result.entries:
            files.append({
                'name': entry.name,
                'path': f"{path.rstrip('/')}/{entry.name}",
                'type': 'folder' if isinstance(entry, dropbox.files.FolderMetadata) else 'file',
                'size': getattr(entry, 'size', 0) if hasattr(entry, 'size') else 0
            })
        return files

    def _get_file_metadata(self, path: str):
        """Get file metadata including ID for sharing."""
        # Try direct first
        try:
            return self._client.files_get_metadata(path)
        except:
            # If direct fails and it's workspace, try workspace client
            if "workspace" in path.lower():
                client = self._get_workspace_client(path)
                if client:
                    relative_path = self._get_relative_path(path)
                    return client.files_get_metadata(relative_path)
        return None

    def _get_workspace_client(self, path: str):
        """Get workspace-namespaced client for given path."""
        # Extract workspace name (first part of path)
        parts = path.strip("/").split("/")
        if not parts or "workspace" not in parts[0].lower():
            return None
        
        workspace_name = parts[0]
        
        # Find namespace ID for this workspace
        shared_folders = self._client.sharing_list_folders().entries
        for folder in shared_folders:
            if hasattr(folder, 'name') and folder.name == workspace_name:
                namespace_id = folder.shared_folder_id
                return self._client.with_path_root(PathRoot.namespace_id(namespace_id))
        
        return None

    def _get_relative_path(self, path: str) -> str:
        """Convert workspace path to relative path within namespace."""
        # Remove workspace name from path: "/Federal Workspace/folder/file" -> "/folder/file"
        parts = path.strip("/").split("/")
        if len(parts) > 1:
            return "/" + "/".join(parts[1:])
        return "/"