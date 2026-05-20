"""
Script to test vector database integration
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.embedding_service import embedding_service
from backend.services.vector_service import vector_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_vector_db():
    """Test vector database operations"""
    try:
        logger.info("Testing vector database integration...")
        
        # Test 1: Initialize vector service
        logger.info("\n1. Initializing vector service...")
        vector_service.initialize()
        logger.info("✅ Vector service initialized")
        
        # Test 2: Get index stats
        logger.info("\n2. Getting index statistics...")
        stats = await vector_service.get_index_stats()
        logger.info(f"✅ Index stats: {stats}")
        
        # Test 3: Create test documents
        logger.info("\n3. Creating test documents...")
        test_docs = [
            {
                "content": "IBM Cloud is a suite of cloud computing services from IBM that offers both platform as a service (PaaS) and infrastructure as a service (IaaS).",
                "metadata": {
                    "title": "IBM Cloud Overview",
                    "url": "https://cloud.ibm.com/docs/overview",
                    "source_type": "IBM Cloud Docs"
                }
            },
            {
                "content": "IBM Watson is a question-answering computer system capable of answering questions posed in natural language.",
                "metadata": {
                    "title": "IBM Watson Introduction",
                    "url": "https://cloud.ibm.com/docs/watson",
                    "source_type": "IBM Watson Docs"
                }
            }
        ]
        logger.info(f"✅ Created {len(test_docs)} test documents")
        
        # Test 4: Embed and ingest documents
        logger.info("\n4. Embedding and ingesting documents...")
        result = await embedding_service.ingest_documents(
            documents=test_docs,
            namespace="test"
        )
        logger.info(f"✅ Ingested {result['vectors_upserted']} vectors")
        
        # Test 5: Search for similar documents
        logger.info("\n5. Searching for similar documents...")
        query = "What is IBM Cloud?"
        results = await embedding_service.search_similar(
            query=query,
            top_k=2,
            namespace="test"
        )
        logger.info(f"✅ Found {len(results)} similar documents")
        
        for i, result in enumerate(results, 1):
            logger.info(f"\nResult {i}:")
            logger.info(f"  Title: {result['metadata'].get('title', 'N/A')}")
            logger.info(f"  Score: {result['score']:.4f}")
            logger.info(f"  Content: {result['content'][:100]}...")
        
        # Test 6: Get updated stats
        logger.info("\n6. Getting updated statistics...")
        stats = await embedding_service.get_statistics()
        logger.info(f"✅ Statistics: {stats}")
        
        # Test 7: Clean up test data
        logger.info("\n7. Cleaning up test data...")
        await vector_service.delete_all(namespace="test")
        logger.info("✅ Test data cleaned up")
        
        logger.info("\n" + "="*50)
        logger.info("✅ All tests passed successfully!")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_vector_db())
    sys.exit(0 if success else 1)

# Made with Bob
