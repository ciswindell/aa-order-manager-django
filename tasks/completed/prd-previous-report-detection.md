# Product Requirements Document: Previous Report Detection Workflow

## Introduction/Overview

The Previous Report Detection workflow automates the identification of existing "Master Documents" files within lease directories to streamline the report creation process. This workflow determines whether a lease already has a completed report, enabling proper work assignment to update teams rather than creating duplicate reports from scratch.

**Problem Statement:** Currently, there is no automated way to detect if a lease directory contains an existing Master Documents report. This leads to inefficient work allocation where new reports may be created when updates to existing reports would be more appropriate.

**Goal:** Implement an automated workflow that searches lease directories for Master Documents files using pattern matching, providing instant visibility into existing report status for optimal work distribution.

**Critical Technical Constraint:** Based on Dropbox API research, shareable links cannot be used for programmatic directory listing. The workflow requires direct directory paths or file IDs, necessitating enhanced metadata storage from the LeaseDirectorySearchWorkflow.

## Goals

1. **Automated Detection:** Automatically identify Master Documents files in lease directories using regex pattern matching
2. **Work Optimization:** Enable proper assignment of lease work to update teams vs. creation teams based on existing report status  
3. **Pattern Flexibility:** Support case-insensitive detection of "Master Documents" files regardless of exact naming variations
4. **Independent Operation:** Function as a standalone workflow that can be orchestrated with other workflows without dependencies
5. **Data Integration:** Seamlessly update OrderItemData models with detection results for downstream processing

## User Stories

**As a** workflow orchestrator system,  
**I want to** automatically detect existing Master Documents in lease directories,  
**So that** I can route work to the appropriate teams (update vs. create) based on existing report status.

**As a** lease processing manager,  
**I want to** know immediately if a lease already has a Master Documents report,  
**So that** I can assign work efficiently and avoid duplicate report creation efforts.

**As a** report creation team member,  
**I want to** receive only leases that require new reports,  
**So that** I can focus on creating reports from scratch rather than updating existing ones.

**As a** report update team member,  
**I want to** receive leases that have existing Master Documents,  
**So that** I can focus on updating and refining existing reports with new information.

## Functional Requirements

### Core Detection Logic
1. The workflow MUST search for files containing "Master Documents" in the filename using case-insensitive regex matching
2. The workflow MUST search only in the root level of the target lease directory (no subdirectory traversal)
3. The workflow MUST return `true` if ANY file matching the "Master Documents" pattern is found
4. The workflow MUST return `false` if NO files matching the pattern are found in an accessible directory
5. The workflow MUST return `null` if an error occurs (authentication, network, directory access issues)

### Input Validation
6. The workflow MUST validate that OrderItemData is provided and contains required lease information
7. The workflow MUST validate that DropboxService is available and authenticated
8. The workflow MUST validate directory access before attempting file pattern matching

### Dropbox Integration
9. The workflow MUST use Dropbox API `/files/list_folder` endpoint to enumerate directory contents
10. The workflow MUST handle business account namespace and authentication requirements
11. The workflow MUST use direct directory paths or file IDs (shareable links cannot be used for programmatic directory listing)
12. The workflow MUST implement proper error handling for Dropbox API rate limits and service unavailability

### Pattern Matching
13. The regex pattern MUST use `.*[Mm]aster [Dd]ocuments.*` to match files containing "Master Documents" in any case variation
14. The pattern MUST match files with any prefix or suffix (e.g., "NMNM 0501759 Master Documents.pdf", "Master Documents - Final.pdf")
15. The workflow MUST search all file types regardless of extension

### Data Integration
16. The workflow MUST update `OrderItemData.previous_report_found` with the boolean detection result
17. The workflow MUST access directory path information from `OrderItemData.directory_path` field (to be added)
18. The workflow MUST preserve all existing OrderItemData fields and relationships

### Independence and Orchestration
19. The workflow MUST operate independently without requiring other workflows to complete first
20. The workflow MUST accept directory information as direct paths or file IDs (directory metadata required from LeaseDirectorySearchWorkflow)
21. The workflow MUST provide structured results suitable for workflow orchestration systems

## Non-Goals (Out of Scope)

