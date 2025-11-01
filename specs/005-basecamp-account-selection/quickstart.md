# Quickstart: Basecamp OAuth Account Selection

**Feature**: 005-basecamp-account-selection  
**Date**: 2025-11-01  
**Purpose**: Quick implementation guide for developers

## Overview

Add account selection to Basecamp OAuth when users have access to multiple accounts. Currently auto-selects first account; this feature lets users choose which account to connect.

**Impact**: 1 modified file, 2 new endpoints, 1 new frontend page  
**No database migrations required** - uses Django session framework

---

## Implementation Checklist

### Backend Changes

- [ ] **1. Modify OAuth Callback** (`web/api/views/integrations.py`)
  - [ ] Detect multiple accounts (`len(accounts) > 1`)
  - [ ] Store accounts + tokens in session
  - [ ] Set 15-minute session expiry
  - [ ] Redirect to selection page for multiple accounts
  - [ ] Keep auto-select for single account

- [ ] **2. Add Get Pending Accounts Endpoint** (`web/api/views/integrations.py`)
  - [ ] Check session for pending accounts
  - [ ] Return 400 if session expired
  - [ ] Return accounts list if valid

- [ ] **3. Add Select Account Endpoint** (`web/api/views/integrations.py`)
  - [ ] Validate account_id against pending accounts
  - [ ] Save tokens with selected account
  - [ ] Clear session data
  - [ ] Return success response

- [ ] **4. Add URL Routes** (`web/api/urls.py`)
  - [ ] Route for get pending accounts: `/api/integrations/basecamp/pending-accounts/`
  - [ ] Route for select account: `/api/integrations/basecamp/select-account/`

- [ ] **5. Add Logging**
  - [ ] Log selection initiated (INFO)
  - [ ] Log account selected (INFO)
  - [ ] Log session expired (WARNING)
  - [ ] Log invalid selection (ERROR)

### Frontend Changes

- [ ] **6. Create Account Selection Page** (`frontend/src/app/basecamp/select-account/page.tsx`)
  - [ ] Fetch pending accounts on load
  - [ ] Display accounts with RadioGroup (shadcn/ui)
  - [ ] Handle session expiry error
  - [ ] Submit selection to backend
  - [ ] Redirect to dashboard on success

- [ ] **7. Install shadcn/ui Components** (if not already installed)
  - [ ] RadioGroup: `mcp_shadcn-ui_get_component("radio-group")`
  - [ ] Button: `mcp_shadcn-ui_get_component("button")`
  - [ ] Label: `mcp_shadcn-ui_get_component("label")`

### Testing

- [ ] **8. Manual Testing**
  - [ ] Test single account (auto-select behavior)
  - [ ] Test multiple accounts (selection page)
  - [ ] Test session expiry (wait 15+ min)
  - [ ] Test invalid selection (manipulate request)
  - [ ] Verify logs are written correctly

---

## Quick Implementation Guide

### Step 1: Modify OAuth Callback

**File**: `web/api/views/integrations.py`

**Find** the `basecamp_callback` function and **replace** the account handling logic:

```python
# BEFORE (current - around line 377)
accounts = auth_details.get("accounts", [])
account = accounts[0]  # Always first
account_id = str(account["id"])
account_name = account["name"]

# AFTER (new logic)
accounts = auth_details.get("accounts", [])

if len(accounts) == 0:
    return Response({'error': 'No accounts available'}, status=400)

elif len(accounts) == 1:
    # Auto-select single account (existing behavior)
    account = accounts[0]
    account_id = str(account["id"])
    account_name = account["name"]
    
    # Save tokens (existing code continues here)
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'account_id': account_id,
        'account_name': account_name,
        'expires_at': None,
        'scope': '',
        'token_type': 'Bearer',
    }
    save_tokens_for_user(request.user, tokens, provider='basecamp')
    
    logger.info(
        "Basecamp auto-connected | user_id=%s | account_id=%s | account_name=%s",
        request.user.id, account_id, account_name
    )
    
    return redirect("http://localhost:3000/dashboard?basecamp=connected")

else:  # len(accounts) > 1
    # NEW: Multiple accounts - store in session and redirect to selection
    if len(accounts) > 20:
        logger.warning(
            "User has %d Basecamp accounts, truncating to 20 | user_id=%s",
            len(accounts), request.user.id
        )
        accounts = accounts[:20]
    
    request.session['basecamp_pending_accounts'] = [
        {'id': str(acc['id']), 'name': acc['name']} 
        for acc in accounts
    ]
    request.session['basecamp_pending_tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    request.session.set_expiry(900)  # 15 minutes
    
    logger.info(
        "Basecamp account selection initiated | user_id=%s | accounts_count=%d",
        request.user.id, len(accounts)
    )
    
    return redirect("http://localhost:3000/basecamp/select-account")
```

