"""
Script to set up Pinecone vector database
"""
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pinecone import Pinecone, ServerlessSpec
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_index(pc, index_name):
    """Delete an existing index"""
    try:
        logger.info(f"Deleting index '{index_name}'...")
        pc.delete_index(index_name)
        logger.info(f"Index '{index_name}' deleted successfully!")
        return True
    except Exception as e:
        logger.error(f"Error deleting index: {str(e)}")
        return False


def create_index(pc, index_name, dimension, environment):
    """Create a new index"""
    try:
        logger.info(f"Creating index '{index_name}'...")
        logger.info(f"Dimension: {dimension}")
        logger.info(f"Region: {environment}")
        
        # Create index with ServerlessSpec
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.PINECONE_CLOUD,
                region=environment
            )
        )
        
        logger.info(f"Index '{index_name}' created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating index: {str(e)}")
        return False


def setup_pinecone(recreate=False):
    """Initialize Pinecone and create index if needed"""
    try:
        logger.info("Initializing Pinecone...")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        logger.info(f"Connected to Pinecone")
        
        # List existing indexes
        existing_indexes = [index.name for index in pc.list_indexes()]
        logger.info(f"Existing indexes: {existing_indexes}")
        
        # Check if our index exists
        if settings.PINECONE_INDEX_NAME in existing_indexes:
            logger.info(f"Index '{settings.PINECONE_INDEX_NAME}' already exists")
            
            # Get index info
            index_info = pc.describe_index(settings.PINECONE_INDEX_NAME)
            logger.info(f"Index dimension: {index_info.dimension}")
            logger.info(f"Index metric: {index_info.metric}")
            
            # Check if dimension matches
            if index_info.dimension != settings.EMBEDDING_DIMENSION:
                logger.warning(f"⚠️  Dimension mismatch! Index has {index_info.dimension}, but config expects {settings.EMBEDDING_DIMENSION}")
                recreate = True
            
            if recreate:
                logger.info("Recreating index with correct dimension...")
                if not delete_index(pc, settings.PINECONE_INDEX_NAME):
                    return False
                
                if not create_index(pc, settings.PINECONE_INDEX_NAME, settings.EMBEDDING_DIMENSION, settings.PINECONE_ENVIRONMENT):
                    return False
            else:
                # Get index stats
                index = pc.Index(settings.PINECONE_INDEX_NAME)
                stats = index.describe_index_stats()
                logger.info(f"Index stats: {stats}")
            
        else:
            if not create_index(pc, settings.PINECONE_INDEX_NAME, settings.EMBEDDING_DIMENSION, settings.PINECONE_ENVIRONMENT):
                return False
        
        logger.info("\n✅ Pinecone setup complete!")
        logger.info(f"Index name: {settings.PINECONE_INDEX_NAME}")
        logger.info(f"Dimension: {settings.EMBEDDING_DIMENSION}")
        logger.info(f"Region: {settings.PINECONE_ENVIRONMENT}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Pinecone: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup Pinecone vector database')
    parser.add_argument('--recreate', action='store_true', help='Delete and recreate the index')
    args = parser.parse_args()
    
    success = setup_pinecone(recreate=args.recreate)
    sys.exit(0 if success else 1)

# Made with Bob
