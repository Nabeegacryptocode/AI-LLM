# Enable Google Discovery Engine - Quick Guide

You're seeing "No access token available, using DuckDuckGo fallback" because Google Cloud authentication isn't configured yet. Follow these steps to enable Discovery Engine:

## Option 1: For Render Deployment (Recommended)

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project ID: `71522359792`
3. Navigate to **IAM & Admin** > **Service Accounts**
4. Click **Create Service Account**
5. Name: `render-discovery-engine`
6. Grant role: **Discovery Engine Viewer**
7. Click **Create and Continue** > **Done**

### Step 2: Create JSON Key

1. Find your service account in the list
2. Click the three dots (⋮) > **Manage keys**
3. Click **Add Key** > **Create new key**
4. Select **JSON** format
5. Click **Create** and save the file

### Step 3: Add to Render

1. Go to Render Dashboard > Your Service > **Environment**
2. Add these variables:

```bash
# Copy entire JSON file content
GOOGLE_APPLICATION_CREDENTIALS_JSON=<paste entire JSON content here>

# Set path where file will be created
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json
```

3. Update your **Start Command** in Render:

```bash
echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/gcp-key.json && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Click **Save Changes** and redeploy

### Step 4: Verify

After deployment, check logs for:
```
✅ Successfully obtained service account access token
✅ Found X Discovery Engine results
```

## Option 2: For Local Development

### Using gcloud CLI (Easiest)

```bash
# Install gcloud CLI
# Windows: https://cloud.google.com/sdk/docs/install
# Mac: brew install google-cloud-sdk
# Linux: curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Set project
gcloud config set project 71522359792

# Test
gcloud auth print-access-token
```

The application will automatically use gcloud authentication.

### Using Service Account Locally

1. Download the service account JSON key
2. Set environment variable:

**Windows PowerShell:**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

3. Or add to `.env` file:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Current Status

✅ **Application is working** - Using DuckDuckGo fallback
⏳ **Discovery Engine** - Requires authentication setup (optional)

The system will automatically switch to Discovery Engine once authentication is configured. No code changes needed!

## Test Discovery Engine

After setup, test with:

```bash
curl -X POST "http://your-app.com/api/chat" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is IBM Cloud?", "conversation_id": "test"}'
```

Check logs for "Discovery Engine" instead of "DuckDuckGo".

## Troubleshooting

### Still seeing "No access token available"?

1. **Check environment variable is set:**
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. **Verify JSON file exists:**
   ```bash
   ls -l $GOOGLE_APPLICATION_CREDENTIALS
   ```

3. **Test authentication:**
   ```bash
   python -c "
   from google.oauth2 import service_account
   creds = service_account.Credentials.from_service_account_file(
       'path/to/key.json',
       scopes=['https://www.googleapis.com/auth/cloud-platform']
   )
   print('✅ Authentication works!')
   "
   ```

4. **Check Render logs** for specific error messages

### Permission Denied?

Ensure service account has **Discovery Engine Viewer** role:
1. Go to IAM & Admin > IAM
2. Find your service account
3. Edit and add role if missing

## Need Help?

- **Documentation**: `docs/GOOGLE_CLOUD_AUTH_RENDER.md`
- **Full Guide**: `docs/GOOGLE_DISCOVERY_ENGINE.md`
- **Check logs**: Look for specific error messages

---

**Note**: The application works perfectly with DuckDuckGo fallback. Discovery Engine is an optional enhancement for better search quality.