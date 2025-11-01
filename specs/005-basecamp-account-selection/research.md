# Research: Basecamp OAuth Account Selection

**Feature**: 005-basecamp-account-selection  
**Date**: 2025-11-01  
**Purpose**: Document technical decisions, patterns, and best practices for implementing OAuth account selection

## Research Questions

### Q1: How should pending account data be stored during OAuth selection?

**Decision**: Use Django session framework with JSON-serialized account data

**Rationale**:
- Django session framework is already configured and available in the project
- Session cookies are HTTP-only and secure (aligns with security requirements)
- 15-minute timeout is easily configurable via `SESSION_COOKIE_AGE` for temporary data
- Lazy cleanup pattern is built-in (sessions checked on access)
- No additional infrastructure needed (vs. Redis, database table)

**Implementation**:
```python
# Store pending data in session
request.session['basecamp_pending_accounts'] = [
    {'id': '12345', 'name': 'American Abstract LLC'},
    {'id': '67890', 'name': 'Dudley Land Company'}
]
request.session['basecamp_pending_tokens'] = {
    'access_token': '...',
    'refresh_token': '...'
}
request.session.set_expiry(900)  # 15 minutes
```

**Alternatives Considered**:
- ❌ Database table: Overkill for temporary data, requires migration and cleanup job
- ❌ Redis cache: Requires additional infrastructure, existing sessions work fine
- ❌ URL parameters: Security risk (tokens in URL), length limits with many accounts

**References**:
- Django session docs: https://docs.djangoproject.com/en/5.2/topics/http/sessions/
- OAuth 2.0 RFC 6749 (state parameter patterns): https://tools.ietf.org/html/rfc6749#section-10.12

---

### Q2: What session timeout pattern should be used?

**Decision**: Per-request session expiry with 15-minute timeout

**Rationale**:
- `request.session.set_expiry(900)` sets absolute timeout from session creation
- Prevents indefinite session storage while allowing reasonable user time
- Lazy cleanup: Django automatically purges expired sessions on access attempt
- No background job needed (aligns with project's simplicity principle)

**Implementation**:
```python
# Set 15-minute absolute timeout after OAuth callback
request.session.set_expiry(900)

# Validate on selection endpoint
if 'basecamp_pending_accounts' not in request.session:
    return Response({
        'error': 'Session expired or invalid',
        'action': 'restart_oauth'
    }, status=400)
```

**Alternatives Considered**:
- ❌ Idle timeout (sliding window): More complex, unnecessary for one-time flow
- ❌ Background cleanup job: Violates DRY (Django handles this), adds complexity
- ❌ Manual expiry checks: Reinventing Django's session framework

**References**:
- Django session.set_expiry() docs: https://docs.djangoproject.com/en/5.2/topics/http/sessions/#django.contrib.sessions.backends.base.SessionBase.set_expiry

---

### Q3: How should OAuth callback detect multiple accounts?

**Decision**: Check length of `accounts` array in authorization response

**Rationale**:
- Basecamp OAuth authorization returns `accounts` array in response
- Simple length check: `if len(accounts) > 1` triggers selection flow
- Auto-select for single account: `if len(accounts) == 1` maintains current behavior
- Zero accounts: Edge case handled by OAuth error (shouldn't happen with valid token)

**Implementation**:
```python
# In basecamp_callback view
accounts = auth_details.get("accounts", [])

if len(accounts) == 0:
    return Response({'error': 'No accounts available'}, status=400)
elif len(accounts) == 1:
    # Auto-select single account (existing behavior)
    account = accounts[0]
    save_tokens_for_user(request.user, tokens, provider='basecamp')
    return redirect('http://localhost:3000/dashboard?basecamp=connected')
else:
    # Multiple accounts - store in session and redirect to selection
    request.session['basecamp_pending_accounts'] = [
        {'id': str(acc['id']), 'name': acc['name']} 
        for acc in accounts
    ]
    request.session['basecamp_pending_tokens'] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }
    request.session.set_expiry(900)
    return redirect('http://localhost:3000/basecamp/select-account')
```

**Alternatives Considered**:
- ❌ Always show selection: Degrades UX for single-account users (majority case)
- ❌ Configure per-user preference: Premature optimization, adds complexity

---

### Q4: What UI component should be used for account selection?

**Decision**: shadcn/ui RadioGroup component

**Rationale**:
- Enforces single selection (requirement: user selects exactly one account)
- Accessible (ARIA-compliant, keyboard navigation)
- Consistent with project's shadcn/ui component library
- Clear visual indication of selected account

**Implementation**:
```tsx
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"

<RadioGroup value={selectedAccountId} onValueChange={setSelectedAccountId}>
  {accounts.map(account => (
    <div key={account.id} className="flex items-center space-x-2">
      <RadioGroupItem value={account.id} id={account.id} />
      <Label htmlFor={account.id}>{account.name}</Label>
    </div>
  ))}
</RadioGroup>
```

**Alternatives Considered**:
- ❌ Select dropdown: Less visible, harder to scan multiple options
- ❌ Button grid: Works but RadioGroup is more semantically correct for single selection
- ❌ Custom component: Reinventing wheel, shadcn provides accessible implementation

**References**:
- shadcn RadioGroup: https://ui.shadcn.com/docs/components/radio-group
- Available via: `mcp_shadcn-ui_get_component("radio-group")`

---

### Q5: How should account selection validate against pending session?

**Decision**: Server-side validation in selection endpoint before saving tokens

**Rationale**:
- Never trust client input (security principle)
- Validate selected account ID exists in pending accounts list
- Prevent race conditions (account access changed between OAuth and selection)
- Return clear error if validation fails

**Implementation**:
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_basecamp_account(request):
    account_id = request.data.get('account_id')
    
    # Retrieve pending data from session
    pending_accounts = request.session.get('basecamp_pending_accounts', [])
    pending_tokens = request.session.get('basecamp_pending_tokens', {})
    
    if not pending_accounts or not pending_tokens:
        return Response({
            'error': 'Session expired or invalid',
            'action': 'restart_oauth'
        }, status=400)
    
    # Validate selection against pending accounts
    selected = next((a for a in pending_accounts if a['id'] == account_id), None)
    if not selected:
        return Response({
            'error': 'Invalid account selection',
            'action': 'choose_again'
        }, status=400)
    
    # Save tokens with validated account
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
        'message': 'Account connected',
        'account': selected
    })
