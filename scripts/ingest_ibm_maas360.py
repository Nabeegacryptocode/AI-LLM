"""
Script to scrape and ingest IBM MaaS360 product information using Playwright
"""
import sys
import os
import asyncio
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.ibm_maas360_headless_scraper import IBMMaaS360HeadlessScraper
from scraper.document_processor import DocumentProcessor
from services.embedding_service import embedding_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_ibm_maas360(
    max_pages: int = 20,
    namespace: str = "ibm-docs"
):
    """
    Scrape and ingest IBM MaaS360 product information
    
    Args:
        max_pages: Maximum pages to scrape
        namespace: Pinecone namespace
    """
    try:
        logger.info("Starting IBM MaaS360 product information ingestion with Playwright")
        logger.info(f"Max pages: {max_pages}")
        
        all_chunks = []
        
        # Scrape using Playwright
        async with IBMMaaS360HeadlessScraper() as scraper:
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping IBM MaaS360 product pages")
            logger.info(f"URL: {scraper.base_url}")
            logger.info(f"{'='*60}\n")
            
            try:
                # Scrape product pages
                documents = await scraper.scrape_urls(
                    urls=[scraper.base_url],
                    max_depth=2,
                    follow_links=True
                )
                
                # Limit to max pages
                documents = documents[:max_pages]
                
                logger.info(f"Scraped {len(documents)} documents from IBM MaaS360")
                
                # Filter out empty documents
                valid_documents = [doc for doc in documents if doc.get('content', '').strip()]
                
                if len(valid_documents) < len(documents):
                    logger.warning(f"Filtered out {len(documents) - len(valid_documents)} documents with empty content")
                
                # Process into chunks
                for doc in valid_documents:
                    chunks = DocumentProcessor.create_chunks_with_metadata(
                        document={
                            'content': doc['content'],
                            'metadata': doc['metadata']
                        }
                    )
                    all_chunks.extend(chunks)
                
                logger.info(f"Created {len(all_chunks)} chunks from IBM MaaS360")
                
            except Exception as e:
                logger.error(f"Error scraping IBM MaaS360: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total chunks to ingest: {len(all_chunks)}")
        logger.info(f"{'='*60}\n")
        
        if not all_chunks:
            logger.warning("No chunks to ingest!")
            return
        
        # Ingest into vector database
        logger.info("Ingesting chunks into vector database...")
        
        result = await embedding_service.ingest_documents(
            documents=all_chunks,
            namespace=namespace
        )
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ Ingestion complete!")
        logger.info(f"Documents processed: {result['documents_processed']}")
        logger.info(f"Vectors upserted: {result['vectors_upserted']}")
        logger.info(f"Namespace: {result['namespace']}")
        logger.info(f"{'='*60}\n")
        
        # Get statistics
        stats = await embedding_service.get_statistics()
        logger.info("Vector database statistics:")
        logger.info(f"Total documents: {stats['total_documents']}")
        logger.info(f"Index fullness: {stats['index_fullness']:.2%}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


async def test_search(query: str, namespace: str = "ibm-docs"):
    """
    Test search after ingestion
    
    Args:
        query: Search query
        namespace: Namespace to search
    """
    logger.info(f"\nTesting search with query: '{query}'")
    
    results = await embedding_service.search_similar(
        query=query,
        top_k=3,
        namespace=namespace
    )
    
    logger.info(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        logger.info(f"Result {i}:")
        logger.info(f"  Title: {result['metadata'].get('title', 'N/A')}")
        logger.info(f"  Score: {result['score']:.4f}")
        logger.info(f"  URL: {result['metadata'].get('url', 'N/A')}")
        logger.info(f"  Content: {result['content'][:150]}...")
        logger.info("")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Ingest IBM MaaS360 product information using Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 10 pages
  python ingest_ibm_maas360.py --max-pages 10
  
  # Scrape 20 pages and test search
  python ingest_ibm_maas360.py --max-pages 20 --test-query "What is MaaS360?"

Note: Requires Playwright to be installed:
  pip install playwright
  playwright install chromium
        """
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Maximum pages to scrape (default: 20)'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        default='ibm-docs',
        help='Pinecone namespace (default: ibm-docs)'
    )
    parser.add_argument(
        '--test-query',
        type=str,
        help='Test query after ingestion'
    )
    
    args = parser.parse_args()
    
    # Check if Playwright is installed
    try:
        import playwright
    except ImportError:
        logger.error("Playwright is not installed!")
        logger.error("Install with: pip install playwright")
        logger.error("Then run: playwright install chromium")
        sys.exit(1)
    
    # Run ingestion
    result = asyncio.run(ingest_ibm_maas360(
        max_pages=args.max_pages,
        namespace=args.namespace
    ))
    
    # Test search if requested
    if args.test_query:
        asyncio.run(test_search(args.test_query, args.namespace))
    
    logger.info("\n✅ Script completed successfully!")
    logger.info("\n📝 Note: This used Playwright for JavaScript-rendered content.")


if __name__ == "__main__":
    main()

# Made with Bob
