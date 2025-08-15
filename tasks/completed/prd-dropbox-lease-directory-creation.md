# Dropbox Lease Directory Creation PRD

## Introduction/Overview
When a lease directory does not exist during background runsheet search, the system must create it in Dropbox and scaffold standard subfolders based on the agency’s configuration. This replaces the legacy local folder creation and aligns with the new workspace‑first Dropbox integration.

## Goals
1. Create the missing lease directory at `<agency_base>/<lease_number>` using Dropbox.
2. Create configured subfolders under the lease directory (per agency).
3. Update the lease to reference the created directory and mark previous report detection as false (no master documents expected in a new, empty directory).
4. Keep the feature generic and reusable for other workflows.

## User Stories
- As a background worker, if no lease directory exists, I create it and its subfolders so downstream tasks have a consistent structure.
- As an operator, I see the lease updated with its cloud directory and the previous report flag set to false when a new directory is created.
- As a developer, I can configure subfolder names per agency without code changes.

## Functional Requirements
1. Directory creation
   1.1. Build target path as `<runsheet_archive_base_path>/<lease_number>`.
   1.2. Create the root lease directory if missing (mkdir -p semantics within the base path).
   1.3. Do NOT create the base path (`runsheet_archive_base_path`). If the base path is missing, log and skip creation (treat as configuration error).
2. Subfolder scaffolding
   2.1. Create the configured subfolders under the lease directory.
   2.2. Do not create share links for subfolders.
3. Lease update
   3.1. Upsert a `CloudLocation` for the lease directory and set `lease.runsheet_directory`.
   3.2. Set `lease.runsheet_report_found = False` when the directory is created due to being previously missing.
4. Idempotency and errors
   4.1. If a folder already exists, treat as success and continue.
   4.2. Failures due to permissions/network are surfaced via existing cloud errors; partial creation is acceptable (log which paths succeeded/failed).
5. Dropbox semantics
   5.1. Use the workspace‑first path handling (PathRoot + relative) already implemented.
   5.2. Use Dropbox SDK v2 calls (e.g., `files_create_folder_v2`) for creation.

## Non-Goals (Out of Scope)
- Creating share links as part of this feature (neither root nor subfolders). Link creation remains in existing flows.
- Uploading files or detecting previous reports during creation.
- Recursive listings beyond what’s already supported.

## Design Considerations
- Configuration-driven
  - Add explicit per‑agency subfolder fields to `AgencyStorageConfig` (nullable):
    - `runsheet_subfolder_documents_name`
    - `runsheet_subfolder_misc_index_name`
    - `runsheet_subfolder_runsheets_name`
    - Add a boolean toggle `auto_create_lease_directories` to enable/disable automatic creation per agency.
  - Defaults by agency (derived from legacy):
    - NMSLO: `^Document Archive`, `^MI Index`, `Runsheets`
    - BLM: `^Document Archive`, `Runsheets`
  - Leave fields empty to skip creating that subfolder.
- Path normalization
  - Ensure single leading slash, no trailing slash; safe join segments; disallow `..`.
- Idempotent creation
  - Treat conflicts (already exists) as success; continue creating the rest.
- Observability
  - Log created vs existed; record mode (workspace/regular) at DEBUG.

## Technical Considerations
- API additions (cloud‑agnostic)
  - `create_directory(path: str, parents: bool = True) -> Optional[CloudFile]`
  - `create_directory_tree(root_path: str, subfolders: list[str], exists_ok: bool = True) -> list[CloudFile]`
- Dropbox implementation
  - Prefer `files_create_folder_v2(path, autorename=False)` for single path creation.
  - Existence check via `files_get_metadata(path)` or handling conflict error codes.
  - Reuse workspace‑first utilities for path resolution.
  - Note: `files_create_folder_batch` can create multiple folders in one request (asynchronously, with job polling). We will not use it now.
- Background task integration
  - In the lease search service: when no files are found AND the directory is confirmed missing, create `<base>/<lease_number>` and configured subfolders; update `Lease.runsheet_directory`; set `Lease.runsheet_report_found = False`.
  - Return structured result indicating creation occurred.

## Success Metrics
- For a lease with no existing directory, the background task creates `<base>/<lease_number>` and configured subfolders, updates the lease’s `runsheet_directory`, and sets `runsheet_report_found` to false.
- Re‑running on an already created directory is a no‑op and returns success without errors.
- Works for both NMSLO and BLM sample configs matching legacy subfolder structures.

## Implementation Status (Brief)
- Model: Added per‑agency subfolder fields and toggle; migrations applied; admin updated.
- Service: Workspace‑first directory creation implemented with normalization and base checks.
- Background: Missing lease directory triggers creation and subfolders; lease updated; no share links created.
- Tests: Added unit tests for config normalization, directory creation, and background flow (including no‑op rerun).

## Open Questions
- Should we add a per‑agency toggle to opt‑out of automatic creation?
- Should we emit an audit log/event when directories are created?
- Do we need batch creation for agencies with larger templates in the near term?
