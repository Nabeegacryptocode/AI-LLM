# PDF Ingestion Guide

Complete guide for ingesting PDF documents into the Pinecone vector database.

## Overview

The PDF ingestion system allows you to:
- Extract text from PDF files
- Chunk documents intelligently
- Generate embeddings
- Store in Pinecone for semantic search
- Query documents via the chat API

## Features

✅ **Multiple PDF Libraries**: Supports both PyPDF2 and pdfplumber
✅ **Automatic Text Extraction**: Extracts text from all pages
✅ **Metadata Extraction**: Captures title, author, pages, etc.
✅ **Smart Chunking**: Breaks documents into optimal chunks
✅ **Batch Processing**: Process multiple PDFs at once
✅ **Directory Ingestion**: Recursively process entire folders
✅ **API Endpoints**: REST API for file uploads
✅ **CLI Script**: Command-line tool for local files

## Installation

### Required Dependencies

```bash
pip install PyPDF2 pdfplumber
```

These are already included in `requirements.txt`:
```
PyPDF2>=3.0.1
pdfplumber>=0.10.3
```

## Usage Methods

### 1. API Upload (Recommended for Production)

#### Single PDF Upload

```bash
curl -X POST "http://localhost:8000/api/pdf/upload" \
  -H "X-API-Key: your_api_key" \
  -F "file=@document.pdf" \
  -F "namespace=my-docs" \
  -F "title=Custom Title" \
  -F "author=John Doe"
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested PDF: document.pdf",
  "data": {
    "filename": "document.pdf",
    "chunks_created": 25,
    "vectors_stored": 25,
    "namespace": "my-docs",
    "metadata": {
      "title": "Custom Title",
      "author": "John Doe",
      "num_pages": 10,
      "file_size": 524288
    }
  }
}
```

#### Multiple PDF Upload

```bash
curl -X POST "http://localhost:8000/api/pdf/upload-multiple" \
  -H "X-API-Key: your_api_key" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "files=@doc3.pdf" \
  -F "namespace=my-docs"
```

**Response:**
```json
{
  "status": "success",
  "message": "Processed 3 of 3 files",
  "data": {
    "total_files": 3,
    "processed": 3,
    "failed": 0,
    "total_chunks": 75,
    "total_vectors": 75,
    "files": [...]
  }
}
```

#### Ingest from Server Path

```bash
curl -X POST "http://localhost:8000/api/pdf/ingest-from-path" \
  -H "X-API-Key: your_api_key" \
  -F "path=/path/to/pdfs/" \
  -F "namespace=my-docs" \
  -F "recursive=true"
```

### 2. Python Script (For Local Files)

#### Single PDF

```bash
cd scripts
python ingest_pdf.py /path/to/document.pdf
```

#### With Namespace

```bash
python ingest_pdf.py /path/to/document.pdf my-namespace
```

#### Entire Directory

```bash
python ingest_pdf.py /path/to/pdfs/
```

#### Directory (Non-Recursive)

```bash
python ingest_pdf.py /path/to/pdfs/ my-namespace --no-recursive
```

### 3. Python Code

```python
import asyncio
from scraper.pdf_scraper import pdf_scraper

async def ingest_pdf():
    # Single PDF
    result = await pdf_scraper.process_pdf(
        pdf_path="/path/to/document.pdf",
        namespace="my-docs",
        custom_metadata={
            "category": "technical",
            "department": "engineering"
        }
    )
    
    print(f"Chunks: {result['chunks_created']}")
    print(f"Vectors: {result['vectors_stored']}")
    
    # Directory
    result = await pdf_scraper.process_pdf_directory(
        directory_path="/path/to/pdfs/",
        namespace="my-docs",
        recursive=True
    )
    
    print(f"Processed: {result['processed']}/{result['total_files']}")

asyncio.run(ingest_pdf())
```

## API Endpoints

### POST /api/pdf/upload

Upload and ingest a single PDF file.

**Parameters:**
- `file` (file, required): PDF file to upload
- `namespace` (string, optional): Pinecone namespace
- `title` (string, optional): Custom title
- `author` (string, optional): Custom author
- `source` (string, optional): Source information

**Headers:**
- `X-API-Key`: Your API key

**Response:** Ingestion results with metadata

### POST /api/pdf/upload-multiple

Upload and ingest multiple PDF files.

**Parameters:**
- `files` (file[], required): Array of PDF files
- `namespace` (string, optional): Pinecone namespace

**Headers:**
- `X-API-Key`: Your API key

**Response:** Batch processing results

### POST /api/pdf/ingest-from-path

Ingest PDFs from a server path.

**Parameters:**
- `path` (string, required): File or directory path
- `namespace` (string, optional): Pinecone namespace
- `recursive` (boolean, optional): Search subdirectories (default: true)

**Headers:**
- `X-API-Key`: Your API key

**Response:** Processing results

## How It Works

### 1. Text Extraction

The system uses two PDF libraries:

**pdfplumber** (Primary):
- Better text extraction quality
- Handles complex layouts
- Extracts tables and structured data

**PyPDF2** (Fallback):
- Faster processing
- Lower memory usage
- Good for simple PDFs

### 2. Metadata Extraction

Automatically extracts:
- Title
- Author
- Subject
- Creator/Producer
- Creation date
- Number of pages
- File size

### 3. Text Processing

- Cleans extracted text
- Removes excessive whitespace
- Normalizes formatting
- Preserves structure

### 4. Chunking

Documents are split into chunks:
- Default size: 800 characters
- Overlap: 200 characters
- Smart boundary detection (sentences)
- Maintains context

### 5. Embedding & Storage

