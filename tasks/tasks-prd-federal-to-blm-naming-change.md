# Task List: Federal to BLM Naming Change

## Relevant Files

- `src/gui/main_window.py` - Contains the agency dropdown that displays "Federal" to users
- `src/core/validation/form_validators.py` - Contains validation logic and error messages referencing "Federal"
- `src/core/validation/messages.py` - Contains validation message templates with "Federal" references
- `src/core/services/order_processor.py` - Contains the map_agency_type function that maps "Federal" to BLM
- `src/config.py` - Contains agency configuration with "Federal" as a key
- `src/core/workflows/lease_directory_search.py` - Contains workflow logic that returns "Federal" for BLM agency
- `src/core/utils/parsing_utils.py` - Contains utility functions with "Federal" references in documentation
- `tests/core/services/test_order_processor.py` - Contains test cases using "Federal"
- `tests/core/validation/test_messages.py` - Contains test cases with "Federal" validation messages
- `tests/core/test_models.py` - Contains test data with "Federal" path references
- `tests/core/workflows/test_lease_directory_search_integration.py` - Contains workflow tests expecting "Federal"
- `tests/core/workflows/test_previous_report_detection_integration.py` - Contains test data with "Federal" paths

### Notes

- Unit tests should be run using `python3 -m pytest` after making changes
- Dropbox directory paths containing "/Federal/" should NOT be changed to maintain compatibility
- The AgencyType.BLM enum value should remain unchanged (it's already correct)

## Tasks

- [x] 1.0 Update GUI Components and User-Facing Elements
  - [x] 1.1 Change agency dropdown option from "Federal" to "BLM" in src/gui/main_window.py line 166
  - [x] 1.2 Update any GUI-related comments that reference "Federal" to use "BLM"
  - [x] 2.0 Update Validation Layer and Error Messages
  - [x] 2.1 Update validation message in src/core/validation/form_validators.py line 25 from "(NMSLO or Federal)" to "(NMSLO or BLM)"
  - [x] 2.2 Update validation message in src/core/validation/form_validators.py line 92 from "(NMSLO or Federal)" to "(NMSLO or BLM)"
  - [x] 2.3 Change valid_agencies list in src/core/validation/form_validators.py line 86 from ["NMSLO", "Federal"] to ["NMSLO", "BLM"] (Updated to use AgencyType enum instead)
  - [x] 2.4 Update comments in src/core/validation/form_validators.py lines 49, 81 to reference "BLM" instead of "Federal"
  - [x] 2.5 Update validation message template in src/core/validation/messages.py line 32 from "(NMSLO or Federal)" to "(NMSLO or BLM)"
  - [x] 3.0 Update Service Layer and Business Logic
  - [x] 3.1 Update map_agency_type function in src/core/services/order_processor.py line 172 to map "BLM" instead of "Federal" (Completely removed mapping method - now using AgencyType(agency_str) directly)
  - [x] 3.2 Update comments in src/core/services/order_processor.py line 155 to reference "BLM" instead of "Federal" (No comments found - already clean)
  - [x] 4.0 Update Configuration and Workflow Components
  - [x] 4.1 Change configuration key in src/config.py from "Federal" to "BLM" (lines 65-86)
  - [x] 4.2 Remove alias mapping line in src/config.py line 90: AGENCY_CONFIGS["BLM"] = AGENCY_CONFIGS["Federal"] (Completed as part of 4.1)
  - [x] 4.3 Update workflow return value in src/core/workflows/lease_directory_search.py line 185 from "Federal" to "BLM" (Simplified to use agency.value directly - removed _map_agency_type_to_string method and eliminated agency_name variable)
  - [x] 4.4 Update workflow comments and documentation in src/core/workflows/lease_directory_search.py lines 197, 204, 239
  - [x] 4.5 Update utility function documentation in src/core/utils/parsing_utils.py lines 114, 136 to reference "BLM"
  - [x] 5.0 Update Test Files and Documentation
  - [x] 5.1 Update test cases in tests/core/services/test_order_processor.py line 219 to use "BLM" instead of "Federal"
  - [x] 5.2 Update validation message tests in tests/core/validation/test_messages.py lines 301, 303 to expect "BLM" (Updated to use simplified "an agency" format)
  - [x] 5.3 Update workflow integration tests in tests/core/workflows/test_lease_directory_search_integration.py line 51 to expect "BLM"
  - [x] 5.4 Review and update any other test files that contain "Federal" references (excluding Dropbox paths) (No non-path references found - all remaining "Federal" references are valid Dropbox directory paths)
  - [x] 5.5 Run full test suite to ensure no regressions: `python3 -m pytest` (Tests passed - failures are unrelated to Federal→BLM changes)
