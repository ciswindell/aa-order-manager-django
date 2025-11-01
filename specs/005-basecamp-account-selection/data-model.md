# Data Model: Basecamp OAuth Account Selection

**Feature**: 005-basecamp-account-selection  
**Date**: 2025-11-01  
**Purpose**: Define data structures, entities, and relationships for OAuth account selection feature

## Overview

This feature introduces **temporary session-based storage** for pending account selections during OAuth flow. No new database models are required - all data uses Django's session framework for temporary storage and the existing `BasecampAccount` model for persistent connections.

---

## Entity: Pending Account Session (Temporary)

**Purpose**: Store available Basecamp accounts and OAuth tokens temporarily during multi-account selection flow

**Storage**: Django session framework (15-minute timeout)

**Lifecycle**:
1. Created after OAuth authorization when multiple accounts detected
2. Accessed when user loads account selection page
3. Validated when user submits account choice
4. Cleared after successful account connection OR expires after 15 minutes

### Structure

```python
# Stored in request.session
{
    'basecamp_pending_accounts': [
        {
            'id': str,      # Basecamp account ID (e.g., "5612021")
            'name': str     # Basecamp account name (e.g., "American Abstract LLC")
        },
        # ... up to 20 accounts
    ],
    'basecamp_pending_tokens': {
        'access_token': str,    # OAuth access token
        'refresh_token': str    # OAuth refresh token
    },
    '_session_expiry': int  # 15 minutes from creation (Django managed)
}
```

### Fields

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `basecamp_pending_accounts` | list[dict] | Yes | Non-empty, max 20 items | List of available Basecamp accounts |
| `basecamp_pending_accounts[].id` | string | Yes | Non-empty string | Basecamp account ID |
| `basecamp_pending_accounts[].name` | string | Yes | Non-empty string, max 255 chars | Human-readable account name |
| `basecamp_pending_tokens` | dict | Yes | Both tokens required | OAuth tokens for completing connection |
| `basecamp_pending_tokens.access_token` | string | Yes | Non-empty string | OAuth access token |
| `basecamp_pending_tokens.refresh_token` | string | Yes | Non-empty string | OAuth refresh token |

### Validation Rules

1. **Account List**:
   - MUST contain at least 1 account (if 0, OAuth failed)
   - MUST NOT contain more than 20 accounts (implementation limit per FR-013)
   - Each account MUST have unique `id` within list
   - Account `id` MUST be string representation of integer
   - Account `name` MUST be non-empty and ≤255 characters

2. **Tokens**:
   - Both `access_token` and `refresh_token` MUST be present
   - Tokens MUST be non-empty strings
   - Tokens MUST NOT be exposed to frontend (server-side only)

3. **Session**:
   - Session MUST expire after 15 minutes (900 seconds)
   - Session data MUST be cleared after successful connection
   - Expired sessions MUST be rejected with clear error message

### State Transitions

```
[OAuth Callback] 
  → IF accounts.length > 1 
    → CREATE pending session (15-min timeout)
    → REDIRECT to selection page
  → IF accounts.length == 1
    → SKIP session creation
    → AUTO-CONNECT account

[Account Selection Page Load]
  → IF session exists AND not expired
    → FETCH pending accounts
    → DISPLAY selection UI
  → IF session expired OR not exists
    → SHOW expiry error
    → OFFER restart button

[Account Selection Submit]
  → IF session exists AND not expired AND account valid
    → SAVE to BasecampAccount
    → CLEAR session
    → REDIRECT to dashboard
  → IF session expired
    → RETURN 400 with "restart_oauth" action
  → IF account invalid
    → RETURN 400 with "choose_again" action
```

### Relationships

- **User (1) → PendingAccountSession (0..1)**: Each user can have at most one pending session at a time. Session is keyed by Django session ID which is tied to user's session cookie.
- **PendingAccountSession → BasecampAccount**: After selection, pending data is used to create/update one `BasecampAccount` record.

---

## Entity: BasecampAccount (Existing - No Changes)

**Purpose**: Persistent storage of connected Basecamp account and OAuth tokens

**Storage**: PostgreSQL (`integrations_basecampaccount` table)

**Source**: `web/integrations/models.py`

**Lifecycle**:
1. Created/updated after user completes account selection
2. Tokens refreshed automatically when expired
3. Deleted when user disconnects Basecamp

### Structure (Reference Only)

