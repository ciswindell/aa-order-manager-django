# Feature Specification: Basecamp OAuth Account Selection

**Feature Branch**: `005-basecamp-account-selection`  
**Created**: 2025-11-01  
**Status**: Draft  
**Input**: User description: "OAuth account selection for Basecamp integration - allow users to choose which Basecamp account to connect when they have access to multiple accounts"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Account When Multiple Available (Priority: P1)

When a user authorizes the application with Basecamp and has access to multiple Basecamp accounts (e.g., "American Abstract LLC" and "Dudley Land Company"), they should be presented with a selection screen to choose which account to connect, rather than having the system automatically select the first account.

**Why this priority**: This is the core value of the feature - preventing the wrong account from being connected automatically. Without this, users cannot control which account is used and must manually edit the database.

**Independent Test**: User with access to multiple Basecamp accounts clicks "Connect Basecamp", authorizes on Basecamp, sees account selection screen, chooses desired account, and confirms connection completes with the correct account.

**Acceptance Scenarios**:

1. **Given** user has access to 2+ Basecamp accounts and no Basecamp account is connected, **When** user completes OAuth authorization, **Then** user sees selection screen listing all available accounts with names clearly displayed
2. **Given** user is on account selection screen with multiple accounts listed, **When** user selects "American Abstract LLC" and clicks "Connect Selected Account", **Then** system connects to American Abstract LLC and shows confirmation with account name
3. **Given** user has connected to "Dudley Land Company", **When** user disconnects and reconnects with access to multiple accounts, **Then** user again sees selection screen (no previous selection is remembered)

---

### User Story 2 - Auto-Select Single Account (Priority: P2)

When a user authorizes the application with Basecamp and only has access to one Basecamp account, the system should automatically connect that account without showing a selection screen.

**Why this priority**: This maintains the existing streamlined experience for users with only one account. The selection screen is unnecessary overhead when there's no choice to make.

**Independent Test**: User with access to only one Basecamp account clicks "Connect Basecamp", authorizes on Basecamp, and is immediately connected without seeing any selection screen.

**Acceptance Scenarios**:

1. **Given** user has access to exactly 1 Basecamp account and no account is connected, **When** user completes OAuth authorization, **Then** system automatically connects that account and redirects to dashboard with success message
2. **Given** user previously had multiple accounts but now only has access to 1 account, **When** user completes OAuth authorization, **Then** system auto-selects without showing selection screen

---

### User Story 3 - Handle Selection Session Expiry (Priority: P3)

When a user's session expires while on the account selection screen (e.g., they left the page open overnight), the system should gracefully handle the expired session and guide the user to restart the OAuth flow.

**Why this priority**: This prevents users from getting stuck in an error state and provides clear recovery steps. While less common, it's important for maintaining a good user experience.

**Independent Test**: Simulate session expiry on account selection page, attempt to select account, verify clear error message and guidance to restart OAuth flow.

**Acceptance Scenarios**:

1. **Given** user is on account selection screen and session has expired, **When** user tries to select an account, **Then** system shows error "Your session has expired. Please connect again." with button to restart OAuth
2. **Given** user sees session expired error, **When** user clicks "Connect Again" button, **Then** system initiates fresh OAuth flow

---

### Edge Cases

