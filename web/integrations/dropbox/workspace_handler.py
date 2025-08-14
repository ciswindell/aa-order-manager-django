"""
Dropbox Workspace Handler - Handles workspace-specific API logic.

This component is responsible for all Dropbox workspace-related operations:
- Workspace path detection and validation
- Workspace client creation with PathRoot
- Path conversion between full and relative workspace paths
"""

from typing import Optional, Tuple, Dict

import dropbox
from dropbox.common import PathRoot


class DropboxWorkspaceHandler:
    """Handles Dropbox workspace-specific operations."""

    def __init__(self, client: dropbox.Dropbox):
        self._client = client
        self._shared_folder_cache: Optional[Dict[str, str]] = None

    def _ensure_shared_folders_cache(self) -> None:
        """Lazily build a cache of shared folder name → namespace_id."""
        if self._shared_folder_cache is not None:
            return

        try:
            shared_folders = self._client.sharing_list_folders().entries
        except Exception:
            # If listing fails, keep cache as empty dict to avoid repeated calls
            self._shared_folder_cache = {}
            return

        cache: Dict[str, str] = {}
        for folder in shared_folders:
            name = getattr(folder, "name", None)
            namespace_id = getattr(folder, "shared_folder_id", None)
            if name and namespace_id:
                cache[name] = namespace_id

        self._shared_folder_cache = cache

    def _get_namespace_id_for_name(self, folder_name: str) -> Optional[str]:
        """Return namespace_id for a shared folder name if present."""
        self._ensure_shared_folders_cache()
        if not self._shared_folder_cache:
            return None
        return self._shared_folder_cache.get(folder_name)

    def reset_shared_folders_cache(self) -> None:
        """Reset the shared folders cache (e.g., on re-authentication)."""
        self._shared_folder_cache = None

    def _parse_path(self, path: str) -> Tuple[str, list]:
        """Parse path into workspace name and parts."""
        parts = path.strip("/").split("/")
        workspace_name = parts[0] if parts else ""
        return workspace_name, parts

    def is_workspace_path(self, path: str) -> bool:
        """Check if the path is under a known shared folder (by first segment)."""
        workspace_name, parts = self._parse_path(path)
        if not parts or not workspace_name:
            return False
        return self._get_namespace_id_for_name(workspace_name) is not None

    def get_workspace_client(self, path: str) -> Optional[dropbox.Dropbox]:
        """Return namespaced client if the first segment matches a shared folder name."""
        workspace_name, parts = self._parse_path(path)
        if not parts or not workspace_name:
            return None

        namespace_id = self._get_namespace_id_for_name(workspace_name)
        if not namespace_id:
            return None

        return self._client.with_path_root(PathRoot.namespace_id(namespace_id))

    def get_relative_path(self, path: str) -> str:
        """Return relative path if first segment is a shared folder; else original path.

        Example: "/Federal Workspace/folder/file" -> "/folder/file"
        """
        workspace_name, parts = self._parse_path(path)
        if len(parts) < 2:
            return path

        if not self._get_namespace_id_for_name(workspace_name):
            return path

        relative_parts = parts[1:]
        return "/" + "/".join(relative_parts)

    def workspace_call(self, path: str, api_func):
        """Generic workspace API call handler."""
        client = self.get_workspace_client(path)
        if not client:
            return None

        try:
            relative_path = self.get_relative_path(path)
            return api_func(client, relative_path)
        except (dropbox.exceptions.ApiError, dropbox.exceptions.BadInputError):
            return None
