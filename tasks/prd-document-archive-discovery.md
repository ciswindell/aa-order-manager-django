# PRD: Document Archive Discovery and Auto-Creation

## Introduction/Overview

This feature extends the existing lease discovery workflow to automatically find or create document archive directories in cloud storage (Dropbox) for each lease. When a lease is created or updated, the system will search for a corresponding document archive directory at `{documents_base_path}/{lease_number}`, create a shareable link, and store it as a `DocumentImagesLink` record.

This parallels the existing runsheet archive discovery functionality, providing users with quick access to document archives directly from the Django admin interface.

**Problem it solves:** Currently, users must manually search for and link document archives for each lease. This feature automates the discovery process, reduces manual work, and ensures consistent directory structures across all leases.

## Goals

1. Automatically discover existing document archive directories when a lease is created or updated
2. Optionally auto-create document archive directories with configured subfolders when not found
3. Generate and store shareable links for document archives
4. Display document archive links in the Django admin interface
5. Maintain a single primary `DocumentImagesLink` per lease (auto-managed), while allowing users to add additional links manually
6. Reuse the modular service architecture established for runsheet archive discovery

## User Stories

1. **As an admin user**, when I create a new lease in the Django admin, I want the system to automatically find or create a document archive directory in Dropbox, so that I can quickly access relevant documents without manual searching.

2. **As an admin user**, when I view a lease in the Django admin, I want to see a clickable link to the document archive that opens in a new tab, so that I can quickly navigate to the documents.

3. **As an admin user**, when I update a lease number, I want the system to automatically re-discover the document archive and update the link, so that the link remains accurate.

4. **As a system administrator**, I want to configure per-agency settings for document archive base paths, subfolder names, and auto-creation behavior, so that different agencies can have different directory structures.

5. **As an admin user**, I want to be able to manually add additional document image links if needed, while the system maintains the primary auto-discovered link.

## Functional Requirements

### Database Schema Changes

1. **FR-1.1:** Add `auto_create_document_archives` boolean field to `AgencyStorageConfig` model (default: `True`)
2. **FR-1.2:** Add `document_subfolder_agency_sourced_documents` CharField (max_length=255, blank=True, null=True) to `AgencyStorageConfig`
3. **FR-1.3:** Add `document_subfolder_unknown_sourced_documents` CharField (max_length=255, blank=True, null=True) to `AgencyStorageConfig`
4. **FR-1.4:** Create a Django migration to add these fields

### Service Architecture

6. **FR-2.1:** Create `DocumentImagesLinkRepository` class with methods:
   - `create_or_update_for_lease(lease, share_url)` - Create a new DocumentImagesLink with the URL, or update existing if one already exists for this lease
   - `create_or_update_cloud_location(provider, path, defaults)` - Create or update CloudLocation (reuse pattern from LeaseRepository)

7. **FR-2.2:** Create `DocumentArchiveFinder` service class (pattern similar to `RunsheetArchiveFinder`) with:
   - `find_archive(lease, cloud_service, agency_config)` method
   - Returns `ArchiveSearchResult` dataclass (reused from runsheet services)
   - Searches for `{documents_base_path}/{lease_number}` directory
   - Creates shareable link if directory is found

8. **FR-2.3:** Create `DocumentArchiveCreator` service class (pattern similar to `RunsheetArchiveCreator`) with:
   - `create_archive(lease, cloud_service, agency_config)` method
   - Returns `ArchiveCreationResult` dataclass (reused from runsheet services)
   - Creates directory at `{documents_base_path}/{lease_number}`
   - Creates configured subfolders (agency_sourced_documents, unknown_sourced_documents)
   - Creates shareable link for the directory

