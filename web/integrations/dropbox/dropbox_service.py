"""
Dropbox Cloud Service - Cloud-Agnostic Implementation

This service implements the cloud-agnostic protocols while preserving
all Dropbox-specific workspace logic and functionality.

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
from typing import Optional, List
import dropbox
from dropbox.sharing import SharedLinkSettings

from ..cloud.models import CloudFile, ShareLink
from ..cloud.protocols import CloudOperations
from ..cloud.errors import map_dropbox_error, CloudAuthError
from .auth import create_dropbox_auth
from .workspace_handler import DropboxWorkspaceHandler

logger = logging.getLogger(__name__)


def _require_auth(func):
    """Decorator to ensure service is authenticated before method execution."""

    def wrapper(self, *args, **kwargs):
        if not self.is_authenticated():
            raise CloudAuthError("Service not authenticated", "dropbox")
        return func(self, *args, **kwargs)

    return wrapper


def _handle_dropbox_errors(func):
    """Decorator to handle Dropbox API errors consistently."""

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            raise map_dropbox_error(e) from e

    return wrapper


class DropboxCloudService(CloudOperations):
    """Dropbox implementation of cloud-agnostic operations using composition."""

    def __init__(self, auth_type: str = None, user=None):
        self._auth_service = create_dropbox_auth(auth_type, user=user)
        self._client = None
        self._workspace_handler = None

    def authenticate(self) -> bool:
        """Authenticate using the auth service."""
        self._auth_service.authenticate()  # Raises CloudAuthError on failure
        self._client = self._auth_service.get_client()
        self._workspace_handler = DropboxWorkspaceHandler(self._client)
        self._workspace_handler.reset_shared_folders_cache()
        return True

    # ----------------------
    # Internal path helpers
    # ----------------------
    def _normalize_path_str(self, path: str) -> str:
        """Normalize Dropbox paths: leading slash, no trailing slash (except '/')."""
        cleaned = (path or "").replace("\\", "/").strip()
        if cleaned == "" or cleaned == "/":
            return "/"
        cleaned = "/" + cleaned.lstrip("/")
        cleaned = cleaned.rstrip("/")
        return cleaned

    def _get_parent_path(self, path: str) -> str:
        """Return normalized parent directory of a path."""
        path = self._normalize_path_str(path)
        if path == "/":
            return "/"
        parts = path.strip("/").split("/")
        if len(parts) <= 1:
            return "/"
        parent = "/" + "/".join(parts[:-1])
        return self._normalize_path_str(parent)

    def _path_exists(self, path: str) -> bool:
        """Return True if metadata exists for path (file or folder)."""
        try:
            md = self._get_metadata(path)
            return md is not None
        except Exception:
            return False

    def is_authenticated(self) -> bool:
        """Check if authenticated using the auth service."""
        # Consider fully authenticated only when both client and workspace handler exist
        return (
            self._auth_service.is_authenticated()
            and self._workspace_handler is not None
        )

    @_require_auth
    @_handle_dropbox_errors
    def list_files(
        self, directory_path: str, recursive: bool = False
    ) -> List[CloudFile]:
        """List files in directory (not directories)."""
        if recursive:
            raise NotImplementedError("Recursive listing not yet implemented")

        items = self._list_items(directory_path)
        return [item for item in items if not item.is_directory]

    @_require_auth
    @_handle_dropbox_errors
    def list_directories(
        self, directory_path: str, recursive: bool = False
    ) -> List[CloudFile]:
        """List directories in directory (not files)."""
        if recursive:
            raise NotImplementedError("Recursive listing not yet implemented")

        items = self._list_items(directory_path)
        return [item for item in items if item.is_directory]

    @_require_auth
    @_handle_dropbox_errors
    def create_share_link(
        self, file_path: str, is_public: bool = True
    ) -> Optional[ShareLink]:
        """Create shareable link for file or directory."""
        file_id = self._get_file_id(file_path)
        if not file_id:
            return None

        existing_link = self._get_existing_link(file_id)
        if existing_link:
            return ShareLink(url=existing_link, is_public=is_public)

        new_link = self._create_new_link(file_id, is_public)
        return ShareLink(url=new_link, is_public=is_public)

    @_require_auth
    @_handle_dropbox_errors
    def create_directory(self, path: str, parents: bool = True) -> Optional[CloudFile]:
        """Create a new directory using Dropbox SDK (workspace-first).

        Note: Parent creation and base-path checks are handled separately.
        """
        path = self._normalize_path_str(path)
        parent = self._get_parent_path(path)
        # Require parent to exist; do not attempt to create it
        if parent and parent != "/" and not self._path_exists(parent):
            logger.info("dropbox: skip create, missing base/parent path=%s", parent)
            return None
        # Try workspace-scoped create first
        result = self._workspace_handler.workspace_call(
            path,
            lambda client, rel_path: client.files_create_folder_v2(
                rel_path, autorename=False
            ),
        )
        if result and hasattr(result, "metadata"):
            logger.info("dropbox: created directory (workspace) path=%s", path)
            return self._convert_metadata_to_cloud_file(result.metadata)

        # Fallback to regular client
        try:
            created = self._client.files_create_folder_v2(path, autorename=False)
            logger.info("dropbox: created directory (regular) path=%s", path)
            return self._convert_metadata_to_cloud_file(created.metadata)
        except dropbox.exceptions.ApiError:
            # Conflict or already exists => treat as success if metadata retrievable
            try:
                md = self._get_metadata(path)
                if md:
                    logger.info("dropbox: directory already existed path=%s", path)
                    return self._convert_metadata_to_cloud_file(md)
            except Exception:
                pass
            raise

    @_require_auth
    @_handle_dropbox_errors
    def create_directory_tree(
        self, root_path: str, subfolders: List[str], exists_ok: bool = True
    ) -> List[CloudFile]:
        """Create multiple subfolders directly under root_path.

        Does not create share links. Returns created/existing directories as CloudFile.
        """
        root_path = self._normalize_path_str(root_path)
        # Root must already exist; do not create it here
        if not self._path_exists(root_path):
            logger.info("dropbox: skip create_tree, missing root path=%s", root_path)
            return []

        created_dirs: List[CloudFile] = []
        for name in subfolders:
            if not name:
                continue
            sub_path = f"{root_path.rstrip('/')}/{name.strip('/')}"
            try:
                created = self.create_directory(sub_path, parents=False)
                if created:
                    logger.info("dropbox: created subdirectory path=%s", sub_path)
                    created_dirs.append(created)
            except Exception:
                if not exists_ok:
                    raise
                # When exists_ok=True, best-effort: return existing metadata if present
                metadata = None
                try:
                    metadata = self._get_metadata(sub_path)
                except Exception:
                    metadata = None
                if metadata:
                    logger.info("dropbox: subdirectory existed path=%s", sub_path)
                    created_dirs.append(self._convert_metadata_to_cloud_file(metadata))
        return created_dirs

    def _list_items(self, path: str) -> List[CloudFile]:
        """List all items (files and directories) in path."""
        result = self._list_folder(path)
        if result and hasattr(result, "entries"):
            return [
                self._convert_metadata_to_cloud_file(entry) for entry in result.entries
            ]
        return []

    def _list_folder(self, path: str):
        """List folder - handles both regular and workspace paths."""
        normalized_path = "" if path == "/" else path
        workspace_result = self._workspace_handler.workspace_call(
            path, lambda client, rel_path: client.files_list_folder(rel_path)
        )
        if workspace_result is not None:
            logger.debug("dropbox: list_folder using workspace mode for path=%s", path)
            return workspace_result
        logger.debug(
            "dropbox: list_folder using regular mode for path=%s", normalized_path
        )
        try:
            return self._client.files_list_folder(normalized_path)
        except dropbox.exceptions.ApiError:
            # Treat not found as empty to allow callers to decide on creation
            return None

    def _convert_metadata_to_cloud_file(self, metadata) -> CloudFile:
        """Convert Dropbox metadata to CloudFile."""
        return CloudFile(
            path=metadata.path_display,
            name=metadata.name,
            is_directory=isinstance(metadata, dropbox.files.FolderMetadata),
            file_id=getattr(metadata, "id", None),
            size=getattr(metadata, "size", None),
            modified_date=getattr(metadata, "server_modified", None),
        )

    def _get_file_id(self, path: str) -> Optional[str]:
        """Get Dropbox file ID for path."""
        try:
            metadata = self._get_metadata(path)
            return metadata.id
        except (dropbox.exceptions.ApiError, AttributeError):
            return None

    def _get_metadata(self, path: str):
        """Get metadata - handles both regular and workspace paths."""
        workspace_result = self._workspace_handler.workspace_call(
            path, lambda client, rel_path: client.files_get_metadata(rel_path)
        )
        if workspace_result is not None:
            logger.debug("dropbox: get_metadata using workspace mode for path=%s", path)
            return workspace_result
        logger.debug("dropbox: get_metadata using regular mode for path=%s", path)
        return self._client.files_get_metadata(path)

    def _get_existing_link(self, file_id: str) -> Optional[str]:
        """Get existing share link for file ID."""
        try:
            links = self._client.sharing_list_shared_links(
                path=file_id, direct_only=True
            )
            return links.links[0].url if links.links else None
        except dropbox.exceptions.ApiError:
            pass
        return None

    def _create_new_link(self, file_id: str, public: bool) -> str:
        """Create new share link for file ID."""
        settings = self._create_link_settings(public)
        link = self._client.sharing_create_shared_link_with_settings(file_id, settings)
        return link.url

    def _create_link_settings(self, public: bool):
        """Create link settings."""
        if public:
            return SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.public
            )
        else:
            return SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.team_only
            )
