# Basecamp OAuth Application Setup

## Registration Instructions

To complete the Basecamp integration, you need to register an OAuth application with Basecamp.

### Steps:

1. **Go to Basecamp Launchpad**:
   - Navigate to https://launchpad.37signals.com/integrations
   - Sign in with your Basecamp account

2. **Register your application**:
   - Click "Register your application"
   - Fill in the required information:
     - **Name**: "AA Order Manager" (or your app name)
     - **Description**: "Order management system with Basecamp integration"
     - **Company**: Your company name
     - **Website**: Your application URL
     - **Redirect URI**: 
       - Development: `http://localhost:8000/api/integrations/basecamp/callback/`
       - Production: `https://yourdomain.com/api/integrations/basecamp/callback/`

3. **Obtain credentials**:
   - After registration, you'll receive:
     - **Client ID** (BASECAMP_APP_KEY)
     - **Client Secret** (BASECAMP_APP_SECRET)

4. **Configure environment variables**:
   - Create or update `.env` file in project root:
     ```env
     BASECAMP_APP_KEY=your_client_id_here
     BASECAMP_APP_SECRET=your_client_secret_here
     BASECAMP_OAUTH_REDIRECT_URI=http://localhost:8000/api/integrations/basecamp/callback/
     ```

5. **Restart Django server**:
   ```bash
   docker-compose restart backend
   # or
   python3 web/manage.py runserver
   ```

## Verification

Once configured, verify the settings are loaded:

```python
from django.conf import settings

print(f"BASECAMP_APP_KEY: {settings.BASECAMP_APP_KEY}")
print(f"BASECAMP_APP_SECRET: {'*' * len(settings.BASECAMP_APP_SECRET)}")
print(f"BASECAMP_OAUTH_REDIRECT_URI: {settings.BASECAMP_OAUTH_REDIRECT_URI}")
```

## Notes

- Use separate OAuth applications for development and production environments
- The redirect URI must match exactly (including trailing slash)
- Keep client secret secure and never commit to version control
- Basecamp OAuth apps are tied to the account that creates them

## Status

- [x] OAuth application registered at Basecamp
- [x] Environment variables configured in `.env`
- [x] Django server restarted with new configuration
- [x] Settings verified in Django shell

✅ **OAuth setup complete!** Ready to proceed with implementation.

