"""
Test script for dynamic PPTX ingestion from Discovery Engine
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.rag_service import rag_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_dynamic_ingestion():
    """
    Test dynamic PPTX ingestion with real queries
    """
    print("\n" + "="*80)
    print("DYNAMIC PPTX INGESTION TEST")
    print("Query → Discovery Engine → Auto-Download PPTX → Ingest → Answer")
    print("="*80)
    
    test_queries = [
        "What is IBM Cloud?",
        "Tell me about IBM LinuxONE security features",
        "How does IBM Bob work?",
        "What are the features of IBM secure computing?",
        "Explain IBM data serving capabilities"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}: {query}")
        print('='*80)
        
        try:
            # Generate answer using RAG pipeline with dynamic ingestion
            result = await rag_service.generate_answer(
                question=query,
                max_tokens=500,
                namespace=""
            )
            
            print(f"\n📝 ANSWER:")
            print("-" * 80)
            print(result['answer'])
            print()
            
            print(f"📚 SOURCES ({len(result.get('sources', []))}):")
            print("-" * 80)
            for j, source in enumerate(result.get('sources', []), 1):
                print(f"  {j}. {source.get('title', 'Unknown')}")
                if source.get('url'):
                    print(f"     URL: {source['url']}")
                print(f"     Type: {source.get('source_type', 'Unknown')}")
            
            print(f"\n📊 METADATA:")
            print("-" * 80)
            print(f"  Retrieved Documents: {result.get('retrieved_docs', 0)}")
            print(f"  Tokens Used: {result.get('tokens_used', 0)}")
            print(f"  Web Search Used: {result.get('web_search_used', False)}")
            print(f"  Dynamic Ingestion Used: {result.get('dynamic_ingestion_used', False)}")
            
            if result.get('dynamic_ingestion_used'):
                print("\n  ✨ PPTX files were dynamically ingested!")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            logger.exception(f"Error processing query: {query}")
        
        # Add delay between queries
        if i < len(test_queries):
            print("\n⏳ Waiting 2 seconds before next query...")
            await asyncio.sleep(2)
    
    print("\n" + "="*80)
    print("✅ DYNAMIC INGESTION TEST COMPLETE")
    print("="*80 + "\n")


async def test_single_query(query: str):
    """
    Test a single query with dynamic ingestion
    """
    print("\n" + "="*80)
    print("SINGLE QUERY TEST WITH DYNAMIC INGESTION")
    print("="*80)
    print(f"\nQuery: {query}\n")
    
    try:
        result = await rag_service.generate_answer(
            question=query,
            max_tokens=500,
            namespace=""
        )
        
        print("="*80)
        print("ANSWER:")
        print("="*80)
        print(result['answer'])
        print()
        
        print("="*80)
        print(f"SOURCES ({len(result.get('sources', []))}):")
        print("="*80)
        for i, source in enumerate(result.get('sources', []), 1):
            print(f"\n{i}. {source.get('title', 'Unknown')}")
            print(f"   Type: {source.get('source_type', 'Unknown')}")
            if source.get('url'):
                print(f"   URL: {source['url']}")
            if source.get('score'):
                print(f"   Relevance: {source['score']:.4f}")
        
        print(f"\n{'='*80}")
        print("METADATA:")
        print("="*80)
        print(f"Retrieved Documents: {result.get('retrieved_docs', 0)}")
        print(f"Tokens Used: {result.get('tokens_used', 0)}")
        print(f"Web Search Used: {result.get('web_search_used', False)}")
        print(f"Dynamic Ingestion Used: {result.get('dynamic_ingestion_used', False)}")
        
        if result.get('dynamic_ingestion_used'):
            print("\n✨ PowerPoint files were automatically downloaded and ingested!")
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        logger.exception(f"Error processing query")


async def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Test single query from command line
        query = " ".join(sys.argv[1:])
        await test_single_query(query)
    else:
        # Test multiple queries
        await test_dynamic_ingestion()


if __name__ == "__main__":
    print("\nDynamic PPTX Ingestion Test")
    print("="*80)
    print("This script tests automatic ingestion of PPTX files found by Discovery Engine")
    print("\nUsage:")
    print("  python test_dynamic_ingestion.py                    # Test multiple queries")
    print('  python test_dynamic_ingestion.py "your question"    # Test single query')
    print("\nExamples:")
    print('  python test_dynamic_ingestion.py "What is IBM LinuxONE?"')
    print('  python test_dynamic_ingestion.py "Tell me about IBM secure computing"')
    print("\nNote: Requires GOOGLE_APPLICATION_CREDENTIALS to be set")
    print("="*80 + "\n")
    
    asyncio.run(main())

# Made with Bob
