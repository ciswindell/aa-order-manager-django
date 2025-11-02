# Quickstart: Integration Account Names Display

**Feature**: Integration Account Names Display  
**Estimated Time**: 2-3 hours  
**Prerequisites**: Django environment running, frontend dev server running

---

## Quick Implementation Checklist

### Phase 1: Basecamp Account Name (P1) - 30 minutes ⭐ Quick Win

- [ ] **Backend**: Modify `BasecampStatusStrategy` to include `account_name`
- [ ] **Backend**: Add `account_name` field to `IntegrationStatus` DTO
- [ ] **Backend**: Update `IntegrationStatusSerializer` to expose new field
- [ ] **Frontend**: Extend `IntegrationStatus` TypeScript interface
- [ ] **Frontend**: Display account name in integrations card
- [ ] **Test**: Verify Basecamp shows "Connected as: [Account Name]"

### Phase 2: Dropbox Account Info (P2) - 1.5 hours

- [ ] **Backend**: Create database migration for `display_name` and `email` fields
- [ ] **Backend**: Run migration: `python3 manage.py migrate`
- [ ] **Backend**: Modify `dropbox_callback` to fetch account info via Dropbox API
- [ ] **Backend**: Add retry logic (2 second delay, one retry)
- [ ] **Backend**: Update `token_store.py` to save display_name and email
- [ ] **Backend**: Modify `DropboxStatusStrategy` to include account info
- [ ] **Backend**: Add `account_email` field to `IntegrationStatus` DTO
- [ ] **Frontend**: Display name and email in Dropbox card
- [ ] **Test**: Connect Dropbox, verify account info displayed

### Phase 3: Connection Timestamps (P3) - 30 minutes (Optional)

- [ ] **Backend**: Add `connected_at` field to `IntegrationStatus` DTO
- [ ] **Backend**: Populate from `created_at` in both status strategies
- [ ] **Frontend**: Display formatted date using `date-fns`
- [ ] **Test**: Verify timestamps show for both integrations

### Phase 4: Log Masking & Polish - 30 minutes

- [ ] **Backend**: Create `log_masking.py` utility
- [ ] **Backend**: Apply masking to OAuth and status logs
- [ ] **Frontend**: Add CSS for name truncation (50 chars + ellipsis)
- [ ] **Frontend**: Add title attribute for full text on hover
- [ ] **Test**: Verify long names truncate correctly
- [ ] **Test**: Verify logs mask PII

---

## Detailed Implementation Steps

### Step 1: Backend - Extend IntegrationStatus DTO

**File**: `web/integrations/status/dto.py`

**Action**: Add new fields to dataclass

```python
@dataclass
class IntegrationStatus:
    # ... existing fields ...
    account_name: Optional[str] = None
    account_email: Optional[str] = None
    connected_at: Optional[datetime] = None
```

---

### Step 2: Backend - Update Basecamp Strategy (P1)

**File**: `web/integrations/status/strategies/basecamp.py`

**Action**: Include account name in status

```python
def assess(self, user, *, now: Optional[datetime] = None, ttl_seconds: int = 600) -> IntegrationStatus:
    now = now or datetime.now(timezone.utc)
    raw = self.assess_raw(user)
    
    # Get account name from tokens
    tokens = get_tokens_for_user(user, provider="basecamp")
    account_name = tokens.get("account_name") if tokens else None
    
    # Get connected_at from account model
    from integrations.models import BasecampAccount
    connected_at = None
    try:
        account = BasecampAccount.objects.get(user=user)
        connected_at = account.created_at
    except BasecampAccount.DoesNotExist:
        pass
    
    status = map_raw_to_status(
        provider=self.provider, raw=raw, now=now, ttl_seconds=ttl_seconds
    )
    
    # Add account info
    status.account_name = account_name
    status.connected_at = connected_at
    
    return status
```

---

### Step 3: Backend - Database Migration (P2)

**File**: `web/integrations/migrations/000X_add_dropbox_account_info.py` (new)

**Command**: Create migration

```bash
cd /home/chris/Code/aa-order-manager
docker compose exec web python3 manage.py makemigrations integrations --name add_dropbox_account_info
```

