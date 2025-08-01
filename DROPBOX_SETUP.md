# 📦 Dropbox Integration Setup

This guide explains how to set up the simplified Dropbox authentication using environment variables instead of the complex OAuth flow.

## 🔧 Quick Setup

### 1. Get Your Dropbox Credentials

#### For App Console Access Token (Recommended)
1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Select your existing app or create a new one
3. Go to the **Settings** tab
4. Scroll down to **Generated access token** section
5. Click **Generate** to create a long-term access token
6. Copy the generated token

#### For App Key & Secret (Optional but Recommended)
1. In the same **Settings** tab
2. Copy your **App key** and **App secret** from the top of the page

### 2. Set Environment Variables

#### Option A: Using .env file (Recommended)
1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual credentials:
   ```bash
   # Required
   DROPBOX_ACCESS_TOKEN=sl.your_actual_long_term_token_here
   
   # Optional but recommended
   DROPBOX_APP_KEY=your_app_key_here
   DROPBOX_APP_SECRET=your_app_secret_here
   ```

#### Option B: System Environment Variables
```bash
export DROPBOX_ACCESS_TOKEN="sl.your_actual_long_term_token_here"
export DROPBOX_APP_KEY="your_app_key_here"
export DROPBOX_APP_SECRET="your_app_secret_here"
```

### 3. Test the Setup

Run the application and check the **Environment Status** section in the GUI. You should see:
- ✓ Access Token: Configured
- ✓ App Key: Configured (if provided)
- ✓ App Secret: Configured (if provided)
- ✓ Ready for use: Yes

## 📁 Agency Directory Configuration

The system uses these default directory mappings:

| Agency | Default Path |
|--------|-------------|
| Federal | `/Federal/` |
| NMState | `/NMState/` |
| State | `/NMState/` (alias) |

### Custom Directory Paths

You can override these defaults with environment variables:

```bash
# Custom agency directories (optional)
DROPBOX_FEDERAL_DIR=/Federal Workspace/^Runsheet Archive/
DROPBOX_NMSTATE_DIR=/State Workspace/^Runsheet Archive/
DROPBOX_STATE_DIR=/State Workspace/^Runsheet Archive/
```

## 🔍 How It Works

### Search Process
1. **Agency Selection**: System determines root directory based on order type
2. **Path Generation**: Combines agency path + lease name (e.g., `/Federal/NMLC 123456/`)
3. **Directory Search**: Uses Dropbox API to find exact directory matches
4. **Link Generation**: Creates shareable links for found directories
5. **Worksheet Population**: Adds links to the "Link" column in exported Excel

### Example Flow
```
Order: Federal Agency, Lease "NMLC 123456"
→ Search Path: "/Federal/NMLC 123456/"
→ Found: ✓ Directory exists
→ Generated: https://dropbox.com/s/abc123/NMLC%20123456
→ Result: Link added to Excel worksheet
```

## 🚨 Troubleshooting

### Common Issues

#### "Access Token Missing"
- **Cause**: `DROPBOX_ACCESS_TOKEN` not set or invalid
- **Solution**: Double-check your token in .env file or environment variables

#### "Authentication Failed"
- **Cause**: Token expired or invalid permissions
- **Solution**: Generate a new access token from App Console

#### "Directory Not Found"
- **Cause**: Lease folder doesn't exist in expected location
- **Solution**: Verify directory structure matches agency mappings

#### "Permission Denied"
- **Cause**: App doesn't have required Dropbox permissions
- **Solution**: Check app permissions in Dropbox App Console

### Debug Steps

1. **Check Environment Status**: Look at the GUI status section
2. **Verify Token**: Test token with a simple API call
3. **Check Directory Structure**: Ensure folders exist in Dropbox
4. **Review Logs**: Check console output for detailed error messages

## 🔐 Security Notes

- **Access Tokens**: Keep your access tokens secure and never commit them to version control
- **Environment Files**: Add `.env` to your `.gitignore` file
- **Token Rotation**: Periodically rotate your access tokens for security
- **Permissions**: Use minimal required permissions for your Dropbox app

## 🆕 What Changed

This simplified authentication replaces the previous complex OAuth flow:

### Before (Complex)
- OAuth 2.0 web browser flow
- Manual authorization code entry  
- Refresh token storage and management
- Multiple authentication steps

### After (Simple)
- Direct access token from environment variables
- No browser interaction required
- No token storage files
- Single-step authentication

## 📚 Related Documentation

- [Dropbox API Documentation](https://dropbox.tech/developers)
- [Environment Variables Guide](.env.example)
- [Order Processing Guide](README.md)

---

**Need help?** Check the Environment Status section in the application GUI for real-time configuration status. 