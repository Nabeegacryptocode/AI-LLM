# Quick Setup Guide: Google Cloud Discovery Engine

This guide will help you quickly set up and test the Google Cloud Discovery Engine integration.

## Prerequisites

- Google Cloud account with billing enabled
- Project ID: `783867443498`
- Discovery Engine already configured (engine ID: `fahm-llm_1779380839747`)

## Step 1: Install Google Cloud CLI

### Windows (PowerShell)
```powershell
# Download and run installer
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### macOS
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

## Step 2: Authenticate with Google Cloud

```bash
# Login to your Google account
gcloud auth login

# Set the project
gcloud config set project 783867443498

# Verify authentication
gcloud auth list

# Test access token generation
gcloud auth print-access-token
```

## Step 3: Configure Environment Variables

Copy the example environment file and update it:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and ensure these settings are present:

```bash
# Google Discovery Engine Settings
GOOGLE_PROJECT_ID=783867443498
GOOGLE_DISCOVERY_LOCATION=global
GOOGLE_DISCOVERY_COLLECTION_ID=default_collection
GOOGLE_DISCOVERY_ENGINE_ID=fahm-llm_1779380839747
GOOGLE_DISCOVERY_SERVING_CONFIG=default_search
USE_DISCOVERY_ENGINE=true
WEB_SEARCH_ENABLED=true
```

## Step 4: Test the Integration

### Quick Test with curl

```bash
# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Test search (replace <QUERY> with your search term)
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/783867443498/locations/global/collections/default_collection/engines/fahm-llm_1779380839747/servingConfigs/default_search:search" \
  -d '{
    "query": "IBM Cloud documentation",
    "pageSize": 5,
    "queryExpansionSpec": {"condition": "AUTO"},
    "spellCorrectionSpec": {"mode": "AUTO"},
    "languageCode": "en-US"
  }'
```

### Test with Python Script

```bash
# From project root
cd scripts
python test_discovery_engine.py
```

Expected output:
```
================================================================================
Testing Google Cloud Discovery Engine Integration
================================================================================

================================================================================
Query: IBM Cloud documentation
================================================================================

✓ Found 3 results

Result 1:
  Title: IBM Cloud Documentation
  Source: Google Discovery Engine
  URL: https://cloud.ibm.com/docs
  Score: 0.95
  Content: IBM Cloud documentation provides comprehensive guides...
```

## Step 5: Verify Integration in Application

Start your backend server:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Test the chat endpoint:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "What is IBM Cloud?",
    "conversation_id": "test-123"
  }'
```

## Troubleshooting

### Issue: "gcloud: command not found"

**Solution**: 
- Restart your terminal after installing gcloud
- Add gcloud to PATH manually:
  - Windows: `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin`
  - macOS/Linux: `~/google-cloud-sdk/bin`

### Issue: "Failed to get gcloud token"

**Solution**:
```bash
# Re-authenticate
gcloud auth login

# Verify
gcloud auth list

# Check project
gcloud config get-value project
```

### Issue: "403 Permission Denied"

**Solution**:
- Verify you have the correct IAM permissions
- Check in Google Cloud Console: IAM & Admin > IAM
- Required role: `Discovery Engine Viewer` or `Discovery Engine Admin`

### Issue: "No results found"

**Solution**:
- Verify the engine has indexed content
- Check engine status in Google Cloud Console
- Try a different query
- Check if engine ID is correct

### Issue: "Service falls back to DuckDuckGo"

**Solution**:
- This is expected behavior if Discovery Engine fails
- Check logs for specific error messages
- Verify gcloud authentication
- Check network connectivity

## Verification Checklist

- [ ] Google Cloud CLI installed
- [ ] Authenticated with `gcloud auth login`
- [ ] Project set to `783867443498`
- [ ] Access token can be generated
- [ ] Environment variables configured
- [ ] curl test returns results
- [ ] Python test script runs successfully
- [ ] Backend server starts without errors
- [ ] Chat endpoint returns responses

## Next Steps

1. **Review Documentation**: Read `docs/GOOGLE_DISCOVERY_ENGINE.md` for detailed information
2. **Monitor Usage**: Check Google Cloud Console for API usage and quotas
3. **Optimize Queries**: Refine queries for better results
4. **Enable Caching**: Consider implementing result caching for better performance
5. **Set Up Monitoring**: Configure logging and monitoring for production

## Support Resources

- **Documentation**: `docs/GOOGLE_DISCOVERY_ENGINE.md`
- **Test Script**: `scripts/test_discovery_engine.py`
- **Service Code**: `backend/services/web_search_service.py`
- **Google Cloud Console**: https://console.cloud.google.com/
- **Discovery Engine Docs**: https://cloud.google.com/generative-ai-app-builder/docs

## Quick Reference

### Useful Commands

```bash
# Check gcloud version
gcloud --version

# Get current project
gcloud config get-value project

# List authenticated accounts
gcloud auth list

# Get access token
gcloud auth print-access-token

# Test Discovery Engine
python scripts/test_discovery_engine.py

# Start backend server
cd backend && python -m uvicorn app.main:app --reload
```

### Configuration Files

- Environment: `backend/.env`
- Config: `backend/app/config.py`
- Service: `backend/services/web_search_service.py`
- Tests: `scripts/test_discovery_engine.py`

---

**Setup Time**: ~10-15 minutes
**Difficulty**: Intermediate
**Last Updated**: 2026-05-21