---

### Step 2: Add New Endpoints

**File**: `web/api/views/integrations.py`

**Add at end of file** (before existing exports):

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_accounts(request):
    """Retrieve pending Basecamp accounts from session."""
    pending_accounts = request.session.get('basecamp_pending_accounts')
    
    if not pending_accounts:
        logger.warning(
            "Basecamp pending accounts session expired | user_id=%s",
            request.user.id
        )
        return Response({
            'error': 'Session expired or invalid',
            'action': 'restart_oauth',
            'message': 'Your session has expired. Please connect again.'
        }, status=400)
    
    logger.info(
        "Basecamp pending accounts retrieved | user_id=%s | accounts_count=%d",
        request.user.id, len(pending_accounts)
    )
    
    return Response({'accounts': pending_accounts})


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
        logger.warning(
            "Basecamp account selection failed - session expired | user_id=%s",
            request.user.id
        )
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
        logger.error(
            "Basecamp account selection failed - invalid account | user_id=%s | selected_id=%s | pending_count=%d",
            request.user.id, account_id, len(pending_accounts)
        )
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
    
    logger.info(
        "Basecamp account selected and connected | user_id=%s | account_id=%s | account_name=%s",
        request.user.id, selected['id'], selected['name']
    )
    
    return Response({
        'message': 'Account connected successfully',
        'account': selected
    })
```

---

### Step 3: Add URL Routes

**File**: `web/api/urls.py`

**Find** the integrations section and **add** these routes:

```python
from api.views.integrations import (
    # ... existing imports ...
    get_pending_accounts,      # ADD
    select_basecamp_account,   # ADD
)

