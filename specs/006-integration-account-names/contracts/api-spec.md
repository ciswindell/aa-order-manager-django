# API Specification: Integration Account Names Display

**Feature**: Integration Account Names Display  
**Date**: November 2, 2025  
**Base URL**: `http://localhost:8000/api` (development) | `https://[production-domain]/api` (production)

---

## Overview

This specification documents the modifications to existing API endpoints to support displaying account names and connection timestamps for integrations.

**Modified Endpoints**: 1  
**New Endpoints**: 0  
**Authentication**: JWT tokens in HTTP-only cookies (existing)

---

## Modified Endpoints

### 1. Get Integration Status (Modified)

**Purpose**: Retrieve status and account information for all configured integrations

**Endpoint**: `GET /api/integrations/status/`

**Authentication**: Required (JWT access token in HTTP-only cookie)

**Request**: None (no query parameters or body)

**Response** (Modified):

**Status**: `200 OK`

**Content-Type**: `application/json`

**Body**:
```json
[
  {
    "provider": "basecamp",
    "is_connected": true,
    "is_authenticated": true,
    "last_sync": "2025-11-02T15:30:00Z",
    "blocking_problem": false,
    "reason": "Connected and ready",
    "cta_label": null,
    "cta_url": null,
    "account_name": "American Abstract LLC",
    "account_email": null,
    "connected_at": "2025-11-01T10:30:00Z"
  },
  {
    "provider": "dropbox",
    "is_connected": true,
    "is_authenticated": true,
    "last_sync": "2025-11-02T14:45:00Z",
    "blocking_problem": false,
    "reason": "Connected and ready",
    "cta_label": null,
    "cta_url": null,
    "account_name": "Chris Windell",
    "account_email": "chris@example.com",
    "connected_at": "2025-11-02T14:15:00Z"
  }
]
```

**New Fields**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `account_name` | `string \| null` | No | Account/organization name | `"American Abstract LLC"` |
| `account_email` | `string \| null` | No | Account email (Dropbox only) | `"chris@example.com"` |
| `connected_at` | `string \| null` | No | ISO 8601 timestamp of connection | `"2025-11-01T10:30:00Z"` |

**Field Population**:
- **Basecamp**: `account_name` = organization name, `account_email` = `null`
- **Dropbox (with info)**: `account_name` = display name, `account_email` = email address
- **Dropbox (legacy)**: `account_name` = `null`, `account_email` = `null`
- **All**: `connected_at` = timestamp from `created_at` field, or `null` if not available

**Response Examples**:

**Example 1: Both integrations connected with account info**
```json
[
  {
    "provider": "basecamp",
    "is_connected": true,
    "is_authenticated": true,
    "last_sync": "2025-11-02T15:30:00Z",
    "blocking_problem": false,
    "reason": "Connected and ready",
    "cta_label": null,
    "cta_url": null,
    "account_name": "American Abstract LLC",
    "account_email": null,
    "connected_at": "2025-11-01T10:30:00Z"
  },
  {
    "provider": "dropbox",
    "is_connected": true,
    "is_authenticated": true,
    "last_sync": "2025-11-02T14:45:00Z",
    "blocking_problem": false,
    "reason": "Connected and ready",
    "cta_label": null,
    "cta_url": null,
    "account_name": "Chris Windell",
    "account_email": "chris@example.com",
    "connected_at": "2025-11-02T14:15:00Z"
  }
]
```

**Example 2: Dropbox legacy connection (no account info)**
```json
[
  {
    "provider": "dropbox",
    "is_connected": true,
    "is_authenticated": true,
    "last_sync": "2025-10-15T09:30:00Z",
    "blocking_problem": false,
    "reason": "Connected and ready",
    "cta_label": null,
    "cta_url": null,
    "account_name": null,
    "account_email": null,
    "connected_at": "2025-10-15T09:20:00Z"
  }
]
```

