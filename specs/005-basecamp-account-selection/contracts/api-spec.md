# API Specification: Basecamp OAuth Account Selection

**Feature**: 005-basecamp-account-selection  
**Date**: 2025-11-01  
**Purpose**: Define API endpoints, request/response formats, and integration contracts

## Overview

This feature modifies the existing OAuth callback endpoint and adds a new account selection endpoint. All endpoints follow REST conventions and use JSON for request/response bodies.

---

## Endpoints

### 1. OAuth Callback (Modified)

**Purpose**: Handle OAuth authorization callback from Basecamp, detect multiple accounts, and redirect appropriately

```http
GET /integrations/basecamp/callback?code={code}&state={state}
```

**Authentication**: None (OAuth callback)

**Request Parameters**:
- `code` (query, required): OAuth authorization code from Basecamp
- `state` (query, required): CSRF protection state parameter

**Behavior Changes**:

**Before** (current implementation):
```python
accounts = auth_response['accounts']
account = accounts[0]  # Always select first account
save_tokens(account)
redirect('/dashboard?basecamp=connected')
```

**After** (new implementation):
```python
accounts = auth_response['accounts']

if len(accounts) == 1:
    # Auto-select single account (same as before)
    account = accounts[0]
    save_tokens(account)
    redirect('/dashboard?basecamp=connected')
    
elif len(accounts) > 1:
    # NEW: Store in session and redirect to selection
    request.session['basecamp_pending_accounts'] = [
        {'id': str(acc['id']), 'name': acc['name']} 
        for acc in accounts
    ]
    request.session['basecamp_pending_tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    request.session.set_expiry(900)  # 15 minutes
    redirect('/basecamp/select-account')
```

**Response** (Single Account):
- Status: `302 Found`
- Location: `http://localhost:3000/dashboard?basecamp=connected`
- Set-Cookie: (existing JWT tokens)

**Response** (Multiple Accounts):
- Status: `302 Found`
- Location: `http://localhost:3000/basecamp/select-account`
- Set-Cookie: `sessionid=...` (with pending account data)

**Error Responses**:

**400 Bad Request** - Invalid OAuth code
```json
{
  "error": "Invalid authorization code",
  "detail": "The OAuth code is invalid or has expired"
}
```

**400 Bad Request** - No accounts available
```json
{
  "error": "No accounts available",
  "detail": "OAuth authorization did not return any Basecamp accounts"
}
```

**Logging**:
```python
# Single account
logger.info(
    "Basecamp auto-connected | user_id=%s | account_id=%s | account_name=%s",
    user.id, account['id'], account['name']
)

# Multiple accounts
logger.info(
    "Basecamp account selection initiated | user_id=%s | accounts_count=%d",
    user.id, len(accounts)
)
```

**Modified File**: `web/api/views/integrations.py` - function `basecamp_callback`

---

### 2. Get Pending Accounts (New)

**Purpose**: Retrieve pending account list for selection page (validates session is active)

```http
GET /api/integrations/basecamp/pending-accounts
```

**Authentication**: Required (session cookie)

**Request Headers**:
```http
Cookie: sessionid=...
```

**Response** (200 OK):
```json
{
  "accounts": [
    {
      "id": "5612021",
      "name": "American Abstract LLC"
    },
    {
      "id": "7890123",
      "name": "Dudley Land Company"
    }
  ]
}
```

**Response Fields**:
- `accounts` (array): List of available Basecamp accounts
  - `id` (string): Basecamp account ID
  - `name` (string): Human-readable account name

**Error Responses**:

**400 Bad Request** - Session expired or invalid
```json
{
  "error": "Session expired or invalid",
  "action": "restart_oauth",
  "message": "Your session has expired. Please connect again."
}
```

**401 Unauthorized** - Not authenticated
```json
{
  "error": "Authentication required",
  "detail": "You must be logged in to access this endpoint"
}
```

**Implementation**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_accounts(request):
    """Retrieve pending Basecamp accounts from session."""
    pending_accounts = request.session.get('basecamp_pending_accounts')
    
    if not pending_accounts:
        return Response({
            'error': 'Session expired or invalid',
            'action': 'restart_oauth',
            'message': 'Your session has expired. Please connect again.'
        }, status=400)
    
    return Response({'accounts': pending_accounts})
```

**Logging**:
```python
# Success
logger.info(
    "Basecamp pending accounts retrieved | user_id=%s | accounts_count=%d",
    request.user.id, len(pending_accounts)
)

