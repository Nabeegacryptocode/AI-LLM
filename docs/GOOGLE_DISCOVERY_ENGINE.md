# Google Cloud Discovery Engine Integration

This document explains how to integrate and use Google Cloud Discovery Engine for enhanced web search capabilities in the FAHM LLM system.

## Overview

The system now supports Google Cloud Discovery Engine as the primary search provider, with DuckDuckGo as a fallback. Discovery Engine provides more accurate and relevant search results specifically tailored to your indexed content.

## Architecture

```
User Query
    ↓
WebSearchService
    ↓
    ├─→ Google Discovery Engine (Primary)
    │   ├─→ Get gcloud access token
    │   ├─→ POST to Discovery Engine API
    │   └─→ Parse and return results
    │
    └─→ DuckDuckGo (Fallback)
        ├─→ GET to DuckDuckGo API
        └─→ Parse and return results
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Web Search Settings
WEB_SEARCH_ENABLED=true

# Google Discovery Engine Settings
GOOGLE_PROJECT_ID=783867443498
GOOGLE_DISCOVERY_LOCATION=global
GOOGLE_DISCOVERY_COLLECTION_ID=default_collection
GOOGLE_DISCOVERY_ENGINE_ID=fahm-llm_1779380839747
GOOGLE_DISCOVERY_SERVING_CONFIG=default_search
USE_DISCOVERY_ENGINE=true
```

### Prerequisites

1. **Google Cloud CLI (gcloud)**
   - Install from: https://cloud.google.com/sdk/docs/install
   - Authenticate: `gcloud auth login`
   - Set project: `gcloud config set project 783867443498`

2. **Required Permissions**
   - `discoveryengine.servingConfigs.search`
   - Or broader role: `roles/discoveryengine.viewer`

3. **Discovery Engine Setup**
   - Engine must be created in Google Cloud Console
   - Content must be indexed
   - Serving config must be configured

## API Endpoint

The service uses the following endpoint:

```
POST https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_ID}/locations/{LOCATION}/collections/{COLLECTION_ID}/engines/{ENGINE_ID}/servingConfigs/{SERVING_CONFIG}:search
```

### Request Format

```json
{
  "query": "<QUERY>",
  "pageSize": 10,
  "queryExpansionSpec": {
    "condition": "AUTO"
  },
  "spellCorrectionSpec": {
    "mode": "AUTO"
  },
  "languageCode": "en-US",
  "userInfo": {
    "timeZone": "America/New_York"
  }
}
```

### Response Format

```json
{
  "results": [
    {
      "document": {
        "id": "doc-id",
        "structData": {
          "title": "Document Title",
          "snippet": "Document snippet...",
          "url": "https://example.com/doc"
        },
        "derivedStructData": {
          "title": "Derived Title",
          "link": "https://example.com/doc",
          "snippets": ["Snippet 1", "Snippet 2"],
          "extractive_answers": [...]
        }
      },
      "relevanceScore": 0.95
    }
  ]
}
```

## Usage

### Basic Search

```python
from services.web_search_service import web_search_service

# Search with Discovery Engine (automatic fallback to DuckDuckGo)
results = await web_search_service.search(
    query="IBM Cloud documentation",
    max_results=5
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
```

### Search and Summarize

```python
# Get formatted context for LLM
context = await web_search_service.search_and_summarize(
    query="IBM MaaS360 features",
    max_results=3
)

# Use context in RAG pipeline
response = await llm_service.generate_response(
    query=user_query,
    context=context
)
```

### Manual Control

```python
# Disable Discovery Engine (use only DuckDuckGo)
web_search_service.disable_discovery_engine()

# Re-enable Discovery Engine
web_search_service.enable_discovery_engine()
```

### Custom Configuration

```python
from services.web_search_service import WebSearchService

# Create service with custom settings
custom_service = WebSearchService(
    project_id="your-project-id",
    location="us-central1",
    collection_id="custom_collection",
    engine_id="custom-engine",
    serving_config="custom_config"
)

results = await custom_service.search("query")
```

## Testing

### Test Script

Run the test script to verify integration:

```bash
cd scripts
python test_discovery_engine.py
```

This will test:
- Discovery Engine search
- Result parsing
- Summary generation
- DuckDuckGo fallback
- Error handling

