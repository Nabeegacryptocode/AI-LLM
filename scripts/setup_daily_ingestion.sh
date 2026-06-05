#!/bin/bash
# Setup script for daily GCS ingestion cron job

echo "🚀 Setting up daily GCS ingestion..."
echo ""

# Get bucket name
read -p "Enter your GCS bucket name: " BUCKET_NAME

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Bucket name is required"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Create cron job
CRON_CMD="0 2 * * * cd $SCRIPT_DIR && /usr/bin/python3 daily_gcs_ingestion.py --bucket $BUCKET_NAME >> $SCRIPT_DIR/daily_ingestion.log 2>&1"

echo ""
echo "📝 Cron job to be added:"
echo "$CRON_CMD"
echo ""

read -p "Add this cron job? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
    echo "✅ Cron job added successfully!"
    echo ""
    echo "The script will run daily at 2:00 AM"
    echo "Logs will be saved to: $SCRIPT_DIR/daily_ingestion.log"
    echo ""
    echo "To view current cron jobs:"
    echo "  crontab -l"
    echo ""
    echo "To remove this cron job:"
    echo "  crontab -e"
else
    echo "❌ Cron job not added"
fi

echo ""
echo "✅ Setup complete!"

# Made with Bob
