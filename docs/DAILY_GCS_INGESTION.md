# Daily GCS Bucket Ingestion Guide

Automatically ingest new content from Google Cloud Storage into Pinecone every day.

## Overview

The daily ingestion system:
- ✅ **Monitors** your GCS bucket for new/modified files
- ✅ **Tracks** processed files to avoid duplicates
- ✅ **Ingests** PDFs and PowerPoint presentations automatically
- ✅ **Runs** daily at 2:00 AM (configurable)
- ✅ **Logs** all activities for monitoring

## Quick Setup

### Prerequisites

1. **Google Cloud credentials** configured:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   ```

2. **Python dependencies** installed:
   ```bash
   pip install google-cloud-storage
   ```

3. **Environment variables** set:
   ```bash
   export PINECONE_API_KEY="your-key"
   export OPENAI_API_KEY="your-key"
   ```

### Setup on Linux/Mac

```bash
cd scripts
chmod +x setup_daily_ingestion.sh
./setup_daily_ingestion.sh
```

Follow the prompts to:
1. Enter your GCS bucket name
2. Confirm cron job creation

### Setup on Windows

```powershell
cd scripts
.\setup_daily_ingestion.ps1
```

Follow the prompts to:
1. Enter your GCS bucket name
2. Confirm Task Scheduler job creation

## Manual Usage

### Process Last 24 Hours

```bash
cd scripts
python daily_gcs_ingestion.py --bucket your-bucket-name
```

### Process Last 7 Days

```bash
python daily_gcs_ingestion.py --bucket your-bucket-name --days 7
```

### Force Reprocess All Files

```bash
python daily_gcs_ingestion.py --bucket your-bucket-name --days 365 --force
```

## How It Works

### 1. File Tracking

The script maintains a `processed_files.json` file that tracks:
- File name
- Last processed timestamp
- File size
- Last modified date

### 2. New File Detection

On each run, the script:
1. Lists all files in the GCS bucket
2. Compares against tracking file
3. Identifies new or modified files
4. Processes only those files

### 3. Processing Pipeline

For each new file:
1. **Download** from GCS to temporary location
2. **Extract** content (text, images, metadata)
3. **Chunk** content into optimal sizes
4. **Generate** embeddings using OpenAI
5. **Store** in Pinecone vector database
6. **Update** tracking file
7. **Clean up** temporary files

### 4. Supported File Types

- ✅ **PowerPoint (.pptx)** - Extracts text from slides
- ✅ **PDF (.pdf)** - Extracts text and metadata

## Configuration

### Change Schedule Time

#### Linux/Mac (Cron)

Edit crontab:
```bash
crontab -e
```

Change the time (format: minute hour day month weekday):
```bash
# Run at 3:00 AM instead of 2:00 AM
0 3 * * * cd /path/to/scripts && python daily_gcs_ingestion.py --bucket your-bucket
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Find task: `FAHM-Daily-GCS-Ingestion`
3. Right-click → Properties
4. Go to Triggers tab
5. Edit trigger and change time

### Change Lookback Period

Modify the `--days` parameter:

```bash
# Look back 3 days instead of 1
python daily_gcs_ingestion.py --bucket your-bucket --days 3
```

### Multiple Buckets

Create separate cron jobs for each bucket:

```bash
# Bucket 1 at 2:00 AM
0 2 * * * cd /path/to/scripts && python daily_gcs_ingestion.py --bucket bucket-1

# Bucket 2 at 3:00 AM
0 3 * * * cd /path/to/scripts && python daily_gcs_ingestion.py --bucket bucket-2
```

## Monitoring

### View Logs

```bash
# Linux/Mac
tail -f scripts/daily_ingestion.log

# Windows
Get-Content scripts\daily_ingestion.log -Tail 50 -Wait
```

### Check Tracking File

```bash
cat scripts/processed_files.json
```

### Verify Cron Job