**Expected Migration**:
```python
operations = [
    migrations.AddField(
        model_name='dropboxaccount',
        name='display_name',
        field=models.CharField(blank=True, default='', max_length=255),
    ),
    migrations.AddField(
        model_name='dropboxaccount',
        name='email',
        field=models.EmailField(blank=True, default='', max_length=254),
    ),
]
```

**Apply Migration**:
```bash
docker compose exec web python3 manage.py migrate
```

---

### Step 4: Backend - Update Dropbox OAuth Callback (P2)

**File**: `web/api/views/integrations.py`

**Action**: Fetch account info after token exchange

```python
def dropbox_callback(request):
    # ... existing token exchange code ...
    
    # After getting result from auth_flow.finish()
    access_token = result.access_token
    account_id = getattr(result, "account_id", "")
    
    # NEW: Fetch account information
    display_name = ""
    email = ""
    try:
        dbx = dropbox.Dropbox(oauth2_access_token=access_token)
        account_info = dbx.users_get_current_account()
        display_name = account_info.name.display_name[:255]  # Truncate
        email = account_info.email
    except Exception as e:
        logger.warning("Dropbox account info fetch failed, retrying | error=%s", str(e))
        # Retry once after 2 seconds
        import time
        time.sleep(2)
        try:
            dbx = dropbox.Dropbox(oauth2_access_token=access_token)
            account_info = dbx.users_get_current_account()
            display_name = account_info.name.display_name[:255]
            email = account_info.email
        except Exception as retry_error:
            logger.error("Dropbox account info fetch failed after retry | error=%s", str(retry_error))
            # Continue with empty display_name and email
    
    tokens = {
        "access_token": access_token,
        "refresh_token": getattr(result, "refresh_token", ""),
        "expires_at": getattr(result, "expires_at", None),
        "account_id": account_id,
        "scope": getattr(result, "scope", ""),
        "token_type": getattr(result, "token_type", ""),
        "display_name": display_name,  # NEW
        "email": email,  # NEW
    }
    
    save_tokens_for_user(user, tokens, provider="dropbox")
    # ... rest of callback ...
```

---

### Step 5: Backend - Update Token Store (P2)

**File**: `web/integrations/utils/token_store.py`

**Action**: Save display_name and email fields

```python
def save_tokens_for_user(user, tokens: OAuthTokens, provider: str = "dropbox"):
    # ... existing code ...
    
    if provider == "dropbox":
        account, created = DropboxAccount.objects.update_or_create(
            user=user,
            defaults={
                "account_id": tokens["account_id"],
                "access_token": tokens["access_token"],
                "refresh_token_encrypted": encrypt_text(tokens["refresh_token"]),
                "expires_at": tokens.get("expires_at"),
                "scope": tokens.get("scope", ""),
                "token_type": tokens.get("token_type", ""),
                "display_name": tokens.get("display_name", ""),  # NEW
                "email": tokens.get("email", ""),  # NEW
            },
        )
```

---

### Step 6: Backend - Update Dropbox Strategy (P2)

**File**: `web/integrations/status/strategies/dropbox.py`

**Action**: Include display_name and email in status

```python
def assess(self, user, *, now: Optional[datetime] = None, ttl_seconds: int = 600) -> IntegrationStatus:
    now = now or datetime.now(timezone.utc)
    raw = self.assess_raw(user)
    
    # Get account info from model
    from integrations.models import DropboxAccount
    account_name = None
    account_email = None
    connected_at = None
    try:
        account = DropboxAccount.objects.get(user=user)
        account_name = account.display_name if account.display_name else None
        account_email = account.email if account.email else None
        connected_at = account.created_at
    except DropboxAccount.DoesNotExist:
        pass
    
    status = map_raw_to_status(
        provider=self.provider, raw=raw, now=now, ttl_seconds=ttl_seconds
    )
    
    # Add account info
    status.account_name = account_name
    status.account_email = account_email
    status.connected_at = connected_at
    
    return status
```

---

### Step 7: Frontend - Update TypeScript Interface

**File**: `frontend/src/lib/api/types.ts`

