# Google Cloud Authentication for Render Deployment

This guide explains how to set up Google Cloud authentication for the Discovery Engine on Render.

## Problem

The application uses Google Cloud Discovery Engine for enhanced search. In production (Render), we can't use `gcloud CLI` authentication, so we need to use service account credentials.

## Solution: Service Account Authentication

### Step 1: Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (ID: 783867443498)
3. Navigate to **IAM & Admin** > **Service Accounts**
4. Click **Create Service Account**
5. Fill in details:
   - **Name**: `render-discovery-engine`
   - **Description**: `Service account for Discovery Engine on Render`
6. Click **Create and Continue**

### Step 2: Grant Permissions

Grant the following role:
- **Discovery Engine Viewer** (`roles/discoveryengine.viewer`)

Or for more access:
- **Discovery Engine Admin** (`roles/discoveryengine.admin`)

Click **Continue** then **Done**

### Step 3: Create and Download Key

1. Find your new service account in the list
2. Click the three dots (⋮) > **Manage keys**
3. Click **Add Key** > **Create new key**
4. Select **JSON** format
5. Click **Create**
6. Save the downloaded JSON file securely (e.g., `service-account-key.json`)

⚠️ **Important**: Keep this file secure! It provides access to your Google Cloud resources.

### Step 4: Deploy to Render

#### Option A: Environment Variable (Recommended for Render)

1. Go to your Render dashboard
2. Select your web service
3. Go to **Environment** tab
4. Add a new environment variable:
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - **Value**: Paste the entire contents of your JSON file
5. Add another variable to parse it:
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS`
   - **Value**: `/tmp/gcp-key.json`

6. Update your start command in Render to create the file:
   ```bash
   echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/gcp-key.json && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

#### Option B: Secret Files (Alternative)

1. In Render dashboard, go to your service
2. Navigate to **Environment** > **Secret Files**
3. Click **Add Secret File**
4. Set:
   - **Filename**: `gcp-key.json`
   - **Contents**: Paste your JSON key content
5. Add environment variable:
   - **Key**: `GOOGLE_APPLICATION_CREDENTIALS`
   - **Value**: `/etc/secrets/gcp-key.json`

### Step 5: Verify Deployment

After deployment, check the logs:

✅ **Success**:
```
Successfully obtained service account access token
Found X Discovery Engine results
```

❌ **Fallback** (if auth fails):
```
No access token available, using DuckDuckGo fallback
Using DuckDuckGo fallback for: query
```

## Local Development

For local development, you have two options:

### Option 1: Use gcloud CLI (Easiest)

```bash
gcloud auth login
gcloud config set project 783867443498
```

The application will automatically use gcloud authentication.

### Option 2: Use Service Account Locally

1. Download the service account JSON key
2. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
   
   # Linux/Mac
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

3. Add to your `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

## Testing Authentication

### Test Script

Create a test file `test_auth.py`:

```python
import asyncio
from services.web_search_service import WebSearchService

async def test():
    service = WebSearchService()
    results = await service.search("IBM Cloud", max_results=3)
    
    if results:
        print(f"✅ Success! Found {len(results)} results")
        for r in results:
            print(f"  - {r['title']}")
    else:
        print("❌ No results (check logs)")

asyncio.run(test())
```

Run it:
```bash
cd backend
python test_auth.py
```

### Manual API Test

```bash
# Get token from service account
python -c "
from google.oauth2 import service_account
from google.auth.transport.requests import Request

creds = service_account.Credentials.from_service_account_file(
    'path/to/key.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
creds.refresh(Request())
print(creds.token)
"
```

## Troubleshooting

### Error: "No module named 'google.auth'"

**Solution**: Install dependencies
```bash
pip install google-auth google-auth-httplib2
```

### Error: "Permission denied"

**Solution**: Check service account has correct role
1. Go to IAM & Admin > IAM
2. Find your service account
3. Ensure it has `Discovery Engine Viewer` or `Discovery Engine Admin` role

### Error: "Service account key not found"

**Solution**: Check environment variable
```bash
# Verify the variable is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify file exists
ls -l $GOOGLE_APPLICATION_CREDENTIALS
```

### Fallback to DuckDuckGo

If authentication fails, the system automatically falls back to DuckDuckGo. This is expected behavior and ensures the application continues working.

To force Discovery Engine:
```python
from services.web_search_service import web_search_service

# Check if Discovery Engine is enabled
print(web_search_service.use_discovery_engine)

# Enable it if disabled
web_search_service.enable_discovery_engine()
```

## Security Best Practices

1. **Never commit** service account keys to git
2. **Rotate keys** regularly (every 90 days recommended)
3. **Use least privilege**: Only grant necessary permissions
4. **Monitor usage**: Check Cloud Console for unexpected API calls
5. **Delete unused keys**: Remove old keys from service accounts

## Environment Variables Summary

Required for Render deployment:

```bash
# Google Cloud Project
GOOGLE_PROJECT_ID=783867443498
GOOGLE_DISCOVERY_LOCATION=global
GOOGLE_DISCOVERY_COLLECTION_ID=default_collection
GOOGLE_DISCOVERY_ENGINE_ID=fahm-llm_1779380839747
GOOGLE_DISCOVERY_SERVING_CONFIG=default_search

# Authentication
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json
GOOGLE_APPLICATION_CREDENTIALS_JSON=<paste JSON content>

# Feature flags
USE_DISCOVERY_ENGINE=true
WEB_SEARCH_ENABLED=true
```

## Cost Considerations

- Discovery Engine API calls are billed per request
- Monitor usage in Google Cloud Console > Billing
- Set up budget alerts to avoid unexpected charges
- DuckDuckGo fallback is free (no API costs)

## Support

If you encounter issues:

1. Check Render logs for error messages
2. Verify service account permissions in GCP Console
3. Test authentication locally first
4. Review this documentation
5. Check `docs/GOOGLE_DISCOVERY_ENGINE.md` for API details

---

**Last Updated**: 2026-05-21
**For**: Render Deployment
**Project**: FAHM LLM System