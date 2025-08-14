## Relevant Files

- `web/integrations/models.py` - Add per-agency subfolder fields and toggle; ensure normalization; generate migration.
- `web/integrations/cloud/protocols.py` - Extend cloud-agnostic interface with directory creation APIs.
- `web/integrations/dropbox/dropbox_service.py` - Implement workspace-first directory creation using Dropbox SDK v2.
- `web/orders/services/lease_directory_search.py` - Invoke directory creation path when missing; update lease fields.
- `web/orders/tasks.py` - Ensure background task wiring handles creation flow and returns structured results.
- `web/integrations/tests/` and `web/orders/tests/` - Unit/integration tests for creation logic and background flow.
- `tasks/prd-dropbox-lease-directory-creation.md` - Source PRD for this task list.

### Notes

- Unit tests should typically be placed alongside the code files they are testing.
- Use your project's test runner (pytest or Django tests) as applicable.

## Tasks

- [ ] 1.0 Update configuration model for agency subfolders and toggle
  - [x] 1.1 Add nullable fields to `AgencyStorageConfig`: `runsheet_subfolder_documents_name`, `runsheet_subfolder_misc_index_name`, `runsheet_subfolder_runsheets_name`, `auto_create_lease_directories` (bool)
  - [x] 1.2 Add validation/normalization (no trailing slash; allow empty to skip)
  - [x] 1.3 Create migration and expose fields in Django admin
  - [x] 1.4 Seed sensible defaults for NMSLO and BLM (optional data migration or admin note)

- [ ] 2.0 Extend cloud interface and implement Dropbox directory creation
  - [x] 2.1 Extend `CloudOperations` with `create_directory(path, parents=True)` and `create_directory_tree(root_path, subfolders, exists_ok=True)`
  - [x] 2.2 Implement Dropbox create via SDK v2 `files_create_folder_v2` with workspace-first handling
  - [x] 2.3 Treat existing folders as success (conflict → ok); do not create base path if missing
  - [x] 2.4 Add path normalization and base-path existence check (skip if base missing)

- [ ] 3.0 Integrate creation flow into lease background search service
  - [x] 3.1 In `lease_directory_search`, when directory not found: verify base exists; if config toggle is on, create `<base>/<lease_number>`
  - [x] 3.2 Create configured subfolders from `AgencyStorageConfig` under the new directory
  - [x] 3.3 Upsert `CloudLocation` for the root lease directory and set `lease.runsheet_directory`
  - [x] 3.4 Set `lease.runsheet_report_found = False` and save

- [ ] 4.0 Add logging, error handling, and idempotency checks
  - [x] 4.1 Log created vs existed (workspace/regular mode)
  - [x] 4.2 Map permission/network errors to existing cloud errors; partial creation acceptable with clear logs
  - [x] 4.3 Ensure no share links are created in this flow

- [ ] 5.0 Write tests (unit + integration) for creation scenarios
  - [x] 5.1 Model tests for new config fields normalization and toggle
  - [x] 5.2 Service tests for `create_directory` and `create_directory_tree` (workspace and non-workspace)
  - [x] 5.3 Background flow test: missing directory → creates root + subfolders, updates lease, sets flag false
  - [x] 5.4 Re-run on existing directory → no-op success

- [ ] 6.0 Generate and apply database migrations; update admin/forms if needed
  - [x] 6.1 Create and apply migrations
  - [x] 6.2 Update admin to manage new fields; add help text

- [ ] 7.0 Documentation updates (config fields, behavior, and operations)
  - [x] 7.1 Update README with new config fields and behavior
  - [x] 7.2 Update PRD status notes upon completion