```

**Alternatives Considered**:
- ❌ Client-side only validation: Security risk, easy to bypass
- ❌ Trust any account ID: Allows connecting to unauthorized accounts
- ❌ Skip validation: Could store invalid data, break integration

---

### Q6: How should frontend handle session expiry during selection?

**Decision**: Check for pending accounts on page load, redirect to OAuth if missing

**Rationale**:
- Session data must exist for selection page to function
- If session expired/missing, user needs to restart OAuth flow
- Clear error message and recovery path (FR-010)
- Prevents showing empty/broken selection page

**Implementation**:
```tsx
// frontend/src/app/basecamp/select-account/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function SelectBasecampAccount() {
  const router = useRouter()
  const [accounts, setAccounts] = useState([])
  const [error, setError] = useState(null)
  
  useEffect(() => {
    // Check if pending accounts exist in session
    fetch('/api/basecamp/pending-accounts', { credentials: 'include' })
      .then(res => {
        if (res.status === 400) {
          // Session expired
          setError('Your session has expired. Please connect again.')
        } else {
          return res.json()
        }
      })
      .then(data => {
        if (data?.accounts) {
          setAccounts(data.accounts)
        }
      })
      .catch(() => {
        setError('Failed to load accounts. Please try again.')
      })
  }, [])
  
  if (error) {
    return (
      <div>
        <p>{error}</p>
        <Button onClick={() => router.push('/integrations')}>
          Connect Again
        </Button>
      </div>
    )
  }
  
  // ... rest of component
}
```

**Alternatives Considered**:
- ❌ No session check: Shows broken page, confusing user experience
- ❌ Optimistic render: Causes layout shift, poor UX
- ❌ Fetch on submit only: User wastes time selecting before learning session expired

---

### Q7: What logging should be implemented?

**Decision**: Log key events with structured context (user ID, timestamp, account info)

**Rationale**:
- Security auditing: Track who connected which account
- Troubleshooting: Identify session expiry vs. validation failures
- Debugging: Understand multi-account flow behavior
- Aligns with existing logging pattern in `basecamp_service.py`

**Implementation**:
```python
import logging
logger = logging.getLogger(__name__)

# In OAuth callback (multiple accounts detected)
logger.info(
    "Basecamp account selection initiated | user_id=%s | accounts_count=%d",
    request.user.id,
    len(accounts)
)

# In selection endpoint (account chosen)
logger.info(
    "Basecamp account selected | user_id=%s | account_id=%s | account_name=%s",
    request.user.id,
    selected['id'],
    selected['name']
)

# Session expiry
logger.warning(
    "Basecamp account selection session expired | user_id=%s",
    request.user.id
)

# Validation failure
logger.error(
    "Basecamp account selection invalid | user_id=%s | selected_id=%s | pending_count=%d",
    request.user.id,
    account_id,
    len(pending_accounts)
)
```

**Alternatives Considered**:
- ❌ Debug logging only: Insufficient for security auditing
- ❌ Verbose logging: Creates noise, includes sensitive token data
- ❌ No logging: Cannot troubleshoot production issues

**References**:
- Existing pattern in `web/integrations/basecamp/basecamp_service.py` (lines 150-200)

---

## Implementation Patterns

### OAuth Flow Pattern (Before)
```
User clicks "Connect Basecamp"
  → Redirect to Basecamp OAuth
  → User authorizes
  → Callback receives accounts array
  → Auto-select accounts[0]  ⚠️ Problem: No user control
  → Save to database
  → Redirect to dashboard