# Session expired
logger.warning(
    "Basecamp pending accounts session expired | user_id=%s",
    request.user.id
)
```

**New File**: Add to `web/api/views/integrations.py`  
**Route**: Add to `web/api/urls.py`

---

### 3. Select Basecamp Account (New)

**Purpose**: Complete OAuth connection with user-selected Basecamp account

```http
POST /api/integrations/basecamp/select-account
```

**Authentication**: Required (session cookie)

**Request Headers**:
```http
Content-Type: application/json
Cookie: sessionid=...
```

**Request Body**:
```json
{
  "account_id": "5612021"
}
```

**Request Fields**:
- `account_id` (string, required): ID of selected Basecamp account (must match one from pending accounts)

**Response** (200 OK):
```json
{
  "message": "Account connected successfully",
  "account": {
    "id": "5612021",
    "name": "American Abstract LLC"
  }
}
```

**Response Fields**:
- `message` (string): Success message
- `account` (object): Connected account details
  - `id` (string): Basecamp account ID
  - `name` (string): Account name

**Error Responses**:

**400 Bad Request** - Missing account_id
```json
{
  "error": "Missing required field",
  "detail": "account_id is required"
}
```

**400 Bad Request** - Session expired
```json
{
  "error": "Session expired or invalid",
  "action": "restart_oauth",
  "message": "Your session has expired. Please connect again."
}
```

**400 Bad Request** - Invalid account selection
```json
{
  "error": "Invalid account selection",
  "action": "choose_again",
  "message": "The selected account is not in your authorized list",
  "detail": "Account ID '12345' not found in pending accounts"
}
```

**401 Unauthorized** - Not authenticated
```json
{
  "error": "Authentication required",
  "detail": "You must be logged in to complete account selection"
}
```

**Implementation**:
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_basecamp_account(request):
    """Complete Basecamp OAuth with user-selected account."""
    account_id = request.data.get('account_id')
    
    if not account_id:
        return Response({
            'error': 'Missing required field',
            'detail': 'account_id is required'
        }, status=400)
    
    # Retrieve pending data from session
    pending_accounts = request.session.get('basecamp_pending_accounts', [])
    pending_tokens = request.session.get('basecamp_pending_tokens', {})
    
    if not pending_accounts or not pending_tokens:
        return Response({
            'error': 'Session expired or invalid',
            'action': 'restart_oauth',
            'message': 'Your session has expired. Please connect again.'
        }, status=400)
    
    # Validate selection against pending accounts
    selected = next(
        (acc for acc in pending_accounts if acc['id'] == account_id),
        None
    )
    
    if not selected:
        return Response({
            'error': 'Invalid account selection',
            'action': 'choose_again',
            'message': 'The selected account is not in your authorized list',
            'detail': f"Account ID '{account_id}' not found in pending accounts"
        }, status=400)
    
    # Save tokens with selected account
    tokens = {
        'access_token': pending_tokens['access_token'],
        'refresh_token': pending_tokens['refresh_token'],
        'account_id': str(selected['id']),
        'account_name': selected['name'],
        'expires_at': None,
        'scope': '',
        'token_type': 'Bearer',
    }
    save_tokens_for_user(request.user, tokens, provider='basecamp')
    
    # Clear session
    del request.session['basecamp_pending_accounts']
    del request.session['basecamp_pending_tokens']
    
    return Response({
        'message': 'Account connected successfully',
        'account': selected
    })
```

**Logging**:
```python
# Success
logger.info(
    "Basecamp account selected and connected | user_id=%s | account_id=%s | account_name=%s",
    request.user.id, selected['id'], selected['name']
)

# Session expired
logger.warning(
    "Basecamp account selection failed - session expired | user_id=%s",
    request.user.id
)

# Invalid selection
logger.error(
    "Basecamp account selection failed - invalid account | user_id=%s | selected_id=%s | pending_count=%d",
    request.user.id, account_id, len(pending_accounts)
)
```

**New File**: Add to `web/api/views/integrations.py`  
**Route**: Add to `web/api/urls.py`

---

## Frontend Integration

### Account Selection Page

**Route**: `/basecamp/select-account`

**Component**: `frontend/src/app/basecamp/select-account/page.tsx`

**Implementation Pattern**:

```tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { api } from '@/lib/api'

interface Account {
  id: string
  name: string
}

export default function SelectBasecampAccount() {
  const router = useRouter()
  const [accounts, setAccounts] = useState<Account[]>([])
  const [selectedAccountId, setSelectedAccountId] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  
  useEffect(() => {
    // Fetch pending accounts on page load
    api.get('/integrations/basecamp/pending-accounts', {
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        if (data.accounts) {
          setAccounts(data.accounts)
          setLoading(false)
        } else if (data.error) {
          setError(data.message || 'Session expired')
          setLoading(false)
        }
      })
      .catch(err => {
        setError('Failed to load accounts. Please try again.')
        setLoading(false)
      })
  }, [])
  
  const handleConnect = async () => {
    if (!selectedAccountId) return
    
    setSubmitting(true)
    setError(null)
    
    try {
      const res = await api.post('/integrations/basecamp/select-account', {
        account_id: selectedAccountId
      }, { credentials: 'include' })
      
      const data = await res.json()
      
      if (res.ok) {
        router.push('/dashboard?basecamp=connected')
      } else {
        setError(data.message || 'Failed to connect account')
        setSubmitting(false)
      }
    } catch (err) {
      setError('Network error. Please try again.')
      setSubmitting(false)
    }
  }
  
  if (loading) {
    return <div>Loading accounts...</div>
  }
  
  if (error) {
    return (
      <div>
        <p className="text-red-600">{error}</p>
        <Button onClick={() => router.push('/integrations')}>
          Connect Again
        </Button>
      </div>
    )
  }
  
  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Select Basecamp Account</h1>
      <p className="text-gray-600 mb-6">
        You have access to multiple Basecamp accounts. Which one would you like to connect?
      </p>
      
      <RadioGroup 
        value={selectedAccountId} 
        onValueChange={setSelectedAccountId}
        className="space-y-3 mb-6"
      >
        {accounts.map(account => (
          <div key={account.id} className="flex items-center space-x-2">
            <RadioGroupItem value={account.id} id={account.id} />
            <Label htmlFor={account.id} className="cursor-pointer">
              {account.name}
            </Label>
          </div>
        ))}
      </RadioGroup>
      
      <Button 
        onClick={handleConnect} 
        disabled={!selectedAccountId || submitting}
        className="w-full"
      >
        {submitting ? 'Connecting...' : 'Connect Selected Account'}
      </Button>
    </div>
  )
}
```

---

## URL Routes

### Backend Routes (Add to `web/api/urls.py`)

```python
from django.urls import path
from api.views.integrations import (
    basecamp_callback,  # MODIFY existing
    get_pending_accounts,  # NEW
    select_basecamp_account,  # NEW
)

urlpatterns = [
    # ... existing routes ...
    
    # MODIFY existing callback (no route change, just implementation)
    path(
        "integrations/basecamp/callback/",
        basecamp_callback,
        name="basecamp_callback",
    ),
    
    # NEW: Get pending accounts
    path(
        "integrations/basecamp/pending-accounts/",
        get_pending_accounts,
        name="basecamp_pending_accounts",
    ),
    
    # NEW: Select account
    path(
        "integrations/basecamp/select-account/",
        select_basecamp_account,
        name="basecamp_select_account",
    ),
]
```

### Frontend Routes (Next.js App Router)

```text
app/
└── basecamp/
    └── select-account/
        └── page.tsx  # NEW: Account selection page
```

**Route**: `http://localhost:3000/basecamp/select-account`

**Protection**: None (accessed during OAuth flow before authentication completes)

---

## Session Management

### Session Keys

| Key | Type | Purpose | Lifetime |
|-----|------|---------|----------|
| `basecamp_pending_accounts` | list[dict] | Available accounts for selection | 15 minutes |
| `basecamp_pending_tokens` | dict | OAuth tokens for connection | 15 minutes |

### Session Operations

**Create** (in OAuth callback):
```python
request.session['basecamp_pending_accounts'] = accounts
request.session['basecamp_pending_tokens'] = tokens
request.session.set_expiry(900)  # 15 minutes
```

**Read** (in pending accounts endpoint):
```python
accounts = request.session.get('basecamp_pending_accounts', [])
if not accounts:
    # Session expired
```

**Delete** (in select account endpoint):
```python
del request.session['basecamp_pending_accounts']
del request.session['basecamp_pending_tokens']
```

**Expiry Check** (automatic):
- Django checks expiry when accessing `request.session`
- If expired, keys return `None` or missing
- No manual expiry check needed

---

## Testing

### Manual Testing Checklist

**Test 1: Single Account (Auto-Select)**
1. Connect Basecamp with single-account user
2. Verify: Redirected to dashboard immediately
3. Verify: No selection page shown
4. Verify: Account connected in database

