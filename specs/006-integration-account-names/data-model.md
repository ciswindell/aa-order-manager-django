# Data Model: Integration Account Names Display

**Feature**: Integration Account Names Display  
**Date**: November 2, 2025

## Overview

This feature adds account identification fields to the Dropbox integration and exposes existing Basecamp account name through the integration status API. No new entities are created - only field additions to existing models and DTO extensions.

---

## Modified Entities

### 1. DropboxAccount (Modified)

**Location**: `web/integrations/models.py`

**Purpose**: Store Dropbox user's display name and email for identification on integrations page

**Changes**: Add 2 new fields

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `display_name` | `CharField` | max_length=255, blank=True, default='' | User's full name from Dropbox (e.g., "Chris Windell") |
| `email` | `EmailField` | blank=True, default='' | User's email address from Dropbox (e.g., "chris@example.com") |

**Existing Fields** (unchanged):
- `user` - OneToOneField to Django User
- `account_id` - Dropbox account identifier
- `access_token` - OAuth access token
- `refresh_token_encrypted` - Encrypted refresh token
- `expires_at` - Token expiration timestamp
- `created_at` - Connection creation timestamp
- `updated_at` - Last update timestamp

**Validation Rules**:
- `display_name`: Truncated to 255 chars before storage (per FR-013)
- `email`: Django EmailField validation (valid email format)
- Both fields are optional (blank=True) to support legacy connections
- UTF-8 characters supported (per FR-014)

**Relationships**: Unchanged (OneToOne with User)

**Migration**:
```python
# Migration: web/integrations/migrations/000X_add_dropbox_account_info.py
operations = [
    migrations.AddField(
        model_name='dropboxaccount',
        name='display_name',
        field=models.CharField(max_length=255, blank=True, default=''),
    ),
    migrations.AddField(
        model_name='dropboxaccount',
        name='email',
        field=models.EmailField(blank=True, default=''),
    ),
]
```

---

### 2. BasecampAccount (Unchanged)

**Location**: `web/integrations/models.py`

**Purpose**: OAuth connection to Basecamp organization (already has `account_name` field)

**Relevant Existing Fields**:
- `account_name` - CharField(max_length=255) - Organization name (e.g., "American Abstract LLC")
- `created_at` - Connection creation timestamp

**No Changes Required**: Account name already stored and will be exposed through status API

---

### 3. IntegrationStatus (DTO - Modified)

**Location**: `web/integrations/status/dto.py`

**Purpose**: Response structure for integration status endpoint, carries account identification to frontend

**Changes**: Add 3 new optional fields

| Field | Type | Purpose |
|-------|------|---------|
| `account_name` | `Optional[str]` | Account/organization name (Basecamp org or Dropbox display name) |
| `account_email` | `Optional[str]` | Account email (Dropbox only, None for Basecamp) |
| `connected_at` | `Optional[datetime]` | When integration was first connected (from created_at) |

**Existing Fields** (unchanged):
- `provider` - Integration provider name ("basecamp" or "dropbox")
- `is_connected` - Boolean connection status
- `is_authenticated` - Boolean authentication validity
- `last_sync` - Last successful sync timestamp
- `blocking_problem` - Boolean if integration has critical issues
- `reason` - Human-readable status message
- `cta_label` - Call-to-action button label
- `cta_url` - Call-to-action URL

**Population Logic**:
- **Basecamp**: `account_name` from `BasecampAccount.account_name`, `account_email` = None
- **Dropbox**: `account_name` from `DropboxAccount.display_name`, `account_email` from `DropboxAccount.email`
- **Both**: `connected_at` from respective model's `created_at` field
- **Legacy/Missing Data**: Fields remain None, frontend shows generic "Connected" message

---

## Data Flow

### Dropbox OAuth Flow (Modified)

```
1. User clicks "Connect Dropbox"
2. OAuth authorization completes → callback receives tokens
3. **NEW**: Exchange tokens → Get account info via users_get_current_account()
4. **NEW**: Retry once (2 sec delay) if API call fails
5. **NEW**: Extract display_name and email from response
6. Save DropboxAccount with all fields (including new display_name, email)
7. Redirect to dashboard
```

### Integration Status API (Modified)

```
GET /api/integrations/status/

1. For each provider (dropbox, basecamp):
   a. Check if account exists for user
   b. Load account model
   c. **NEW**: Extract account_name (and email for Dropbox)
   d. **NEW**: Extract connected_at from created_at
   e. Build IntegrationStatus DTO with new fields
2. Serialize and return array of statuses
```

### Frontend Display (Modified)