```

### OAuth Flow Pattern (After)
```
User clicks "Connect Basecamp"
  → Redirect to Basecamp OAuth
  → User authorizes
  → Callback receives accounts array
  → IF len(accounts) == 1:
      → Auto-select (existing behavior)
      → Save to database
      → Redirect to dashboard
  → ELSE len(accounts) > 1:
      → Store accounts + tokens in session (15-min timeout)
      → Redirect to account selection page
      → User selects account
      → POST /api/basecamp/select-account
      → Validate selection against session
      → Save to database
      → Clear session
      → Redirect to dashboard
```

### Error Recovery Pattern
```
Session expires during selection
  → User clicks "Connect Selected Account"
  → Backend returns 400 with action: 'restart_oauth'
  → Frontend shows error: "Your session has expired. Please connect again."
  → User clicks "Connect Again"
  → Restarts OAuth flow
```

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Session Storage | Django session framework | Already configured, secure, lazy cleanup built-in |
| Session Timeout | 15 minutes absolute | Balances security and user experience per clarifications |
| Cleanup Strategy | Lazy (on access) | Built into Django sessions, no background job needed |
| UI Component | shadcn RadioGroup | Enforces single selection, accessible, project standard |
| Validation | Server-side in endpoint | Security requirement, never trust client |
| Logging | INFO level for events | Security audit trail, troubleshooting, error tracking |
| Account Limit | 20 accounts | Per clarifications, no pagination/search needed |
| Frontend Framework | Next.js App Router | Project standard, new page under app/basecamp/ |
| API Style | REST POST endpoint | Consistent with existing integration endpoints |

---

## Dependencies

### Existing Code (No Changes)
- `web/integrations/models.py`: `BasecampAccount` model (OneToOne with User)
- `web/integrations/basecamp/basecamp_service.py`: API methods for project/task management
- Django session middleware (already enabled)
- Next.js frontend with TanStack Query

### Modified Code
- `web/api/views/integrations.py`: OAuth callback logic (add multi-account detection)
- `web/api/urls.py`: Add `/integrations/basecamp/select-account/` route

### New Code
- `frontend/src/app/basecamp/select-account/page.tsx`: Account selection UI
- Backend endpoint for account selection (in `integrations.py`)
- Optional: Backend endpoint to fetch pending accounts for page load validation

---

## Performance Considerations

**Session Storage**:
- Impact: Minimal (JSON serialization of 1-20 account objects, ~1-2KB per session)
- Cleanup: Automatic via Django's lazy cleanup on session access
- No index needed (session framework handles lookups)

**Account Selection Page**:
- Target: Load within 2 seconds (SC-003)
- Data size: 20 accounts × ~100 bytes = ~2KB JSON
- No pagination needed up to 20 accounts (scrollable list)
- Single API call to submit selection

**Database Impact**:
- No new tables (using existing `BasecampAccount`)
- No additional queries (still one INSERT/UPDATE on connection)
- Session storage is separate (not in PostgreSQL by default)

---

## Security Considerations

**Session Security**:
- HTTP-only cookies (existing configuration)
- 15-minute timeout limits exposure window
- Secure flag in production (existing configuration)
- SameSite=Lax prevents CSRF (existing configuration)

**Token Storage**:
- Tokens stored in session (not URL or localStorage)
- Session cleared after successful connection
- Tokens never exposed to client (only account ID/name sent)

**Validation**:
- Server validates selected account against pending list
- Cannot connect to account not in authorized list
- Session expiry prevents stale/manipulated data

**Logging**:
- User ID logged for audit trail
- Account IDs logged (not sensitive)
- Tokens never logged
- INFO level prevents log flooding

---

## Testing Strategy

**Manual Testing** (no automated tests requested):
1. Test single account (auto-select maintains existing behavior)
2. Test multiple accounts (selection screen appears)
3. Test session expiry (15-minute timeout, clear error recovery)
4. Test invalid selection (backend rejects, clear error)
5. Test 20 accounts (verify no UI degradation)

**Test Account**: American Abstract LLC (ID: 5612021) - has access to multiple accounts

**Verification**:
- ✅ User sees account names clearly
- ✅ Can select desired account
- ✅ Connection saves correct account ID/name
- ✅ Dashboard shows connected account name
- ✅ Session expires after 15 minutes
- ✅ Error recovery guides user to restart OAuth

---

## Open Questions

None - all technical unknowns resolved during research phase.

