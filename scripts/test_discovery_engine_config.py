#!/usr/bin/env python3
"""
Test script to verify Google Discovery Engine configuration
Tests both the API endpoint and authentication
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.web_search_service import WebSearchService


async def test_discovery_engine():
    """Test Discovery Engine configuration"""
    print("=" * 60)
    print("Testing Google Discovery Engine Configuration")
    print("=" * 60)
    
    # Initialize service with correct configuration
    service = WebSearchService(
        project_id="71522359792",
        location="global",
        collection_id="default_collection",
        engine_id="fahmllmdiscoveryengine_1779465166335",
        serving_config="default_search"
    )
    
    print(f"\n✓ Service initialized")
    print(f"  Project ID: {service.project_id}")
    print(f"  Engine ID: {service.engine_id}")
    print(f"  API URL: {service.discovery_api_url}")
    
    # Check authentication
    print(f"\n📋 Checking authentication...")
    print(f"  Service Account Path: {service.service_account_key_path or 'Not set'}")
    print(f"  Use Discovery Engine: {service.use_discovery_engine}")
    
    # Try to get access token
    print(f"\n🔑 Attempting to get access token...")
    token = await service._get_access_token()
    
    if token:
        print(f"  ✓ Successfully obtained access token")
        print(f"  Token (first 20 chars): {token[:20]}...")
    else:
        print(f"  ⚠ Could not obtain access token")
        print(f"  Will fall back to DuckDuckGo search")
    
    # Test search
    print(f"\n🔍 Testing search functionality...")
    test_query = "What is IBM Cloud?"
    
    try:
        results = await service.search(test_query, max_results=3, use_cache=False)
        
        if results:
            print(f"  ✓ Search successful! Found {len(results)} results")
            print(f"\n📄 Results:")
            for i, result in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"    Title: {result.get('title', 'N/A')[:80]}")
                print(f"    Source: {result.get('source', 'N/A')}")
                print(f"    URL: {result.get('url', 'N/A')[:80]}")
                print(f"    Score: {result.get('score', 'N/A')}")
                content = result.get('content', '')
                if content:
                    print(f"    Content: {content[:150]}...")
        else:
            print(f"  ⚠ No results found")
            
    except Exception as e:
        print(f"  ❌ Search failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_discovery_engine())

# Made with Bob
