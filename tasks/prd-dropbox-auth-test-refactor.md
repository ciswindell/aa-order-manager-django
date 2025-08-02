# PRD: Refactor Dropbox Auth Unit Tests

## Introduction/Overview

The current dropbox auth unit test file (`tests/integrations/dropbox/test_auth.py`) is overly comprehensive with 619 lines covering every possible edge case and scenario. This makes the tests difficult to maintain and slower to run. The goal is to refactor these tests to focus on essential functionality with clear, basic tests that ensure the auth code works correctly without excessive complexity.

## Goals

1. **Simplify test complexity**: Reduce the test file from comprehensive edge-case coverage to essential functionality testing
2. **Improve maintainability**: Create clear, focused tests that are easy to understand and modify
3. **Ensure core functionality**: Maintain coverage of critical auth flows while removing redundant test cases
4. **Prepare for future refactoring**: Structure tests to easily accommodate the planned OAuth flow refactor

## User Stories

- **As a developer**, I want to run auth tests quickly to verify basic functionality works
- **As a maintainer**, I want simple tests that are easy to understand and modify when the auth code changes
- **As a CI/CD pipeline**, I want fast-running tests that catch real auth issues without excessive overhead
- **As a future developer**, I want tests that won't break when we refactor from dev credentials to OAuth flow

## Functional Requirements

1. **Basic Initialization Testing**
   - Test successful DropboxAuthHandler initialization
   - Test initialization failure when Dropbox SDK is unavailable
   - Verify basic property setting (app_key, app_secret, token_file_path)

2. **Core Authentication Flow Testing**
   - Test authentication with existing valid refresh token
   - Test authentication flow when no refresh token exists (OAuth flow)
   - Test authentication failure scenarios
   - Test `is_authenticated()` and `get_client()` methods

3. **Token Management Testing**
   - Test refresh token loading from file
   - Test refresh token saving to file
   - Test token clearing functionality

4. **Error Handling Testing**
   - Test basic error scenarios (invalid tokens, network failures)
   - Test graceful degradation when authentication fails

5. **Test Structure Requirements**
   - Use mocking for all external dependencies (Dropbox SDK, file system, network)
   - Avoid using real credentials or making real API calls
   - Keep each test method focused on a single responsibility
   - Use descriptive test names and clear assertions

## Non-Goals (Out of Scope)

1. **Comprehensive edge case testing**: No need to test every possible error condition or obscure scenario
2. **Real API integration testing**: No tests that make actual Dropbox API calls
3. **Performance testing**: No load testing or timing-sensitive tests
4. **Team authentication testing**: Skip complex Dropbox Business team scenarios
5. **Browser automation testing**: No actual web browser interaction testing
6. **Complex mock scenarios**: Avoid overly intricate mock setups that are hard to understand

## Technical Considerations

- **Maintain existing mock patterns**: Use similar mocking approaches but simplified
- **Keep test isolation**: Each test should be independent and not rely on others
- **Use temporary directories**: For file-based tests, use proper cleanup
- **Future OAuth compatibility**: Structure tests to easily adapt when OAuth flow is implemented
- **Follow existing patterns**: Use similar setUp/tearDown patterns but streamlined

## Success Metrics

- **Test file size**: Reduce from 619 lines to approximately 150-250 lines
- **Test execution time**: Tests should run in under 5 seconds
- **Test clarity**: Each test method should be under 20 lines and test one specific behavior
- **Coverage maintenance**: Maintain coverage of core authentication paths
- **Zero flaky tests**: All tests should be deterministic and reliable

## Open Questions

1. Should we keep any of the existing comprehensive test classes or start fresh?
2. What's the minimum number of test scenarios needed to catch real auth issues?
3. Should we add any integration test hooks for future OAuth testing? 