# Documentation Scraping Guide

Complete guide for scraping and ingesting IBM documentation into the vector database.

## Overview

The scraping system extracts content from IBM documentation websites, processes it into chunks, and ingests it into the vector database for RAG-powered question answering.

## Architecture

```
IBM Documentation
    ↓
Base Scraper (fetch & parse)
    ↓
Document Processor (clean & chunk)
    ↓
Embedding Service (generate embeddings)
    ↓
Vector Database (Pinecone)
```

## Components

### 1. Base Scraper (`scraper/base_scraper.py`)

Generic scraper with:
- Async HTTP requests with rate limiting
- HTML parsing with BeautifulSoup
- Link extraction and following
- Visited URL tracking
- Configurable concurrency

### 2. Document Processor (`scraper/document_processor.py`)

Text processing utilities:
- Text cleaning and normalization
- Smart chunking with overlap
- Section extraction
- Metadata preservation

### 3. IBM Cloud Scraper (`scraper/ibm_cloud_scraper.py`)

Specialized scraper for IBM Cloud docs:
- Custom parsing for IBM doc structure
- Breadcrumb extraction
- Section-based scraping
- Predefined documentation sections

## Quick Start

### 1. Scrape Overview Section

```bash
cd backend
python ../scripts/ingest_ibm_docs.py --sections overview --max-pages 10
```

### 2. Scrape Multiple Sections

```bash
python ../scripts/ingest_ibm_docs.py \
  --sections overview containers kubernetes \
  --max-pages 20
```

### 3. Scrape All Sections

```bash
python ../scripts/ingest_ibm_docs.py \
  --sections all \
  --max-pages 50
```

### 4. Test After Ingestion

```bash
python ../scripts/ingest_ibm_docs.py \
  --sections overview \
  --test-query "What is IBM Cloud?"
```

## Available Sections

The IBM Cloud scraper includes predefined sections:

| Section | Description | URL |
|---------|-------------|-----|
| `overview` | IBM Cloud overview | /docs/overview |
| `account` | Account management | /docs/account |
| `iam` | Identity & Access Management | /docs/account?topic=account-iamoverview |
| `containers` | Container services | /docs/containers |
| `kubernetes` | Kubernetes service | /docs/containers?topic=containers-getting-started |
| `openshift` | OpenShift service | /docs/openshift |
| `vpc` | Virtual Private Cloud | /docs/vpc |
| `compute` | Virtual servers | /docs/virtual-servers |
| `storage` | Object storage | /docs/cloud-object-storage |
| `networking` | VPC networking | /docs/vpc?topic=vpc-about-networking-for-vpc |
| `databases` | Database services | /docs/databases-for-postgresql |
| `ai` | Watson AI services | /docs/watson |
| `devops` | DevOps tools | /docs/ContinuousDelivery |
| `security` | Security & compliance | /docs/security-compliance |

## Usage Examples

### Basic Scraping

```python
from scraper.ibm_cloud_scraper import IBMCloudScraper

async def scrape_docs():
    async with IBMCloudScraper() as scraper:
        # Scrape a single section
        documents = await scraper.scrape_section(
            section_url="https://cloud.ibm.com/docs/overview",
            max_pages=20
        )
        
        print(f"Scraped {len(documents)} documents")
        
        # Process into chunks
        chunks = scraper.process_documents(documents)
        print(f"Created {len(chunks)} chunks")
        
        return chunks
```

### Custom Scraping

```python
from scraper.base_scraper import BaseScraper

async def custom_scrape():
    scraper = BaseScraper(
        base_url="https://example.com",
        source_type="Custom Docs",
        max_concurrent=10
    )
    
    async with scraper:
        documents = await scraper.scrape_urls(
            urls=["https://example.com/doc1", "https://example.com/doc2"],
            max_depth=2,
            follow_links=True
        )
        
        return documents
```

### Document Processing

```python
from scraper.document_processor import DocumentProcessor

# Clean text
cleaned = DocumentProcessor.clean_text(raw_text)

# Chunk document
chunks = DocumentProcessor.chunk_document(
    content=cleaned,
    chunk_size=800,
    chunk_overlap=200
)

# Create chunks with metadata
chunk_docs = DocumentProcessor.create_chunks_with_metadata(
    document={
        'content': content,
        'metadata': {
            'title': 'Document Title',
            'url': 'https://...',
            'source_type': 'IBM Cloud Docs'
        }
    }
)
```

### Complete Ingestion Pipeline

```python
from scraper.ibm_cloud_scraper import IBMCloudScraper
from services.embedding_service import embedding_service

async def ingest_pipeline():
    # 1. Scrape documents
    async with IBMCloudScraper() as scraper:
        documents = await scraper.scrape_section(
            section_url="https://cloud.ibm.com/docs/overview",
            max_pages=20
        )
        
        # 2. Process into chunks
        chunks = scraper.process_documents(documents)
    
    # 3. Ingest into vector database
    result = await embedding_service.ingest_documents(
        documents=chunks,
        namespace="ibm-cloud"
    )
    
    print(f"Ingested {result['vectors_upserted']} vectors")
```

## Configuration

### Scraper Settings

```python
scraper = BaseScraper(
    base_url="https://cloud.ibm.com/docs",
    source_type="IBM Cloud Docs",
    max_concurrent=5,      # Concurrent requests
    timeout=30             # Request timeout (seconds)
)
```

### Chunking Settings

In `.env`:

