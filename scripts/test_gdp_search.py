"""Quick test script to verify GDP search is working"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from services.embedding_service import embedding_service

async def test_search():
    queries = [
        "What is Guardium?",
        "How to install Guardium?",
        "Guardium security policies"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        print("="*60)
        
        results = await embedding_service.search_similar(
            query=query,
            top_k=3,
            namespace='ibm-docs'
        )
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['metadata'].get('title', 'N/A')}")
            print(f"   Score: {result['score']:.4f}")
            print(f"   Content: {result['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_search())