**Example 3: Not connected**
```json
[
  {
    "provider": "basecamp",
    "is_connected": false,
    "is_authenticated": false,
    "last_sync": null,
    "blocking_problem": false,
    "reason": "Not connected",
    "cta_label": "Connect Basecamp",
    "cta_url": "/api/integrations/basecamp/connect/",
    "account_name": null,
    "account_email": null,
    "connected_at": null
  }
]
```

**Error Responses**:

| Status | Condition | Response Body |
|--------|-----------|---------------|
| `401 Unauthorized` | No valid JWT token | `{"detail": "Authentication credentials were not provided."}` |
| `403 Forbidden` | Invalid/expired token | `{"detail": "Given token not valid for any token type"}` |

**Performance**:
- Target response time: <200ms
- No additional database queries (fields in existing models)
- Cached for 10 minutes per user (existing TTL)

---

## Internal Endpoint (Modified OAuth Callback)

### Dropbox OAuth Callback (Internal Modification)

**Endpoint**: `GET /api/integrations/dropbox/callback/`

**Purpose**: Handle OAuth authorization and store account information

**Changes**: Add Dropbox API call to fetch account information

**Flow** (Modified):
1. Exchange authorization code for tokens (existing)
2. **NEW**: Call `dbx.users_get_current_account()` to fetch account info
3. **NEW**: Retry once after 2 seconds if call fails
4. **NEW**: Extract `display_name` and `email` from response
5. Save `DropboxAccount` with tokens **and** account info (modified)
6. Redirect to frontend dashboard (existing)

**Dropbox API Integration**:

**Method**: Uses Dropbox Python SDK

**Endpoint Called**: `users/get_current_account` (via `dbx.users_get_current_account()`)

**Response Structure**:
```python
FullAccount(
    account_id="dbid:...",
    name=Name(
        given_name="Chris",
        surname="Windell",
        familiar_name="Chris",
        display_name="Chris Windell",  # Used for account_name
        abbreviated_name="CW"
    ),
    email="chris@example.com",  # Used for account_email
    email_verified=True,
    disabled=False,
    ...
)
```

**Extracted Fields**:
- `account_info.name.display_name` → `DropboxAccount.display_name`
- `account_info.email` → `DropboxAccount.email`

**Error Handling**:
- First attempt fails → Wait 2 seconds → Retry
- Retry fails → Save connection without account info (empty strings)
- Frontend shows generic "Connected" message for empty account info

**No API Changes**: This is an internal backend modification, no new frontend-facing endpoints

---

## TypeScript Interface (Frontend)

**File**: `frontend/src/lib/api/types.ts`

**Modification**: Extend existing `IntegrationStatus` interface

```typescript
export interface IntegrationStatus {
  provider: string;
  is_connected: boolean;
  is_authenticated: boolean;
  last_sync: string;
  blocking_problem: boolean;
  reason: string;
  cta_label: string | null;
  cta_url: string | null;
  // NEW FIELDS:
  account_name?: string | null;
  account_email?: string | null;
  connected_at?: string | null;
}
```

**Usage in Frontend**:
```typescript
// Fetch integration status
const response = await getIntegrationStatus();
const integrations: IntegrationStatus[] = response.data;

// Display account info
integrations.forEach(integration => {
  if (integration.account_name) {
    console.log(`Connected as: ${integration.account_name}`);
  }
  if (integration.account_email) {
    console.log(`Email: ${integration.account_email}`);
  }
  if (integration.connected_at) {
    const date = format(new Date(integration.connected_at), 'MMM d, yyyy');
    console.log(`Connected on: ${date}`);
  }
});
```

---

## Testing Manual Procedures

### Test Case 1: Verify Basecamp account name display

**Setup**: User with connected Basecamp account "American Abstract LLC"

**Steps**:
1. Make authenticated GET request to `/api/integrations/status/`
2. Verify response includes Basecamp object with `account_name` = "American Abstract LLC"
3. Verify `account_email` = `null` for Basecamp
4. Verify `connected_at` is an ISO 8601 timestamp

**Expected Result**:
```json
{
  "provider": "basecamp",
  "account_name": "American Abstract LLC",
  "account_email": null,
  "connected_at": "2025-11-01T10:30:00Z"
}
```

