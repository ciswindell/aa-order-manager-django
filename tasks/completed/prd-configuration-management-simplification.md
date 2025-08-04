# PRD: Configuration Management Simplification

## Introduction/Overview

The current configuration system is over-engineered with 1,177+ lines of complex validation, factory patterns, and scattered environment variable handling across multiple files. This creates maintenance burden and makes it difficult for developers to understand or modify configurations. The goal is to replace this complex system with a simple, centralized configuration manager that handles environment loading, agency directory paths, column widths, and Dropbox credential access in one unified place.

## Goals

1. **Reduce Complexity**: Replace 1,177+ lines of configuration code with ~60 lines
2. **Centralize Configuration**: Single source of truth for all configuration needs
3. **Improve Maintainability**: Make configuration changes simple and obvious
4. **Maintain Functionality**: Preserve all existing configuration capabilities
5. **Simplify Integration**: Make Dropbox auth use the unified config manager

## User Stories

1. **As a developer**, I want to easily modify column widths for agencies so that I can adjust Excel export formatting without navigating complex configuration classes
2. **As a developer**, I want to update agency directory paths so that I can change Dropbox search locations in one obvious place
3. **As a developer**, I want to add a new agency configuration so that I can extend the system without understanding factory patterns and validation logic
4. **As a system administrator**, I want to update Dropbox credentials so that I can manage authentication through environment variables
5. **As a new developer**, I want to understand the configuration system in under 5 minutes so that I can quickly contribute to the project

## Functional Requirements

1. **Environment Loading**: The system must automatically load environment variables from .env file when the configuration module is imported
2. **Agency Configuration**: The system must provide hardcoded directory paths, column widths, and folder structures for NMSLO and Federal agencies
3. **Dropbox Credential Access**: The system must provide accessor functions for Dropbox authentication credentials (access token, app key, app secret) from environment variables
4. **Directory Path Management**: The system must provide hardcoded agency directory paths in the configuration
5. **Column Width Configuration**: The system must provide agency-specific column width dictionaries for Excel export formatting
6. **Simple Accessor Functions**: The system must provide simple functions like get_agency_config(), get_directory_path(), get_column_widths()
7. **Backward Compatibility**: The system must maintain the same functional interface that existing code expects
8. **Integration with Dropbox Auth**: The DropboxAuthHandler must use the config manager for credential access instead of direct environment calls

## Non-Goals (Out of Scope)

1. **Complex Validation**: No extensive validation logic for configuration values
2. **Multiple Configuration Sources**: No support for JSON files, different config file formats
3. **Dynamic Configuration**: No runtime configuration changes or hot-reloading
4. **Configuration History**: No tracking of configuration changes over time
5. **Role-Based Configuration**: No user-specific or permission-based configuration

## Design Considerations

- **Single File Design**: All configuration logic in `src/core/config.py`
- **Simple Data Structures**: Use `@dataclass` for agency configuration, basic dictionaries for data
- **Environment for Credentials Only**: Load .env file once when module imports, use environment variables only for sensitive Dropbox credentials
- **No Validation**: Trust the configuration values, let the application handle invalid values gracefully
- **Clear Naming**: Use AgencyConfig instead of confusing names like "AgencyBehaviorConfig"

## Technical Considerations

1. **Migration Strategy**: 
   - Create new `src/core/config.py` 
   - Update imports gradually across the codebase
   - Delete old config files after migration complete
2. **Integration Points**:
   - Update `DropboxAuthHandler` to use config manager accessors
   - Update processors to use new configuration interface
   - Update workflow components to use simplified config
3. **Environment Variables**:
   - Only load sensitive Dropbox credentials from environment (DROPBOX_ACCESS_TOKEN, DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
   - All other configuration values hardcoded in the config file
4. **Dependencies**: Maintain zero external dependencies for configuration

## Success Metrics

1. **Lines of Code**: Reduce configuration code from 1,177+ lines to under 100 lines
2. **File Count**: Reduce from 4 configuration files to 1 configuration file  
3. **Import Complexity**: Replace complex import chains with single `from src.core.config import get_*` statements
4. **Developer Onboarding**: New developers can understand configuration system in under 5 minutes
5. **Functional Preservation**: All existing functionality works without changes to end-user experience

## Open Questions

1. ~~Should we maintain any configuration validation, or trust that invalid configs will fail gracefully?~~ **Resolved: No validation needed**
2. ~~Are there any other scattered environment variable usages that should be centralized?~~ **Resolved: Only Dropbox credentials from env**
3. ~~Should the configuration file handle any other application settings beyond what's currently in the config system?~~ **Resolved: No other settings yet, but design for future extensibility**
4. ~~Do we need any configuration caching, or is direct environment variable access sufficient?~~ **Resolved: No caching needed**