**Action**: Add new fields

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
  account_name?: string | null;  // NEW
  account_email?: string | null;  // NEW
  connected_at?: string | null;  // NEW
}
```

---

### Step 8: Frontend - Update Integrations Page

**File**: `frontend/src/app/dashboard/integrations/page.tsx`

**Action**: Display account information

```tsx
// Inside the Card component for each integration
<CardDescription>
  {isConnected ? (
    <div className="space-y-1">
      {/* Account name display */}
      {integration.account_name && (
        <div className="font-medium">
          Connected as:{" "}
          <span
            className="truncate inline-block max-w-[300px] align-bottom"
            title={integration.account_name}
          >
            {integration.account_name.length > 50
              ? `${integration.account_name.substring(0, 50)}...`
              : integration.account_name}
          </span>
        </div>
      )}
      
      {/* Email for Dropbox */}
      {integration.account_email && (
        <div className="text-sm text-muted-foreground">
          {integration.account_email}
        </div>
      )}
      
      {/* Connection date */}
      {integration.connected_at && (
        <div className="text-xs text-muted-foreground">
          Connected on: {format(new Date(integration.connected_at), "MMM d, yyyy")}
        </div>
      )}
      
      {/* Last sync (existing) */}
      {!integration.account_name && (
        <div>Last synced: {format(new Date(integration.last_sync), "PPp")}</div>
      )}
    </div>
  ) : (
    integration.reason || "Not connected"
  )}
</CardDescription>
```

---

## Testing Scripts

### Test Basecamp Account Name

```bash
# 1. Login to Django admin
# 2. Verify BasecampAccount has account_name populated
# 3. Open http://localhost:3000/dashboard/integrations
# 4. Verify Basecamp card shows "Connected as: [Account Name]"
```

### Test Dropbox New Connection

```bash
# 1. Disconnect existing Dropbox connection (if any)
# 2. Click "Connect Dropbox"
# 3. Complete OAuth
# 4. Verify integrations page shows:
#    - Display name
#    - Email address
#    - Connection date
```

### Test Dropbox Legacy Connection

```bash
# 1. Create test account without display_name/email (via Django shell):
docker compose exec web python3 manage.py shell

from django.contrib.auth import get_user_model
from integrations.models import DropboxAccount
User = get_user_model()
user = User.objects.first()
DropboxAccount.objects.create(
    user=user,
    account_id="test123",
    access_token="test_token",
    refresh_token_encrypted="test_encrypted",
    display_name="",
    email=""
)

# 2. Verify integrations page shows generic "Connected" (no name/email)
```

---

## Troubleshooting

### Issue: Migration fails

**Solution**: Check for conflicting migrations
```bash
docker compose exec web python3 manage.py showmigrations integrations
```

### Issue: Dropbox account info not displaying

**Check**:
1. OAuth callback logs for account info fetch success/failure
2. Database: `display_name` and `email` fields populated
3. Status strategy returning fields in response
4. Frontend TypeScript interface matches backend response

### Issue: Long names breaking layout

**Solution**: Verify CSS truncation:
```css
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

---

## Rollback Procedure

### If issues occur in production:

1. **Revert frontend**: Deploy previous version (no data loss)
2. **Revert backend API**: Deploy previous version (new fields ignored by old frontend)
3. **Revert migration** (if needed):
```bash
docker compose exec web python3 manage.py migrate integrations <previous_migration_name>
```

**Note**: Rollback is safe - new fields are optional and nullable.

---

## Success Criteria Checklist

After implementation, verify:

- [ ] **SC-001**: Basecamp shows organization name without additional clicks
- [ ] **SC-002**: Dropbox shows name and email on integrations page
- [ ] **SC-003**: Page loads with account info in <2 seconds
- [ ] **SC-004**: New Dropbox connections capture account info (100%)
- [ ] **SC-005**: Names >50 chars truncate with ellipsis, full name on hover
- [ ] **SC-006**: (Post-deployment) Monitor support tickets for reduction

---

## Next Steps

After completing implementation:

1. **Create PR**: Merge to `django/main` branch
2. **Deploy**: Follow standard deployment procedure
3. **Monitor**: Check logs for Dropbox API success rate
4. **Communicate**: Notify users of new account identification feature
5. **Track Metrics**: Monitor support ticket reduction over 2 weeks

