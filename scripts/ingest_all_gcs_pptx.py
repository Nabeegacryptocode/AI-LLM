"""
Comprehensive script to ingest all PPTX files from GCS bucket to Pinecone
"""
import asyncio
import sys
import os
from pathlib import Path
import tempfile
import time

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
from services.vector_service import vector_service
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def list_pptx_files(bucket_name: str, service_account_path: str):
    """List all PPTX files in GCS bucket"""
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        print("\n📋 Listing PPTX files in GCS bucket...")
        blobs = bucket.list_blobs()
        
        pptx_files = []
        for blob in blobs:
            if blob.name.lower().endswith(('.pptx', '.ppt')):
                pptx_files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'updated': blob.updated
                })
        
        return pptx_files, bucket
        
    except Exception as e:
        logger.error(f"Error listing GCS files: {str(e)}")
        raise


def download_file(bucket, blob_name: str, local_path: str):
    """Download a single file from GCS"""
    try:
        blob = bucket.blob(blob_name)
        blob.download_to_filename(local_path)
        return True
    except Exception as e:
        logger.error(f"Error downloading {blob_name}: {str(e)}")
        return False


async def process_and_ingest(local_path: str, gcs_path: str, filename: str, namespace: str, chunk_by_slide: bool):
    """Process PPTX and ingest to Pinecone"""
    try:
        result = await pptx_scraper.process_pptx(
            local_path,
            namespace=namespace,
            custom_metadata={
                'gcs_bucket': 'llm-bucketfahm',
                'gcs_path': gcs_path,
                'source': 'Google Cloud Storage',
                'original_filename': filename
            },
            chunk_by_slide=chunk_by_slide
        )
        return result
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        return {'success': False, 'error': str(e)}


