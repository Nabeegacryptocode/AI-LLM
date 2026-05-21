"""
Ingest FAHM Partners website content into Pinecone
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from scraper.fahm_partners_scraper import FAHMPartnersScraper
from scraper.document_processor import DocumentProcessor
from services.vector_service import vector_service
from services.llm_service import llm_service
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main ingestion function"""
    try:
        logger.info("=" * 80)
        logger.info("FAHM Partners Website Ingestion")
        logger.info("=" * 80)
        
        # Initialize scraper
        logger.info("Initializing FAHM Partners scraper...")
        scraper = FAHMPartnersScraper()
        
        # Scrape documents
        logger.info("Scraping FAHM Partners website...")
        documents = await scraper.scrape()
        
        if not documents:
            logger.error("No documents scraped!")
            return
        
        logger.info(f"Scraped {len(documents)} documents")
        
        # Process documents
        logger.info("Processing documents...")
        processor = DocumentProcessor()
        processed_docs = []
        
        for doc in documents:
            chunks = processor.create_chunks_with_metadata(
                document={
                    'content': doc['content'],
                    'metadata': {
                        'title': doc['title'],
                        'url': doc['url'],
                        'source': doc['source'],
                        **doc.get('metadata', {})
                    }
                }
            )
            processed_docs.extend(chunks)
        
        logger.info(f"Created {len(processed_docs)} chunks from {len(documents)} documents")
        
        # Generate embeddings and store in Pinecone
        logger.info("Generating embeddings and storing in Pinecone...")
        
        batch_size = 100
        total_stored = 0
        
        for i in range(0, len(processed_docs), batch_size):
            batch = processed_docs[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(processed_docs)-1)//batch_size + 1}")
            
            # Generate embeddings
            texts = [doc['content'] for doc in batch]
            embeddings = await llm_service.generate_embeddings_batch(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for j, (doc, embedding) in enumerate(zip(batch, embeddings)):
                vector_id = f"fahm_{i+j}_{hash(doc['content'][:100])}"
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': {
                        'content': doc['content'][:1000],  # Store first 1000 chars
                        'title': doc['metadata'].get('title', 'Untitled'),
                        'url': doc['metadata'].get('url', ''),
                        'source': doc['metadata'].get('source', 'FAHM Partners'),
                        'chunk_index': doc['metadata'].get('chunk_index', 0),
                        'total_chunks': doc['metadata'].get('total_chunks', 1)
                    }
                })
            
            # Store in Pinecone
            await vector_service.upsert_vectors(vectors)
            total_stored += len(vectors)
            logger.info(f"Stored {len(vectors)} vectors (Total: {total_stored})")
        
        logger.info("=" * 80)
        logger.info(f"✅ Successfully ingested {len(documents)} documents ({total_stored} chunks)")
        logger.info("=" * 80)
        
        # Print sample documents
        logger.info("\nSample documents:")
        for i, doc in enumerate(documents[:3], 1):
            logger.info(f"\n{i}. {doc['title']}")
            logger.info(f"   URL: {doc['url']}")
            logger.info(f"   Content length: {len(doc['content'])} chars")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