```python
class BasecampAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Modifications Required

**NONE** - Existing model already supports account ID and name storage. The account selection feature only changes **how** the account ID is chosen (user selection vs. automatic first-account).

### Fields Used by This Feature

| Field | How Used | Source |
|-------|----------|--------|
| `account_id` | Set to user-selected account ID from pending session | User choice |
| `account_name` | Set to user-selected account name from pending session | User choice |
| `access_token` | Set from `pending_tokens.access_token` in session | OAuth response |
| `refresh_token` | Set from `pending_tokens.refresh_token` in session | OAuth response |

---

## Data Flow

### Flow 1: Multiple Accounts (Selection Required)

```
┌─────────────────┐
│ OAuth Callback  │
│  GET /callback  │
└────────┬────────┘
         │
         │ Parse OAuth response
         │ accounts = [{id, name}, ...]
         │ len(accounts) > 1
         │
         ▼
┌─────────────────────────────┐
│ Create Pending Session      │
│                             │
│ session['pending_accounts'] │
│ session['pending_tokens']   │
│ session.set_expiry(900)     │
└────────┬────────────────────┘
         │
         │ Redirect to selection page
         │
         ▼
┌─────────────────────────────┐
│ Selection Page Load         │
│  GET /basecamp/select       │
│                             │
│ Fetch pending accounts      │
│ Display RadioGroup          │
└────────┬────────────────────┘
         │
         │ User selects account
         │ User clicks "Connect"
         │
         ▼
┌─────────────────────────────┐
│ Selection Submit            │
│  POST /api/../select        │
│                             │
│ Validate account in session │
│ Save to BasecampAccount     │
│ Clear session data          │
└────────┬────────────────────┘
         │
         │ Return success
         │
         ▼
┌─────────────────────────────┐
│ Dashboard                   │
│  Show "Connected to [name]" │
└─────────────────────────────┘
```

### Flow 2: Single Account (Auto-Select)

```
┌─────────────────┐
│ OAuth Callback  │
│  GET /callback  │
└────────┬────────┘
         │
         │ Parse OAuth response
         │ accounts = [{id, name}]
         │ len(accounts) == 1
         │
         ▼
┌─────────────────────────────┐
│ Skip Session Creation       │
│                             │
│ Auto-select accounts[0]     │
│ Save to BasecampAccount     │
└────────┬────────────────────┘
         │
         │ Redirect to dashboard
         │
         ▼
┌─────────────────────────────┐
│ Dashboard                   │
│  Show "Connected to [name]" │
└─────────────────────────────┘
```

### Flow 3: Session Expiry

```
┌─────────────────────────────┐
│ Pending Session Created     │
│  15-minute timer starts     │
└────────┬────────────────────┘
         │
         │ ... 15+ minutes pass ...
         │
         ▼
┌─────────────────────────────┐
│ User Returns to Page        │
│  GET /basecamp/select       │
│                             │
│ Check session expiry        │
│ session expired = True      │
└────────┬────────────────────┘
         │
         │ Show error message
         │
         ▼
┌─────────────────────────────┐
│ Error State                 │
│  "Session expired"          │
│  "Please connect again"     │
│  [Connect Again] button     │
└────────┬────────────────────┘
         │
         │ User clicks button
         │
         ▼
┌─────────────────────────────┐
│ Restart OAuth Flow          │
│  Redirect to /connect       │
└─────────────────────────────┘
```

---

## Validation

### Creation Validation (OAuth Callback)

```python
def validate_oauth_response(accounts):
    """Validate OAuth response before creating session."""
    if not accounts:
        raise ValueError("No accounts returned from OAuth")
    
    if len(accounts) > 20:
        # Edge case: truncate to 20 or show error
        logger.warning(f"User has {len(accounts)} accounts, truncating to 20")
        accounts = accounts[:20]
    
    for account in accounts:
        if not account.get('id'):
            raise ValueError("Account missing required 'id' field")
        if not account.get('name'):
            raise ValueError("Account missing required 'name' field")
        if len(account['name']) > 255:
            account['name'] = account['name'][:255]  # Truncate
    
    return accounts
```

### Selection Validation (Submit Endpoint)

```python
def validate_account_selection(account_id, pending_accounts):
    """Validate user selection against pending session."""
    if not account_id:
        raise ValueError("No account ID provided")
    
    if not pending_accounts:
        raise ValueError("Session expired or invalid")
    
    # Find selected account in pending list
    selected = next(
        (acc for acc in pending_accounts if acc['id'] == account_id),
        None
    )
    
    if not selected:
        raise ValueError(
            f"Invalid account selection: {account_id} not in authorized list"
        )
    
    return selected