### Manual Testing with curl

```bash
# Get access token
ACCESS_TOKEN=$(gcloud auth print-access-token)

# Test search
curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/783867443498/locations/global/collections/default_collection/engines/fahm-llm_1779380839747/servingConfigs/default_search:search" \
  -d '{
    "query": "IBM Cloud",
    "pageSize": 5,
    "queryExpansionSpec": {"condition": "AUTO"},
    "spellCorrectionSpec": {"mode": "AUTO"},
    "languageCode": "en-US"
  }'
```

## Features

### Query Enhancement
- **Auto Query Expansion**: Automatically expands queries for better results
- **Spell Correction**: Corrects spelling mistakes in queries
- **Language Support**: Supports multiple languages (default: en-US)

### Result Quality
- **Relevance Scoring**: Each result includes a relevance score
- **Extractive Answers**: Highlights specific answer snippets
- **Structured Data**: Returns well-formatted, structured results

### Fallback Mechanism
- **Automatic Fallback**: Falls back to DuckDuckGo if Discovery Engine fails
- **Graceful Degradation**: System continues working even if gcloud is unavailable
- **Error Handling**: Comprehensive error handling and logging

## Integration with RAG Pipeline

The web search service integrates seamlessly with the RAG pipeline:

```python
# In rag_service.py
async def search_with_fallback(self, query: str) -> str:
    # Try vector database first
    vector_results = await self.vector_service.search(query)
    
    if not vector_results or vector_results[0]['score'] < threshold:
        # Use web search as fallback
        web_context = await web_search_service.search_and_summarize(query)
        return web_context
    
    return format_vector_results(vector_results)
```

## Monitoring and Logging

The service provides detailed logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Search queries
# - Result counts
# - API response times
# - Fallback triggers
# - Error details
```

## Troubleshooting

### Common Issues

1. **"gcloud CLI not found"**
   - Install Google Cloud SDK
   - Add gcloud to PATH
   - Verify: `gcloud --version`

2. **"Failed to get gcloud token"**
   - Run: `gcloud auth login`
   - Check: `gcloud auth list`
   - Verify project: `gcloud config get-value project`

3. **"Discovery Engine search failed with status 403"**
   - Check IAM permissions
   - Verify service account has required roles
   - Ensure engine exists and is accessible

4. **"No results found"**
   - Verify engine has indexed content
   - Check query syntax
   - Review engine configuration in Cloud Console

5. **"Timeout errors"**
   - Increase timeout in service initialization
   - Check network connectivity
   - Verify API endpoint is accessible

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('services.web_search_service').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Caching**: Consider caching search results for frequently asked queries
- **Rate Limiting**: Discovery Engine has quota limits - monitor usage
- **Timeout**: Default timeout is 30 seconds - adjust based on needs
- **Batch Queries**: For multiple queries, consider batching if supported

## Security

- **Access Tokens**: Tokens are obtained dynamically and not stored
- **Token Expiry**: Tokens expire after 1 hour - automatically refreshed
- **API Keys**: No API keys stored in code - uses gcloud authentication
- **HTTPS**: All API calls use HTTPS encryption

## Cost Optimization

- **Query Optimization**: Use specific queries to reduce API calls
- **Result Limits**: Limit page size to needed results only
- **Fallback Strategy**: DuckDuckGo is free - use as primary for non-critical queries
- **Caching**: Cache results to reduce API calls

## Future Enhancements

Potential improvements:
- [ ] Add result caching with Redis
- [ ] Implement query rewriting for better results
- [ ] Add support for faceted search
- [ ] Integrate with Google Cloud Monitoring
- [ ] Add A/B testing between search providers
- [ ] Implement semantic search ranking
- [ ] Add multi-language support
- [ ] Create search analytics dashboard

## References

- [Google Discovery Engine Documentation](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction)
- [Discovery Engine API Reference](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest)
- [gcloud CLI Documentation](https://cloud.google.com/sdk/gcloud)
- [IAM Permissions](https://cloud.google.com/generative-ai-app-builder/docs/access-control)

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Run test script: `python scripts/test_discovery_engine.py`
3. Review this documentation
4. Check Google Cloud Console for engine status

---

**Last Updated**: 2026-05-21
**Version**: 1.0.0