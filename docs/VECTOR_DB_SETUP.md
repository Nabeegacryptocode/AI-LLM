# Vector Database Setup Guide

This guide explains how to set up and use the Pinecone vector database integration for the IBM Docs LLM system.

## Overview

The vector database stores document embeddings and enables semantic search for the RAG (Retrieval Augmented Generation) pipeline.

## Architecture

```
User Question
    ↓
Embedding Service (OpenAI)
    ↓
Vector Search (Pinecone)
    ↓
Retrieved Documents
    ↓
LLM Generation (GPT-4)
    ↓
Answer with Sources
```

## Prerequisites

1. **Pinecone Account**: Sign up at https://www.pinecone.io
2. **API Key**: Get your API key from Pinecone dashboard
3. **Environment**: Note your Pinecone environment (e.g., us-west1-gcp)

## Setup Steps

### 1. Configure Environment Variables

Add to your `.env` file:

```env
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=ibm-docs
EMBEDDING_DIMENSION=1536
```

### 2. Initialize Pinecone Index

Run the setup script:

```bash
cd backend
python ../scripts/setup_pinecone.py
```

This will:
- Connect to Pinecone
- Create the index if it doesn't exist
- Configure metadata indexing
- Display index statistics

### 3. Test the Integration

Run the test script:

```bash
python ../scripts/test_vector_db.py
```

This will:
- Initialize the vector service
- Create test documents
- Generate embeddings
- Store in Pinecone
- Perform similarity search
- Clean up test data

## Services Overview

### Vector Service (`services/vector_service.py`)

Handles direct Pinecone operations:

```python
from services.vector_service import vector_service

# Initialize
vector_service.initialize()

# Upsert vectors
await vector_service.upsert_vectors(vectors, namespace="docs")

# Search
results = await vector_service.search(
    query_vector=embedding,
    top_k=5,
    namespace="docs"
)

# Get stats
stats = await vector_service.get_index_stats()
```

### Embedding Service (`services/embedding_service.py`)

Manages embeddings and document ingestion:

```python
from services.embedding_service import embedding_service

# Ingest documents
result = await embedding_service.ingest_documents(
    documents=[
        {
            "content": "Document text...",
            "metadata": {
                "title": "Doc Title",
                "url": "https://...",
                "source_type": "IBM Cloud"
            }
        }
    ],
    namespace="docs"
)

# Search similar documents
results = await embedding_service.search_similar(
    query="What is IBM Cloud?",
    top_k=5,
    namespace="docs"
)
```

### RAG Service (`services/rag_service.py`)

Complete RAG pipeline:

```python
from services.rag_service import rag_service

# Generate answer with RAG
result = await rag_service.generate_answer(
    question="How do I deploy on IBM Cloud?",
    max_tokens=1000
)

# Result contains:
# - answer: Generated response
# - sources: Retrieved documents
# - conversation_id: Conversation tracking
# - tokens_used: Token count
```

## Document Format

Documents should follow this structure:

```python
{
    "content": "The actual text content of the document...",
    "metadata": {
        "title": "Document Title",
        "url": "https://source-url.com",
        "source_type": "IBM Cloud Docs",
        "section": "Getting Started",
        "last_updated": "2024-01-01"
    }
}
```

## Ingestion Workflow

### 1. Prepare Documents

```python
documents = [
    {
        "content": "IBM Cloud provides...",
        "metadata": {
            "title": "IBM Cloud Overview",
            "url": "https://cloud.ibm.com/docs/overview",
            "source_type": "IBM Cloud Docs"
        }
    }
]
```

### 2. Ingest to Vector DB

```python
from services.embedding_service import embedding_service

result = await embedding_service.ingest_documents(
    documents=documents,
    namespace="ibm-docs"
)

print(f"Ingested {result['vectors_upserted']} documents")
```

### 3. Verify Ingestion

```python
stats = await embedding_service.get_statistics()
print(f"Total documents: {stats['total_documents']}")
```

## Search and Retrieval

### Basic Search

```python
results = await embedding_service.search_similar(
    query="What is IBM Watson?",
    top_k=5
)

for result in results:
    print(f"Title: {result['metadata']['title']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:200]}...")
```

