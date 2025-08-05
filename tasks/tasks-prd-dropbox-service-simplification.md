## Relevant Files

- `src/integrations/dropbox/service.py` - Current bloated DropboxService implementation that needs simplification
- `src/integrations/dropbox/service_simplified.py` - New simplified DropboxService implementation (temporary during development)
- `src/core/workflows/lease_directory_search.py` - Critical workflow that must continue working with simplified service
- `src/core/workflows/previous_report_detection.py` - Critical workflow that must continue working with simplified service
- `test_source_of_truth_integration.py` - Integration test using known lease "NMLC 0028446A" as regression protection
- `src/core/processors.py` - Legacy code that uses old service (breaking changes acceptable)

### Notes

- Integration test serves as source of truth to verify service functionality during refactoring
- New service will completely replace old service (no legacy preservation)
- Only workflows `lease_directory_search.py` and `previous_report_detection.py` need compatibility
- Breaking `processors.py` is acceptable as it's legacy unused code

## Tasks

- [x] 1.0 Create Source of Truth Integration Test
  - [x] 1.1 Use existing `test_final_integration.py` with lease_directory_search workflow test
  - [x] 1.2 Use known lease "NMLC 0028446A" as test data
  - [x] 1.3 Verify test covers: authentication, directory finding, and shareable link creation
  - [x] 1.4 Run test with current service to establish baseline (must pass)
- [x] 2.0 Implement Simplified DropboxService
  - [x] 2.1 Create `src/integrations/dropbox/service_simplified.py` with new implementation
  - [x] 2.2 Simplify constructor: `__init__(self, auth_handler)` (remove config_manager parameter)
  - [x] 2.3 Remove business logic from `search_directory()` method (remove agency parameter, take full path only)
  - [x] 2.4 Keep `search_directory_with_metadata()` unchanged (already clean)
  - [x] 2.5 Keep `list_directory_files()` unchanged (already clean)
  - [x] 2.6 Keep `authenticate()` and `is_authenticated()` unchanged
  - [x] 2.7 Consolidate private methods: replace 6+ methods with 3 clean ones (`_find_directory`, `_create_shareable_link`, `_list_files`)
  - [x] 2.8 Remove all config_manager usage and agency mapping logic
  - [x] 2.9 Verify new service has under 300 lines ✅ (213 lines = 65% reduction from 600 lines!)
- [x] 3.0 Update DropboxServiceInterface
  - [x] 3.1 Update interface method signatures to match simplified service ✅ (Already updated)
  - [x] 3.2 Remove any unused abstract methods ✅ (All methods used)
  - [x] 3.3 Ensure new simplified service implements updated interface ✅ (Perfect match)
- [x] 4.0 Replace Legacy Service and Update Imports
  - [x] 4.1 Rename `service_simplified.py` to `service.py` (replace legacy completely) ✅ (Test passes!)
  - [x] 4.2 Manually update import in `src/core/workflows/lease_directory_search.py` ✅ (No changes needed)
  - [x] 4.3 Manually update import in `src/core/workflows/previous_report_detection.py` ✅ (No changes needed)
  - [x] 4.4 Leave `src/core/processors.py` unchanged (legacy code, breaking changes acceptable) ✅
- [x] 5.0 Verify and Clean Up
  - [x] 5.1 Run source of truth integration test with new service ✅ (PASS with shareable link!)
  - [x] 5.2 Run any existing workflow tests to verify compatibility ✅ (Integration test passes!)
  - [x] 5.3 Verify line count reduction achieved ✅ (213 lines - exceeded target of <300!)
  - [x] 5.4 Remove any temporary files or legacy code remnants ✅ (All temp files cleaned up)
  - [x] 5.5 Confirm both critical workflows (`lease_directory_search.py`, `previous_report_detection.py`) work with simplified service ✅ (Method names updated and tested!)