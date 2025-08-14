# Dropbox Workspace-First Simplification PRD

## Introduction/Overview
Simplify the Dropbox integration by making all path handling workspace-first with automatic fallback to regular (root) paths. This removes brittle substring checks (e.g., paths containing "workspace"), prefers Dropbox PathRoot behavior when the first path segment is a shared folder name, and eliminates the dev-only listing endpoint. Scope remains limited to listing directories/files and creating share links; recursive listing and directory creation are out of scope for now.

## Implementation Status (Brief)
- Workspace-first logic implemented with shared folder cache and deterministic fallback.
- Substring-based workspace detection removed from behavior.
- Dev-only listing endpoint removed.

## Goals
1. Prefer workspace mode by default when the path begins with a shared folder name; otherwise fall back to regular client paths.
2. Remove substring-based workspace detection; rely on shared folder name lookup.
3. Cache shared-folder-name → namespace_id resolution per authentication session.
4. Preserve existing public interface (`CloudOperations`) and current behavior of callers.
5. Remove the dev-only endpoint that allows arbitrary path listings.

## User Stories
- As a background job, when I receive a path under a shared folder, I can list contents or create a share link successfully using workspace (PathRoot) semantics.
- As a developer, I can pass paths from `agency_config.runsheet_archive_base_path` without adding workspace detection; the service resolves the correct mode automatically.
- As an operator, if a path is not under a shared folder, the service still works via root-client fallback.

## Functional Requirements
1. Workspace-first resolution
   1.1. Parse the first path segment; if it matches a shared folder name, obtain a namespaced client via `PathRoot.namespace_id(namespace_id)`.
   1.2. Compute the relative path by removing the first segment (the shared folder name) from the full path.
   1.3. Execute the Dropbox API call with the namespaced client and the relative path.
   1.4. If no matching shared folder is found (or the workspace call returns `None`), call the regular client with the original path.
2. Shared folder lookup and caching
   2.1. On first use in a session, retrieve `sharing_list_folders()` and build a cache: `{folder_name: namespace_id}`.
   2.2. Store the cache within the workspace handler; reset it on authentication (i.e., when a new Dropbox client is set).
   2.3. Lookup is case-sensitive per Dropbox UI semantics; do not use substring matching.
3. Public API behavior (unchanged)
   3.1. `list_directories(path, recursive=False)` and `list_files(path, recursive=False)` remain; `recursive=True` raises `NotImplementedError`.
   3.2. `create_share_link(path, is_public=True)` remains; internally ensures file-id retrieval and metadata access follow workspace-first logic.
   3.3. Error mapping and auth decorators remain unchanged.
4. Dev endpoint removal
   4.1. Remove `GET /integrations/dropbox/list/` route and its view (`views.dropbox_list`).
   4.2. Ensure no remaining references in code or documentation.
5. Logging and observability
   5.1. Log whether a request used workspace vs regular mode at `INFO` or `DEBUG` level.
   5.2. Keep error logging consistent with current mapping.

## Non-Goals (Out of Scope)
- Recursive listing.
- Directory creation (planned next).
- Any additional Dropbox operations beyond listing and share link creation.
- Broader path sources beyond the first segment of `agency_config.runsheet_archive_base_path` (future work may add more sources).

## Design Considerations (Optional)
- Keep the `DropboxCloudService` public surface area and method signatures unchanged to avoid ripple effects on callers.
- Avoid exception-driven mode switching; use deterministic lookup + fallback to reduce noisy error handling.
- The path normalization should not mutate valid non-shared-folder paths; only remove the first segment when a shared folder match exists.

## Technical Considerations (Optional)
- Workspace handler
  - `get_workspace_client(path)`: returns namespaced client if first segment matches a shared folder name from the cache; otherwise `None`.
  - `get_relative_path(path)`: returns `"/" + "/".join(parts[1:])` when a shared folder match is present; otherwise returns the original path.
  - `workspace_call(path, api_func)`: use namespaced client + relative path; return `None` on failure (no exceptions leaked).
  - `is_workspace_path(path)`: checks first segment against the shared-folder cache (no substring heuristics).
- Caching
  - Store the cache dict on the handler; initialize lazily on first lookup.
  - Reset cache when the service authenticates (new client).
  - No TTL required now; future work can consider invalidation if folder membership changes frequently.
- Compatibility
  - `lease_directory_search` and other background tasks rely on `agency_config.runsheet_archive_base_path`; first segment is expected to be a shared folder name.
  - Fallback ensures non-workspace paths continue to function.
- Removal of dev endpoint
  - Delete URL pattern and the view to prevent arbitrary path introspection.

## Success Metrics
- Background tasks that use the Dropbox service continue to succeed without code changes:
  - Lease directory search: detects directories under shared folders and can create public share links when directories exist.
  - Non-workspace paths (if any) still list successfully via fallback.
- No usage of substring-based workspace detection remains.
- Dev-only listing endpoint removed.
- Logs show correct mode selection (workspace vs regular) for representative paths.

## Open Questions
- Should shared folder name matching be case-insensitive to align with potential user expectations? (Default: case-sensitive as per Dropbox.)
- Do we need a manual cache invalidation hook if admins rename shared folders during runtime?
- Will future path sources ever require matching nested shared folders or team spaces beyond `sharing_list_folders()`?