---

### Test Case 2: Verify Dropbox account info after new connection

**Setup**: User connects new Dropbox account

**Steps**:
1. Complete Dropbox OAuth flow
2. Make authenticated GET request to `/api/integrations/status/`
3. Verify response includes Dropbox object with both `account_name` and `account_email` populated
4. Verify `connected_at` matches the connection timestamp

**Expected Result**:
```json
{
  "provider": "dropbox",
  "account_name": "Chris Windell",
  "account_email": "chris@example.com",
  "connected_at": "2025-11-02T14:15:00Z"
}
```

---

### Test Case 3: Verify legacy Dropbox connection (no account info)

**Setup**: User with Dropbox connection created before this feature

**Steps**:
1. Make authenticated GET request to `/api/integrations/status/`
2. Verify response includes Dropbox object with `account_name` = `null`
3. Verify `account_email` = `null`
4. Verify `connected_at` has the original connection timestamp

**Expected Result**:
```json
{
  "provider": "dropbox",
  "account_name": null,
  "account_email": null,
  "connected_at": "2025-10-15T09:20:00Z"
}
```

---

### Test Case 4: Verify Dropbox API failure handling

**Setup**: Simulate Dropbox API failure during OAuth

**Steps**:
1. Mock `dbx.users_get_current_account()` to raise exception
2. Complete Dropbox OAuth flow
3. Verify connection saved with empty `display_name` and `email`
4. Make authenticated GET request to `/api/integrations/status/`
5. Verify response includes Dropbox object with `account_name` = `null`

**Expected Result**: Connection succeeds, account info fields are null/empty, frontend shows generic "Connected" message

---

### Test Case 5: Verify authentication required

**Setup**: Unauthenticated request

**Steps**:
1. Make GET request to `/api/integrations/status/` without JWT cookie
2. Verify 401 Unauthorized response

**Expected Result**:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Backward Compatibility

**Breaking Changes**: None

**Deprecated Fields**: None

**Optional Fields**: All new fields (`account_name`, `account_email`, `connected_at`) are optional and nullable

**Client Compatibility**:
- Existing clients ignore new fields (additive change)
- Frontend updated to display new fields when present
- Legacy connections gracefully show generic "Connected" message

---

## Rate Limiting & Performance

**Endpoint Rate Limits**: None (existing authentication-based access control applies)

**Caching**: Existing 10-minute TTL cache per user maintained

**Dropbox API Rate Limit**: 
- Dropbox `users/get_current_account` endpoint: No specific limit documented, covered by general 3000 req/hour limit
- Only called during OAuth (infrequent operation)
- Single call per OAuth flow (not repeated)

**Performance Impact**:
- OAuth callback: +200-500ms for Dropbox account info fetch (acceptable during user wait)
- Status endpoint: No measurable impact (fields in same database table)

---

## Security Considerations

**PII in Logs**:
- Account names and emails MUST be masked in application logs
- Format: `"chris@example.com"` logged as `"ch***@ex***.com"`
- Masking function: `web/integrations/utils/log_masking.py`

**Access Control**:
- Integration status endpoint requires authentication (existing)
- Users can only see their own integration status (existing)
- No additional authorization logic needed

**Data Transmission**:
- All API calls over HTTPS (existing)
- JWT tokens in HTTP-only cookies (existing)
- No PII in URLs or query parameters

---

## Monitoring & Observability

**Metrics to Track**:
- Dropbox API success rate during OAuth (target: >95%)
- Status endpoint response time (target: <200ms)
- Account info population rate for new connections (target: 100% for new, N/A for legacy)

**Log Events** (with PII masking):
```
INFO: Dropbox account info fetched | user_id=123 | display_name=Ch***s Win***l
INFO: Integration status retrieved | user_id=123 | providers=basecamp,dropbox
WARNING: Dropbox account info fetch failed, retry scheduled | user_id=123
ERROR: Dropbox account info fetch failed after retry | user_id=123
```

**Alerts**:
- Dropbox API failure rate >10% over 1 hour
- Status endpoint p95 latency >500ms

