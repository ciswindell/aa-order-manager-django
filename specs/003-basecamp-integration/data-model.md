# Data Model: Basecamp API Integration

**Feature**: 003-basecamp-integration | **Date**: 2025-10-26 | **Phase**: 1 (Design)

## Entity Overview

This feature introduces one new entity (**BasecampAccount**) to the existing `web/integrations` app.

## Entities

### BasecampAccount

**Purpose**: Stores authenticated user connection to a single Basecamp account with OAuth credentials

**Location**: `web/integrations/models.py` (alongside existing DropboxAccount)

**Schema**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BigAutoField | PK, Auto | Django auto primary key |
| user | ForeignKey | NOT NULL, UNIQUE, CASCADE | One-to-one with Django User model |
| account_id | CharField(255) | NOT NULL, UNIQUE, INDEX | Basecamp account ID from OAuth response |
| account_name | CharField(255) | NOT NULL | Basecamp account name (e.g., "Acme Corp") |
| access_token | TextField | NOT NULL | Current OAuth access token |
| refresh_token_encrypted | TextField | NOT NULL | Encrypted OAuth refresh token for long-term access |
| expires_at | DateTimeField | NULL, BLANK | Token expiration timestamp (if provided by Basecamp) |
| scope | TextField | BLANK, DEFAULT="" | OAuth scope (empty for Basecamp 3 default) |
| token_type | CharField(50) | BLANK, DEFAULT="Bearer" | OAuth token type |
| created_at | DateTimeField | AUTO_NOW_ADD | Account connection timestamp |
| updated_at | DateTimeField | AUTO_NOW | Last modified timestamp |

**Relationships**:
- `user → User`: One-to-one relationship enforcing single Basecamp account per user (FR-004)
  - Related name: `basecamp_account`
  - On delete: CASCADE (remove account when user deleted)

**Indexes**:
- Primary key on `id`
- Unique index on `user` (enforces one-to-one)
- Unique index on `account_id` (prevents duplicate Basecamp accounts)

**Validation Rules**:
- FR-004: One BasecampAccount per User (enforced by OneToOneField)
- FR-005: Tokens encrypted at rest (refresh_token_encrypted uses encryption utility)
- FR-018: Store account metadata (account_id, account_name, expires_at, scope)

**Model Implementation** (Django):

```python
from django.conf import settings
from django.db import models

class BasecampAccount(models.Model):
    """Per-user Basecamp 3 OAuth credentials.
    
    Stores current access token, encrypted refresh token, and metadata for a single
    Basecamp account linked to a Django user. Enforces one-to-one relationship
    (FR-004: single Basecamp account per user).
    
    OAuth tokens stored encrypted at rest per FR-005. Access token used for API calls,
    refresh token for long-term access renewal.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="basecamp_account",
        help_text="Application user who owns this Basecamp connection"
    )
    
    account_id = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Basecamp account ID from OAuth authorization"
    )
    
    account_name = models.CharField(
        max_length=255,
        help_text="Human-readable Basecamp account name (e.g., 'Acme Corp')"
    )
    
    access_token = models.TextField(
        help_text="Current OAuth access token for Basecamp API calls"
    )
    
    refresh_token_encrypted = models.TextField(
        help_text="Encrypted OAuth refresh token for long-term access"
    )
    
    expires_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Token expiration timestamp (optional, Basecamp tokens may not expire)"
    )
    
    scope = models.TextField(
        blank=True, 
        default="",
        help_text="OAuth scope (empty for Basecamp 3 default full access)"
    )
    
    token_type = models.CharField(
        max_length=50, 
        blank=True, 
        default="Bearer",
        help_text="OAuth token type (typically 'Bearer')"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user first connected Basecamp account"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp (token refresh, etc.)"
    )
    
    class Meta:
        db_table = "integrations_basecamp_account"
        verbose_name = "Basecamp Account"
        verbose_name_plural = "Basecamp Accounts"
        indexes = [
            models.Index(fields=["account_id"]),
        ]
    
    def __str__(self) -> str:
        return f"BasecampAccount(user={self.user}, account_id={self.account_id}, name={self.account_name})"
```

## State Transitions

### BasecampAccount Lifecycle

