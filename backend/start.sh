#!/bin/bash
set -e

# Handle Google Cloud credentials
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS_JSON" ]; then
    echo "Setting up Google Cloud credentials from environment variable..."
    
    # Write credentials to file, preserving all formatting
    echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/gcp-key.json
    
    # Validate JSON format
    if python3 -c "import json; json.load(open('/tmp/gcp-key.json'))" 2>/dev/null; then
        export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json
        echo "✓ Google Cloud credentials configured successfully"
    else
        echo "⚠ Warning: Invalid JSON in GOOGLE_APPLICATION_CREDENTIALS_JSON"
        echo "⚠ Service will fall back to gcloud CLI or DuckDuckGo search"
        rm -f /tmp/gcp-key.json
    fi
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "Using GOOGLE_APPLICATION_CREDENTIALS file path: $GOOGLE_APPLICATION_CREDENTIALS"
else
    echo "No Google Cloud credentials configured, will use gcloud CLI or DuckDuckGo fallback"
fi

# Set default port if not specified
PORT=${PORT:-8000}

echo "Starting application on port $PORT..."

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Made with Bob
