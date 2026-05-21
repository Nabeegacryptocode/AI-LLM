"""Quick test script to verify search is working"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.embedding_service import embedding_service

async def test_search():
    query = "What is Maximo?"
    print(f"\nSearching for: '{query}'")
    print("="*60)
    
    results = await embedding_service.search_similar(
        query=query,
        top_k=5,
        namespace='ibm-docs'
    )
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['metadata'].get('title', 'N/A')}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Content: {result['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_search())
