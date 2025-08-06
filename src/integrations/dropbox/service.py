"""
Clean Dropbox Service - Minimal with Essential Workspace Support

Only includes the absolute minimum needed for workspace paths to work.

IMPORTANT: Workspace Logic is Required
=====================================

Dropbox API treats workspaces as separate namespaces that require special handling:

1. Workspace paths need a workspace-namespaced client with PathRoot
2. Full paths must be converted to relative paths within the workspace
3. Example: "/Federal Workspace/folder/file" -> "/folder/file" (relative)

This is NOT business logic - it's a Dropbox API requirement:
- Regular paths: Use default client with full path
- Workspace paths: Use workspace client with relative path

DO NOT remove workspace logic - it will break workspace path access.
The service must handle both regular and workspace paths correctly.
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


def _require_auth(func):
    """Decorator to ensure method requires authentication."""
    def wrapper(self, *args, **kwargs):
        if not self.is_authenticated():
            raise DropboxAuthenticationError("Service not authenticated")
        return func(self, *args, **kwargs)
    return wrapper


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

    @_require_auth
    def get_directory_link(self, directory_path: str) -> Optional[str]:
        """Get shareable link for directory."""
        _, shareable_link = self._get_directory_with_link(directory_path)
        return shareable_link

    @_require_auth
    def get_directory_details(self, directory_path: str) -> Dict[str, Optional[str]]:
        """Get directory path and shareable link."""
        found_path, shareable_link = self._get_directory_with_link(directory_path)
        return {"path": found_path, "shareable_link": shareable_link}

    @_require_auth
    def list_directory_files(self, directory_path: str) -> List[Dict[str, Any]]:
        """List files in directory."""
        return self._list_files(directory_path)

    @_require_auth
    def get_shareable_link(self, path: str, public: bool = True) -> Optional[str]:
        """Generate shareable link for path."""
        file_id = self._get_file_id(path)
        if not file_id:
            return None
        
        # Check for existing link first
        existing_link = self._get_existing_link(file_id)
        if existing_link:
            return existing_link
        
        # Create new link
        return self._create_new_link(file_id, public)

    # ==========================================
    # CLEAN HELPERS - SOLID/DRY IMPLEMENTATION
    # ==========================================

    def _get_directory_with_link(self, directory_path: str) -> tuple[Optional[str], Optional[str]]:
        """Get directory path and shareable link."""
        found_path = self._find_directory(directory_path)
        shareable_link = self.get_shareable_link(found_path) if found_path else None
        return found_path, shareable_link

    def _find_directory(self, path: str) -> Optional[str]:
        """Find directory."""
        result = self._get_metadata(path)
        return path if isinstance(result, dropbox.files.FolderMetadata) else None

    def _list_files(self, path: str) -> List[Dict[str, Any]]:
        """List files in directory."""
        result = self._list_folder(path)
        if not result:
            return []
        
        files = []
        for entry in result.entries:
            files.append({
                'name': entry.name,
                'path': f"{path.rstrip('/')}/{entry.name}",
                'is_file': isinstance(entry, dropbox.files.FileMetadata),
                'size': getattr(entry, 'size', 0) if hasattr(entry, 'size') else 0
            })
        return files

    def _get_file_metadata(self, path: str):
        """Get file metadata."""
        return self._get_metadata(path)

    # ==========================================
    # CORE API WRAPPERS - HANDLES WORKSPACE LOGIC
    # ==========================================

    def _get_metadata(self, path: str):
        """Get metadata - handles both regular and workspace paths."""
        # Try direct first
        try:
            return self._client.files_get_metadata(path)
        except dropbox.exceptions.ApiError:
            return self._get_workspace_metadata(path)

    def _list_folder(self, path: str):
        """List folder - handles both regular and workspace paths."""
        # Try direct first
        try:
            return self._client.files_list_folder(path)
        except dropbox.exceptions.ApiError:
            return self._get_workspace_list(path)

    # ==========================================
    # WORKSPACE HANDLING - DRY IMPLEMENTATION
    # ==========================================

    def _get_workspace_metadata(self, path: str):
        """Get workspace metadata."""
        return self._workspace_call(path, lambda client, rel_path: client.files_get_metadata(rel_path))

    def _get_workspace_list(self, path: str):
        """Get workspace list."""
        return self._workspace_call(path, lambda client, rel_path: client.files_list_folder(rel_path))

    def _workspace_call(self, path: str, api_func):
        """Generic workspace API call handler."""
        if "workspace" not in path.lower():
            return None
        
        client = self._get_workspace_client(path)
        if not client:
            return None
        
        try:
            relative_path = self._get_relative_path(path)
            return api_func(client, relative_path)
        except dropbox.exceptions.ApiError:
            return None

    # ==========================================
    # WORKSPACE UTILITIES
    # ==========================================
    def _get_workspace_client(self, path: str):
        """
        Get workspace-namespaced client for given path.
        
        REQUIRED: Dropbox API needs workspace-specific clients for workspace paths.
        This is not business logic - it's a Dropbox API architectural requirement.
        """
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
        """
        Convert workspace path to relative path within namespace.
        
        REQUIRED: Dropbox API needs relative paths within workspace namespace.
        Full path: "/Federal Workspace/folder/file" 
        Relative path: "/folder/file"
        
        This is not business logic - it's how Dropbox API works with workspaces.
        """
        # Remove workspace name from path: "/Federal Workspace/folder/file" -> "/folder/file"
        parts = path.strip("/").split("/")
        if len(parts) > 1:
            return "/" + "/".join(parts[1:])
        return "/"

    # ==========================================
    # SHARING UTILITIES
    # ==========================================

    def _get_file_id(self, path: str) -> Optional[str]:
        """Get file ID from path."""
        file_metadata = self._get_file_metadata(path)
        return file_metadata.id if file_metadata and hasattr(file_metadata, 'id') else None

    def _get_existing_link(self, file_id: str) -> Optional[str]:
        """Check for existing shareable link."""
        links = self._client.sharing_list_shared_links(path=file_id, direct_only=True)
        return links.links[0].url if links.links else None

    def _create_new_link(self, file_id: str, public: bool) -> str:
        """Create new shareable link."""
        settings = self._create_link_settings(public)
        result = self._client.sharing_create_shared_link_with_settings(file_id, settings)
        return result.url

    def _create_link_settings(self, public: bool):
        """Create sharing settings."""
        if public:
            return dropbox.sharing.SharedLinkSettings(allow_download=True)
        else:
            return dropbox.sharing.SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.team_only,
                allow_download=True
            )
