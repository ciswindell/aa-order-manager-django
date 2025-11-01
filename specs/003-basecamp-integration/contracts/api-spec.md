# API Contract: Basecamp Integration

**Feature**: 003-basecamp-integration | **Date**: 2025-10-26 | **Phase**: 1 (Design)

## Overview

This document defines the REST API endpoints for Basecamp OAuth 2.0 integration. All endpoints follow Django REST Framework conventions and are protected by application authentication (JWT tokens in HTTP-only cookies).

**Base Path**: `/api/integrations/basecamp/`

**Authentication**: Required for all endpoints (JWT access token in HTTP-only cookie)

**CORS**: Configured with credentials support

## Endpoints

### 1. Initiate OAuth Connection

**Purpose**: Start Basecamp OAuth 2.0 authorization flow (FR-010)

```
POST /api/integrations/basecamp/connect/
```

**Request**:
- Headers:
  - `Cookie: access_token=<jwt>` (application authentication)
- Body: None

**Response** (200 OK):
```json
{
  "authorization_url": "https://launchpad.37signals.com/authorization/new?type=web_server&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={STATE}"
}
```

**Response Fields**:
- `authorization_url` (string): Full URL to redirect user to for Basecamp OAuth
  - Includes query parameters: `type`, `client_id`, `redirect_uri`, `state`
  - `state` parameter: CSRF protection token (stored in session)

**Error Responses**:

**401 Unauthorized**: User not authenticated
```json
{
  "error": "authentication_required",
  "message": "User must be logged in to connect Basecamp"
}
```

**400 Bad Request**: OAuth credentials not configured
```json
{
  "error": "configuration_error",
  "message": "Basecamp OAuth is not configured. Contact administrator."
}
```

**400 Bad Request**: User already has connected account (FR-014)
```json
{
  "error": "account_already_connected",
  "message": "You already have a Basecamp account connected. Disconnect first or use replace option.",
  "account_name": "Acme Corporation"
}
```

**Implementation Notes**:
- Generate and store `state` parameter in session for CSRF validation
- Check for existing BasecampAccount (FR-014)
- Return authorization URL, frontend redirects user
- Log connection attempt (FR-016)

---

### 2. OAuth Callback Handler

**Purpose**: Handle OAuth callback from Basecamp, exchange code for tokens (FR-001, FR-003)

```
GET /api/integrations/basecamp/callback/?code={CODE}&state={STATE}
```

**Request**:
- Headers:
  - `Cookie: access_token=<jwt>` (application authentication)
- Query Parameters:
  - `code` (string, required): OAuth authorization code from Basecamp
  - `state` (string, required): CSRF protection token (must match session)

**Response** (200 OK): Success page or redirect to integrations
```json
{
  "status": "connected",
  "account": {
    "account_id": "888888",
    "account_name": "Acme Corporation"
  }
}
```

**Response Fields**:
- `status` (string): "connected"
- `account.account_id` (string): Basecamp account ID (FR-018)
- `account.account_name` (string): Basecamp account name (FR-018)

**Error Responses**:

**401 Unauthorized**: User not authenticated
```json
{
  "error": "authentication_required",
  "message": "User must be logged in"
}
```

**400 Bad Request**: Invalid state parameter (CSRF)
```json
{
  "error": "invalid_state",
  "message": "Invalid OAuth state. Please try connecting again."
}
```

**400 Bad Request**: OAuth error from Basecamp
```json
{
  "error": "oauth_error",
  "message": "Basecamp authorization failed: {error_description}",
  "error_code": "{error}"
}
```

**500 Internal Server Error**: Token exchange failed
```json
{
  "error": "token_exchange_failed",
  "message": "Failed to exchange authorization code for access token"
}
```

**Implementation Notes**:
- Validate `state` parameter matches session (CSRF protection)
- Exchange `code` for tokens via Basecamp token endpoint
- Call Basecamp authorization.json to get account details
- Store account (check for existing first per FR-014)
- Encrypt refresh token before storage (FR-005)
- Log successful connection (FR-016)

---

### 3. Get Connection Status

**Purpose**: Retrieve current Basecamp connection status (FR-012)

```
GET /api/integrations/basecamp/status/
```

**Request**:
- Headers:
  - `Cookie: access_token=<jwt>` (application authentication)
- Body: None

**Response** (200 OK): Connected status
```json
{
  "provider": "basecamp",
  "status": "connected",
  "connected": true,
  "authenticated": true,
  "account_name": "Acme Corporation",
  "account_id": "888888",
  "connected_at": "2025-10-26T12:00:00Z",
  "cta_url": null
}
```

**Response** (200 OK): Disconnected status
```json
{
  "provider": "basecamp",
  "status": "not_connected",
  "connected": false,
  "authenticated": false,
  "account_name": null,
  "account_id": null,
  "connected_at": null,
  "cta_url": "/api/integrations/basecamp/connect/"
}
```

