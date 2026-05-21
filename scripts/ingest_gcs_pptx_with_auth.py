"""
Script to download PPTX files from GCS and ingest into Pinecone with proper authentication
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
    sys.exit(1)

from scraper.pptx_scraper import pptx_scraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def list_and_download_pptx_files(bucket_name: str, service_account_path: str, temp_dir: str):
    """
    List and download all PPTX files from GCS bucket
    
    Args:
        bucket_name: GCS bucket name
        service_account_path: Path to service account JSON key
        temp_dir: Temporary directory to download files
        
    Returns:
        List of downloaded file paths
    """
    try:
        # Set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        # List all blobs
        blobs = bucket.list_blobs()
        
        pptx_files = []
        downloaded_files = []
        
        print("\n📋 Listing PPTX files in GCS bucket...")
        for blob in blobs:
            if blob.name.lower().endswith(('.pptx', '.ppt')):
                pptx_files.append(blob)
        
        print(f"✅ Found {len(pptx_files)} PPTX files\n")
        
        # Download files
        for i, blob in enumerate(pptx_files, 1):
            print(f"[{i}/{len(pptx_files)}] Downloading: {blob.name}")
            
            # Create safe filename
            safe_name = Path(blob.name).name
            local_path = os.path.join(temp_dir, safe_name)
            
            try:
                blob.download_to_filename(local_path)
                downloaded_files.append({
                    'local_path': local_path,
                    'gcs_path': blob.name,
                    'filename': safe_name
                })
                print(f"    ✅ Downloaded to {local_path}")
            except Exception as e:
                print(f"    ❌ Error downloading: {str(e)}")
        
        return downloaded_files
        
    except Exception as e:
        logger.error(f"Error accessing GCS: {str(e)}")
        raise


async def ingest_pptx_files(files: list, namespace: str = "", chunk_by_slide: bool = True):
    """
    Ingest downloaded PPTX files into Pinecone
    
    Args:
        files: List of file dictionaries with local_path, gcs_path, filename
        namespace: Pinecone namespace
        chunk_by_slide: Whether to chunk by slide
        
    Returns:
        Ingestion results
    """
    print("\n" + "="*80)
    print("INGESTING PPTX FILES INTO PINECONE")
    print("="*80)
    
    results = {
        'total_files': len(files),
        'processed': 0,
        'failed': 0,
        'total_chunks': 0,
        'total_vectors': 0,
        'total_slides': 0
    }
    
    for i, file_info in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {file_info['filename']}")
        print("-" * 80)
        
        try:
            result = await pptx_scraper.process_pptx(
                file_info['local_path'],
                namespace=namespace,
                custom_metadata={
                    'gcs_bucket': 'llm-bucketfahm',
                    'gcs_path': file_info['gcs_path'],
                    'source': 'Google Cloud Storage',
                    'original_filename': file_info['filename']
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
            logger.exception(f"Failed to process {file_info['filename']}")
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
    
    return results


async def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python ingest_gcs_pptx_with_auth.py <bucket_name> <service_account_json_path> [namespace] [--by-slide]")
        print("\nExamples:")
        print('  python ingest_gcs_pptx_with_auth.py llm-bucketfahm "C:\\path\\to\\key.json"')
        print('  python ingest_gcs_pptx_with_auth.py llm-bucketfahm "C:\\path\\to\\key.json" my-namespace')
        print('  python ingest_gcs_pptx_with_auth.py llm-bucketfahm "C:\\path\\to\\key.json" my-namespace --by-slide')
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    service_account_path = sys.argv[2]
    namespace = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else ""
    chunk_by_slide = '--by-slide' in sys.argv or '--chunk-by-slide' in sys.argv
    
    # Verify service account file exists
    if not os.path.exists(service_account_path):
        print(f"\n❌ Service account file not found: {service_account_path}")
        sys.exit(1)
    
    print("\n" + "="*80)
    print("GCS PPTX INGESTION WITH AUTHENTICATION")
    print("="*80)
    print(f"\nBucket: {bucket_name}")
    print(f"Service Account: {service_account_path}")
    print(f"Namespace: {namespace or '(default)'}")
    print(f"Chunk by slide: {chunk_by_slide}")
    print()
    
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Using temporary directory: {temp_dir}\n")
            
            # Download files from GCS
            files = list_and_download_pptx_files(bucket_name, service_account_path, temp_dir)
            
            if not files:
                print("\n❌ No PPTX files downloaded")
                sys.exit(1)
            
            # Ingest into Pinecone
            results = await ingest_pptx_files(files, namespace, chunk_by_slide)
            
            print("✅ Ingestion complete!\n")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Ingestion failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
