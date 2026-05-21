"""
Test script for Google Cloud Discovery Engine integration
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.web_search_service import WebSearchService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_discovery_engine():
    """Test Google Discovery Engine search"""
    
    # Initialize service
    service = WebSearchService()
    
    # Test queries
    test_queries = [
        "IBM Cloud documentation",
        "IBM MaaS360 mobile device management",
        "IBM Maximo Application Suite features",
        "IBM Global Data Platform"
    ]
    
    print("\n" + "="*80)
    print("Testing Google Cloud Discovery Engine Integration")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}\n")
        
        try:
            # Test search
            results = await service.search(query, max_results=3)
            
            if results:
                print(f"✓ Found {len(results)} results\n")
                
                for i, result in enumerate(results, 1):
                    print(f"Result {i}:")
                    print(f"  Title: {result.get('title', 'N/A')}")
                    print(f"  Source: {result.get('source', 'N/A')}")
                    print(f"  URL: {result.get('url', 'N/A')}")
                    print(f"  Score: {result.get('score', 'N/A')}")
                    print(f"  Content: {result.get('content', 'N/A')[:200]}...")
                    print()
            else:
                print("✗ No results found")
                
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            logger.exception("Search failed")
    
    print("\n" + "="*80)
    print("Testing search_and_summarize method")
    print("="*80 + "\n")
    
    try:
        summary = await service.search_and_summarize(
            "IBM Cloud Pak for Data",
            max_results=2
        )
        
        if summary:
            print("✓ Summary generated:\n")
            print(summary)
        else:
            print("✗ No summary generated")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        logger.exception("Summary generation failed")
    
    print("\n" + "="*80)
    print("Testing DuckDuckGo fallback")
    print("="*80 + "\n")
    
    # Disable Discovery Engine to test fallback
    service.disable_discovery_engine()
    
    try:
        results = await service.search("IBM Watson", max_results=3)
        
        if results:
            print(f"✓ Fallback working - Found {len(results)} results\n")
            
            for i, result in enumerate(results, 1):
                print(f"Result {i}:")
                print(f"  Title: {result.get('title', 'N/A')}")
                print(f"  Source: {result.get('source', 'N/A')}")
                print(f"  URL: {result.get('url', 'N/A')}")
                print()
        else:
            print("✗ Fallback failed - No results found")
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        logger.exception("Fallback test failed")
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_discovery_engine())

# Made with Bob