- What happens when user closes the account selection page without choosing? Session data remains in storage but user can return to selection page via "Connect Basecamp" button
- How does system handle race condition if user opens multiple OAuth windows? Each OAuth flow has independent session data; completing any one invalidates others
- What happens if user's access to accounts changes between authorization and selection? System validates selected account against current access list before completing connection
- How does system handle network failure during account selection submission? Show user-friendly error with retry button
- What happens if session storage is full or unavailable? Fall back to auto-selecting first account (current behavior) and log warning

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect when OAuth authorization response contains multiple Basecamp accounts
- **FR-002**: System MUST store account list and pending tokens in session storage when multiple accounts detected
- **FR-003**: System MUST redirect user to account selection page when multiple accounts are available
- **FR-004**: System MUST display account selection page showing all available accounts with their names
- **FR-005**: System MUST allow user to select exactly one account from the list
- **FR-006**: System MUST validate that selected account ID matches one of the pending accounts before completing connection
- **FR-007**: System MUST save OAuth tokens with the selected account ID and name to database
- **FR-008**: System MUST clear pending session data after successful account connection
- **FR-009**: System MUST auto-select and connect single account without showing selection page when only one account available
- **FR-010**: System MUST show error message and restart option when session expires during account selection
- **FR-011**: System MUST prevent connection completion with invalid or expired session data
- **FR-012**: System MUST display currently connected account name on dashboard after successful connection
- **FR-013**: System MUST support displaying up to 20 Basecamp accounts in the selection UI without degradation
- **FR-014**: System MUST log key events during account selection: selection flow initiated, account chosen by user, session expired, and all errors
- **FR-015**: System MUST include user ID and timestamp in all account selection log entries
- **FR-016**: System MUST check session expiry when accessed and remove expired sessions at that time (lazy cleanup pattern)

### Key Entities

- **Pending Account Session**: Temporary storage of available accounts and OAuth tokens during selection process
  - Attributes: list of account IDs/names, access token, refresh token, creation timestamp, expiry timestamp (15 minutes from creation)
  - Lifecycle: Created after OAuth authorization, cleared after account selection or removed on next access if expired (lazy cleanup)
  
- **Basecamp Account Connection**: Persistent record of user's connected Basecamp account
  - Attributes: user ID, selected account ID, account name, OAuth tokens, connection timestamp
  - Relationships: Belongs to one user, references one Basecamp account

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with multiple Basecamp accounts can successfully select desired account 100% of the time without requiring database edits
- **SC-002**: Users with single Basecamp account experience no additional steps (connection completes in same time as before)
- **SC-003**: Account selection page loads and displays available accounts within 2 seconds of OAuth callback
- **SC-004**: Zero instances of users connecting to wrong account due to automatic first-account selection
- **SC-005**: 100% of session expiry scenarios result in clear error message and recovery option (no cryptic errors or broken states)
- **SC-006**: Dashboard accurately displays connected account name immediately after connection for user verification

## Clarifications

### Session 2025-11-01

- Q: What specific timeout value should be used for pending account selection sessions? → A: 15 minutes
- Q: What is the maximum number of Basecamp accounts the selection UI should handle gracefully? → A: 20 accounts
- Q: What events should be logged during the account selection process? → A: Key events only (selection started, account chosen, session expiry, errors)
- Q: How should expired account selection sessions be removed from storage? → A: Lazy cleanup on access (check-on-use pattern)

## Assumptions *(include if applicable)*

- OAuth authorization response from Basecamp API includes complete list of accounts user has access to
- Account access list is current at time of authorization (no significant delay between authorization and selection)
- Session storage is available in the deployment environment and can store JSON data
- Users can visually distinguish between their Basecamp accounts by account name alone
- Session lifetime for pending account selection is 15 minutes (balances security with user experience)
- Frontend framework supports session-based flows and redirects

## Dependencies *(include if applicable)*

- **Phase 1 (Basecamp Project API)**: Already completed - OAuth authentication and token storage exist
- **Basecamp OAuth API**: Authorization endpoint must continue to return accounts array in response
- **Session Management**: Backend session storage must be functional and available

## Out of Scope

- Connecting multiple Basecamp accounts simultaneously (one account per user limit remains)
- Switching between connected accounts without disconnecting (requires disconnect then reconnect)
- Remembering previous account selection for future connections
- Searching or filtering account list (supports up to 20 accounts with simple scrollable list)
- Displaying account details beyond name (e.g., account ID, member count, project count)
- Batch operations or bulk account connections for multiple users
- Handling more than 20 accounts (edge case requiring pagination/search features)