```bash
# Linux/Mac
crontab -l

# Windows
Get-ScheduledTask -TaskName "FAHM-Daily-GCS-Ingestion"
```

## Example Output

```
================================================================================
🚀 STARTING DAILY GCS INGESTION
📦 Bucket: fahm-documents
📅 Looking for files from last 1 day(s)
⏰ Start Time: 2026-06-05 02:00:00
================================================================================

✅ Connected to GCS bucket: fahm-documents
🆕 New file: presentations/Q4-2026-Report.pptx
🆕 New file: documents/Product-Guide.pdf
Found 2 new/modified files

📊 Processing PPTX: presentations/Q4-2026-Report.pptx
✅ Ingested 45 chunks from presentations/Q4-2026-Report.pptx

📄 Processing PDF: documents/Product-Guide.pdf
✅ Ingested 78 chunks from documents/Product-Guide.pdf

================================================================================
📊 INGESTION SUMMARY
================================================================================
✅ Successfully processed: 2
❌ Failed: 0
📁 Total files tracked: 127
================================================================================
```

## Troubleshooting

### Issue: Authentication Error

**Error:** `google.auth.exceptions.DefaultCredentialsError`

**Solution:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Issue: No New Files Found

**Possible causes:**
1. All files already processed
2. No files modified in lookback period
3. Bucket name incorrect

**Solution:**
```bash
# Force reprocess with longer lookback
python daily_gcs_ingestion.py --bucket your-bucket --days 7
```

### Issue: Cron Job Not Running

**Check if cron service is running:**
```bash
# Linux
sudo service cron status

# Mac
sudo launchctl list | grep cron
```

**Check cron logs:**
```bash
# Linux
grep CRON /var/log/syslog

# Mac
log show --predicate 'process == "cron"' --last 1h
```

### Issue: Task Scheduler Not Running (Windows)

**Check task status:**
```powershell
Get-ScheduledTask -TaskName "FAHM-Daily-GCS-Ingestion" | Get-ScheduledTaskInfo
```

**Run task manually:**
```powershell
Start-ScheduledTask -TaskName "FAHM-Daily-GCS-Ingestion"
```

### Issue: Out of Memory

**Solution:** Process files in smaller batches:
```bash
# Process only 1 day at a time
python daily_gcs_ingestion.py --bucket your-bucket --days 1
```

## Best Practices

### 1. Regular Monitoring

Set up alerts for failed ingestions:
```bash
# Add to cron job
0 2 * * * cd /path/to/scripts && python daily_gcs_ingestion.py --bucket your-bucket || echo "Ingestion failed" | mail -s "Alert" admin@example.com
```

### 2. Backup Tracking File

```bash
# Daily backup
0 1 * * * cp /path/to/scripts/processed_files.json /path/to/backups/processed_files_$(date +\%Y\%m\%d).json
```

### 3. Log Rotation

```bash
# Keep only last 30 days of logs
find /path/to/scripts -name "daily_ingestion.log.*" -mtime +30 -delete
```

### 4. Test Before Production

```bash
# Test with a small lookback period
python daily_gcs_ingestion.py --bucket your-bucket --days 1
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Daily GCS Ingestion

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Setup GCS credentials
        env:
          GCS_CREDENTIALS: ${{ secrets.GCS_CREDENTIALS }}
        run: echo "$GCS_CREDENTIALS" > /tmp/gcs-key.json
      
      - name: Run ingestion
        env:
          GOOGLE_APPLICATION_CREDENTIALS: /tmp/gcs-key.json
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd scripts
          python daily_gcs_ingestion.py --bucket ${{ secrets.GCS_BUCKET_NAME }}
```

## Support

For issues or questions:
- Check logs: `scripts/daily_ingestion.log`
- Review tracking file: `scripts/processed_files.json`
- Contact FAHM Technology Partners support

---

**Last Updated:** 2026-06-05  
**Version:** 1.0.0