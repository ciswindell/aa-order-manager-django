"""
Dropbox Workspace Handler - Handles workspace-specific API logic.

This component is responsible for all Dropbox workspace-related operations:
- Workspace path detection and validation
- Workspace client creation with PathRoot
- Path conversion between full and relative workspace paths
"""

from typing import Optional, Tuple

import dropbox
from dropbox.common import PathRoot


class DropboxWorkspaceHandler:
    """Handles Dropbox workspace-specific operations."""

    def __init__(self, client: dropbox.Dropbox):
        self._client = client

    def _parse_path(self, path: str) -> Tuple[str, list]:
        """Parse path into workspace name and parts."""
        parts = path.strip("/").split("/")
        workspace_name = parts[0] if parts else ""
        return workspace_name, parts

    def is_workspace_path(self, path: str) -> bool:
        """Check if path is a workspace path."""
        return "workspace" in path.lower()

    def get_workspace_client(self, path: str) -> Optional[dropbox.Dropbox]:
        """Get workspace-specific client for path."""
        if not self.is_workspace_path(path):
            return None

        workspace_name, parts = self._parse_path(path)
        if not parts or not self.is_workspace_path(workspace_name):
            return None

        # Find namespace ID for this workspace
        shared_folders = self._client.sharing_list_folders().entries
        for folder in shared_folders:
            if hasattr(folder, "name") and folder.name == workspace_name:
                namespace_id = folder.shared_folder_id
                return self._client.with_path_root(PathRoot.namespace_id(namespace_id))

        return None

    def get_relative_path(self, path: str) -> str:
        """Convert workspace path to relative path."""
        # Example: "/Federal Workspace/folder/file" -> "/folder/file"
        _, parts = self._parse_path(path)
        if len(parts) < 2:
            return path

        # Remove workspace name from path
        relative_parts = parts[1:]
        return "/" + "/".join(relative_parts)

    def workspace_call(self, path: str, api_func):
        """Generic workspace API call handler."""
        if not self.is_workspace_path(path):
            return None

        client = self.get_workspace_client(path)
        if not client:
            return None

        try:
            relative_path = self.get_relative_path(path)
            return api_func(client, relative_path)
        except (dropbox.exceptions.ApiError, dropbox.exceptions.BadInputError):
            return None
