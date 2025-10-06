# Task List: Document Archive Discovery and Auto-Creation

**Based on:** `prd-document-archive-discovery.md`

## Relevant Files

- `web/integrations/models.py` - Add new fields to AgencyStorageConfig model
- `web/integrations/migrations/000X_add_document_archive_config.py` - Migration for new fields
- `web/integrations/admin.py` - Update AgencyStorageConfigAdmin to display new fields
- `web/orders/repositories/__init__.py` - Add forward import for DocumentImagesLinkRepository
- `web/orders/repositories/document_images_link_repository.py` - NEW - Repository for DocumentImagesLink CRUD
- `web/orders/services/document_archive/__init__.py` - NEW - Package initialization
- `web/orders/services/document_archive/archive_finder.py` - NEW - Document archive finder service
- `web/orders/services/document_archive/archive_creator.py` - NEW - Document archive creator service
- `web/orders/services/document_archive/discovery_workflow.py` - NEW - Document discovery workflow orchestration
- `web/orders/services/runsheet/discovery_workflow.py` - Extend FullRunsheetDiscoveryWorkflow to include document discovery
- `web/orders/admin.py` - Add document_archive_link_display field to LeaseAdmin

### Notes

- This feature follows the same service architecture pattern as the runsheet discovery refactoring
- Reuse exceptions and result dataclasses from `orders.services.runsheet`
- Document discovery should be best-effort (log errors, don't fail workflow)
- No automated tests in this iteration (per user requirements)

## Tasks

- [ ] 1.0 Database Schema and Configuration Changes
  - [ ] 1.1 Add `auto_create_document_archives` BooleanField to `AgencyStorageConfig` (default=True)
  - [ ] 1.2 Add `document_subfolder_agency_sourced_documents` CharField to `AgencyStorageConfig` (max_length=255, blank=True, null=True)
  - [ ] 1.3 Add `document_subfolder_unknown_sourced_documents` CharField to `AgencyStorageConfig` (max_length=255, blank=True, null=True)
  - [ ] 1.4 Update `AgencyStorageConfig.save()` method to normalize the two new subfolder fields (add to existing normalization logic)
  - [ ] 1.5 Create Django migration: `python3 manage.py makemigrations integrations`
  - [ ] 1.6 Update `AgencyStorageConfigAdmin` fieldsets:
    - Add `auto_create_document_archives` to the main configuration section
    - Create new "Document Subfolders" fieldset with the two new subfolder fields
  - [ ] 1.7 Apply migration in Docker: `docker compose exec web python manage.py migrate`

- [ ] 2.0 Create Document Archive Repository Layer
  - [ ] 2.1 Create `web/orders/repositories/document_images_link_repository.py`
  - [ ] 2.2 Implement `DocumentImagesLinkRepository` class with:
    - `create_or_update_for_lease(lease, share_url)` method:
      - Get first DocumentImagesLink for the lease or create new
      - Update URL field
      - Save and log the operation
    - `create_or_update_cloud_location(provider, path, defaults)` method:
      - Reuse pattern from `LeaseRepository.create_or_update_cloud_location`
      - Same logic for CloudLocation.objects.update_or_create()
  - [ ] 2.3 Add forward import to `web/orders/repositories/__init__.py`:
    - Import and expose `DocumentImagesLinkRepository`
    - Update package docstring

- [ ] 3.0 Create Document Archive Services
  - [ ] 3.1 Create directory: `web/orders/services/document_archive/`
  - [ ] 3.2 Create `web/orders/services/document_archive/__init__.py`:
    - Add package docstring
    - Forward import all services and workflow classes
  - [ ] 3.3 Create `DocumentArchiveFinder` service (`archive_finder.py`):
    - Copy pattern from `runsheet/archive_finder.py` (~90% similar)
    - Change: Use `agency_config.documents_base_path` instead of `runsheet_archive_base_path`
    - Change: Constructor accepts `DocumentImagesLinkRepository` instead of `LeaseRepository`
    - Keep: All cloud service logic, share link creation, CloudLocation upsert
    - Reuse: `ArchiveSearchResult` from `orders.services.runsheet.results`
    - Reuse: Exceptions from `orders.services.runsheet.exceptions`
  - [ ] 3.4 Create `DocumentArchiveCreator` service (`archive_creator.py`):
    - Copy pattern from `runsheet/archive_creator.py` (~85% similar)
    - Change: Use `agency_config.documents_base_path`
    - Change: Extract subfolder names from `document_subfolder_agency_sourced_documents` and `document_subfolder_unknown_sourced_documents`
    - Change: If no subfolders configured, log warning and skip creation (return failure result)
    - Keep: Base path validation, directory creation logic, share link creation
    - Reuse: `ArchiveCreationResult` from `orders.services.runsheet.results`
    - Reuse: `BasePathMissingError`, `DirectoryCreationError` from `orders.services.runsheet.exceptions`
  - [ ] 3.5 Create `DocumentDiscoveryWorkflow` orchestration (`discovery_workflow.py`):
    - Copy pattern from `runsheet/discovery_workflow.py` `RunsheetDiscoveryWorkflow` class
    - Change: Use `DocumentImagesLinkRepository` instead of `LeaseRepository`
    - Change: Use `DocumentArchiveFinder` and `DocumentArchiveCreator`
    - Change: Update `DocumentImagesLink` via `repository.create_or_update_for_lease()`
    - Change: Use `documents_base_path` from agency config
    - Keep: Same orchestration pattern (find → auto-create if not found → update record)
    - Implement: `execute(lease_id, user_id)` method returning dict with results
    - Error handling: Wrap in try/except, log errors, don't raise (best-effort)

- [ ] 4.0 Integrate Document Discovery into Workflow
  - [ ] 4.1 Import `DocumentDiscoveryWorkflow` in `web/orders/services/runsheet/discovery_workflow.py`
  - [ ] 4.2 Update `FullRunsheetDiscoveryWorkflow.execute()` method:
    - After runsheet discovery completes, call document discovery
    - Wrap document discovery in try/except block
    - Log any errors at ERROR level
    - Include document discovery results in return dict (even if None on error)
    - Example structure:
      ```python
      document_result = None
      try:
          doc_workflow = DocumentDiscoveryWorkflow()
          document_result = doc_workflow.execute(lease_id, user_id)
      except Exception as e:
          logger.error("Document discovery failed for lease %s: %s", lease_id, str(e))
      
      return {
          "search": {...},  # existing runsheet results
          "detection": {...},  # existing detection results
          "document": document_result,  # NEW
      }
      ```
  - [ ] 4.3 Restart Docker services to load new code: `docker compose restart web worker`
  - [ ] 4.4 Monitor worker logs for any import errors: `docker compose logs worker --tail 50`

- [ ] 5.0 Update Django Admin Interface
  - [ ] 5.1 Add `document_archive_link_display` method to `LeaseAdmin`:
    - Get first `DocumentImagesLink` for the lease (via `lease.document_images_links.first()`)
    - If exists, format as clickable link with `target="_blank"` and `rel="noopener noreferrer"`
    - If not exists, return "-"
    - Set `short_description = "Document archive link"`
  - [ ] 5.2 Add `"document_archive_link_display"` to `readonly_fields` in `LeaseAdmin`
  - [ ] 5.3 Update field ordering in admin (place document link between runsheet link and misc index link)
  - [ ] 5.4 Verify admin display:
    - Restart web service: `docker compose restart web`
    - Open admin at http://localhost:8000/admin/
    - Edit a lease and verify document archive link displays correctly
  - [ ] 5.5 Test end-to-end workflow:
    - Create or update a lease with a configured agency (NMSLO or BLM)
    - Watch worker logs: `docker compose logs worker -f`
    - Verify document discovery runs after runsheet discovery
    - Check Flower at http://localhost:5555/ for task completion
    - Verify `DocumentImagesLink` is created/updated with share URL
    - Verify link displays in admin and opens in new tab