**Test 2: Multiple Accounts (Selection)**
1. Connect Basecamp with multi-account user (American Abstract)
2. Verify: Redirected to `/basecamp/select-account`
3. Verify: All accounts displayed
4. Select "American Abstract LLC"
5. Click "Connect Selected Account"
6. Verify: Redirected to dashboard with success message
7. Verify: Correct account ID saved in database

**Test 3: Session Expiry**
1. Connect Basecamp with multi-account user
2. Wait 15+ minutes on selection page
3. Try to select account
4. Verify: Error message "Session expired"
5. Verify: "Connect Again" button shown
6. Click button
7. Verify: Restarted OAuth flow

**Test 4: Invalid Selection**
1. Connect Basecamp with multi-account user
2. Intercept POST request
3. Modify `account_id` to invalid value
4. Submit request
5. Verify: 400 error returned
6. Verify: Error logged with user ID and invalid account

**Test 5: Maximum Accounts (20)**
1. Connect with user having 20+ accounts
2. Verify: First 20 accounts shown
3. Verify: Warning logged about truncation
4. Select any account from list
5. Verify: Connection succeeds

### cURL Examples

**Get Pending Accounts**:
```bash
curl -X GET \
  http://localhost:8000/api/integrations/basecamp/pending-accounts \
  -H 'Cookie: sessionid=...' \
  -H 'Authorization: Bearer ...'
```

**Select Account**:
```bash
curl -X POST \
  http://localhost:8000/api/integrations/basecamp/select-account \
  -H 'Content-Type: application/json' \
  -H 'Cookie: sessionid=...' \
  -H 'Authorization: Bearer ...' \
  -d '{
    "account_id": "5612021"
  }'
```

---

## Security

### Authentication & Authorization

| Endpoint | Auth Required | Permission | Session Required |
|----------|---------------|------------|------------------|
| OAuth Callback | No | None | No (creates session) |
| Get Pending Accounts | Yes | IsAuthenticated | Yes (reads session) |
| Select Account | Yes | IsAuthenticated | Yes (reads/clears session) |

### Data Protection

1. **Tokens Never Exposed**:
   - Stored in session (HTTP-only cookie)
   - Never sent to frontend
   - Only accessed server-side

2. **Session Security**:
   - HTTP-only cookies (no JavaScript access)
   - Secure flag in production (HTTPS only)
   - SameSite=Lax (CSRF protection)
   - 15-minute timeout

3. **Validation**:
   - Server validates all account selections
   - Cannot select unauthorized account
   - Session expiry enforced

---

## Error Handling

### Error Response Format

All error responses follow this structure:

```json
{
  "error": "Error type/category",
  "message": "User-friendly error message",
  "detail": "Technical details (optional)",
  "action": "recovery_action (optional)"
}
```

### Recovery Actions

| Action | Meaning | Frontend Behavior |
|--------|---------|-------------------|
| `restart_oauth` | Session expired, restart OAuth flow | Show "Connect Again" button → `/integrations` |
| `choose_again` | Invalid selection, let user retry | Show error, keep selection page open |
| None | Fatal error | Show error, provide "Go Back" button |

---

## Logging

### Log Levels

| Event | Level | Message Template |
|-------|-------|------------------|
| Selection initiated | INFO | `Basecamp account selection initiated \| user_id=%s \| accounts_count=%d` |
| Account selected | INFO | `Basecamp account selected and connected \| user_id=%s \| account_id=%s \| account_name=%s` |
| Auto-connected (single) | INFO | `Basecamp auto-connected \| user_id=%s \| account_id=%s \| account_name=%s` |
| Session expired | WARNING | `Basecamp account selection failed - session expired \| user_id=%s` |
| Invalid selection | ERROR | `Basecamp account selection failed - invalid account \| user_id=%s \| selected_id=%s \| pending_count=%d` |
| >20 accounts | WARNING | `User has %d Basecamp accounts, truncating to 20 \| user_id=%s` |

### Log Context

All logs include:
- User ID
- Timestamp (automatic)
- Feature context (Basecamp account selection)
- Action-specific data (account IDs, counts)

---

## Summary

This feature adds **one modified endpoint** (OAuth callback) and **two new endpoints** (get pending accounts, select account). All endpoints follow REST conventions, use JSON for data exchange, and implement proper error handling with recovery actions. Session management uses Django's built-in framework with HTTP-only cookies for security. The frontend adds a single account selection page using shadcn/ui components.

