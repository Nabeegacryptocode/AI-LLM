"""
Test the full RAG pipeline: Query -> Pinecone -> LLM -> Answer
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


async def test_rag_pipeline():
    """
    Test the full RAG pipeline with real queries
    """
    print("\n" + "="*80)
    print("FULL RAG PIPELINE TEST")
    print("Query -> Pinecone Vector Search -> LLM -> Answer")
    print("="*80)
    
    test_queries = [
        "What is IBM Cloud and what services does it provide?",
        "Tell me about IBM Watson AI services",
        "What security features does IBM Cloud have?",
        "How do I get started with IBM Cloud?",
        "What are the key features and benefits of IBM Cloud?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"QUERY {i}: {query}")
        print('='*80)
        
        try:
            # Generate answer using RAG pipeline
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
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            logger.exception(f"Error processing query: {query}")
    
    print("\n" + "="*80)
    print("✅ RAG PIPELINE TEST COMPLETE")
    print("="*80 + "\n")


async def test_single_query(query: str):
    """
    Test a single query through the RAG pipeline
    """
    print("\n" + "="*80)
    print("SINGLE QUERY TEST")
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
        print(f"Conversation ID: {result.get('conversation_id', 'N/A')}")
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
        await test_rag_pipeline()


if __name__ == "__main__":
    print("\nUsage:")
    print("  python test_full_rag_pipeline.py                    # Test multiple queries")
    print('  python test_full_rag_pipeline.py "your question"    # Test single query')
    print("\nExamples:")
    print('  python test_full_rag_pipeline.py "What is IBM Cloud?"')
    print('  python test_full_rag_pipeline.py "Tell me about Watson AI services"')
    print()
    
    asyncio.run(main())

# Made with Bob