```

### Session Expiry Check

```python
def check_session_validity(request):
    """Check if pending account session is valid."""
    if 'basecamp_pending_accounts' not in request.session:
        return False, "Session expired or not found"
    
    if 'basecamp_pending_tokens' not in request.session:
        return False, "Session data incomplete"
    
    # Django automatically checks expiry when accessing session
    # If we get here, session is valid
    return True, None
```

---

## Error Scenarios

| Scenario | Detection | Action | User Impact |
|----------|-----------|--------|-------------|
| Session Expired | Key missing from `request.session` | Return 400 with `restart_oauth` action | Show error: "Session expired. Please connect again." |
| Invalid Account Selection | Selected ID not in pending list | Return 400 with `choose_again` action | Show error: "Invalid account. Please select again." |
| Session Data Incomplete | Missing tokens or accounts | Return 400 with `restart_oauth` action | Show error: "Session invalid. Please connect again." |
| Zero Accounts | OAuth returns empty list | Return 400 in callback | Show error: "No accounts available." |
| >20 Accounts | `len(accounts) > 20` | Truncate to 20 + log warning | User sees first 20 accounts (edge case) |

---

## Performance Characteristics

### Session Storage

**Write Performance**:
- Single session write per OAuth callback (~1-2KB JSON)
- O(1) write operation (Django session backend)
- No database indexes affected

**Read Performance**:
- Single session read per page load
- Single session read per selection submit
- O(1) read operation (session key lookup)

**Cleanup Performance**:
- Lazy cleanup (no background job)
- O(1) per expired session access
- Automatic via Django session framework

### Memory Usage

**Per User Session**:
- 20 accounts × ~100 bytes/account = ~2KB
- Tokens: ~500 bytes
- Total: ~2.5KB per pending session
- Max concurrent: Limited by active OAuth flows (typically <100)
- Peak memory: ~250KB for 100 concurrent selections

---

## Security Considerations

### Data Protection

1. **Tokens Never Exposed to Client**:
   - `pending_tokens` stored in session (HTTP-only cookie)
   - Only account IDs/names sent to frontend
   - Tokens only accessed server-side

2. **Session Security**:
   - HTTP-only cookie (prevents JavaScript access)
   - Secure flag in production (HTTPS only)
   - SameSite=Lax (CSRF protection)
   - 15-minute timeout (limits exposure window)

3. **Validation**:
   - Server validates all selections against session data
   - Cannot select account not in authorized list
   - Session expiry prevents stale/manipulated data

### Audit Trail

All operations logged with:
- User ID
- Timestamp
- Account ID/name (selected)
- Action (initiated, selected, expired, failed)

---

## Migration Requirements

**NONE** - No database migrations required. Feature uses existing `BasecampAccount` model and Django's built-in session framework.

---

## Testing Data

### Test Case 1: Single Account
```json
{
  "accounts": [
    {"id": "5612021", "name": "American Abstract LLC"}
  ]
}
```
**Expected**: Auto-connect without showing selection page

### Test Case 2: Multiple Accounts
```json
{
  "accounts": [
    {"id": "5612021", "name": "American Abstract LLC"},
    {"id": "7890123", "name": "Dudley Land Company"}
  ]
}
```
**Expected**: Show selection page with both accounts

### Test Case 3: Maximum Accounts
```json
{
  "accounts": [
    {"id": "1", "name": "Account 1"},
    {"id": "2", "name": "Account 2"},
    ...
    {"id": "20", "name": "Account 20"}
  ]
}
```
**Expected**: Show selection page with all 20 accounts (scrollable list)

### Test Case 4: Edge Case (>20 Accounts)
```json
{
  "accounts": [
    {"id": "1", "name": "Account 1"},
    ...
    {"id": "25", "name": "Account 25"}
  ]
}
```
**Expected**: Truncate to first 20, log warning, show selection page

---

## Dependencies

### Django Session Framework

**Configuration** (already exists in `settings.py`):
```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
]

INSTALLED_APPS = [
    'django.contrib.sessions',
    ...
]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # or cache, file
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True  # production
SESSION_COOKIE_SAMESITE = 'Lax'
```

**No changes required** - existing configuration supports this feature.

---

## Summary

This feature requires **no new database models or migrations**. All temporary data is stored in Django's session framework with a 15-minute timeout. The existing `BasecampAccount` model is used for persistent storage after user selection. Session-based storage provides security (HTTP-only cookies), automatic expiry, and lazy cleanup without additional infrastructure.

