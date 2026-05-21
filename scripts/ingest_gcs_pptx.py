"""
Script to download PPTX files from Google Cloud Storage and ingest into Pinecone
"""
import asyncio
import sys
import os
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("❌ google-cloud-storage not installed")
    print("Install with: pip install google-cloud-storage")
    sys.exit(1)

from scraper.pptx_scraper import pptx_scraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def download_from_gcs(bucket_name: str, blob_name: str, destination_path: str):
    """
    Download a file from Google Cloud Storage
    
    Args:
        bucket_name: GCS bucket name
        blob_name: Blob name (file path in bucket)
        destination_path: Local destination path
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        blob.download_to_filename(destination_path)
        logger.info(f"Downloaded {blob_name} to {destination_path}")
        
    except Exception as e:
        logger.error(f"Error downloading from GCS: {str(e)}")
        raise


def list_pptx_files_in_gcs(bucket_name: str, prefix: str = "") -> list:
    """
    List all PPTX files in a GCS bucket
    
    Args:
        bucket_name: GCS bucket name
        prefix: Prefix to filter files
        
    Returns:
        List of blob names
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        blobs = bucket.list_blobs(prefix=prefix)
        
        pptx_files = []
        for blob in blobs:
            if blob.name.lower().endswith(('.pptx', '.ppt')):
                pptx_files.append(blob.name)
        
        return pptx_files
        
    except Exception as e:
        logger.error(f"Error listing GCS files: {str(e)}")
        raise


async def ingest_from_gcs(
    bucket_name: str,
    namespace: str = "",
    prefix: str = "",
    chunk_by_slide: bool = False
):
    """
    Download PPTX files from GCS and ingest into Pinecone
    
    Args:
        bucket_name: GCS bucket name
        namespace: Pinecone namespace
        prefix: Prefix to filter files
        chunk_by_slide: Chunk by slide or use standard chunking
    """
    print("\n" + "="*80)
    print("GCS PPTX Ingestion Script")
    print("="*80)
    print(f"\nBucket: {bucket_name}")
    print(f"Prefix: {prefix or '(root)'}")
    print(f"Namespace: {namespace or '(default)'}")
    print(f"Chunk by slide: {chunk_by_slide}")
    print()
    
    # List PPTX files
    print("📋 Listing PPTX files in GCS...")
    pptx_files = list_pptx_files_in_gcs(bucket_name, prefix)
    
    if not pptx_files:
        print(f"\n❌ No PPTX files found in gs://{bucket_name}/{prefix}")
        return
    
    print(f"✅ Found {len(pptx_files)} PPTX files\n")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        results = {
            'total_files': len(pptx_files),
            'processed': 0,
            'failed': 0,
            'total_chunks': 0,
            'total_vectors': 0,
            'total_slides': 0
        }
        
        # Process each file
        for i, blob_name in enumerate(pptx_files, 1):
            print(f"\n[{i}/{len(pptx_files)}] Processing: {blob_name}")
            print("-" * 80)
            
            try:
                # Download file
                local_path = os.path.join(temp_dir, Path(blob_name).name)
                print(f"  📥 Downloading...")
                download_from_gcs(bucket_name, blob_name, local_path)
                
                # Process PPTX
                print(f"  📄 Extracting text...")
                result = await pptx_scraper.process_pptx(
                    local_path,
                    namespace=namespace,
                    custom_metadata={
                        'gcs_bucket': bucket_name,
                        'gcs_path': blob_name,
                        'source': 'Google Cloud Storage'
                    },
                    chunk_by_slide=chunk_by_slide
                )
                
                if result['success']:
                    print(f"  ✅ Success!")
                    print(f"     Slides: {result['slides_processed']}/{result['total_slides']}")
                    print(f"     Chunks: {result['chunks_created']}")
                    print(f"     Vectors: {result['vectors_stored']}")
                    
                    results['processed'] += 1
                    results['total_chunks'] += result['chunks_created']
                    results['total_vectors'] += result['vectors_stored']
                    results['total_slides'] += result['total_slides']
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                    results['failed'] += 1
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                logger.exception(f"Failed to process {blob_name}")
                results['failed'] += 1
        
        # Print summary
        print("\n" + "="*80)
        print("INGESTION SUMMARY")
        print("="*80)
        print(f"Total files: {results['total_files']}")
        print(f"✅ Processed: {results['processed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📊 Total slides: {results['total_slides']}")
        print(f"📦 Total chunks: {results['total_chunks']}")
        print(f"🔢 Total vectors: {results['total_vectors']}")
        print("="*80 + "\n")


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python ingest_gcs_pptx.py <bucket_name> [namespace] [prefix] [--by-slide]")
        print("\nExamples:")
        print("  python ingest_gcs_pptx.py llm-bucketfahm")
        print("  python ingest_gcs_pptx.py llm-bucketfahm my-namespace")
        print("  python ingest_gcs_pptx.py llm-bucketfahm my-namespace presentations/")
        print("  python ingest_gcs_pptx.py llm-bucketfahm my-namespace \"\" --by-slide")
        print("\nNote: Requires GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("      or gcloud authentication (gcloud auth application-default login)")
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else ""
    prefix = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else ""
    chunk_by_slide = '--by-slide' in sys.argv
    
    try:
        await ingest_from_gcs(bucket_name, namespace, prefix, chunk_by_slide)
        print("✅ Ingestion complete!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Ingestion failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
