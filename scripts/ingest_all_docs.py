"""
Unified script to scrape and ingest IBM documentation from multiple sources
"""
import sys
import os
import asyncio
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.ibm_cloud_scraper import IBMCloudScraper, IBM_CLOUD_SECTIONS
from scraper.ibm_mas_scraper import IBMMAScraper, IBM_MAS_SECTIONS
from services.embedding_service import embedding_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def ingest_documentation(
    source: str = "cloud",
    sections: list = None,
    max_pages_per_section: int = 20,
    namespace: str = None
):
    """
    Scrape and ingest IBM documentation
    
    Args:
        source: Documentation source ('cloud' or 'mas')
        sections: List of section names to scrape (default: all)
        max_pages_per_section: Maximum pages per section
        namespace: Pinecone namespace (auto-determined if None)
    """
    try:
        # Select scraper and sections based on source
        if source == "cloud":
            scraper_class = IBMCloudScraper
            available_sections = IBM_CLOUD_SECTIONS
            default_namespace = "ibm-cloud"
            source_name = "IBM Cloud"
        elif source == "mas":
            scraper_class = IBMMAScraper
            available_sections = IBM_MAS_SECTIONS
            default_namespace = "ibm-mas"
            source_name = "IBM Maximo Application Suite"
        else:
            raise ValueError(f"Unknown source: {source}. Use 'cloud' or 'mas'")
        
        namespace = namespace or default_namespace
        
        logger.info(f"Starting {source_name} documentation ingestion")
        
        # Determine which sections to scrape
        if sections:
            section_urls = {k: v for k, v in available_sections.items() if k in sections}
        else:
            section_urls = available_sections
        
        logger.info(f"Scraping {len(section_urls)} sections: {list(section_urls.keys())}")
        
        all_chunks = []
        
        # Scrape each section
        async with scraper_class() as scraper:
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
        logger.info(f"Source: {source_name}")
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


async def test_search(query: str, namespace: str):
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
        description='Ingest IBM documentation from multiple sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest IBM Cloud overview section
  python ingest_all_docs.py --source cloud --sections overview --max-pages 20
  
  # Ingest IBM MAS overview and installation sections
  python ingest_all_docs.py --source mas --sections overview installation --max-pages 30
  
  # Ingest all IBM Cloud sections (limited pages)
  python ingest_all_docs.py --source cloud --sections all --max-pages 10
  
  # Ingest and test search
  python ingest_all_docs.py --source mas --sections overview --test-query "What is Maximo?"
        """
    )
    
    parser.add_argument(
        '--source',
        choices=['cloud', 'mas'],
        default='cloud',
        help='Documentation source: cloud (IBM Cloud) or mas (IBM Maximo Application Suite)'
    )
    parser.add_argument(
        '--sections',
        nargs='+',
        default=['overview'],
        help='Sections to scrape (default: overview). Use "all" for all sections.'
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
        help='Pinecone namespace (default: auto-determined based on source)'
    )
    parser.add_argument(
        '--test-query',
        type=str,
        help='Test query after ingestion'
    )
    
    args = parser.parse_args()
    
    # Validate sections based on source
    if args.source == 'cloud':
        available_sections = list(IBM_CLOUD_SECTIONS.keys())
    else:
        available_sections = list(IBM_MAS_SECTIONS.keys())
    
    # Handle 'all' sections
    if 'all' in args.sections:
        sections = None
    else:
        # Validate section names
        invalid_sections = [s for s in args.sections if s not in available_sections]
        if invalid_sections:
            logger.error(f"Invalid sections for {args.source}: {invalid_sections}")
            logger.info(f"Available sections: {available_sections}")
            sys.exit(1)
        sections = args.sections
    
    # Run ingestion
    result = asyncio.run(ingest_documentation(
        source=args.source,
        sections=sections,
        max_pages_per_section=args.max_pages,
        namespace=args.namespace
    ))
    
    # Test search if requested
    if args.test_query:
        namespace = args.namespace or ('ibm-cloud' if args.source == 'cloud' else 'ibm-mas')
        asyncio.run(test_search(args.test_query, namespace))
    
    logger.info("\n✅ Script completed successfully!")


if __name__ == "__main__":
    main()

# Made with Bob
