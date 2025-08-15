## Relevant Files

- `web/orders/services/runsheet_archive_search.py` - Service that searches for the runsheet archive directory; business-specific naming to update.
- `web/orders/tasks.py` - Celery tasks referencing the search service; task name and imports to update.
- `web/orders/services/previous_report_detection.py` - References the runsheet directory field; update field name usage if renamed in models.
- `web/orders/models.py` - `Lease` model includes `runsheet_directory`; DB field rename required.
- `web/orders/migrations/0002_lease_runsheet_directory_lease_runsheet_link_and_more.py` - Migration history referencing the field; new migration to handle rename.
- `web/orders/migrations/0003_rename_runsheet_directory_to_runsheet_archive.py` - New migration created to rename the field from runsheet_directory to runsheet_archive.
- `web/orders/tests/test_services.py` - Tests import and call the search service; update imports and expectations.
- `web/orders/tests/test_tasks.py` - Tests for Celery tasks; update task import/name and patch targets.
- `web/orders/tests/test_e2e_runsheet.py` - End-to-end test patches the search service; update patch target.
- `web/integrations/models.py` - `AgencyStorageConfig` contains `auto_create_lease_directories`; consider business rename decision per PRD.
- `web/integrations/admin.py` - Admin form shows `auto_create_lease_directories`; reflect any rename if performed.
- `web/integrations/migrations/0007_rename_auto_create_lease_directories_to_auto_create_runsheet_archives.py` - New migration created to rename the auto_create field.
- `tasks/prd-runsheet-archive-naming-convention.md` - The PRD driving these changes.

### Notes

- Do not modify any files under `legacy/` (deprecated codebase).
- Do not modify cloud service interfaces, Dropbox service implementations, or generic cloud operations.
- Keep generic variables like `directory_path` and `base_path` unchanged unless they are business-specific.
- All existing tests must continue to pass after renaming.

## Tasks

- [x] 1.0 Rename business-specific service and references
  - [x] 1.1 Rename file `web/orders/services/lease_directory_search.py` → `web/orders/services/runsheet_archive_search.py` (module path only; no behavior changes)
  - [x] 1.2 In the renamed module, rename function `run_lease_directory_search` → `run_runsheet_archive_search`
  - [x] 1.3 Update all imports/patch targets referencing the module/function:
    - [x] `web/orders/tasks.py`
    - [x] `web/orders/tests/test_services.py`
    - [x] `web/orders/tests/test_tasks.py`
    - [x] `web/orders/tests/test_e2e_runsheet.py`
  - [x] 1.4 Update docstrings, log messages, and console tags to say "runsheet archive" (e.g., change `[lease-dir-create]` → `[runsheet-archive-create]`)
  - [x] 1.5 Do NOT rename generic variables like `directory_path` or `base_path`; keep cloud calls and signatures unchanged
  - [x] 1.6 Verify no cloud interface or Dropbox service code is changed by these edits

- [x] 2.0 Rename Lease model field and update all references
  - [x] 2.1 In `web/orders/models.py`, rename field `runsheet_directory` → `runsheet_archive`
  - [x] 2.2 Create a new Django migration using `RenameField` for `Lease.runsheet_directory` → `runsheet_archive`
  - [x] 2.3 Update all references to the field across code/tests:
    - [x] `web/orders/services/runsheet_archive_search.py` (formerly `lease_directory_search.py`)
    - [x] `web/orders/services/previous_report_detection.py`
    - [x] `web/orders/signals.py` (`task_only_fields` set)
    - [x] Tests: `test_services.py`, `test_tasks.py`, `test_e2e_runsheet.py`, `test_lease_directory_creation_flow.py`
  - [x] 2.4 Run makemigrations and ensure the migration compiles cleanly
  - [x] 2.5 Confirm that tests referencing `.path` access `lease.runsheet_archive.path`

- [x] 3.0 Update tasks and tests to new names
  - [x] 3.1 In `web/orders/tasks.py`, rename task `lease_directory_search_task` → `runsheet_archive_search_task`
  - [x] 3.2 Update logger text to reflect new task name
  - [x] 3.3 Update imports to `run_runsheet_archive_search` from the new module
  - [x] 3.4 Update `full_runsheet_discovery_task` to call `run_runsheet_archive_search`
  - [x] 3.5 Update tests:
    - [x] `test_tasks.py`: update imports and patch targets
    - [x] `test_e2e_runsheet.py`: update `@patch` module path
    - [x] `test_services.py`: update import and optionally rename class to `TestRunsheetArchiveSearch`

- [x] 4.0 Add migration(s) and ensure seeding remains reproducible
  - [x] 4.1 In `web/integrations/models.py`, rename `auto_create_lease_directories` → `auto_create_runsheet_archives`
  - [x] 4.2 Create a schema migration in `web/integrations/migrations/` to rename the field
  - [x] 4.3 Update `web/integrations/admin.py` field lists to the new name
  - [x] 4.4 Update tests referencing the field:
    - [x] `web/integrations/tests/test_agency_storage_config.py`
    - [x] `web/orders/tests/test_lease_directory_creation_flow.py`
  - [x] 4.5 If needed, add a data migration to backfill defaults (DB is empty but keep migration correctness) - SKIPPED

- [ ] 5.0 Update docs/comments/logs using business terminology
  - [x] 5.1 Update docstrings/comments in `web/orders/services/runsheet_archive_search.py`
  - [x] 5.2 Update docstrings in `web/orders/services/previous_report_detection.py` to say "runsheet archive" where applicable
  - [x] 5.3 Update top-level `README.md` to replace "lease directory" with "runsheet archive" for active features
  - [x] 5.4 Ensure no changes are made under `legacy/` and no cloud/Dropbox service interfaces are altered
