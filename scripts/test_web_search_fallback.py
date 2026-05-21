"""
Test script for web search fallback functionality
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.web_search_service import web_search_service
from backend.services.rag_service import rag_service


async def test_web_search_service():
    """Test the web search service directly"""
    print("\n" + "="*80)
    print("Testing Web Search Service")
    print("="*80 + "\n")
    
    # Test query that won't be in IBM docs
    query = "What is the capital of France?"
    
    print(f"Query: {query}\n")
    
    # Test search
    print("1. Testing web_search_service.search()...")
    results = await web_search_service.search(query, max_results=3)
    
    if results:
        print(f"✓ Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Content: {result.get('content', 'N/A')[:100]}...")
    else:
        print("✗ No results found")
    
    # Test search and summarize
    print("\n2. Testing web_search_service.search_and_summarize()...")
    context = await web_search_service.search_and_summarize(query, max_results=3)
    
    if context:
        print(f"✓ Generated context ({len(context)} chars)")
        print(f"\nContext preview:\n{context[:300]}...")
    else:
        print("✗ No context generated")
    
    return len(results) > 0


async def test_rag_fallback():
    """Test RAG service fallback to web search"""
    print("\n" + "="*80)
    print("Testing RAG Service Web Search Fallback")
    print("="*80 + "\n")
    
    # Query that definitely won't be in IBM documentation
    query = "Who won the 2024 FIFA World Cup?"
    
    print(f"Query: {query}\n")
    print("This query should trigger web search fallback...\n")
    
    try:
        result = await rag_service.generate_answer(
            question=query,
            max_tokens=500
        )
        
        print("✓ RAG service returned a response")
        print(f"\nWeb search used: {result.get('web_search_used', False)}")
        print(f"Retrieved docs: {result.get('retrieved_docs', 0)}")
        print(f"Tokens used: {result.get('tokens_used', 0)}")
        print(f"\nAnswer:\n{result.get('answer', 'N/A')[:300]}...")
        
        if result.get('sources'):
            print(f"\nSources ({len(result['sources'])}):")
            for source in result['sources']:
                print(f"  - {source.get('title', 'N/A')}")
        
        return result.get('web_search_used', False)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_rag_with_docs():
    """Test RAG service with a query that should find docs"""
    print("\n" + "="*80)
    print("Testing RAG Service with Documentation Query")
    print("="*80 + "\n")
    
    # Query that should be in IBM documentation
    query = "What is IBM Cloud?"
    
    print(f"Query: {query}\n")
    print("This query should find documentation (no web search)...\n")
    
    try:
        result = await rag_service.generate_answer(
            question=query,
            max_tokens=500
        )
        
        print("✓ RAG service returned a response")
        print(f"\nWeb search used: {result.get('web_search_used', False)}")
        print(f"Retrieved docs: {result.get('retrieved_docs', 0)}")
        print(f"Tokens used: {result.get('tokens_used', 0)}")
        print(f"\nAnswer:\n{result.get('answer', 'N/A')[:300]}...")
        
        if result.get('sources'):
            print(f"\nSources ({len(result['sources'])}):")
            for source in result['sources']:
                print(f"  - {source.get('title', 'N/A')}")
        
        return not result.get('web_search_used', True)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("WEB SEARCH FALLBACK TEST SUITE")
    print("="*80)
    
    results = []
    
    # Test 1: Web search service
    try:
        result = await test_web_search_service()
        results.append(("Web Search Service", result))
    except Exception as e:
        print(f"\n✗ Web Search Service test failed: {str(e)}")
        results.append(("Web Search Service", False))
    
    # Test 2: RAG fallback
    try:
        result = await test_rag_fallback()
        results.append(("RAG Web Search Fallback", result))
    except Exception as e:
        print(f"\n✗ RAG fallback test failed: {str(e)}")
        results.append(("RAG Web Search Fallback", False))
    
    # Test 3: RAG with docs
    try:
        result = await test_rag_with_docs()
        results.append(("RAG with Documentation", result))
    except Exception as e:
        print(f"\n✗ RAG with docs test failed: {str(e)}")
        results.append(("RAG with Documentation", False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

# Made with Bob