9. **FR-2.4:** Create `DocumentDiscoveryWorkflow` orchestration class (pattern similar to `RunsheetDiscoveryWorkflow`) with:
   - `execute(lease_id, user_id)` method
   - Orchestrates finder and creator services
   - Updates `DocumentImagesLink` record via repository
   - Handles errors gracefully (log and continue, don't block runsheet discovery)

10. **FR-2.5:** Reuse existing exception classes from `orders.services.runsheet.exceptions`:
    - `RunsheetServiceError` (conceptually represents archive service errors)
    - `BasePathMissingError`
    - `DirectoryCreationError`

### Workflow Integration

11. **FR-3.1:** Extend `FullRunsheetDiscoveryWorkflow` to run document discovery after runsheet discovery:
    - If runsheet discovery succeeds, run document discovery
    - If runsheet discovery fails, still attempt document discovery
    - Errors in document discovery should not fail the entire workflow (log and continue)

12. **FR-3.2:** The existing `Lease` post_save signal should trigger the extended workflow (no changes needed to signal)

13. **FR-3.3:** Document discovery should respect the same 120-second deduplication window as runsheet discovery (no additional dedup key needed)

### DocumentImagesLink Management

14. **FR-4.1:** When document archive is found or created:
    - Check if a `DocumentImagesLink` already exists for the lease
    - If exists: Update the existing link's URL
    - If not exists: Create a new `DocumentImagesLink` with the share URL
    - Simple approach: Get or create the first link, update its URL

### Django Admin Integration

17. **FR-5.1:** Update `LeaseAdmin` to display the first document archive link:
    - Add a read-only `document_archive_link_display` field
    - Format as clickable link with `target="_blank"` and `rel="noopener noreferrer"`
    - Display "-" if no links exist

18. **FR-5.2:** Keep the existing `DocumentImagesLinkInline` in `LeaseAdmin` as-is:
    - Users can view, add, edit, and delete links manually
    - Auto-discovered link appears alongside any manual links

19. **FR-5.3:** Update `AgencyStorageConfigAdmin` to include new fields:
    - Add `auto_create_document_archives` to the main configuration section
    - Create a new "Document Subfolders" fieldset with the subfolder name fields

### Error Handling

20. **FR-6.1:** If document archive discovery fails (cloud error, config missing, etc.):
    - Log the error with appropriate severity level
    - Do not raise an exception that would block runsheet discovery
    - Do not fail the lease save operation

21. **FR-6.2:** If `documents_base_path` is not configured for an agency:
    - Log a warning
    - Skip document archive discovery for that lease
    - Continue with workflow

22. **FR-6.3:** If subfolder configuration is missing when auto-creation is enabled:
    - Log a warning
    - Skip document archive auto-creation for that lease
    - Continue with workflow (attempt to find existing archive)

23. **FR-6.4:** If cloud service is not authenticated during document discovery:
    - Log an error
    - Skip document archive discovery
    - Continue with workflow

### Logging

24. **FR-7.1:** Add comprehensive logging at INFO level for:
    - Document archive search start/completion
    - Document archive found/not found
    - Document archive creation start/completion
    - DocumentImagesLink creation/update

25. **FR-7.2:** Add logging at WARNING level for:
    - Missing `documents_base_path` configuration
    - Missing subfolder configuration when auto-creation is enabled
    - Auto-creation disabled but archive not found
    - Failed share link creation

26. **FR-7.3:** Add logging at ERROR level for:
    - Cloud service errors during document discovery
    - Base path does not exist (if auto-creation is enabled)
    - Unexpected errors during document discovery

## Non-Goals (Out of Scope)

1. **Searching for files within document archives** - This feature only discovers/creates directories and generates links, it does not scan for specific files
2. **Automatic document upload** - This feature does not upload documents to the archive
3. **Document archive cleanup** - This feature does not delete or archive old document directories
4. **Misc Index archive discovery** - Misc index archives are out of scope for this feature (may be a future enhancement)
5. **Background periodic re-scanning** - Discovery only happens on lease create/update, not on a schedule
6. **Multi-cloud provider support** - This feature only supports Dropbox (same as runsheet discovery)
7. **Celery task retry customization** - Document discovery uses the same retry policy as runsheet discovery
8. **Testing** - Automated tests are deferred to a future task

## Design Considerations

### Admin UI Layout

**Lease Admin Display:**
```
Lease: BLM NMLC 0028053B

Agency: BLM
Lease number: NMLC 0028053B
Runsheet link: [clickable URL, opens in new tab]
Document archive link: [clickable URL, opens in new tab]  ← NEW (first DocumentImagesLink)
Misc index link: [clickable URL, opens in new tab]
Runsheet report found: ✓

Document Images Links:
  [Inline table showing all DocumentImagesLink records]
  - URL: [link] | [Edit] [Delete]
  - URL: [link] | [Edit] [Delete]
  [+ Add another Document images link]
```

**Agency Storage Config Admin:**
```
Document Archives Section:
  ☑ Auto create document archives
  
Document Subfolders:
  Agency sourced documents: [text field]
  Unknown sourced documents: [text field]
```

### Service Module Structure

```
web/orders/services/document_archive/
├── __init__.py                  # Package with forward imports
├── archive_finder.py            # DocumentArchiveFinder service
├── archive_creator.py           # DocumentArchiveCreator service
└── discovery_workflow.py        # DocumentDiscoveryWorkflow orchestration

web/orders/repositories/
├── lease_repository.py                        # ✅ Already exists
└── document_images_link_repository.py         # 🆕 NEW
```

### Workflow Flow Diagram

```
Lease Save (Signal)
    ↓
full_runsheet_discovery_task
    ↓
FullRunsheetDiscoveryWorkflow.execute()
    ├─→ RunsheetDiscoveryWorkflow.execute()  [Existing]
    │       ├─→ Find runsheet archive
    │       └─→ Auto-create if not found
    │
    └─→ DocumentDiscoveryWorkflow.execute()  [NEW]
            ├─→ Find document archive
            ├─→ Auto-create if not found
            └─→ Update/create DocumentImagesLink
                    ↓
              (Log and continue on error, don't fail)
```

## Technical Considerations

1. **Database Migration:**
   - Single migration to add 3 fields to `AgencyStorageConfig`
   - No changes needed to `DocumentImagesLink` model

2. **Reuse Existing Architecture:**
   - Reuse `ArchiveSearchResult` and `ArchiveCreationResult` dataclasses
   - Reuse `RunsheetServiceError`, `BasePathMissingError`, `DirectoryCreationError` exceptions
   - Follow the same repository pattern as `LeaseRepository`
   - Follow the same service pattern as runsheet services

3. **Cloud Service Consistency:**
   - Use the same `get_cloud_service()` factory method
   - Use the same authentication checks
   - Use the same Dropbox client methods (list_files, create_directory, etc.)

4. **Celery Task Integration:**
   - No new Celery task needed - extend `FullRunsheetDiscoveryWorkflow`
   - No new retry configuration needed - inherit from parent task
   - No new dedup key needed - uses same lease-level dedup

5. **Performance Considerations:**
   - Document discovery runs sequentially after runsheet discovery (not parallel)
   - Total task time will increase by ~2-5 seconds
   - Task timeout limits (90s soft, 120s hard) should still be sufficient

## Success Metrics

1. **Functional Success:**
   - 100% of leases with configured agencies have document archive links auto-populated
   - 0% of lease saves are blocked by document discovery errors
   - Admin users can view and click document archive links from the lease admin

2. **Performance Success:**
   - Document archive discovery completes within 5 seconds on average
   - Total workflow (runsheet + document) completes within 15 seconds on average
   - No increase in Celery task timeout failures

3. **User Experience Success:**
   - Reduction in time spent manually searching for document archives
   - Positive feedback from admin users on link visibility and accessibility

## Open Questions

None - All requirements clarified and finalized.

---

**Document Version:** 1.0  
**Created:** October 4, 2025  
**Author:** AI Assistant  
**Status:** Draft - Awaiting Review

