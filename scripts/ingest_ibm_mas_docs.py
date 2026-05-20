"""
Script to scrape and ingest IBM Maximo Application Suite (MAS) documentation
"""
import sys
import os
import asyncio
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.ibm_mas_scraper import IBMMAScraper, IBM_MAS_SECTIONS
from services.embedding_service import embedding_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_ibm_mas_docs(
    sections: list = None,
    max_pages_per_section: int = 20,
    namespace: str = "ibm-mas"
):
    """
    Scrape and ingest IBM MAS documentation
    
    Args:
        sections: List of section names to scrape (default: all)
        max_pages_per_section: Maximum pages per section
        namespace: Pinecone namespace
    """
    try:
        logger.info("Starting IBM MAS documentation ingestion")
        
        # Determine which sections to scrape
        if sections:
            section_urls = {k: v for k, v in IBM_MAS_SECTIONS.items() if k in sections}
        else:
            section_urls = IBM_MAS_SECTIONS
        
        logger.info(f"Scraping {len(section_urls)} sections: {list(section_urls.keys())}")
        
        all_chunks = []
        
        # Scrape each section
        async with IBMMAScraper() as scraper:
            for section_name, section_url in section_urls.items():
                logger.info(f"\n{'='*60}")
                logger.info(f"Scraping section: {section_name}")
                logger.info(f"URL: {section_url}")
                logger.info(f"{'='*60}\n")
                
                try:
                    # Scrape section
                    documents = await scraper.scrape_section(
                        section_url=section_url,
                        max_pages=max_pages_per_section
                    )
                    
                    logger.info(f"Scraped {len(documents)} documents from {section_name}")
                    
                    # Process into chunks
                    chunks = scraper.process_documents(documents)
                    
                    logger.info(f"Created {len(chunks)} chunks from {section_name}")
                    
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.error(f"Error scraping {section_name}: {str(e)}")
                    continue
        
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


async def test_search(query: str, namespace: str = "ibm-mas"):
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
    parser = argparse.ArgumentParser(description='Ingest IBM MAS documentation')
    parser.add_argument(
        '--sections',
        nargs='+',
        choices=list(IBM_MAS_SECTIONS.keys()) + ['all'],
        default=['overview'],
        help='Sections to scrape (default: overview)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Maximum pages per section (default: 20)'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        default='ibm-mas',
        help='Pinecone namespace (default: ibm-mas)'
    )
    parser.add_argument(
        '--test-query',
        type=str,
        help='Test query after ingestion'
    )
    
    args = parser.parse_args()
    
    # Handle 'all' sections
    sections = None if 'all' in args.sections else args.sections
    
    # Run ingestion
    result = asyncio.run(ingest_ibm_mas_docs(
        sections=sections,
        max_pages_per_section=args.max_pages,
        namespace=args.namespace
    ))
    
    # Test search if requested
    if args.test_query:
        asyncio.run(test_search(args.test_query, args.namespace))
    
    logger.info("\n✅ Script completed successfully!")


if __name__ == "__main__":
    main()

# Made with Bob
