# Cloud-Agnostic Service Architecture PRD

## Introduction/Overview

The current `DropboxService` creates vendor lock-in and limits future flexibility if the client decides to migrate to another cloud storage provider (Google Drive, OneDrive, etc.). This feature creates a cloud-agnostic architecture that abstracts storage operations behind provider-independent interfaces, allowing seamless migration between cloud storage providers without changing business logic in workflows.

**Problem**: Hard dependency on Dropbox API throughout the codebase makes it difficult and risky to switch cloud storage providers.

**Goal**: Create a flexible, extensible cloud storage abstraction that supports the current Dropbox operations while enabling future provider additions and migrations.

## Goals

1. **Provider Independence**: Abstract cloud storage operations behind generic interfaces that work with any provider
2. **Zero Workflow Disruption**: Existing workflows continue working with minimal changes
3. **Easy Migration**: Client can switch from Dropbox to Google Drive (or other providers) through configuration change only
4. **Future Extensibility**: Design supports adding new cloud providers and operations without breaking existing code
5. **Maintain Performance**: No significant performance degradation from abstraction layer
6. **Preserve Functionality**: All current Dropbox operations continue working identically

## User Stories

- **As a business stakeholder**, I want to be able to switch cloud storage providers without code changes so that I can negotiate better contracts and avoid vendor lock-in
- **As a developer**, I want to work with generic cloud storage interfaces so that I can focus on business logic rather than provider-specific APIs
- **As a system administrator**, I want to configure the cloud provider through config files so that I can manage deployments easily
- **As a future developer**, I want to add new cloud providers easily so that the system can grow with business needs
- **As a workflow implementer**, I want existing workflows to continue working so that there's no disruption during the migration

## Functional Requirements

### Cloud-Agnostic Data Models
1. The system must define generic `CloudFile` data structure with path, name, directory flag, size, and modification date
2. The system must define generic `ShareLink` data structure with URL, expiration, and visibility settings
3. The system must define generic `CloudError` types mapped from provider-specific errors

### Protocol Interfaces
4. The system must implement `CloudAuthentication` protocol with authenticate() and is_authenticated() methods
5. The system must implement `CloudFileOperations` protocol with find_file() and list_files() methods  
6. The system must implement `CloudSharingOperations` protocol with create_share_link() method
7. The system must include placeholder protocol `CloudDirectoryOperations` for future directory creation functionality

### Service Implementation
8. The system must refactor existing DropboxService to implement the new protocols and return generic data types
9. The system must rename current DropboxService to `DropboxServiceLegacy` for reference
10. The system must create new `DropboxCloudService` that implements cloud-agnostic protocols
11. The system must map all Dropbox-specific responses to generic CloudFile and ShareLink objects

### Configuration Integration
12. The system must use existing config.py to specify cloud provider ("dropbox" initially)
13. The system must create `CloudServiceFactory` that instantiates the correct provider based on configuration
14. The system must support runtime provider switching through configuration change

### Workflow Integration
15. The system must update `lease_directory_search.py` workflow to use generic cloud interfaces
16. The system must update `previous_report_detection.py` workflow to use generic cloud interfaces
17. The system must ensure both workflows continue working with identical functionality

### Error Handling
18. The system must map provider-specific errors (dropbox.exceptions.ApiError) to generic cloud error types
19. The system must maintain error context and debugging information in mapped errors
20. The system must provide consistent error handling across all cloud providers

## Non-Goals (Out of Scope)

1. **Multiple Provider Support**: Not implementing Google Drive, OneDrive, or other providers initially - just designing for extensibility
2. **Advanced Cloud Features**: Not implementing file uploads, advanced permissions, or complex sharing beyond current functionality
3. **Backward Compatibility**: Not maintaining compatibility with old DropboxService interface - clean break approach
4. **Performance Optimization**: Not focusing on performance improvements beyond maintaining current speed
5. **Complex Migration Tools**: Not building automated migration scripts - manual config change approach
6. **Provider-Specific Features**: Not exposing provider-unique features that don't map to generic interface

## Technical Considerations

1. **Protocol vs ABC**: Use Python `Protocol` (typing.Protocol) instead of ABC for more flexible duck typing
2. **Dependency Injection**: CloudServiceFactory should handle provider instantiation and dependency injection
3. **Legacy Preservation**: Keep DropboxServiceLegacy file for reference during development and testing
4. **Workspace Logic**: Preserve Dropbox workspace handling logic within DropboxCloudService implementation
5. **Type Safety**: Maintain full type hints throughout generic interfaces and implementations
6. **Testing Strategy**: Existing integration test should work with new cloud service without modification

## Success Metrics

1. **Migration Readiness**: Switching cloud provider requires only config.py change (no code changes)
2. **Workflow Compatibility**: Both critical workflows (`lease_directory_search.py`, `previous_report_detection.py`) pass integration tests with new architecture
3. **Code Reduction**: Generic interfaces reduce future provider integration effort by >70%
4. **Performance Maintenance**: New abstraction layer adds <5% overhead to existing operations
5. **Developer Experience**: Junior developer can add new cloud provider in <2 days following established patterns
6. **Legacy Preservation**: DropboxServiceLegacy remains functional for emergency rollback

## Implementation Decisions

1. **File Organization**: Create new `src/integrations/cloud/` directory for generic interfaces and implementations
2. **Migration Strategy**: Implement new service alongside legacy, switch workflows one at a time, remove legacy after validation
3. **Error Mapping**: Create centralized error mapping utilities in cloud package
4. **Interface Design**: Keep interfaces minimal and focused (ISP principle) rather than monolithic
5. **Factory Pattern**: Use simple factory pattern for provider instantiation rather than complex dependency injection framework

---

**Target Audience**: Junior developers should be able to understand the cloud abstraction concept and add new providers following the established DropboxCloudService pattern.

**Implementation Priority**: High - this architectural improvement enables business flexibility and reduces future development risk.