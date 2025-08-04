# Tasks: Dropbox Authentication Strategy Pattern

## Relevant Files

- `src/integrations/dropbox/auth.py` - Main authentication handler file refactored with Strategy pattern (reduced from 486 to ~165 lines)
- `src/config.py` - Configuration system that needs DROPBOX_AUTH_TYPE environment variable support
- `src/integrations/dropbox/service.py` - DropboxService that integrates with auth handlers
- `app.py` - Main application that creates and uses auth handlers
- `tests/integrations/dropbox/test_auth_strategy.py` - Unit tests for the new authentication strategy pattern
- `tests/integrations/dropbox/test_token_auth.py` - Unit tests for TokenAuthHandler
- `tests/integrations/dropbox/test_oauth_auth.py` - Unit tests for OAuthAuthHandler placeholder

### Notes

- The current `auth.py` file has 486 lines and will be completely refactored
- Existing `create_simple_auth()` interface will be replaced with new factory methods
- All tests should verify that existing token-based authentication continues to work
- Use `python3 -m pytest tests/integrations/dropbox/` to run authentication tests

## Tasks

- [x] 1.0 Create Abstract Base Authentication Handler Interface
  - [x] 1.1 Import ABC and abstractmethod from abc module
  - [x] 1.2 Define BaseAuthHandler abstract class with required imports
  - [x] 1.3 Add abstract authenticate() method that returns Optional[dropbox.Dropbox]
  - [x] 1.4 Add concrete is_authenticated() method that checks self._client
  - [x] 1.5 Add concrete get_client() method that returns self._client
  - [x] 1.6 Add shared __init__ method with dropbox SDK availability check

- [x] 2.0 Implement Token-Based Authentication Handler  
  - [x] 2.1 Create TokenAuthHandler class inheriting from BaseAuthHandler
  - [x] 2.2 Implement authenticate() method that calls authenticate_with_token()
  - [x] 2.3 Implement authenticate_with_token() method with token and team_member_id parameters
  - [x] 2.4 Add logic to get token from config.get_dropbox_access_token()
  - [x] 2.5 Implement regular user account authentication with dropbox.Dropbox()
  - [x] 2.6 Implement team token detection and _authenticate_team_token() method
  - [x] 2.7 Add proper error handling and logging for all authentication paths
  - [x] 2.8 Test authentication with existing token to ensure functionality

- [x] 3.0 Create OAuth Authentication Handler Placeholder
  - [x] 3.1 Create OAuthAuthHandler class inheriting from BaseAuthHandler
  - [x] 3.2 Implement authenticate() method that raises NotImplementedError with helpful message
  - [x] 3.3 Add docstring explaining this is a placeholder for future OAuth implementation
  - [x] 3.4 Add placeholder methods for future OAuth-specific functionality

- [x] 4.0 Implement Factory Method for Handler Creation
  - [x] 4.1 Create DropboxAuthHandler class with static factory methods
  - [x] 4.2 Implement create_auth_handler() method that reads DROPBOX_AUTH_TYPE from environment
  - [x] 4.3 Add logic to return TokenAuthHandler for "token" or default case
  - [x] 4.4 Add logic to return OAuthAuthHandler for "oauth" case
  - [x] 4.5 Implement create_simple_auth() method for backward compatibility (calls TokenAuthHandler)
  - [x] 4.6 Add proper error handling for invalid auth types

- [x] 5.0 Update Configuration System and Integration Points
  - [x] 5.1 Add DROPBOX_AUTH_TYPE environment variable support to src/config.py
  - [x] 5.2 Add get_dropbox_auth_type() function with default value "token"
  - [x] 5.3 Update app.py to use new factory methods (DropboxAuthHandler.create_simple_auth())
  - [x] 5.4 Verify DropboxService integration works with new auth handler interface
  - [x] 5.5 Test end-to-end authentication flow with existing token
  - [x] 5.6 Add environment variable documentation for DROPBOX_AUTH_TYPE