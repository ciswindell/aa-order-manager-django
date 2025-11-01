# Quickstart: Basecamp API Integration

**Feature**: 003-basecamp-integration | **Date**: 2025-10-26 | **Phase**: 1 (Design)

## Overview

Quick guide for developers to set up and test the Basecamp OAuth 2.0 integration locally.

## Prerequisites

- Docker & Docker Compose installed
- Basecamp account for testing (personal or organization)
- Text editor / IDE

## Setup Steps

### 1. Register Basecamp OAuth Application

**Purpose**: Obtain OAuth credentials (client_id, client_secret)

1. Go to https://launchpad.37signals.com/integrations
2. Click "Register your application"
3. Fill in application details:
   - **Name**: "AA Order Manager (Dev)" (or similar)
   - **Description**: "Order management system with Basecamp integration"
   - **Company**: Your company name
   - **Website**: http://localhost:3000 (development)
   - **Redirect URI**: http://localhost:8000/api/integrations/basecamp/callback/
4. Submit and receive:
   - **Client ID**: `abc123...`
   - **Client Secret**: `xyz789...`
5. **Save these credentials** - you'll need them for environment variables

**Notes**:
- Use separate OAuth apps for development and production
- Production redirect URI will be your actual domain
- Multiple redirect URIs not supported - must match exactly

### 2. Configure Environment Variables

**Backend** (`web/.env` or Docker Compose environment):

```bash
# Basecamp OAuth Credentials
BASECAMP_APP_KEY=your_client_id_from_step_1
BASECAMP_APP_SECRET=your_client_secret_from_step_1

# Optional: Redirect URI (defaults to /api/integrations/basecamp/callback/)
BASECAMP_OAUTH_REDIRECT_URI=http://localhost:8000/api/integrations/basecamp/callback/

# Existing settings (should already be configured)
DJANGO_SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://user:password@db:5432/aa_order_manager
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

**Docker Compose** (update `docker-compose.yml` or `.env`):

```yaml
services:
  backend:
    environment:
      - BASECAMP_APP_KEY=${BASECAMP_APP_KEY}
      - BASECAMP_APP_SECRET=${BASECAMP_APP_SECRET}
```

### 3. Start Development Environment

```bash
# From project root
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# backend    Up    8000/tcp
# frontend   Up    3000/tcp
# db         Up    5432/tcp
# redis      Up    6379/tcp
```

### 4. Apply Database Migrations

```bash
# Run Django migrations for BasecampAccount model
docker-compose exec backend python3 web/manage.py migrate

# Verify migration applied
docker-compose exec backend python3 web/manage.py showmigrations integrations
```

**Expected Output**:
```
integrations
 [X] 0001_initial
 [X] 0002_dropbox_account
 [X] XXXX_basecamp_account
```

### 5. Create Test User

```bash
# Create superuser for testing
docker-compose exec backend python3 web/manage.py createsuperuser

# Enter credentials:
# Username: admin
# Email: admin@example.com
# Password: admin123 (or your preference)
```

### 6. Test OAuth Flow

1. **Login to Application**:
   - Navigate to http://localhost:3000
   - Login with test user credentials

2. **Navigate to Integrations**:
   - Go to http://localhost:3000/dashboard/integrations
   - Should see Basecamp integration card with "Not Connected" status

3. **Connect Basecamp**:
   - Click "Connect Basecamp" button
   - Redirects to Basecamp authorization page
   - Login to Basecamp (if not already logged in)
   - Select Basecamp account (if you have multiple)
   - Click "Yes, I'll allow access"

4. **Verify Connection**:
   - Redirected back to integrations page
   - Status should show "Connected" with account name
   - Check Django admin to verify BasecampAccount record created

### 7. Verify in Django Admin

```bash
# Access Django admin
open http://localhost:8000/admin/

# Login with superuser credentials
# Navigate to: Integrations > Basecamp Accounts
# Should see entry with:
# - User: admin
# - Account ID: (your Basecamp account ID)
# - Account Name: (your Basecamp account name)
# - Access Token: (encrypted)
# - Created/Updated timestamps
```

### 8. Test Disconnection

1. **Navigate to Integrations Page**
2. **Click "Disconnect" button** next to Basecamp
3. **Confirm disconnection**
4. **Verify**:
   - Status returns to "Not Connected"
   - BasecampAccount record deleted from database
   - Can reconnect again

## Development Workflow

### Running Backend

```bash
# Start backend with hot reload
docker-compose up backend

# Check logs
docker-compose logs -f backend

# Run Django shell for debugging
docker-compose exec backend python3 web/manage.py shell
```

### Running Frontend

```bash
# Start frontend with hot reload
docker-compose up frontend

# Check logs
docker-compose logs -f frontend

# Access at http://localhost:3000
```

### Database Access

```bash
# PostgreSQL shell
docker-compose exec db psql -U user -d aa_order_manager

# Query BasecampAccount records
SELECT user_id, account_id, account_name, created_at FROM integrations_basecamp_account;

