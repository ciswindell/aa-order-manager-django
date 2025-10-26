# Research: Basecamp API Integration

**Feature**: 003-basecamp-integration | **Date**: 2025-10-26 | **Phase**: 0 (Research)

## Research Questions

### Q1: What are the Basecamp 3 OAuth 2.0 implementation details?

**Decision**: Use Basecamp 3 OAuth 2.0 with standard authorization code flow

**Rationale**:
- Basecamp 3 (launchpad.37signals.com) uses standard OAuth 2.0 authorization code grant
- Authorization endpoint: `https://launchpad.37signals.com/authorization/new`
- Token endpoint: `https://launchpad.37signals.com/authorization/token`
- User authorization endpoint: `https://launchpad.37signals.com/authorization`
- Token refresh supported via `grant_type=refresh_token`
- Requires app registration at https://launchpad.37signals.com to obtain client_id and client_secret
- Redirect URI must be registered and match exactly during OAuth flow

**Alternatives Considered**:
- Basecamp 2 API: Deprecated, limited adoption
- Basecamp 4 API: Too new, limited documentation and adoption
- ✅ Basecamp 3 API: Mature, well-documented, widest adoption

**Implementation Notes**:
- OAuth flow requires `type=web_server` parameter
- Access tokens don't expire automatically but can be revoked by user
- Refresh tokens provided for long-term access
- Account selection happens during Basecamp OAuth flow if user has multiple accounts

### Q2: What OAuth scopes does Basecamp 3 support?

**Decision**: Request no specific scopes (default identity access only)

**Rationale**:
- Basecamp 3 OAuth doesn't use granular scopes like Google/GitHub
- OAuth access grants full API access to user's account by default
- Cannot request "read-only" scope - authorization is all-or-nothing
- For authentication foundation, we accept full access but only use identity endpoints
- Future workflow features will use same token for project/file operations

**Alternatives Considered**:
- Request specific read-only scope: Not available in Basecamp 3 OAuth
- Use separate tokens for different operations: Unnecessary complexity, same scope anyway
- ✅ Accept default scope, use least privilege in practice: Simplest, standard pattern

**Implementation Notes**:
- Don't include `scope` parameter in OAuth request
- Document in code that only identity endpoints are used for this feature
- Future features can use same token for expanded operations

### Q3: How does account selection work in Basecamp 3 OAuth?

**Decision**: Basecamp handles account selection in their OAuth UI

**Rationale**:
- When user has multiple Basecamp accounts (personal + organizations), Basecamp's OAuth flow presents account picker
- Account selection happens on Basecamp's authorization page, not in our application
- OAuth callback receives account-specific token
- Account ID included in authorization response
- Our responsibility: Store selected account, enforce one-account-per-user limit in our database

**Alternatives Considered**:
- Build our own account selector: Unnecessary, Basecamp OAuth already provides this
- Allow multiple accounts per user: Violates spec requirement FR-004
- ✅ Use Basecamp's account picker, enforce single-account in DB: Standard OAuth pattern

**Implementation Notes**:
- Basecamp OAuth UI shows account picker automatically when user has multiple accounts
- Parse account ID from OAuth callback
- Check for existing BasecampAccount before saving new one
- Provide UI option to "replace" existing account if user wants to switch

### Q4: What authentication endpoints and data structures does Basecamp 3 use?

**Decision**: Use Basecamp 3 authorization.json endpoint for account identity

**Rationale**:
- GET `https://launchpad.37signals.com/authorization.json` returns current authorization details
- Response includes: account ID, account name, identity (user info), expires_at, product (Basecamp 3)
- This endpoint validates token and retrieves account metadata
- No separate "identity" or "userinfo" endpoint needed
- Used for both initial account retrieval and token validation

**Response Structure**:
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

**Alternatives Considered**:
- Use account-specific API endpoint: Requires knowing account ID first
- Parse tokens client-side: Basecamp tokens are opaque, not JWT
- ✅ Use authorization.json: Official way to get account info and validate tokens

**Implementation Notes**:
- Call after receiving OAuth callback to get account details
- Store account ID, name from response
- Use for periodic token validation
- Handle multiple accounts in response (user selected one during OAuth)

### Q5: How should token encryption follow the Dropbox pattern?

**Decision**: Reuse existing token encryption mechanism from DropboxAccount

**Rationale**:
- DropboxAccount already has `refresh_token_encrypted` field with encryption at rest
- Same encryption mechanism works for Basecamp tokens
- Django's SECRET_KEY based encryption via existing utility
- Consistent security posture across integrations

**Implementation Pattern** (from existing Dropbox code):
```python
# In models.py
class BasecampAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="basecamp_account")
    account_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()  # Current token
    refresh_token_encrypted = models.TextField()  # Encrypted long-term token
    expires_at = models.DateTimeField(null=True, blank=True)
    # ... other fields
```

**Alternatives Considered**:
- Use Django's encryption framework directly: More complex, already have working solution
- Store tokens in separate secure storage: Unnecessary for this scale
- ✅ Mirror DropboxAccount encryption pattern: DRY, proven, consistent

**Implementation Notes**:
- Check existing encryption utility in integrations app
- Ensure same encryption/decryption methods work for Basecamp
- Document encryption in model docstring

### Q6: What Python library should be used for Basecamp API calls?

**Decision**: Use `requests` library directly (no official Basecamp Python SDK)

