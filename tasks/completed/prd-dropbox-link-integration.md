# PRD: Dropbox API Integration for Automated Lease Folder Links

## Introduction/Overview

This feature will integrate the official Dropbox API to automatically search for and populate lease folder links in the order worksheet "Link" column, eliminating the current manual process where users must search for folders in Dropbox, copy links, and paste them into worksheets. The feature will use exact name matching to find directories that correspond to lease names and generate shareable Dropbox links for use in the organization's web application.

**Example workflow**: For a Federal agency order with lease "NMLC 123456", the system will search within the "/Federal/" directory for a subdirectory named "NMLC 123456", then generate a shareable link to "/Federal/NMLC 123456/" and populate it in the "Link" column of the exported worksheet.

**Goal**: Automate the process of finding and linking lease folders from Dropbox to reduce manual work and improve workflow efficiency.

## Goals

1. **Eliminate Manual Work**: Remove the need for users to manually search Dropbox, copy links, and paste them into worksheets
2. **Improve Accuracy**: Ensure consistent and accurate linking of lease folders through automated exact name matching
3. **Enhance User Experience**: Provide a seamless integration with optional GUI controls for user choice
4. **Maintain Reliability**: Implement robust error handling that allows workflow continuation even when Dropbox integration fails
5. **Support Both Agencies**: Work with both Federal and NMState agency directory structures

## User Stories

1. **As a user**, I want the system to automatically find my lease folders in Dropbox so that I don't have to manually search and copy links
2. **As a user**, I want the option to enable or disable Dropbox link population so that I can control when this feature is used
3. **As a user**, I want the system to authenticate with Dropbox through my web browser so that I can securely authorize access without exposing credentials
4. **As a user**, I want the system to continue working even if Dropbox is unavailable so that my workflow isn't interrupted
5. **As a project manager**, I want clickable Dropbox links in the exported worksheets so that team members can easily navigate to lease folders from our web application

## Functional Requirements

1. **Dropbox Authentication**
   - The system must support OAuth 2.0 web browser authentication flow with offline access
   - The system must store refresh tokens locally for long-term API access
   - The system must handle authentication errors gracefully and allow continued operation without Dropbox features

2. **Directory Search**
   - The system must search for directories using exact name matching against the "Lease" column values
   - The system must search within agency-specific root directories (e.g., Federal agency searches within "/Federal/" directory, NMState agency searches within "/NMState/" directory)
   - For each lease name (e.g., "NMLC 123456"), the system must look for a subdirectory with that exact name within the appropriate agency root directory
   - The system must use Dropbox API v2 `/files/search_v2` endpoint for directory searches
   - Search process: Agency "Federal" + Lease "NMLC 123456" → Find "/Federal/NMLC 123456/" directory

3. **Link Generation**
   - The system must generate shareable Dropbox links for the specific lease directories found (e.g., shareable link to "/Federal/NMLC 123456/" directory)
   - The generated links must work in web browsers and allow users to navigate directly to the lease folder on Dropbox.com
   - The system must populate the "Link" column in the order worksheet before export
   - The system must handle cases where no matching directory is found (leave Link column blank)

4. **GUI Integration**
   - The system must provide a checkbox option in the GUI to enable/disable Dropbox link population
   - The checkbox must be clearly labeled and positioned in the existing "Options" section
   - The feature must be disabled by default to maintain current user workflow

5. **Error Handling**
   - The system must continue worksheet export if Dropbox API is unavailable
   - The system must log appropriate error messages for debugging
   - The system must handle authentication token expiration automatically using refresh tokens
   - The system must handle network connectivity issues gracefully

6. **Performance**
   - The system must populate links before worksheet export (as part of the create_order_worksheet process)
   - The system must provide user feedback during Dropbox operations (progress indication)
   - The system must not significantly delay the worksheet creation process

## Non-Goals (Out of Scope)

1. **Multiple Directory Matching**: Will not handle cases where multiple directories match the same lease name
2. **Directory Creation**: Will not create new directories in Dropbox if they don't exist
3. **File-Level Search**: Will only search for directories, not individual files
4. **Partial Name Matching**: Will not implement fuzzy or partial name matching algorithms
5. **Dropbox File Management**: Will not provide features to upload, download, or modify files in Dropbox
6. **Team Management**: Will not handle Dropbox team administration or user management features

## Design Considerations

1. **Modular Design**: Design all Dropbox functionality as a completely independent module that can be imported and used in other applications
2. **GUI Layout**: Add the Dropbox option checkbox to the existing "Options" section alongside "Generate Lease Folders"
3. **Authentication Flow**: Use a separate window or default web browser for OAuth authorization
4. **Credential Storage**: Store refresh tokens in a secure local configuration file
5. **Agency Directory Mapping**: Configure agency-specific root directory paths (e.g., Federal → "/Federal/", NMState → "/NMState/") in the application settings for scoped directory searches
6. **Service Interface**: Define clear interfaces/contracts for the Dropbox service to ensure loose coupling and easy testing

## Technical Considerations

1. **Dependencies**: Add `dropbox` Python package to requirements.txt for official Dropbox SDK support
2. **Modular Architecture**: All Dropbox functionality must be completely separate from existing order processing code following SOLID and DRY principles to enable reuse in other applications
3. **Service Layer**: Create a standalone `DropboxService` class that encapsulates all Dropbox API interactions with clear interfaces
4. **Token Management**: Implement automatic refresh token handling using the official SDK within the service layer
5. **Configuration**: Store app credentials and agency-specific root directory paths (e.g., "/Federal/", "/NMState/") in a configuration system separate from business logic
6. **Loose Coupling**: Use dependency injection or service interfaces to integrate Dropbox functionality without tight coupling to existing processors
7. **Integration Points**: Modify both `NMStateOrderProcessor` and `FederalOrderProcessor` to optionally use the Dropbox service through clean interfaces

## Success Metrics

1. **Time Reduction**: Reduce manual link population time from ~2-3 minutes per order to under 30 seconds
2. **Error Rate**: Maintain <5% error rate for successful link population when directories exist
3. **Workflow Continuity**: Ensure 100% of worksheet exports complete successfully regardless of Dropbox status

## Open Questions

1. Should the system cache Dropbox search results for performance optimization?
2. What should happen if a user's Dropbox authentication expires during operation?
3. Should there be a batch re-authentication process for multiple users?
4. How should the system handle very large Dropbox directories that may affect search performance?
5. Should there be a manual refresh option for Dropbox links in case directory names change after initial worksheet creation? 