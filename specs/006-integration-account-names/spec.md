# Feature Specification: Integration Account Names Display

**Feature Branch**: `006-integration-account-names`  
**Created**: November 2, 2025  
**Status**: Draft  
**Input**: User description: "add the basecamp account name and option 2 for Dropbox to the integrations page"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Display Basecamp Account Name (Priority: P1)

When a user views the integrations page with a connected Basecamp account, they should see which specific Basecamp organization they're connected to, not just a generic "Connected" status.

**Why this priority**: Quick win - Basecamp account names are already stored in the database (`account_name` field). This provides immediate value by helping users verify they're connected to the correct organization, especially important after implementing multi-account selection.

**Independent Test**: User connects Basecamp account, navigates to integrations page, and sees "Connected as: [Account Name]" instead of just "Connected" status.

**Acceptance Scenarios**:

1. **Given** user has connected Basecamp account "American Abstract LLC", **When** user views integrations page, **Then** they see "Connected as: American Abstract LLC" displayed
2. **Given** user has no Basecamp connection, **When** user views integrations page, **Then** they see "Not connected" status (no account name shown)
3. **Given** user just completed Basecamp multi-account selection, **When** user returns to integrations page, **Then** they see the account name of the selected organization

---

### User Story 2 - Display Dropbox Account Information (Priority: P2)

When a user views the integrations page with a connected Dropbox account, they should see their Dropbox account name and email address to verify which Dropbox account is connected.

**Why this priority**: Requires database migration and OAuth callback updates. Provides clarity for users who may have multiple Dropbox accounts (personal and business).

**Independent Test**: User connects Dropbox account, navigates to integrations page, and sees "Connected as: [Display Name] ([email])" displayed.

**Acceptance Scenarios**:

1. **Given** user connects new Dropbox account, **When** OAuth completes, **Then** system fetches and stores display name and email from Dropbox API
2. **Given** user has connected Dropbox account, **When** user views integrations page, **Then** they see "Connected as: Chris Windell (chris@example.com)"
3. **Given** user has legacy Dropbox connection (before this feature), **When** user views integrations page, **Then** they see generic "Connected" until they reconnect
4. **Given** Dropbox API fails to return account info during OAuth, **When** connection completes, **Then** system stores connection but shows generic "Connected" message

---

### User Story 3 - Show Connection Timestamps (Priority: P3)

Users should be able to see when they first connected each integration to help with troubleshooting and account management.

**Why this priority**: Nice-to-have information that helps users track integration history. Data already exists in `created_at` field.

**Independent Test**: User views integrations page and sees "Connected on: [Date]" for each active integration.

**Acceptance Scenarios**:

1. **Given** user connected Basecamp on Nov 1, 2025, **When** user views integrations page, **Then** they see "Connected on: Nov 1, 2025"
2. **Given** user has multiple integrations with different connection dates, **When** user views integrations page, **Then** each integration shows its own connection date

---

## Clarifications

### Session 2025-11-02

- Q: Should account names and email addresses be treated as sensitive data requiring special handling? → A: Store plaintext in database, mask in logs - Standard approach, mask email/names in application logs
- Q: Should the system retry fetching Dropbox account info automatically, or only on manual reconnection? → A: Retry once after 2 seconds, then give up - Save connection with generic message
- Q: At what character count should account names be truncated in the UI? → A: 50 characters

---

### Edge Cases

- **Long account names**: What happens when Basecamp account name exceeds 50 characters? (Truncate at 50 chars with ellipsis in UI; full name available on hover. Database stores up to 255 chars.)
- **Missing Dropbox account info**: If OAuth flow completes but API call for account info fails, how is this handled? (Fallback to generic "Connected" message)
- **Legacy connections**: What happens for existing Dropbox connections created before this feature? (Show generic "Connected" until user reconnects)
- **Special characters**: How are names with emojis, non-Latin characters displayed? (Display as-is, rely on UTF-8 support)
- **Account name updates**: If user renames their Basecamp/Dropbox account externally, when does our system reflect the change? (Only on reconnection, not auto-synced)