**Response** (200 OK): Token expired status (FR-009)
```json
{
  "provider": "basecamp",
  "status": "expired",
  "connected": true,
  "authenticated": false,
  "account_name": "Acme Corporation",
  "account_id": "888888",
  "connected_at": "2025-10-26T12:00:00Z",
  "cta_url": "/api/integrations/basecamp/connect/",
  "message": "Your Basecamp connection has expired. Please reconnect."
}
```

**Response Fields**:
- `provider` (string): Always "basecamp"
- `status` (string): "connected" | "not_connected" | "expired" | "error"
- `connected` (boolean): True if BasecampAccount exists
- `authenticated` (boolean): True if token valid and not expired
- `account_name` (string | null): Basecamp account name if connected (FR-012)
- `account_id` (string | null): Basecamp account ID if connected
- `connected_at` (string | null): ISO 8601 timestamp of connection
- `cta_url` (string | null): URL for "Connect" action if not connected (FR-013)
- `message` (string, optional): User-friendly status message

**Error Responses**:

**401 Unauthorized**: User not authenticated
```json
{
  "error": "authentication_required",
  "message": "User must be logged in"
}
```

**Implementation Notes**:
- Use BasecampStatusStrategy.assess() (existing pattern)
- Check token expiration (FR-009)
- Return within 1 second per SC-002
- Frontend polls this endpoint or uses TanStack Query

---

### 4. Disconnect Basecamp

**Purpose**: Revoke Basecamp access and delete stored credentials (FR-011)

```
DELETE /api/integrations/basecamp/disconnect/
```

**Request**:
- Headers:
  - `Cookie: access_token=<jwt>` (application authentication)
- Body: None

**Response** (200 OK):
```json
{
  "status": "disconnected",
  "message": "Basecamp account disconnected successfully"
}
```

**Error Responses**:

**401 Unauthorized**: User not authenticated
```json
{
  "error": "authentication_required",
  "message": "User must be logged in"
}
```

**404 Not Found**: No connected account
```json
{
  "error": "not_connected",
  "message": "No Basecamp account is currently connected"
}
```

**Implementation Notes**:
- Delete BasecampAccount record (CASCADE handles cleanup)
- Log disconnection event (FR-016)
- Optionally: Revoke token via Basecamp API (nice-to-have)

---

## External API: Basecamp OAuth Endpoints

These are **external Basecamp endpoints** called by backend, not exposed to frontend.

### Exchange Authorization Code for Tokens

**Basecamp Endpoint**:
```
POST https://launchpad.37signals.com/authorization/token
Content-Type: application/x-www-form-urlencoded
```

**Request Body**:
```
type=web_server
&client_id={BASECAMP_APP_KEY}
&client_secret={BASECAMP_APP_SECRET}
&redirect_uri={REDIRECT_URI}
&code={AUTHORIZATION_CODE}
```

**Response** (200 OK):
```json
{
  "access_token": "e2e6a6d6c8d5e5f7a8b9c0d1e2f3g4h5",
  "refresh_token": "r2e6a6d6c8d5e5f7a8b9c0d1e2f3g4h5",
  "expires_in": null,
  "token_type": "Bearer"
}
```

**Note**: Basecamp 3 tokens don't have `expires_in`, rely on refresh token for longevity

---

### Get Account Authorization Details

**Basecamp Endpoint**:
```
GET https://launchpad.37signals.com/authorization.json
Authorization: Bearer {ACCESS_TOKEN}
User-Agent: AA Order Manager (your-email@example.com)
```

**Response** (200 OK):
```json
{
  "expires_at": "2025-01-01T00:00:00-00:00",
  "identity": {
    "id": 9999999,
    "email_address": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "accounts": [
    {
      "product": "bc3",
      "id": 888888,
      "name": "Acme Corporation",
      "href": "https://3.basecampapi.com/888888"
    }
  ]
}
```

**Usage**:
- Called after token exchange to get account details
- Extract account ID and name for storage (FR-018)
- Used for token validation

---

### Refresh Access Token

**Basecamp Endpoint**:
```
POST https://launchpad.37signals.com/authorization/token
Content-Type: application/x-www-form-urlencoded
```

**Request Body**:
```
type=refresh
&refresh_token={REFRESH_TOKEN}
&client_id={BASECAMP_APP_KEY}
&client_secret={BASECAMP_APP_SECRET}
```

**Response** (200 OK):
```json
{
  "access_token": "new_e2e6a6d6c8d5e5f7a8b9c0d1e2f3g4h5",
  "token_type": "Bearer"
}
```

**Usage**:
- Called automatically when access token expires (FR-007)
- 95% success rate expected (SC-003)
- On failure: Show warning, allow app access, require re-auth (FR-008)

---

## Data Flow Diagrams

### OAuth Connection Flow

