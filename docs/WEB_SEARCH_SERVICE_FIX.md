# Web Search Service - Service Account Token Error Fix

## Issue Description

**Error Log:**
```
2026-05-22 15:06:36,700 - services.web_search_service - ERROR - Error getting service account token: Invalid control character at: line 1 column 168 (char 167)
```

## Root Cause

The error occurred in the `_get_service_account_token()` method when attempting to parse a Google Cloud service account JSON file. The issue was caused by:

1. **Missing or Invalid Service Account File**: The `GOOGLE_APPLICATION_CREDENTIALS` environment variable was not properly set, or the file path pointed to a non-existent or corrupted file.

2. **Poor Error Handling**: The original code attempted to load the service account credentials without first validating:
   - Whether the file path exists
   - Whether the file contains valid JSON
   - Specific error types (FileNotFoundError, JSONDecodeError)

3. **JSON Parsing Error**: When the `service_account.Credentials.from_service_account_file()` method tried to parse an invalid or non-existent file, it raised a generic exception with the cryptic "Invalid control character" message.

## Solution Implemented

### Enhanced Error Handling

The `_get_service_account_token()` method now includes:

1. **Pre-validation Checks**:
   - Checks if `service_account_key_path` is configured
   - Verifies the file exists before attempting to load it
   - Validates JSON format before loading credentials

2. **Specific Exception Handling**:
   - `FileNotFoundError`: Handles missing files gracefully
   - `json.JSONDecodeError`: Catches invalid JSON format errors
   - Generic `Exception`: Catches any other unexpected errors

3. **Improved Logging**:
   - Debug-level logs for expected scenarios (no path configured, file not found)
   - Error-level logs for actual problems (invalid JSON, authentication failures)
   - Clear, actionable error messages

### Code Changes

```python
async def _get_service_account_token(self) -> Optional[str]:
    """
    Get access token using service account credentials
    
    Returns:
        Access token or None if failed
    """
    if not GOOGLE_AUTH_AVAILABLE:
        logger.warning("google-auth library not installed")
        return None
    
    # Check if file exists first
    if not self.service_account_key_path:
        logger.debug("No service account key path configured")
        return None
        
    if not os.path.exists(self.service_account_key_path):
        logger.debug(f"Service account key file not found: {self.service_account_key_path}")
        return None
    
    try:
        # Validate JSON file before attempting to load
        with open(self.service_account_key_path, 'r', encoding='utf-8') as f:
            try:
                json.load(f)
            except json.JSONDecodeError as json_err:
                logger.error(f"Invalid JSON in service account key file: {json_err}")
                return None
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_key_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Refresh the token
        request = Request()
        credentials.refresh(request)
        
        logger.debug("Successfully obtained service account access token")
        return credentials.token
        
    except FileNotFoundError:
        logger.error(f"Service account key file not found: {self.service_account_key_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in service account key file at {self.service_account_key_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting service account token: {str(e)}")
        return None
```

## Configuration Requirements

### For Production Deployment

1. **Set Environment Variable**:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

2. **Ensure Valid Service Account Key**:
   - Download from Google Cloud Console
   - Verify JSON format is valid
   - Ensure file has proper permissions (readable by application)

3. **Required Permissions**:
   The service account needs:
   - `Discovery Engine API` access
   - `discoveryengine.search` permission

### For Development

The service automatically falls back to `gcloud` CLI authentication if:
- No service account key is configured
- Service account authentication fails
- `gcloud` is installed and authenticated

## Fallback Behavior

The web search service has multiple fallback layers:

1. **Primary**: Google Cloud Discovery Engine with service account
2. **Secondary**: Google Cloud Discovery Engine with gcloud CLI
3. **Tertiary**: DuckDuckGo search API

This ensures the service remains functional even when Google Cloud authentication is unavailable.

## Testing

To verify the fix:

```bash
# Test with valid service account
python scripts/test_web_search_fallback.py

# Check logs for proper error handling
tail -f logs/app.log | grep "web_search_service"
```

## Prevention

To prevent similar issues:

1. **Always validate file paths** before attempting to read files
2. **Use specific exception types** for better error handling
3. **Validate JSON format** before parsing
4. **Provide clear error messages** for debugging
5. **Implement graceful fallbacks** for critical services

## Related Files

- `backend/services/web_search_service.py` - Main service file
- `backend/.env` - Environment configuration
- `docs/GOOGLE_DISCOVERY_ENGINE.md` - Discovery Engine setup guide
- `docs/GOOGLE_CLOUD_AUTH_RENDER.md` - Authentication guide for Render

## Status

✅ **Fixed** - Enhanced error handling prevents cryptic JSON parsing errors and provides clear diagnostic information.