**Rationale**:
- Basecamp doesn't provide an official Python SDK
- Third-party libraries exist but unmaintained or incomplete
- OAuth 2.0 and REST API simple enough for direct `requests` usage
- Matches Dropbox integration pattern (uses dropbox SDK, but we'll use requests)
- More control, no external dependency risk, easier to maintain

**API Call Pattern**:
```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'User-Agent': 'AA Order Manager (your-email@example.com)'
}

response = requests.get(
    'https://launchpad.37signals.com/authorization.json',
    headers=headers
)
```

**Alternatives Considered**:
- Use basecamp3-wrapper: Unmaintained, last update 2018
- Use python-basecamp: Incomplete, Basecamp 2 focused
- ✅ Use requests directly: No dependencies, full control, matches OAuth pattern

**Implementation Notes**:
- Add User-Agent header per Basecamp API guidelines
- Implement retry logic for network failures
- Handle rate limiting (Basecamp uses standard HTTP 429)
- Centralize API calls in BasecampService class

### Q7: How should status strategy be implemented?

**Decision**: Enhance existing BasecampStatusStrategy placeholder

**Rationale**:
- File already exists at `web/integrations/status/strategies/basecamp.py`
- Currently returns hardcoded "not connected" status
- Need to implement real status check following DropboxStatusStrategy pattern
- Check token store, validate expiration, optionally probe API

**Status Strategy Pattern** (from DropboxStatusStrategy):
```python
class BasecampStatusStrategy(IntegrationStatusStrategy):
    provider = "basecamp"
    
    def assess_raw(self, user) -> RawStatusSignals:
        tokens = get_tokens_for_user(user, provider='basecamp')
        env_ok = bool(settings.BASECAMP_APP_KEY and settings.BASECAMP_APP_SECRET)
        connected = bool(tokens and tokens.get('access_token'))
        # Check expiration, optionally probe API
        return RawStatusSignals(...)
    
    def assess(self, user, *, now=None, ttl_seconds=600) -> IntegrationStatus:
        raw = self.assess_raw(user)
        return map_raw_to_status(provider=self.provider, raw=raw, ...)
```

**Alternatives Considered**:
- Create separate status service: Violates existing pattern
- Always probe API: Too slow, spec requires <1sec status display
- ✅ Enhance existing strategy, cheap checks first: Matches Dropbox, efficient

**Implementation Notes**:
- Extend token_store.py to support Basecamp provider
- Add INTEGRATIONS_STATUS_LIVE_PROBE support for Basecamp
- Return CTA URL pointing to basecamp_connect view

## Technology Stack

**Backend**:
- Django 5.2+ (existing)
- Django REST Framework (existing)
- requests library (for Basecamp API calls)
- PostgreSQL (existing, for BasecampAccount model)
- Existing token encryption utilities

**Frontend**:
- Next.js 16+ (existing)
- TypeScript (existing)
- Existing integrations UI components
- TanStack Query (existing, for status fetching)

**Configuration**:
- Environment variables: BASECAMP_APP_KEY, BASECAMP_APP_SECRET
- Settings: BASECAMP_OAUTH_REDIRECT_URI (default to /integrations/basecamp/callback/)

## Best Practices

### OAuth Implementation
1. **Security**:
   - Use state parameter to prevent CSRF
   - Validate redirect_uri matches registered URI exactly
   - Store tokens encrypted at rest
   - Use HTTP-only cookies for session management (existing)

2. **User Experience**:
   - Handle OAuth errors gracefully with user-friendly messages
   - Provide clear "Connect Basecamp" call-to-action
   - Show account name after connection
   - Allow easy disconnection

3. **Reliability**:
   - Implement token refresh flow
   - Handle network failures with retries
   - Log authentication events for debugging
   - Graceful degradation on refresh failures

### Django Integration Pattern
1. **Models**: Single BasecampAccount model in shared models.py (matches DropboxAccount)
2. **Services**: Separate basecamp/ module with auth.py, basecamp_service.py, config.py
3. **Views**: Add OAuth views (connect, callback, disconnect) to existing views.py
4. **URLs**: Add basecamp patterns to existing urls.py
5. **Status**: Enhance existing strategies/basecamp.py

### Code Organization (DRY)
1. **Reuse** existing token_store utilities
2. **Extend** cloud factory to support Basecamp provider
3. **Mirror** Dropbox integration architecture
4. **Share** integration UI components in frontend

## Implementation Sequence

1. **Phase 1A - Models & Configuration**:
   - Add BasecampAccount model
   - Add environment variables to settings
   - Create database migration

2. **Phase 1B - OAuth Service**:
   - Create basecamp/ module
   - Implement BasecampOAuthAuth
   - Implement OAuth helper functions

3. **Phase 1C - Views & URLs**:
   - Add connect view (initiate OAuth)
   - Add callback view (handle OAuth response)
   - Add disconnect view
   - Wire up URL patterns

4. **Phase 1D - Status Integration**:
   - Enhance BasecampStatusStrategy
   - Extend token_store for Basecamp
   - Update cloud factory

5. **Phase 1E - Frontend** (minimal changes):
   - Verify integration status API works for Basecamp
   - Confirm UI displays Basecamp status correctly

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Basecamp API changes | High | Use stable v3 API, monitor Basecamp changelog, version in code comments |
| OAuth token revocation | Medium | Detect via status checks, prompt re-authentication, log events |
| Rate limiting | Low | Implement exponential backoff, avoid excessive API calls |
| Account selection UX confusion | Low | Clear UI messaging, document Basecamp account picker behavior |
| Token encryption key rotation | Medium | Use existing encryption mechanism, document key management |

## Open Questions

None - all research questions resolved. Ready for Phase 1 (Design & Contracts).

