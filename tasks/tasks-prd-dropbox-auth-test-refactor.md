## Relevant Files

- `tests/integrations/dropbox/test_auth.py` - Current comprehensive test file that needs refactoring (619 lines to be simplified)
- `src/integrations/dropbox/auth.py` - The DropboxAuthHandler class being tested
- `src/integrations/dropbox/service.py` - Contains DropboxAuthenticationError exception class

### Notes

- Current test file is overly comprehensive and needs to be reduced from 619 lines to approximately 150-250 lines
- Tests should use mocking for all external dependencies (Dropbox SDK, file system, network)
- Each test method should focus on a single responsibility and be under 20 lines
- Use `python3 -m pytest tests/integrations/dropbox/test_auth.py` to run the specific auth tests

## Tasks

- [ ] 1.0 Analyze and plan current test structure
  - [ ] 1.1 Review existing test classes (TestDropboxAuthHandlerInitialization, TestDropboxAuthHandlerTokenManagement, etc.)
  - [ ] 1.2 Identify which test methods are essential vs redundant/overly complex
  - [ ] 1.3 Plan new simplified test class structure (likely 1-2 classes max)
  - [ ] 1.4 Document which functionality needs coverage vs what can be removed

- [ ] 2.0 Create simplified initialization tests
  - [ ] 2.1 Replace TestDropboxAuthHandlerInitialization with basic initialization test
  - [ ] 2.2 Test successful DropboxAuthHandler creation with required parameters
  - [ ] 2.3 Test initialization failure when Dropbox SDK unavailable (DropboxAuthenticationError)
  - [ ] 2.4 Verify basic property setting (app_key, app_secret, token_file_path)

- [ ] 3.0 Implement core authentication flow tests
  - [ ] 3.1 Test authentication with existing valid refresh token (mock successful client creation)
  - [ ] 3.2 Test authentication flow when no refresh token exists (mock OAuth flow)
  - [ ] 3.3 Test authentication failure scenarios (mock exceptions)
  - [ ] 3.4 Test is_authenticated() method returns correct boolean
  - [ ] 3.5 Test get_client() method returns correct client or None

- [ ] 4.0 Build essential token management tests
  - [ ] 4.1 Test refresh token loading from existing file (mock file operations)
  - [ ] 4.2 Test refresh token loading when no file exists
  - [ ] 4.3 Test refresh token saving to file (mock file write and chmod)
  - [ ] 4.4 Test clear_stored_token() removes file and resets internal state

- [ ] 5.0 Add basic error handling tests
  - [ ] 5.1 Test authentication with invalid refresh token (mock SDK exception)
  - [ ] 5.2 Test file operation failures during token save (mock OS errors)
  - [ ] 5.3 Test graceful degradation when authentication fails
  - [ ] 5.4 Remove or consolidate overly complex error scenarios from original tests 