```env
CHUNK_SIZE=800           # Characters per chunk
CHUNK_OVERLAP=200        # Overlap between chunks
```

Or programmatically:

```python
chunks = DocumentProcessor.chunk_document(
    content=text,
    chunk_size=1000,
    chunk_overlap=250
)
```

## Best Practices

### 1. Rate Limiting

- Use `max_concurrent` to limit simultaneous requests
- Add delays between requests if needed
- Respect robots.txt

### 2. Chunk Size Optimization

- **Small chunks (500-700)**: Better precision, more chunks
- **Medium chunks (800-1000)**: Balanced approach (recommended)
- **Large chunks (1000-1500)**: More context, fewer chunks

### 3. Metadata Management

Always include:
- `title`: Document title
- `url`: Source URL
- `source_type`: Documentation source
- `breadcrumbs`: Navigation context (if available)

### 4. Error Handling

```python
try:
    documents = await scraper.scrape_section(url)
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    # Handle error appropriately
```

### 5. Incremental Updates

```python
# Check if document already exists
existing_docs = await vector_service.fetch_vectors(
    ids=[doc_id],
    namespace="ibm-cloud"
)

if not existing_docs:
    # Only ingest if new
    await embedding_service.ingest_documents([doc])
```

## Performance Optimization

### 1. Batch Processing

```python
# Process in batches
batch_size = 50
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    await embedding_service.ingest_documents(batch)
```

### 2. Concurrent Scraping

```python
# Scrape multiple sections concurrently
sections = ['overview', 'containers', 'vpc']
tasks = [scraper.scrape_section(url) for url in section_urls]
results = await asyncio.gather(*tasks)
```

### 3. Caching

```python
# Cache scraped content
import json

# Save to file
with open('scraped_docs.json', 'w') as f:
    json.dump(documents, f)

# Load from file
with open('scraped_docs.json', 'r') as f:
    documents = json.load(f)
```

## Monitoring

### Track Progress

```python
logger.info(f"Scraped {len(documents)} documents")
logger.info(f"Created {len(chunks)} chunks")
logger.info(f"Average chunk size: {sum(len(c['content']) for c in chunks) / len(chunks):.0f} chars")
```

### Verify Ingestion

```python
# Get statistics
stats = await embedding_service.get_statistics()
print(f"Total documents: {stats['total_documents']}")
print(f"Index fullness: {stats['index_fullness']:.2%}")
```

### Test Search

```python
# Test retrieval
results = await embedding_service.search_similar(
    query="What is IBM Cloud?",
    top_k=5
)

for result in results:
    print(f"{result['metadata']['title']}: {result['score']:.2f}")
```

## Troubleshooting

### Issue: Timeout Errors

**Solution**: Increase timeout or reduce concurrency

```python
scraper = BaseScraper(
    base_url=url,
    max_concurrent=3,  # Reduce from 5
    timeout=60         # Increase from 30
)
```

### Issue: Empty Content

**Solution**: Check HTML structure and selectors

```python
# Debug HTML structure
soup = BeautifulSoup(html, 'html.parser')
print(soup.prettify()[:1000])

# Try different selectors
main = soup.find('main') or soup.find('article')
```

### Issue: Too Many Chunks

**Solution**: Increase chunk size or merge short chunks

```python
# Increase chunk size
chunks = DocumentProcessor.chunk_document(
    content=text,
    chunk_size=1200,  # Larger chunks
    chunk_overlap=200
)

# Merge short chunks
merged = DocumentProcessor.merge_short_chunks(
    chunks=chunks,
    min_size=500
)
```

### Issue: Rate Limiting

**Solution**: Add delays and reduce concurrency

```python
import asyncio

async def scrape_with_delay():
    for url in urls:
        doc = await scraper.scrape_url(url)
        await asyncio.sleep(1)  # 1 second delay
```

## Advanced Usage

### Custom Scraper

```python
from scraper.base_scraper import BaseScraper

class CustomScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://custom-docs.com",
            source_type="Custom Docs"
        )
    
    def _extract_content(self, soup):
        # Custom content extraction
        content_div = soup.find('div', class_='custom-content')
        return content_div.get_text() if content_div else ""
    
    def _extract_metadata(self, soup, url):
        # Custom metadata extraction
        return {
            'title': soup.find('h1').text,
            'author': soup.find('meta', {'name': 'author'})['content'],
            'date': soup.find('time')['datetime']
        }
```

### Selective Scraping

```python
# Only scrape pages matching pattern
async def selective_scrape(scraper, urls):
    filtered_urls = [
        url for url in urls
        if '/docs/' in url and not '/api/' in url
    ]
    
    return await scraper.scrape_urls(filtered_urls)
```

### Content Filtering

```python
# Filter out low-quality content
def filter_chunks(chunks):
    return [
        chunk for chunk in chunks
        if len(chunk['content']) > 200  # Minimum length
        and not chunk['content'].startswith('Error')  # No errors
    ]
```

## Next Steps

1. ✅ Scrape IBM Cloud documentation
2. ✅ Process and chunk documents
3. ✅ Ingest into vector database
4. 🔄 Test question answering
5. 🔄 Add more documentation sources
6. 🔄 Implement incremental updates
7. 🔄 Schedule regular re-scraping

## Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [IBM Cloud Docs](https://cloud.ibm.com/docs)

## Support

For scraping issues:
1. Check logs for error messages
2. Verify URL accessibility
3. Inspect HTML structure
4. Test with small batches first
5. Review rate limiting settings