- Generates embeddings using OpenAI
- Stores in Pinecone with metadata
- Enables semantic search

## Configuration

### Chunk Settings

Modify in `backend/app/config.py`:

```python
CHUNK_SIZE = 800  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
```

### PDF Extraction Method

Choose extraction method:

```python
# Auto (tries pdfplumber, falls back to PyPDF2)
result = await pdf_scraper.process_pdf(pdf_path, method='auto')

# Force pdfplumber
result = await pdf_scraper.process_pdf(pdf_path, method='pdfplumber')

# Force PyPDF2
result = await pdf_scraper.process_pdf(pdf_path, method='pypdf2')
```

## Examples

### Example 1: Technical Documentation

```bash
# Upload technical manual
curl -X POST "http://localhost:8000/api/pdf/upload" \
  -H "X-API-Key: your_key" \
  -F "file=@ibm-cloud-manual.pdf" \
  -F "namespace=ibm-docs" \
  -F "title=IBM Cloud Manual" \
  -F "source=IBM Documentation"
```

### Example 2: Research Papers

```python
import asyncio
from scraper.pdf_scraper import pdf_scraper

async def ingest_research_papers():
    result = await pdf_scraper.process_pdf_directory(
        directory_path="/research/papers/",
        namespace="research",
        custom_metadata={
            "category": "research",
            "year": "2024"
        }
    )
    
    print(f"Ingested {result['processed']} papers")
    print(f"Total vectors: {result['total_vectors']}")

asyncio.run(ingest_research_papers())
```

### Example 3: Batch Processing

```bash
# Process entire directory
python scripts/ingest_pdf.py /documents/manuals/ technical-docs

# Output:
# ✅ Successfully processed directory: /documents/manuals/
#    Total files: 15
#    Processed: 15
#    Failed: 0
#    Total chunks: 375
#    Total vectors: 375
```

## Querying Ingested PDFs

After ingestion, query via chat API:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What does the manual say about installation?",
    "conversation_id": "user-123"
  }'
```

The system will:
1. Search Pinecone for relevant chunks
2. Retrieve matching PDF content
3. Generate contextual answer
4. Include source citations

## Troubleshooting

### Issue: "No PDF library available"

**Solution**: Install dependencies
```bash
pip install PyPDF2 pdfplumber
```

### Issue: "Extracted text too short"

**Causes**:
- Scanned PDF (image-based)
- Encrypted PDF
- Corrupted file

**Solutions**:
1. Use OCR for scanned PDFs
2. Decrypt PDF first
3. Try different extraction method

### Issue: "Failed to extract text"

**Solution**: Try different method
```python
# If pdfplumber fails, try PyPDF2
result = await pdf_scraper.process_pdf(pdf_path, method='pypdf2')
```

### Issue: Poor text quality

**Solution**: Use pdfplumber
```python
result = await pdf_scraper.process_pdf(pdf_path, method='pdfplumber')
```

### Issue: Memory errors with large PDFs

**Solutions**:
1. Process in smaller batches
2. Increase chunk size
3. Use PyPDF2 (lower memory)

## Best Practices

### 1. Organize by Namespace

```python
# Separate by category
await pdf_scraper.process_pdf(doc, namespace="technical-docs")
await pdf_scraper.process_pdf(doc, namespace="user-guides")
await pdf_scraper.process_pdf(doc, namespace="research")
```

### 2. Add Rich Metadata

```python
custom_metadata = {
    "category": "technical",
    "department": "engineering",
    "version": "2.0",
    "language": "en",
    "tags": ["cloud", "infrastructure"]
}

result = await pdf_scraper.process_pdf(
    pdf_path,
    custom_metadata=custom_metadata
)
```

### 3. Batch Processing

Process multiple files efficiently:

```python
# Use directory processing
result = await pdf_scraper.process_pdf_directory(
    "/path/to/pdfs/",
    namespace="docs"
)
```

### 4. Error Handling

```python
result = await pdf_scraper.process_pdf(pdf_path)

if result['success']:
    print(f"✅ Success: {result['vectors_stored']} vectors")
else:
    print(f"❌ Error: {result['error']}")
```

### 5. Monitor Progress

```python
for pdf_file in pdf_files:
    result = await pdf_scraper.process_pdf(pdf_file)
    print(f"Processed: {pdf_file} - {result['chunks_created']} chunks")
```

## Performance

### Processing Speed

- Small PDF (10 pages): ~5-10 seconds
- Medium PDF (50 pages): ~20-30 seconds
- Large PDF (200 pages): ~1-2 minutes

### Optimization Tips

1. **Use batch processing** for multiple files
2. **Choose appropriate chunk size** (larger = fewer chunks)
3. **Use PyPDF2** for simple PDFs (faster)
4. **Process during off-peak hours** for large batches

## Limitations

1. **Scanned PDFs**: Requires OCR (not included)
2. **Encrypted PDFs**: Must be decrypted first
3. **Complex Layouts**: May lose formatting
4. **Images**: Text in images not extracted
5. **Tables**: May not preserve structure perfectly

## Future Enhancements

Planned features:
- [ ] OCR support for scanned PDFs
- [ ] Table extraction and preservation
- [ ] Image text extraction
- [ ] PDF form data extraction
- [ ] Multi-language support
- [ ] Progress tracking for large batches
- [ ] Automatic PDF decryption
- [ ] PDF validation before processing

## Support

For issues:
1. Check logs: `backend/logs/`
2. Test with sample PDF
3. Try different extraction method
4. Review this documentation
5. Check PDF file integrity

## References

- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [Pinecone Documentation](https://docs.pinecone.io/)

---

**Last Updated**: 2026-05-21
**Version**: 1.0.0