urlpatterns = [
    # ... existing routes ...
    
    # ADD: Basecamp account selection endpoints
    path(
        "integrations/basecamp/pending-accounts/",
        get_pending_accounts,
        name="basecamp_pending_accounts",
    ),
    path(
        "integrations/basecamp/select-account/",
        select_basecamp_account,
        name="basecamp_select_account",
    ),
]
```

---

### Step 4: Create Frontend Page

**Create directory**:
```bash
mkdir -p frontend/src/app/basecamp/select-account
```

**File**: `frontend/src/app/basecamp/select-account/page.tsx`

**Get shadcn/ui components first** (if not installed):
```bash
# Use MCP tools to get component source
mcp_shadcn-ui_get_component("radio-group")
mcp_shadcn-ui_get_component("button")
mcp_shadcn-ui_get_component("label")
```

**Create page**:
```tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"

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
    fetch('http://localhost:8000/api/integrations/basecamp/pending-accounts/', {
      credentials: 'include',
      headers: {
        'Authorization': `Bearer ${document.cookie.match(/access_token=([^;]+)/)?.[1] || ''}`
      }
    })
      .then(async res => {
        const data = await res.json()
        if (res.ok && data.accounts) {
          setAccounts(data.accounts)
        } else {
          setError(data.message || 'Session expired')
        }
        setLoading(false)
      })
      .catch(() => {
        setError('Failed to load accounts. Please try again.')
        setLoading(false)
      })
  }, [])
  
  const handleConnect = async () => {
    if (!selectedAccountId) return
    
    setSubmitting(true)
    setError(null)
    
    try {
      const res = await fetch('http://localhost:8000/api/integrations/basecamp/select-account/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${document.cookie.match(/access_token=([^;]+)/)?.[1] || ''}`
        },
        body: JSON.stringify({ account_id: selectedAccountId })
      })
      
      const data = await res.json()
      
      if (res.ok) {
        router.push('/dashboard?basecamp=connected')
      } else {
        setError(data.message || 'Failed to connect account')
        setSubmitting(false)
      }
    } catch {
      setError('Network error. Please try again.')
      setSubmitting(false)
    }
  }
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading accounts...</p>
      </div>
    )
  }
  
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-red-600">{error}</p>
        <Button onClick={() => router.push('/integrations')}>
          Connect Again
        </Button>
      </div>
    )
  }
  
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="max-w-md w-full p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Select Basecamp Account</h1>
          <p className="text-gray-600 mt-2">
            You have access to multiple Basecamp accounts. Which one would you like to connect?
          </p>
        </div>
        
        <RadioGroup 
          value={selectedAccountId} 
          onValueChange={setSelectedAccountId}
          className="space-y-3"
        >
          {accounts.map(account => (
            <div key={account.id} className="flex items-center space-x-2 p-3 border rounded hover:bg-gray-50">
              <RadioGroupItem value={account.id} id={account.id} />
              <Label 
                htmlFor={account.id} 
                className="cursor-pointer flex-1"
              >
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
    </div>
  )
}
```

---

## Testing

### Manual Test Script

```bash
# Terminal 1: Start backend
cd web
python3 manage.py runserver

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser:
# 1. Navigate to http://localhost:3000/integrations
# 2. Click "Connect Basecamp"
# 3. Authorize on Basecamp (use account with multiple orgs)
# 4. Verify: Redirected to /basecamp/select-account
# 5. Verify: All accounts displayed
# 6. Select desired account
# 7. Click "Connect Selected Account"
# 8. Verify: Redirected to /dashboard?basecamp=connected
# 9. Verify: Dashboard shows correct account name

# Test session expiry:
# 1. Start OAuth flow
# 2. Wait on selection page for 15+ minutes
# 3. Try to select account
# 4. Verify: Error shown "Session expired"
# 5. Verify: "Connect Again" button present
# 6. Click button
# 7. Verify: Restarted OAuth flow

# Test single account:
# 1. Use account with only 1 Basecamp org
# 2. Click "Connect Basecamp"
# 3. Authorize on Basecamp
# 4. Verify: Immediately redirected to dashboard (no selection page)
```

### Verify Logs

```bash
# Check Django logs for these entries:
grep "Basecamp" web/logs/django.log

# Expected log entries:
# INFO: Basecamp account selection initiated | user_id=1 | accounts_count=2
# INFO: Basecamp pending accounts retrieved | user_id=1 | accounts_count=2
# INFO: Basecamp account selected and connected | user_id=1 | account_id=5612021 | account_name=American Abstract LLC
```

---

## Troubleshooting

### Issue: Selection page shows "Session expired" immediately

**Cause**: Session not being saved in OAuth callback

**Fix**: Ensure `SessionMiddleware` is enabled in `settings.py`:
```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

---

### Issue: "Invalid account selection" error when selecting valid account

**Cause**: Account ID format mismatch (integer vs string)

**Fix**: Ensure account IDs are converted to strings:
```python
request.session['basecamp_pending_accounts'] = [
    {'id': str(acc['id']), 'name': acc['name']}  # str() is important
    for acc in accounts
]
```

---

### Issue: Session data not clearing after selection

**Cause**: Session keys not being deleted

**Fix**: Explicitly delete session keys:
```python
del request.session['basecamp_pending_accounts']
del request.session['basecamp_pending_tokens']
request.session.modified = True  # Force save
```

---

### Issue: Frontend can't fetch pending accounts (CORS error)

**Cause**: CORS not configured for credentials

**Fix**: Verify CORS settings in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

---

## Performance Notes

- **Session storage**: ~2KB per user during selection (negligible impact)
- **Page load**: Single API call to fetch accounts (<100ms)
- **No database queries**: Session framework handles storage
- **Lazy cleanup**: Expired sessions auto-removed on access

---

## Success Criteria

✅ Single-account users: Auto-connected without selection page  
✅ Multi-account users: See selection page with all accounts  
✅ Session expires after 15 minutes with clear error  
✅ Invalid selections rejected with appropriate error  
✅ Logs show all events with user ID and context  
✅ Dashboard shows connected account name  
✅ No database migrations required

---

## Next Steps

After implementing this feature:
1. **Manual testing** with American Abstract LLC account (has multiple orgs)
2. **Verify logs** are written correctly
3. **Test edge cases** (session expiry, invalid selection)
4. **Create PR** and request code review
5. **Deploy to staging** for user acceptance testing

---

## Time Estimate

- Backend changes: 2-3 hours
- Frontend page: 1-2 hours
- Testing: 1 hour
- **Total**: 4-6 hours

---

## References

- **Feature Spec**: `specs/005-basecamp-account-selection/spec.md`
- **Research**: `specs/005-basecamp-account-selection/research.md`
- **Data Model**: `specs/005-basecamp-account-selection/data-model.md`
- **API Spec**: `specs/005-basecamp-account-selection/contracts/api-spec.md`
- **Django Sessions**: https://docs.djangoproject.com/en/5.2/topics/http/sessions/
- **shadcn/ui RadioGroup**: https://ui.shadcn.com/docs/components/radio-group