### Filtered Search

```python
results = await embedding_service.search_similar(
    query="Container deployment",
    top_k=5,
    filter_dict={"source_type": "IBM Cloud Docs"}
)
```

### Using Namespaces

Organize documents by namespace:

```python
# Ingest to specific namespace
await embedding_service.ingest_documents(
    documents=cloud_docs,
    namespace="ibm-cloud"
)

await embedding_service.ingest_documents(
    documents=watson_docs,
    namespace="ibm-watson"
)

# Search specific namespace
results = await embedding_service.search_similar(
    query="AI services",
    namespace="ibm-watson"
)
```

## Configuration Options

### Chunk Size

Control document chunking:

```env
CHUNK_SIZE=800          # Characters per chunk
CHUNK_OVERLAP=200       # Overlap between chunks
```

### Retrieval Settings

```env
TOP_K_RESULTS=5              # Number of documents to retrieve
MIN_RELEVANCE_SCORE=0.7      # Minimum similarity score
```

### Embedding Model

```env
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

## Performance Optimization

### 1. Batch Processing

Process documents in batches:

```python
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i + batch_size]
    await embedding_service.ingest_documents(batch)
```

### 2. Metadata Indexing

Index frequently filtered fields:

```python
pinecone.create_index(
    name="ibm-docs",
    dimension=1536,
    metadata_config={
        "indexed": ["source_type", "title", "url"]
    }
)
```

### 3. Namespace Organization

Use namespaces for logical separation:
- `ibm-cloud` - IBM Cloud documentation
- `ibm-watson` - Watson documentation
- `ibm-products` - Product documentation

## Monitoring

### Index Statistics

```python
stats = await vector_service.get_index_stats()
print(f"Total vectors: {stats['total_vector_count']}")
print(f"Index fullness: {stats['index_fullness']}")
print(f"Namespaces: {stats['namespaces']}")
```

### Query Performance

Log search times:

```python
import time

start = time.time()
results = await embedding_service.search_similar(query)
duration = time.time() - start

logger.info(f"Search completed in {duration:.2f}s")
```

## Troubleshooting

### Connection Issues

```python
# Test connection
try:
    vector_service.initialize()
    print("✅ Connected to Pinecone")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Index Not Found

```bash
# Recreate index
python scripts/setup_pinecone.py
```

### Low Relevance Scores

- Adjust `MIN_RELEVANCE_SCORE` in config
- Improve document chunking
- Use better source documents

### Slow Queries

- Reduce `TOP_K_RESULTS`
- Use metadata filters
- Optimize chunk size

## Cost Management

### Pinecone Pricing

- **Free Tier**: 100k vectors, 1 index
- **Starter**: $70/month, 5M vectors
- **Standard**: Custom pricing

### Optimization Tips

1. Use appropriate chunk sizes (800-1000 chars)
2. Remove duplicate content
3. Archive old documents
4. Use namespaces efficiently

## Best Practices

### 1. Document Preparation

- Clean HTML/markdown
- Remove navigation/boilerplate
- Maintain context in chunks
- Include metadata

### 2. Embedding Strategy

- Batch embed when possible
- Cache embeddings
- Monitor token usage
- Handle rate limits

### 3. Search Optimization

- Use metadata filters
- Adjust relevance threshold
- Implement caching
- Monitor performance

### 4. Maintenance

- Regular index cleanup
- Update stale documents
- Monitor index size
- Track costs

## API Integration

The vector database is integrated into the chat API:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I deploy containers on IBM Cloud?",
    "max_tokens": 1000
  }'
```

Response includes:
- Generated answer
- Source documents with relevance scores
- Token usage
- Conversation ID

## Next Steps

1. ✅ Set up Pinecone index
2. ✅ Test vector operations
3. 🔄 Implement document scraping
4. 🔄 Ingest IBM documentation
5. 🔄 Test RAG pipeline
6. 🔄 Deploy to production

## Resources

- [Pinecone Documentation](https://docs.pinecone.io)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)

## Support

For issues with vector database integration:
1. Check Pinecone dashboard for index status
2. Verify API keys and environment
3. Review application logs
4. Test with `test_vector_db.py` script