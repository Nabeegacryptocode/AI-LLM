"""
Test script for Google Discovery Engine queries
"""
import asyncio
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.web_search_service import web_search_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_discovery_queries():
    """
    Test queries against Google Discovery Engine
    """
    print("\n" + "="*80)
    print("Google Discovery Engine Query Test")
    print("="*80)
    
    test_queries = [
        "What is IBM Cloud?",
        "Tell me about IBM Watson services",
        "What security features does IBM Cloud provide?",
        "How do I get started with IBM Cloud?",
        "What are the key features of IBM Cloud?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 80)
        
        try:
            # Use web search service which includes Discovery Engine
            results = await web_search_service.search(query, max_results=3)
            
            if results:
                print(f"Found {len(results)} results:\n")
                for j, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    url = result.get('url', 'No URL')
                    snippet = result.get('snippet', 'No snippet')[:200]
                    
                    print(f"  Result {j}")
                    print(f"  Title: {title}")
                    print(f"  URL: {url}")
                    print(f"  Snippet: {snippet}...")
                    print()
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            logger.exception(f"Error querying: {query}")
    
    print("="*80)


async def test_discovery_with_summary():
    """
    Test queries with summarization
    """
    print("\n" + "="*80)
    print("Google Discovery Engine Query Test with Summarization")
    print("="*80)
    
    query = "What are the key features of IBM Cloud?"
    print(f"\nQuery: {query}")
    print("-" * 80)
    
    try:
        # Get search results with summary
        summary = await web_search_service.search_and_summarize(query, max_results=5)
        
        if summary:
            print("\nSummarized Context:")
            print("-" * 80)
            print(summary)
        else:
            print("No summary generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.exception(f"Error with summarization")
    
    print("\n" + "="*80)


async def main():
    """Main function"""
    print("\n" + "="*80)
    print("Discovery Engine Test Suite")
    print("="*80)
    
    # Test basic queries
    await test_discovery_queries()
    
    # Test with summarization
    await test_discovery_with_summary()
    
    print("\n✅ Test complete!\n")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
