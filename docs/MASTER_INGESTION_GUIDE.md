# Master Ingestion Guide

Complete guide for ingesting all new information into the FAHM Faris vector database.

## Overview

The `ingest_all_new_content.py` script is a comprehensive orchestrator that handles ingestion from **all** data sources:

- 🌩️ **IBM Cloud** documentation
- 🏭 **IBM Maximo Application Suite (MAS)** documentation
- 🛡️ **IBM Guardium Data Protection (GDP)** documentation
- 📱 **IBM MaaS360** documentation
- 🏢 **FAHM Partners** website content
- 📄 **PDF** documents
- 📊 **PowerPoint (PPTX)** presentations

## Quick Start

### 1. Ingest Everything (Recommended for Initial Setup)

```bash
cd scripts
python ingest_all_new_content.py
```

This will:
- Scrape all IBM documentation sources (20 pages per section by default)
- Ingest FAHM Partners website content
- Process and store everything in the vector database

### 2. Ingest Specific Sources

```bash
# Only IBM Guardium and MaaS360
python ingest_all_new_content.py --sources ibm_gdp ibm_maas360

# Only FAHM Partners content
python ingest_all_new_content.py --sources fahm_partners

# IBM Cloud and Maximo
python ingest_all_new_content.py --sources ibm_cloud ibm_mas
```

### 3. Ingest with Custom Page Limits

```bash
# Scrape more pages per section (for comprehensive coverage)
python ingest_all_new_content.py --max-pages 50

# Quick test with fewer pages
python ingest_all_new_content.py --max-pages 5
```

### 4. Include PDF Documents

```bash
# From local directory
python ingest_all_new_content.py --pdf-dir ./documents/pdfs

# Combine with other sources
python ingest_all_new_content.py --sources ibm_gdp pdfs --pdf-dir ./documents/pdfs
```

### 5. Include PowerPoint Presentations

```bash
# From local directory
python ingest_all_new_content.py --pptx-dir ./documents/presentations

# From Google Cloud Storage bucket
python ingest_all_new_content.py --gcs-bucket your-bucket-name

# Both local and GCS
python ingest_all_new_content.py --pptx-dir ./presentations --gcs-bucket your-bucket
```

## Complete Examples

### Example 1: Full Production Ingestion

```bash
python ingest_all_new_content.py \
  --max-pages 100 \
  --pdf-dir ./documents/pdfs \
  --pptx-dir ./documents/presentations \
  --gcs-bucket fahm-presentations
```

### Example 2: Quick Update (New Content Only)

```bash
# Just update FAHM Partners and recent IBM docs
python ingest_all_new_content.py \
  --sources fahm_partners ibm_gdp ibm_maas360 \
  --max-pages 10
```

### Example 3: Document-Only Ingestion

```bash
# Only process PDFs and PPTX files
python ingest_all_new_content.py \
  --sources pdfs pptx \
  --pdf-dir ./new_documents \
  --pptx-dir ./new_presentations
```

## Available Sources

| Source | Description | Namespace |
|--------|-------------|-----------|
| `ibm_cloud` | IBM Cloud documentation | `ibm-cloud` |
| `ibm_mas` | IBM Maximo Application Suite | `ibm-mas` |
| `ibm_gdp` | IBM Guardium Data Protection | `ibm-docs` |
| `ibm_maas360` | IBM MaaS360 Mobile Device Management | `ibm-docs` |
| `fahm_partners` | FAHM Technology Partners website | `fahm-partners` |
| `pdfs` | PDF documents | `ibm-docs` |
| `pptx` | PowerPoint presentations | `ibm-docs` |

## Command-Line Options

```
--sources [SOURCE ...]
    Specific sources to ingest (default: all)
    Choices: ibm_cloud, ibm_mas, ibm_gdp, ibm_maas360, fahm_partners, pdfs, pptx

--max-pages INT
    Maximum pages per section for web scraping (default: 20)

--pdf-dir PATH
    Directory containing PDF files to ingest

--pptx-dir PATH
    Directory containing PPTX files to ingest

--gcs-bucket NAME
    Google Cloud Storage bucket name for PPTX files
```