```
[No Account]
     |
     | User initiates OAuth (FR-010)
     v
[OAuth In Progress] (external to database)
     |
     | OAuth callback received, account selected
     v
[Connected] (BasecampAccount created)
     |
     +--[Token Refresh]--+
     |                   |
     | refresh_token     |
     | used to get new   |
     | access_token      |
     | (FR-007)          |
     |                   |
     +<------------------+
     |
     | User disconnects (FR-011)
     | OR User deletes account
     | OR User account cascade delete
     v
[Deleted] (BasecampAccount removed)
```

**State Descriptions**:

1. **No Account**: User has no BasecampAccount record
   - Status display: "Not Connected"
   - Action: Show "Connect Basecamp" button (FR-013)

2. **OAuth In Progress**: User clicked "Connect", redirected to Basecamp
   - No database state (external OAuth flow)
   - Basecamp handles account selection if user has multiple accounts

3. **Connected**: BasecampAccount record exists
   - Status display: "Connected" with account_name (FR-012)
   - Token valid: Normal operations
   - Token expired: Auto-refresh attempt (FR-007, SC-003: 95% success)
   - Refresh fails: Warning banner, prompt re-auth (FR-008, Clarification #2)

4. **Deleted**: BasecampAccount removed from database
   - Trigger: User clicks disconnect (FR-011)
   - Trigger: User account deleted (CASCADE)
   - Action: Return to "No Account" state

## Token Management

### Token Refresh Flow

```
[Access Token Expires]
     |
     | Detect expired token (FR-009)
     v
[Attempt Refresh] (FR-007)
     |
     +-- Success (95%) -->  [Update access_token]
     |                      [Update expires_at]
     |                      [Continue operation]
     |                      (SC-003)
     |
     +-- Failure (5%) --->  [Show warning banner]
                            [Allow app session continue]
                            [Require re-auth on next Basecamp action]
                            (FR-008, Clarification #2)
```

### Token Storage Security

**Encryption** (FR-005):
- `access_token`: Stored as plaintext (short-lived, needed frequently)
- `refresh_token_encrypted`: Stored encrypted using existing Django encryption utility
- Encryption key: Django SECRET_KEY (existing infrastructure)
- Pattern: Mirrors DropboxAccount implementation

**Retrieval** (for use in token_store.py):
```python
def get_tokens_for_user(user, provider='basecamp'):
    """Retrieve decrypted tokens for Basecamp API calls."""
    try:
        account = user.basecamp_account
        return {
            'access_token': account.access_token,
            'refresh_token': decrypt(account.refresh_token_encrypted),
            'expires_at': account.expires_at,
            'account_id': account.account_id,
            'account_name': account.account_name,
        }
    except BasecampAccount.DoesNotExist:
        return None
```

## Database Migration

**Migration Name**: `XXXX_basecamp_account.py`

**Operations**:
1. Create `integrations_basecamp_account` table
2. Add unique index on `user_id`
3. Add unique index on `account_id`
4. Add standard index on `account_id`

**Dependencies**:
- Requires existing User model
- Requires existing integrations app

**Rollback**: Drop `integrations_basecamp_account` table

## Data Access Patterns

### Create Account (OAuth Callback)

```python
# In views.py OAuth callback handler
from web.integrations.models import BasecampAccount
from web.integrations.utils.encryption import encrypt_token

def handle_oauth_callback(user, oauth_response):
    # Check for existing account (FR-014)
    if hasattr(user, 'basecamp_account'):
        # User already has account - handle replacement
        user.basecamp_account.delete()
    
    # Create new account
    account = BasecampAccount.objects.create(
        user=user,
        account_id=oauth_response['account']['id'],
        account_name=oauth_response['account']['name'],
        access_token=oauth_response['access_token'],
        refresh_token_encrypted=encrypt_token(oauth_response['refresh_token']),
        expires_at=parse_expiration(oauth_response.get('expires_at')),
        scope=oauth_response.get('scope', ''),
        token_type=oauth_response.get('token_type', 'Bearer'),
    )
    
    # Log connection event (FR-016)
    logger.info(f"Basecamp account connected: user={user.id}, account={account.account_id}")
    
    return account
```

### Read Account Status

```python
# In status/strategies/basecamp.py
def assess_raw(self, user) -> RawStatusSignals:
    try:
        account = user.basecamp_account
        connected = True
        authenticated = account.expires_at is None or account.expires_at > now()
        has_refresh = bool(account.refresh_token_encrypted)
    except BasecampAccount.DoesNotExist:
        connected = False
        authenticated = False
        has_refresh = False
    
    return RawStatusSignals(
        connected=connected,
        authenticated=authenticated,
        has_refresh=has_refresh,
        env_ok=bool(settings.BASECAMP_APP_KEY and settings.BASECAMP_APP_SECRET),
        cta_url=reverse('integrations:basecamp_connect'),
    )
```

### Update Tokens (Refresh)

```python
# In basecamp/auth.py refresh method
def refresh_access_token(user):
    account = user.basecamp_account
    refresh_token = decrypt(account.refresh_token_encrypted)
    
    # Call Basecamp token endpoint
    new_tokens = exchange_refresh_token(refresh_token)
    
    # Update account
    account.access_token = new_tokens['access_token']
    account.expires_at = parse_expiration(new_tokens.get('expires_at'))
    account.updated_at = timezone.now()  # Auto-updated by auto_now
    account.save(update_fields=['access_token', 'expires_at', 'updated_at'])
    
    # Log refresh event (FR-016)
    logger.info(f"Basecamp token refreshed: user={user.id}, account={account.account_id}")
```

### Delete Account (Disconnect)

```python
# In views.py disconnect handler
def disconnect_basecamp(request):
    try:
        account = request.user.basecamp_account
        account_id = account.account_id  # For logging
        account.delete()
        
        # Log disconnection event (FR-016)
        logger.info(f"Basecamp account disconnected: user={request.user.id}, account={account_id}")
        
        return JsonResponse({'status': 'disconnected'})
    except BasecampAccount.DoesNotExist:
        return JsonResponse({'error': 'No account connected'}, status=400)
```

## Queries & Performance

### Expected Query Patterns

1. **Status Check** (most frequent):
   ```sql
   SELECT * FROM integrations_basecamp_account WHERE user_id = ?
   ```
   - Index: user_id (unique, OneToOneField creates index)
   - Frequency: Every page load of integrations page (SC-002: <1 sec)

2. **OAuth Callback** (infrequent):
   ```sql
   SELECT * FROM integrations_basecamp_account WHERE user_id = ?  -- Check existing
   INSERT INTO integrations_basecamp_account (...) VALUES (...)   -- Create new
   ```
   - Index: user_id
   - Frequency: Only during OAuth connection

3. **Token Refresh** (periodic):
   ```sql
   SELECT * FROM integrations_basecamp_account WHERE user_id = ?
   UPDATE integrations_basecamp_account SET access_token = ?, expires_at = ?, updated_at = ? WHERE id = ?
   ```
   - Index: id (PK)
   - Frequency: When access token expires (varies, but infrequent)

### Performance Considerations

- **Small table size**: One row per user, max ~10K users initially
- **Simple queries**: All queries use indexed columns (user_id, account_id)
- **No joins**: BasecampAccount accessed via OneToOneField, no complex joins needed
- **Caching**: Status strategy can cache results (ttl_seconds parameter)

## Data Integrity

### Constraints

1. **Uniqueness**:
   - One BasecampAccount per User (OneToOneField)
   - One BasecampAccount per Basecamp account_id (unique constraint)
   - Prevents duplicate connections (FR-004, FR-014)

2. **Referential Integrity**:
   - CASCADE delete when User deleted
   - Ensures no orphaned BasecampAccount records

3. **Required Fields**:
   - user, account_id, account_name, access_token, refresh_token_encrypted: NOT NULL
   - Enforces FR-018 (store account metadata)

### Validation

**Model-level**:
- Django model validation on save()
- Field max_length constraints

**Application-level**:
- Check for existing account before OAuth callback (FR-014)
- Validate OAuth response before saving
- Log all create/update/delete operations (FR-016)

## Dependencies

**Database**:
- PostgreSQL (existing)
- Django migrations framework

**Related Models**:
- Django User model (AUTH_USER_MODEL)

**Related Code**:
- Encryption utility (existing, from DropboxAccount)
- Token store utility (extend for Basecamp)
- Status strategies framework (existing)

## Migration Strategy

1. **Development**: Create migration, apply to dev database
2. **Testing**: Verify constraints work (one account per user, unique account_id)
3. **Production**: Apply migration (zero downtime, no existing data)

**Rollback Plan**: Drop table, remove migration from history