## Requirements *(mandatory)*

### Functional Requirements

**Basecamp Display (P1)**:

- **FR-001**: System MUST display the connected Basecamp account name on the integrations page when a Basecamp connection exists
- **FR-002**: System MUST retrieve account name from existing `BasecampAccount.account_name` field
- **FR-003**: System MUST show "Not connected" message when no Basecamp account is linked
- **FR-004**: Account name display MUST update immediately after user completes multi-account selection

**Dropbox Display (P2)**:

- **FR-005**: System MUST store Dropbox display name and email address when user completes OAuth authorization
- **FR-006**: System MUST fetch account information from Dropbox API `users_get_current_account()` endpoint during OAuth callback
- **FR-007**: System MUST display both display name and email address on integrations page in format "Connected as: [Name] ([email])"
- **FR-008**: System MUST handle OAuth completion gracefully if Dropbox account info fetch fails by retrying once after 2 seconds, then storing connection with generic message if still failing
- **FR-009**: Database MUST store Dropbox display name (max 255 chars) and email (valid email format)

**General Display (P3)**:

- **FR-010**: System MUST display connection date for each active integration
- **FR-011**: System MUST format connection dates in user-friendly format (e.g., "Nov 2, 2025")
- **FR-012**: UI MUST truncate account names longer than 50 characters with ellipsis (e.g., "Very Long Account Name That Exceeds Fifty..." with full name on hover)

**Data Handling**:

- **FR-013**: System MUST truncate account names longer than 255 characters before storage
- **FR-014**: System MUST handle UTF-8 characters (emojis, non-Latin scripts) in account names
- **FR-015**: Account name updates MUST occur only during new connections, not via background sync

**Security & Privacy**:

- **FR-016**: System MUST mask account names and email addresses in application logs (e.g., "chris@example.com" logged as "ch***@ex***.com")

### Key Entities

- **BasecampAccount**: Represents Basecamp OAuth connection with existing `account_name` field (already stores organization name like "American Abstract LLC")
- **DropboxAccount**: Represents Dropbox OAuth connection, needs new `display_name` field (user's name) and `email` field (user's email address)
- **IntegrationStatus**: Response DTO that includes connection status, needs new `account_name`, `account_email`, and `connected_at` fields

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can immediately identify which Basecamp organization they're connected to without additional clicks or navigation
- **SC-002**: Users can identify which Dropbox account they're connected to by viewing name and email on integrations page
- **SC-003**: Integrations page displays account information within 2 seconds of page load (no additional API calls required after initial page load)
- **SC-004**: 100% of new Dropbox connections capture and display account information (for connections after feature deployment)
- **SC-005**: Account name display truncates at 50 characters with ellipsis without layout breaking, full name accessible on hover
- **SC-006**: Support tickets asking "Which account am I connected to?" reduce by 80% after feature deployment

## Assumptions

- Basecamp account names are already stored and don't need additional API calls
- Dropbox API `users_get_current_account()` endpoint is reliable and returns display name + email
- Users reconnecting Dropbox after this feature launches is acceptable for legacy connections
- 255 character limit for account names is sufficient for real-world use cases
- Connection timestamps from `created_at` field are accurate enough for user needs
- No real-time sync of account name changes is required (only updates on reconnection)
- Account names and email addresses stored in plaintext in database (protected by HTTPS in transit, masked in logs)

## Out of Scope

- Real-time syncing of account name changes from external platforms
- Displaying additional Dropbox account metadata (storage usage, team info, etc.)
- Allowing users to edit or override displayed account names
- Historical connection tracking (showing previous connections)
- Account switching UI (user must disconnect and reconnect to change accounts)
- Email verification or validation beyond what Dropbox API provides
