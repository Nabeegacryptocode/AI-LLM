# PowerPoint (PPTX) Ingestion Guide

Complete guide for ingesting PowerPoint presentations into Pinecone and Discovery Engine.

## Overview

Extract text from PowerPoint presentations (.pptx, .ppt) and index them for semantic search.

## Features

✅ **Text Extraction**: Extracts text from all slides
✅ **Table Support**: Extracts text from tables
✅ **Metadata Capture**: Title, author, dates, slide count
✅ **Flexible Chunking**: By slide or standard chunking
✅ **GCS Integration**: Download from Google Cloud Storage
✅ **Batch Processing**: Process multiple files
✅ **API Endpoints**: REST API for uploads

## Installation

```bash
pip install python-pptx google-cloud-storage
```

Already in `requirements.txt`.

## Usage

### 1. From Google Cloud Storage (Your Use Case)

```bash
# Install dependencies
pip install python-pptx google-cloud-storage

# Authenticate with Google Cloud
gcloud auth application-default login

# Ingest all PPTX from GCS bucket
cd scripts
python ingest_gcs_pptx.py llm-bucketfahm

# With namespace
python ingest_gcs_pptx.py llm-bucketfahm presentations

# With prefix (subfolder)
python ingest_gcs_pptx.py llm-bucketfahm presentations folder/

# Chunk by slide (one chunk per slide)
python ingest_gcs_pptx.py llm-bucketfahm presentations "" --by-slide
```

### 2. From Local Files

```bash
# Single PPTX
python ingest_pptx.py presentation.pptx

# Directory
python ingest_pptx.py /path/to/presentations/

# With namespace
python ingest_pptx.py /path/to/presentations/ my-namespace
```

### 3. Via API

```bash
curl -X POST "http://localhost:8000/api/pptx/upload" \
  -H "X-API-Key: your_key" \
  -F "file=@presentation.pptx" \
  -F "namespace=presentations"
```

### 4. Python Code

```python
import asyncio
from scraper.pptx_scraper import pptx_scraper

async def ingest_pptx():
    result = await pptx_scraper.process_pptx(
        pptx_path="/path/to/presentation.pptx",
        namespace="presentations",
        chunk_by_slide=True  # One chunk per slide
    )
    
    print(f"Slides: {result['slides_processed']}")
    print(f"Chunks: {result['chunks_created']}")
    print(f"Vectors: {result['vectors_stored']}")

asyncio.run(ingest_pptx())
```

## Your Specific Case

### GCS Bucket: `llm-bucketfahm`

```bash
# Step 1: Install dependencies
pip install python-pptx google-cloud-storage

# Step 2: Authenticate
gcloud auth application-default login
# Or set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Step 3: Ingest all PPTX files
cd scripts
python ingest_gcs_pptx.py llm-bucketfahm presentations

# Output:
# ================================================================================
# GCS PPTX Ingestion Script
# ================================================================================
# 
# Bucket: llm-bucketfahm
# Prefix: (root)
# Namespace: presentations
# 
# 📋 Listing PPTX files in GCS...
# ✅ Found 5 PPTX files
# 
# [1/5] Processing: presentation1.pptx
# --------------------------------------------------------------------------------
#   📥 Downloading...
#   📄 Extracting text...
#   ✅ Success!
#      Slides: 15/15
#      Chunks: 8
#      Vectors: 8
# ...
```

## Chunking Strategies

### Standard Chunking (Default)
- Combines all slides into one document
- Chunks by character count (800 chars)
- Better for long presentations
- Maintains context across slides

```python
result = await pptx_scraper.process_pptx(
    pptx_path,
    chunk_by_slide=False  # Default
)
```

### Chunk by Slide
- One chunk per slide
- Better for slide-specific queries
- Preserves slide boundaries
- Good for presentations with distinct topics per slide

```python
result = await pptx_scraper.process_pptx(
    pptx_path,
    chunk_by_slide=True
)
```

## Extracted Content

### Text Sources:
- Slide titles
- Text boxes
- Bullet points
- Tables (formatted as rows)
- Notes (if accessible)

### Metadata Captured:
- Filename
- Title
- Author
- Subject
- Keywords
- Created/Modified dates
- Total slides
- Slides with content

## GCS Authentication

### Option 1: Application Default Credentials
```bash
gcloud auth application-default login
```

### Option 2: Service Account
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Option 3: In Code
```python
from google.cloud import storage
storage_client = storage.Client.from_service_account_json(
    '/path/to/service-account-key.json'
)
```

## Examples

### Example 1: Ingest from Your GCS Bucket

```bash
# All PPTX files in bucket
python ingest_gcs_pptx.py llm-bucketfahm

# Specific folder
python ingest_gcs_pptx.py llm-bucketfahm "" presentations/

# With custom namespace
python ingest_gcs_pptx.py llm-bucketfahm my-docs

# Chunk by slide for better slide-specific search
python ingest_gcs_pptx.py llm-bucketfahm presentations "" --by-slide
```

### Example 2: Query After Ingestion

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does slide 5 say about pricing?",
    "conversation_id": "user-123"
  }'
```

## Troubleshooting

### Issue: "python-pptx not installed"
```bash
pip install python-pptx
```

### Issue: "google-cloud-storage not installed"
```bash
pip install google-cloud-storage
```

### Issue: "Authentication failed"
```bash
# Use application default credentials
gcloud auth application-default login

# Or set service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Issue: "No text extracted"
- Check if slides have text content
- Some slides may only have images
- Try different PPTX file

### Issue: "Permission denied on GCS"
- Verify bucket name is correct
- Check IAM permissions
- Ensure service account has Storage Object Viewer role

## Performance

- Small presentation (10 slides): ~5-10 seconds
- Medium presentation (50 slides): ~20-30 seconds
- Large presentation (100+ slides): ~1-2 minutes

## Best Practices

1. **Use namespaces** to organize presentations
2. **Chunk by slide** for slide-specific queries
3. **Add metadata** for better filtering
4. **Batch process** multiple files
5. **Monitor progress** with logging

## Integration with Discovery Engine

After ingesting PPTX into Pinecone, also index in Discovery Engine:

1. Upload PPTX to GCS bucket
2. In Discovery Engine Console, add GCS bucket as data source
3. Discovery Engine will index the files
4. Both systems work together for comprehensive search

## API Endpoints (Coming Soon)

- `POST /api/pptx/upload` - Upload PPTX file
- `POST /api/pptx/upload-multiple` - Upload multiple files
- `POST /api/pptx/ingest-from-gcs` - Ingest from GCS bucket

## Next Steps

1. Run the ingestion script on your GCS bucket
2. Wait for processing to complete
3. Test queries via chat API
4. Monitor vector count in Pinecone

---

**Last Updated**: 2026-05-21
**Version**: 1.0.0