# Exit: \q
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Authentication events (grep for Basecamp)
docker-compose logs backend | grep -i basecamp
```

## Testing Checklist

### Happy Path

- [ ] User can initiate OAuth connection
- [ ] User redirected to Basecamp authorization page
- [ ] User can authorize and select account
- [ ] User redirected back to application
- [ ] BasecampAccount record created in database
- [ ] Status displays "Connected" with account name
- [ ] User can disconnect
- [ ] BasecampAccount record deleted on disconnect

### Edge Cases

- [ ] User with existing connection sees error when trying to connect again
- [ ] OAuth state parameter validation prevents CSRF
- [ ] Expired tokens detected and displayed in status
- [ ] Missing OAuth credentials show configuration error
- [ ] User can replace existing connection (disconnect then reconnect)
- [ ] Multiple browser tabs don't cause issues

### Status Strategy

- [ ] `GET /api/integrations/basecamp/status/` returns correct status
- [ ] Status displays within 1 second (SC-002)
- [ ] Status shows "connected" when account exists
- [ ] Status shows "not_connected" when no account
- [ ] Status shows "expired" when token expired
- [ ] CTA URL provided when not connected

### Authentication Events

- [ ] Connection logged with user_id, account_id, timestamp
- [ ] Disconnection logged
- [ ] OAuth failures logged with error details
- [ ] Token refresh attempts logged

## Common Issues

### Issue: "Redirect URI mismatch"

**Symptom**: OAuth callback fails with error about redirect URI

**Solution**:
1. Check registered redirect URI in Basecamp OAuth app settings
2. Ensure it exactly matches `BASECAMP_OAUTH_REDIRECT_URI` environment variable
3. Include protocol (http/https), port (if non-standard), and trailing slash
4. Example: `http://localhost:8000/api/integrations/basecamp/callback/`

### Issue: "Configuration error - Basecamp OAuth not configured"

**Symptom**: Connect button shows configuration error

**Solution**:
1. Verify `BASECAMP_APP_KEY` and `BASECAMP_APP_SECRET` in environment
2. Restart backend service: `docker-compose restart backend`
3. Check settings.py loads environment variables correctly

### Issue: "State parameter mismatch"

**Symptom**: OAuth callback fails with CSRF error

**Solution**:
1. Check session middleware is enabled in Django settings
2. Ensure cookies are working (check browser dev tools)
3. Try clearing cookies and reconnecting
4. Verify `SESSION_COOKIE_SECURE = False` for development (http)

### Issue: "Token encryption error"

**Symptom**: Error saving or retrieving tokens

**Solution**:
1. Verify `DJANGO_SECRET_KEY` is set
2. Check encryption utility is imported correctly
3. Review error logs for stack trace

### Issue: Frontend doesn't show updated status

**Symptom**: Status shows "Not Connected" after successful OAuth

**Solution**:
1. Check frontend polling/refetch logic
2. Verify TanStack Query cache invalidation
3. Manually refresh page
4. Check browser console for errors

## Debugging Tips

### Enable Django Debug Logging

**In `web/order_manager_project/settings.py`**:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'integrations': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Test OAuth Flow Manually

```bash
# 1. Get authorization URL
curl -X POST http://localhost:8000/api/integrations/basecamp/connect/ \
  -H "Cookie: access_token=YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# 2. Open authorization_url in browser
# 3. After callback, check database
docker-compose exec backend python3 web/manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='admin')
print(user.basecamp_account)  # Should print account details
```

### Inspect Token Store

```python
# In Django shell
from web.integrations.utils.token_store import get_tokens_for_user
tokens = get_tokens_for_user(user, provider='basecamp')
print(tokens)  # Should print access_token, refresh_token, etc.
```

### Test Status Strategy

```python
# In Django shell
from web.integrations.status.strategies.basecamp import BasecampStatusStrategy
strategy = BasecampStatusStrategy()
status = strategy.assess(user)
print(status.__dict__)  # Should print status details
```

## Next Steps

After quickstart is working:

1. **Review code**:
   - `web/integrations/models.py` - BasecampAccount model
   - `web/integrations/basecamp/auth.py` - OAuth service
   - `web/integrations/views.py` - OAuth endpoints
   - `web/integrations/status/strategies/basecamp.py` - Status strategy

2. **Implement remaining features** (see tasks.md):
   - Token refresh logic
   - Graceful degradation on refresh failures
   - Enhanced error handling
   - Comprehensive logging

3. **Test thoroughly**:
   - Multiple accounts (if available)
   - Token expiration scenarios
   - Network failures
   - Concurrent OAuth flows

4. **Prepare for production**:
   - Register production OAuth app
   - Update redirect URI
   - Configure production environment variables
   - Test with production Basecamp account

## Resources

**Basecamp API Documentation**:
- OAuth Guide: https://github.com/basecamp/api/blob/master/sections/authentication.md
- Basecamp 3 API: https://github.com/basecamp/bc3-api

**Django Documentation**:
- Models: https://docs.djangoproject.com/en/5.2/topics/db/models/
- Migrations: https://docs.djangoproject.com/en/5.2/topics/migrations/
- REST Framework: https://www.django-rest-framework.org/

**Project Documentation**:
- Constitution: `.specify/memory/constitution.md`
- Dropbox Integration: `web/integrations/dropbox/` (reference implementation)
- Docker Setup: `DOCKER_DEV_README.md`

## Support

For questions or issues:
1. Check this quickstart guide
2. Review research.md for design decisions
3. Check contracts/api-spec.md for API details
4. Review data-model.md for database schema
5. Check Django logs: `docker-compose logs backend`
6. Ask team for help

## Summary

This quickstart should get you from zero to a working Basecamp OAuth integration in ~15 minutes:

1. ✅ Register OAuth app (5 min)
2. ✅ Configure environment (2 min)
3. ✅ Start services (2 min)
4. ✅ Apply migrations (1 min)
5. ✅ Create test user (1 min)
6. ✅ Test OAuth flow (4 min)

Total: ~15 minutes to working integration.