```
Integrations Page Load:

1. Fetch /api/integrations/status/
2. Receive enhanced IntegrationStatus objects
3. **NEW**: Display account_name in card (truncate at 50 chars)
4. **NEW**: Display email for Dropbox (format: "Name (email)")
5. **NEW**: Display connected_at as formatted date
6. **NEW**: Add title attribute for full text on hover
```

---

## Database Schema Changes

**New Migration Required**: `web/integrations/migrations/000X_add_dropbox_account_info.py`

**Tables Modified**: 1 (`integrations_dropbox_account`)

**Columns Added**: 2
- `display_name` VARCHAR(255) DEFAULT ''
- `email` VARCHAR(254) DEFAULT '' (EmailField standard length)

**Indexes**: None needed (fields not used for queries, display only)

**Data Migration**: None required (existing records keep NULL/empty values)

**Reversibility**: Migration is reversible via `RunPython` operations if needed

---

## Validation & Constraints

### Storage Validation

- `display_name`: Max 255 chars, truncated before save
- `email`: Django EmailField validation (RFC 5322 compliance)
- Both fields: UTF-8 encoding supported
- Legacy records: Empty strings handled gracefully

### Display Validation

- Account names >50 chars: Truncated with ellipsis in UI
- Missing account info: Show generic "Connected" message
- Special characters: Display as-is (UTF-8 support)

### API Validation

- Session authentication required for `/api/integrations/status/`
- No user input validation needed (data from trusted OAuth sources)
- Log masking: PII fields masked in application logs

---

## State Transitions

### Dropbox Account States

1. **Not Connected** → User clicks "Connect" → OAuth flow
2. **OAuth In Progress** → Fetching account info → **NEW: Retry logic**
3. **Account Info Retrieved** → Save with display_name + email → **Connected with Info**
4. **Account Info Failed** → Save without display_name/email → **Connected (Generic)**
5. **Connected (Generic)** → User reconnects → Retry account info fetch → **Connected with Info**

### Display States

1. **Not Connected**: Show "Not connected" message
2. **Connected with Info**: Show "Connected as: [Name] ([email])" for Dropbox or "Connected as: [Name]" for Basecamp
3. **Connected (Generic)**: Show "Connected" (legacy or failed account info fetch)
4. **With Timestamp**: Additionally show "Connected on: [Date]" below account name

---

## Edge Cases

1. **Dropbox API Failure During OAuth**:
   - Attempt: Fetch account info
   - Retry: Once after 2 seconds
   - Fallback: Save connection with empty display_name/email
   - Display: Generic "Connected" message
   - Recovery: User can disconnect and reconnect to retry

2. **Legacy Dropbox Connections**:
   - State: Empty display_name/email fields
   - Display: Generic "Connected" message
   - Migration: No automatic backfill
   - Resolution: User reconnects naturally to populate data

3. **Account Name Longer Than 50 Chars**:
   - Storage: Full name (up to 255 chars) in database
   - Display: Truncated at 50 chars with "..." ellipsis
   - Hover: Full name shown in title attribute
   - Example: "Very Long Organization Name That Exceeds..." (hover shows full)

4. **Special Characters in Names**:
   - Storage: UTF-8 encoding preserves emojis, non-Latin scripts
   - Display: Rendered as-is in browser
   - Logging: Masked for PII protection
   - Example: "Café François 🇫🇷" displays correctly

5. **Account Renamed Externally**:
   - Detection: None (no background sync)
   - Sync: Only on reconnection
   - Display: Shows stale name until user reconnects
   - Acceptable: Per FR-015 (out of scope for real-time sync)

---

## Performance Considerations

- **OAuth Overhead**: Additional API call adds ~200-500ms to OAuth flow (acceptable during user wait for redirect)
- **Status Endpoint**: No additional queries (fields in same table, no joins)
- **Frontend Rendering**: Minimal impact (simple text display with CSS truncation)
- **Database Size**: Negligible (2 fields × ~10-100 users = <10KB)

---

## Security & Privacy

- **PII Storage**: Account names and emails stored in plaintext (protected by HTTPS, database access control)
- **PII Logging**: Masked in application logs (FR-016)
- **Access Control**: Integration status endpoint requires authentication
- **Token Security**: Unchanged (OAuth tokens remain in HTTP-only cookies)

---

## Testing Data

**Basecamp Test Account**:
```json
{
  "account_name": "American Abstract LLC",
  "connected_at": "2025-11-01T10:30:00Z"
}
```

**Dropbox Test Account (with info)**:
```json
{
  "display_name": "Chris Windell",
  "email": "chris@example.com",
  "connected_at": "2025-11-02T14:15:00Z"
}
```

**Dropbox Test Account (legacy)**:
```json
{
  "display_name": "",
  "email": "",
  "connected_at": "2025-10-15T09:20:00Z"
}
```