async def ingest_all_pptx(bucket_name: str, service_account_path: str, namespace: str = "", chunk_by_slide: bool = True, max_files: int = None):
    """
    Main ingestion function
    
    Args:
        bucket_name: GCS bucket name
        service_account_path: Path to service account JSON
        namespace: Pinecone namespace
        chunk_by_slide: Whether to chunk by slide
        max_files: Maximum number of files to process (None = all)
    """
    print("\n" + "="*80)
    print("GCS TO PINECONE PPTX INGESTION")
    print("="*80)
    print(f"\nBucket: {bucket_name}")
    print(f"Service Account: {service_account_path}")
    print(f"Namespace: {namespace or '(default)'}")
    print(f"Chunk by slide: {chunk_by_slide}")
    print(f"Max files: {max_files or 'All'}")
    print()
    
    # List files
    pptx_files, bucket = list_pptx_files(bucket_name, service_account_path)
    
    if not pptx_files:
        print("❌ No PPTX files found in bucket")
        return
    
    print(f"✅ Found {len(pptx_files)} PPTX files\n")
    
    # Limit files if specified
    if max_files:
        pptx_files = pptx_files[:max_files]
        print(f"📌 Processing first {len(pptx_files)} files\n")
    
    # Display files
    print("Files to process:")
    print("-" * 80)
    for i, file_info in enumerate(pptx_files, 1):
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"  {i}. {file_info['name']} ({size_mb:.2f} MB)")
    print()
    
    # Process files
    results = {
        'total_files': len(pptx_files),
        'processed': 0,
        'failed': 0,
        'skipped': 0,
        'total_chunks': 0,
        'total_vectors': 0,
        'total_slides': 0,
        'files': []
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary directory: {temp_dir}\n")
        print("="*80)
        print("PROCESSING FILES")
        print("="*80)
        
        for i, file_info in enumerate(pptx_files, 1):
            print(f"\n[{i}/{len(pptx_files)}] {file_info['name']}")
            print("-" * 80)
            
            start_time = time.time()
            
            # Create safe local filename
            safe_name = Path(file_info['name']).name
            local_path = os.path.join(temp_dir, safe_name)
            
            # Download
            print(f"  📥 Downloading...")
            if not download_file(bucket, file_info['name'], local_path):
                print(f"  ❌ Download failed")
                results['failed'] += 1
                results['files'].append({
                    'name': file_info['name'],
                    'status': 'download_failed'
                })
                continue
            
            print(f"  ✅ Downloaded ({file_info['size'] / 1024:.1f} KB)")
            
            # Process and ingest
            print(f"  📄 Processing PPTX...")
            result = await process_and_ingest(
                local_path,
                file_info['name'],
                safe_name,
                namespace,
                chunk_by_slide
            )
            
            elapsed = time.time() - start_time
            
            if result['success']:
                print(f"  ✅ Success! ({elapsed:.1f}s)")
                print(f"     Slides: {result['slides_processed']}/{result['total_slides']}")
                print(f"     Chunks: {result['chunks_created']}")
                print(f"     Vectors: {result['vectors_stored']}")
                
                results['processed'] += 1
                results['total_chunks'] += result['chunks_created']
                results['total_vectors'] += result['vectors_stored']
                results['total_slides'] += result['total_slides']
                results['files'].append({
                    'name': file_info['name'],
                    'status': 'success',
                    'slides': result['total_slides'],
                    'chunks': result['chunks_created'],
                    'vectors': result['vectors_stored']
                })
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
                results['failed'] += 1
                results['files'].append({
                    'name': file_info['name'],
                    'status': 'failed',
                    'error': result.get('error', 'Unknown')
                })
            
            # Clean up local file
            try:
                os.remove(local_path)
            except:
                pass
    
    # Print summary
    print("\n" + "="*80)
    print("INGESTION SUMMARY")
    print("="*80)
    print(f"Total files: {results['total_files']}")
    print(f"✅ Processed: {results['processed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"\n📊 Total slides: {results['total_slides']}")
    print(f"📦 Total chunks: {results['total_chunks']}")
    print(f"🔢 Total vectors: {results['total_vectors']}")
    
    if results['failed'] > 0:
        print(f"\n❌ Failed files:")
        for file_info in results['files']:
            if file_info['status'] == 'failed':
                print(f"  - {file_info['name']}: {file_info.get('error', 'Unknown error')}")
    
    print("="*80 + "\n")
    
    # Check final vector count
    print("📊 Checking Pinecone vector count...")
    try:
        vector_service.initialize()
        stats = vector_service.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"✅ Total vectors in Pinecone: {total_vectors}")
    except Exception as e:
        print(f"⚠️  Could not check vector count: {str(e)}")
    
    return results


async def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python ingest_all_gcs_pptx.py <bucket_name> <service_account_json> [namespace] [options]")
        print("\nOptions:")
        print("  --by-slide          Chunk by slide (default)")
        print("  --standard-chunks   Use standard chunking")
        print("  --max-files N       Process only first N files")
        print("\nExamples:")
        print('  python ingest_all_gcs_pptx.py llm-bucketfahm "C:\\path\\to\\key.json"')
        print('  python ingest_all_gcs_pptx.py llm-bucketfahm "C:\\path\\to\\key.json" my-namespace')
        print('  python ingest_all_gcs_pptx.py llm-bucketfahm "C:\\path\\to\\key.json" "" --max-files 5')
        sys.exit(1)
    
    bucket_name = sys.argv[1]
    service_account_path = sys.argv[2]
    namespace = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else ""
    
    # Parse options
    chunk_by_slide = '--standard-chunks' not in sys.argv
    max_files = None
    
    if '--max-files' in sys.argv:
        try:
            idx = sys.argv.index('--max-files')
            max_files = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ Invalid --max-files value")
            sys.exit(1)
    
    # Verify service account file
    if not os.path.exists(service_account_path):
        print(f"\n❌ Service account file not found: {service_account_path}")
        sys.exit(1)
    
    try:
        await ingest_all_pptx(bucket_name, service_account_path, namespace, chunk_by_slide, max_files)
        print("✅ Ingestion complete!\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Ingestion failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
