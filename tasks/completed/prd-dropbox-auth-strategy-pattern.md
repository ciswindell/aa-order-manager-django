# PRD: Dropbox Authentication Strategy Pattern

## Introduction/Overview

The current Dropbox authentication handler (`src/integrations/dropbox/auth.py`) is overly complex at 486 lines, containing both token-based authentication and OAuth browser flow code. This creates maintenance burden and confusion since only token-based authentication is currently used in development.

This feature will implement a clean Strategy pattern to separate authentication methods, reduce complexity, and provide a foundation for future expansion while maintaining simplicity for current development needs.

## Goals

1. **Reduce complexity**: Simplify the authentication codebase from 486 lines to ~100 lines
2. **Separation of concerns**: Isolate token-based authentication from future OAuth implementation
3. **Future-ready architecture**: Provide a clean foundation for adding OAuth when needed
4. **Maintainable code**: Create clear, readable code that junior developers can understand
5. **Seamless integration**: Work with existing config system (`src/config.py`) and environment variables

## User Stories

- As a developer, I want simplified authentication code so that I can easily understand and maintain it
- As a developer, I want to use token-based authentication for development so that I don't need complex OAuth setup
- As a developer, I want a clear path to add OAuth in the future so that production deployment is straightforward when needed
- As a developer, I want to control authentication method through configuration so that I can switch methods without code changes

## Functional Requirements

1. **Strategy Pattern Implementation**: The system must implement a Strategy pattern with separate classes for different authentication methods
2. **Token Authentication**: The system must provide a `TokenAuthHandler` class that handles token-based authentication for development
3. **OAuth Placeholder**: The system must provide an `OAuthAuthHandler` class that raises `NotImplementedError` for future implementation
4. **Factory Method**: The system must provide a factory method that creates the appropriate authentication handler based on configuration
5. **Config Integration**: The system must use the existing `src/config.py` system to determine authentication method via environment variables
6. **Backward Compatibility**: The system must maintain the core interface methods (`is_authenticated()`, `get_client()`, `authenticate()`)
7. **Team Token Support**: The system must continue to support Dropbox Business team tokens
8. **Error Handling**: The system must provide clear error messages when authentication fails
9. **Logging**: The system must log authentication attempts and results for debugging

## Non-Goals (Out of Scope)

1. **OAuth Implementation**: Full OAuth browser flow implementation is out of scope for this iteration
2. **Multi-Service Support**: Support for other services (Google Drive, etc.) is out of scope
3. **Complex Token Management**: Refresh token storage and management is out of scope for token-based auth
4. **Backward Compatibility**: Maintaining existing method signatures like `create_simple_auth()` is out of scope

## Design Considerations

- Use Abstract Base Class (`ABC`) to define the authentication interface
- Implement separate concrete classes for each authentication strategy
- Use a factory method pattern for handler creation
- Leverage existing config system for authentication method selection
- Keep token authentication simple and focused on development needs

## Technical Considerations

1. **Dependencies**: Must work with existing `dropbox` SDK and `src/config.py`
2. **Integration**: Must integrate with existing `DropboxService` class without breaking changes to its interface
3. **Configuration**: Add `DROPBOX_AUTH_TYPE` environment variable with values `token` (default) or `oauth`
4. **File Structure**: Maintain existing file location at `src/integrations/dropbox/auth.py`

## Success Metrics

1. **Code Reduction**: Reduce authentication code from 486 lines to approximately 100 lines
2. **Maintainability**: Code should be understandable by junior developers (measured by code review feedback)
3. **Functionality**: All existing token-based authentication functionality continues to work
4. **Future-Ready**: OAuth can be implemented by filling in the `OAuthAuthHandler.authenticate()` method

## Open Questions

1. Should the environment variable be `DROPBOX_AUTH_TYPE` or `DROPBOX_AUTH_METHOD`?
2. Should the default authentication type be `token` or should it be explicit?
3. Are there any specific error messages or logging formats required for consistency with the existing codebase?