```
User (Browser)          Frontend (Next.js)      Backend (Django)        Basecamp OAuth
      |                        |                        |                       |
      |  Click "Connect"       |                        |                       |
      |----------------------->|                        |                       |
      |                        |  POST /basecamp/connect/                       |
      |                        |----------------------->|                       |
      |                        |                        | Generate state        |
      |                        |                        | Store in session      |
      |                        |  {authorization_url}   |                       |
      |                        |<-----------------------|                       |
      |  Redirect to Basecamp  |                        |                       |
      |<-----------------------|                        |                       |
      |                                                  |                       |
      |  Authorize app & select account                                         |
      |----------------------------------------------------------------------------->|
      |                                                                          | User approves
      |  Redirect to callback?code=XXX&state=YYY                               |
      |<-----------------------------------------------------------------------------|
      |                        |  GET /basecamp/callback/?code=XXX&state=YYY        |
      |                        |---------------------------------------->|           |
      |                        |                        | Validate state|           |
      |                        |                        | Exchange code |---------->|
      |                        |                        | for tokens    |           |
      |                        |                        |<--------------| {tokens}  |
      |                        |                        | Get account   |---------->|
      |                        |                        | details       |           |
      |                        |                        |<--------------| {account} |
      |                        |                        | Save account  |           |
      |                        |  {status: connected}   |               |           |
      |                        |<------------------------|               |           |
      |  Show success          |                        |               |           |
      |<-----------------------|                        |               |           |
```

### Status Check Flow

```
User (Browser)          Frontend (Next.js)      Backend (Django)        Database
      |                        |                        |                    |
      |  View integrations     |                        |                    |
      |----------------------->|                        |                    |
      |                        |  GET /basecamp/status/ |                    |
      |                        |----------------------->|                    |
      |                        |                        | Query user.basecamp_account
      |                        |                        |------------------->|
      |                        |                        |  BasecampAccount   |
      |                        |                        |<-------------------|
      |                        |                        | Check expiration   |
      |                        |                        | Build status DTO   |
      |                        |  {status: connected}   |                    |
      |                        |<-----------------------|                    |
      |  Display status        |                        |                    |
      |<-----------------------|                        |                    |
```

## Security Considerations

### CSRF Protection
- Use `state` parameter in OAuth flow (stored in session, validated on callback)
- Django's CSRF middleware protects POST/DELETE endpoints
- Frontend sends CSRF token in headers

### Token Storage
- Access tokens: Encrypted in transit (HTTPS), plaintext at rest (short-lived)
- Refresh tokens: Encrypted at rest using Django SECRET_KEY (FR-005)
- Application JWT tokens: HTTP-only cookies (existing pattern)

### Input Validation
- Validate `state` parameter matches session
- Validate OAuth `code` parameter format
- Validate Basecamp API responses before storing

### Rate Limiting
- Basecamp API: Standard HTTP 429 responses
- Backend should implement exponential backoff
- Status endpoint can be cached (ttl_seconds parameter)

## Error Handling

### User-Friendly Messages (FR-015)

| Error Scenario | User Message |
|---------------|-------------|
| OAuth denied | "Basecamp authorization was cancelled. Click 'Connect' to try again." |
| State mismatch | "Security check failed. Please try connecting again." |
| Token exchange failed | "Could not connect to Basecamp. Please try again later." |
| Already connected | "You already have a Basecamp account connected: {account_name}." |
| Network error | "Could not reach Basecamp. Check your internet connection." |
| Configuration error | "Basecamp integration is not configured. Contact support." |

### Logging (FR-016)

All authentication events logged with metadata:
- Timestamp (ISO 8601)
- User ID
- Action (connect, callback, refresh, disconnect)
- Status (success/failure)
- Error details (if failure)

Example log entry:
```
2025-10-26T12:00:00Z | INFO | Basecamp OAuth callback | user_id=123 | status=success | account_id=888888
```

## Testing Scenarios

### Happy Path
1. User clicks "Connect Basecamp"
2. User authorizes and selects account on Basecamp
3. Callback succeeds, account stored
4. Status endpoint returns "connected"

### Edge Cases
- User has multiple Basecamp accounts → Basecamp shows picker
- User already connected → Show error with account name
- OAuth state mismatch → Show security error
- Token exchange fails → Show connection error
- Token expired → Status shows "expired", prompt reconnect

### Error Recovery
- Callback failure → Allow retry (don't store partial data)
- Network timeout → Show retry option
- Token refresh failure → Warning banner (FR-008)

## Performance Requirements

- **SC-002**: Status endpoint responds within 1 second
- **SC-001**: OAuth flow completes within 2 minutes (mostly Basecamp external)
- Cache status checks where appropriate (ttl_seconds parameter)

## Frontend Integration

### Expected Frontend Calls

1. **Page Load**: Call `/status/` to display current state
2. **Connect Click**: Call `/connect/`, redirect to `authorization_url`
3. **After Callback**: Poll `/status/` to update UI
4. **Disconnect Click**: Call `/disconnect/`, update UI

### UI States

- **Not Connected**: Show "Connect Basecamp" button
- **Connected**: Show "Connected to {account_name}" with disconnect option
- **Expired**: Show warning with "Reconnect" button
- **Error**: Show error message with retry option

## Versioning

**API Version**: v1 (implicit in `/api/` prefix)

Future changes:
- Additive changes (new fields) are backward compatible
- Breaking changes require new version or migration plan