1. **File Content Analysis:** Will not analyze the contents of found files to verify they are actual Master Documents
2. **File Download/Storage:** Will not download or store copies of detected Master Documents files  
3. **Version Control:** Will not determine which Master Documents file is the most recent if multiple exist
4. **File Modification:** Will not create, modify, or delete any files during detection process
5. **Directory Creation:** Will not create missing directories or handle directory setup
6. **Multi-Directory Search:** Will not search across multiple lease directories in a single operation
7. **Historical Tracking:** Will not maintain history of when files were detected or detection frequency

## Technical Considerations

### Dropbox API Enhancement
- **Enhancement Required:** DropboxService must be extended with `list_directory_files()` method using `/2/files/list_folder` endpoint
- **Business Account Support:** Must handle namespace requirements for business accounts using proper API headers
- **Authentication:** Must leverage existing token-based authentication system from current DropboxService implementation

### Directory Access Methods
- **Path-Based Access Required:** Shareable links cannot be used with `/2/files/list_folder` endpoint - must use direct directory paths or file IDs
- **Business Account Paths:** Support direct directory path access using business account authentication
- **Metadata Storage Enhancement:** REQUIRED - LeaseDirectorySearchWorkflow must store directory path in OrderItemData.directory_path field alongside shareable links for file listing capabilities

### Integration Architecture
- **Workflow Framework:** Built on existing WorkflowBase architecture with consistent error handling and logging
- **Executor Integration:** Compatible with WorkflowExecutor registration and factory patterns
- **Data Model Integration:** Seamless integration with existing OrderItemData structure

### Performance Considerations
- **API Rate Limiting:** Implement appropriate retry logic and respect Dropbox API rate limits
- **Caching Strategy:** Consider caching directory contents for short periods to reduce API calls
- **Timeout Handling:** Set reasonable timeouts for directory listing operations

## Design Considerations

### Workflow Identity
- **Type:** `previous_report_detection`
- **Name:** `Previous Report Detection Workflow`
- **Configuration:** Support for regex pattern customization and timeout settings

### Error Handling Strategy
- **Graceful Degradation:** Return `null` for detection status when errors occur, allowing downstream processes to handle missing data
- **Comprehensive Logging:** Log all detection attempts, API calls, and error conditions for debugging
- **Error Classification:** Distinguish between authentication errors, network errors, and directory access errors

### Testing Strategy
- **Unit Testing:** Mock DropboxService for isolated workflow logic testing
- **Integration Testing:** Test with real Dropbox directories containing various file patterns
- **Edge Case Testing:** Empty directories, permission denied scenarios, network failures

## Success Metrics

1. **Detection Accuracy:** 99%+ accuracy in identifying Master Documents files using pattern matching
2. **Performance:** Complete detection process within 10 seconds for typical directory sizes (< 100 files)
3. **Reliability:** 95%+ success rate in handling various directory access methods and error conditions
4. **Integration Success:** 100% compatibility with existing OrderItemData workflow processing
5. **Error Handling:** Graceful handling of all anticipated error scenarios without workflow crashes

## Open Questions

1. **Directory Input Method:** ✅ **RESOLVED** - LeaseDirectorySearchWorkflow will be enhanced to provide directory path/ID metadata required for file listing

2. **Path Storage Strategy:** ✅ **RESOLVED** - Directory paths will be stored in OrderItemData with new `directory_path` field

3. **Pattern Customization:** ✅ **RESOLVED** - Single case-insensitive pattern: `.*[Mm]aster [Dd]ocuments.*` for all agencies

4. **File Type Filtering:** ✅ **RESOLVED** - Search all files regardless of extension

5. **Multiple Matches:** ✅ **RESOLVED** - Boolean detection only (`true` if any Master Documents file found)

6. **DropboxService Enhancement:** ✅ **RESOLVED** - New `list_directory_files()` method will be implemented as part of this workflow

---

## Summary of Required Changes

Based on the resolved decisions, this workflow implementation will require:

1. **OrderItemData Enhancement:** Add `directory_path` field to store directory path from LeaseDirectorySearchWorkflow
2. **LeaseDirectorySearchWorkflow Enhancement:** Store directory path alongside shareable link generation  
3. **DropboxService Enhancement:** Add `list_directory_files()` method using `/2/files/list_folder` endpoint
4. **New Workflow Implementation:** `PreviousReportDetectionWorkflow` with pattern matching logic
5. **Integration Testing:** Validate end-to-end workflow with real Dropbox directories

*This PRD defines the foundation for implementing automated Master Documents detection to optimize lease processing workflows and improve work allocation efficiency.*