## Output and Monitoring

The script provides detailed progress information:

```
🚀 STARTING MASTER INGESTION PIPELINE
⏰ Start Time: 2026-06-05 09:00:00
================================================================================

🌩️  INGESTING IBM CLOUD DOCUMENTATION
================================================================================
📄 Scraping: Overview
✅ Overview: 15 docs, 234 chunks
📄 Scraping: Getting Started
✅ Getting Started: 12 docs, 189 chunks
...

📊 INGESTION SUMMARY
================================================================================
⏰ Duration: 0:15:32

✅ IBM CLOUD: success
   📄 Documents: 127
   🔢 Chunks: 1,845

✅ IBM MAS: success
   📄 Documents: 98
   🔢 Chunks: 1,432
...

📊 TOTAL DOCUMENTS: 450
🔢 TOTAL CHUNKS: 6,789
================================================================================
```

## Scheduling Regular Updates

### Using Cron (Linux/Mac)

```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/FAHM/scripts && python ingest_all_new_content.py --max-pages 30

# Run weekly on Sunday at 3 AM (comprehensive)
0 3 * * 0 cd /path/to/FAHM/scripts && python ingest_all_new_content.py --max-pages 100
```

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 2:00 AM)
4. Action: Start a program
   - Program: `python`
   - Arguments: `ingest_all_new_content.py --max-pages 30`
   - Start in: `C:\path\to\FAHM\scripts`

### Using Python Script

```python
# scheduled_ingestion.py
import schedule
import time
import subprocess

def run_ingestion():
    subprocess.run([
        "python", "ingest_all_new_content.py",
        "--max-pages", "30"
    ])

# Run every day at 2 AM
schedule.every().day.at("02:00").do(run_ingestion)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Troubleshooting

### Issue: Import Errors

**Solution:** Make sure you're running from the `scripts` directory and the backend path is correct:

```bash
cd scripts
python ingest_all_new_content.py
```

### Issue: Authentication Errors (GCS)

**Solution:** Set up Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Issue: Rate Limiting

**Solution:** Reduce `--max-pages` or add delays between requests:

```bash
python ingest_all_new_content.py --max-pages 10
```

### Issue: Memory Errors

**Solution:** Process sources separately:

```bash
# Process one at a time
python ingest_all_new_content.py --sources ibm_cloud
python ingest_all_new_content.py --sources ibm_mas
python ingest_all_new_content.py --sources ibm_gdp
```

## Best Practices

### 1. Initial Setup (First Time)

```bash
# Comprehensive ingestion with high page limits
python ingest_all_new_content.py --max-pages 100
```

### 2. Regular Updates (Daily/Weekly)

```bash
# Moderate page limits for new content
python ingest_all_new_content.py --max-pages 20
```

### 3. Quick Refresh (After Known Updates)

```bash
# Target specific sources
python ingest_all_new_content.py --sources fahm_partners --max-pages 10
```

### 4. Document Processing

```bash
# Process new documents as they arrive
python ingest_all_new_content.py \
  --sources pdfs pptx \
  --pdf-dir ./new_docs \
  --pptx-dir ./new_presentations
```

## Monitoring Vector Database

After ingestion, check the database statistics:

```bash
python scripts/check_vector_count.py
```

Or use the API:

```bash
curl -X GET "https://your-api.railway.app/api/metrics" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Daily Content Ingestion

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
        run: |
          pip install -r backend/requirements.txt
      
      - name: Run ingestion
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd scripts
          python ingest_all_new_content.py --max-pages 30
```

## Support

For issues or questions:
- Check logs in the console output
- Review `docs/TROUBLESHOOTING.md`
- Contact FAHM Technology Partners support

---

**Last Updated:** 2026-06-05  
**Version:** 1.0.0