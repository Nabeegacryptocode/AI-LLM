"""
Daily GCS Bucket Ingestion Script
Automatically ingests new content from Google Cloud Storage bucket into Pinecone
Tracks processed files to avoid duplicates
"""
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

from google.cloud import storage
from scraper.pptx_scraper import PPTXScraper
from scraper.pdf_scraper import PDFScraper
from services.embedding_service import embedding_service
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyGCSIngestion:
    """Handles daily ingestion from GCS bucket"""
    
    def __init__(self, bucket_name: str, tracking_file: str = "processed_files.json"):
        self.bucket_name = bucket_name
        self.tracking_file = Path(__file__).parent / tracking_file
        self.processed_files = self.load_processed_files()
        self.storage_client = None
        self.bucket = None
        
    def load_processed_files(self) -> dict:
        """Load list of already processed files"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracking file: {e}")
                return {}
        return {}
    
    def save_processed_files(self):
        """Save list of processed files"""
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.processed_files, f, indent=2)
            logger.info(f"Saved tracking file: {len(self.processed_files)} files tracked")
        except Exception as e:
            logger.error(f"Error saving tracking file: {e}")
    
    def connect_to_gcs(self):
        """Connect to Google Cloud Storage"""
        try:
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            logger.info(f"✅ Connected to GCS bucket: {self.bucket_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to GCS: {e}")
            return False
    
    def get_new_files(self, days_back: int = 1) -> list:
        """Get files added/modified in the last N days"""
        if not self.bucket:
            if not self.connect_to_gcs():
                return []
        
        # Use timezone-aware datetime
        from datetime import timezone
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        new_files = []
        
        try:
            blobs = self.bucket.list_blobs()
            
            for blob in blobs:
                # Check if file is supported type
                if not (blob.name.endswith('.pptx') or blob.name.endswith('.pdf')):
                    continue
                
                # Check if already processed
                if blob.name in self.processed_files:
                    # Check if file was modified since last processing
                    last_processed_str = self.processed_files[blob.name]['processed_at']
                    last_processed = datetime.fromisoformat(last_processed_str)
                    # Make timezone-aware if needed
                    if last_processed.tzinfo is None:
                        last_processed = last_processed.replace(tzinfo=timezone.utc)
                    
                    if blob.updated > last_processed:
                        logger.info(f"File modified: {blob.name}")
                        new_files.append(blob)
                    continue
                
                # Check if file is new (within cutoff date)
                if blob.updated > cutoff_date:
                    logger.info(f"New file: {blob.name}")
                    new_files.append(blob)
            
            logger.info(f"Found {len(new_files)} new/modified files")
            return new_files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def process_pptx(self, blob) -> bool:
        """Process a PowerPoint file"""
        try:
            logger.info(f"Processing PPTX: {blob.name}")
            
            # Download to temp file (cross-platform)
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, Path(blob.name).name)
            blob.download_to_filename(temp_path)
            
            # Process with PPTX scraper
            scraper = PPTXScraper()
            result = await scraper.process_pptx(temp_path, namespace="ibm-docs")
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result.get('success'):
                logger.info(f"Ingested {result.get('chunks_created', 0)} chunks from {blob.name}")
                return True
            else:
                logger.warning(f"No content extracted from {blob.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing PPTX {blob.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def process_pdf(self, blob) -> bool:
        """Process a PDF file"""
        try:
            logger.info(f"Processing PDF: {blob.name}")
            
            # Download to temp file (cross-platform)
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, Path(blob.name).name)
            blob.download_to_filename(temp_path)
            
            # Process with PDF scraper
            scraper = PDFScraper()
            result = await scraper.process_pdf(temp_path, namespace="ibm-docs")
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result.get('success'):
                logger.info(f"Ingested {result.get('chunks_created', 0)} chunks from {blob.name}")
                return True
            else:
                logger.warning(f"No content extracted from {blob.name}: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing PDF {blob.name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def process_file(self, blob) -> bool:
        """Process a single file based on its type"""
        if blob.name.endswith('.pptx'):
            success = await self.process_pptx(blob)
        elif blob.name.endswith('.pdf'):
            success = await self.process_pdf(blob)
        else:
            logger.warning(f"⚠️ Unsupported file type: {blob.name}")
            return False
        
        if success:
            # Mark as processed with timezone-aware timestamp
            from datetime import timezone
            self.processed_files[blob.name] = {
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'size': blob.size,
                'updated': blob.updated.isoformat()
            }
            self.save_processed_files()
        
        return success
    
    async def run_daily_ingestion(self, days_back: int = 1):
        """Run the daily ingestion process"""
        logger.info("\n" + "="*80)
        logger.info("🚀 STARTING DAILY GCS INGESTION")
        logger.info(f"📦 Bucket: {self.bucket_name}")
        logger.info(f"📅 Looking for files from last {days_back} day(s)")
        logger.info(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")
        
        # Get new files
        new_files = self.get_new_files(days_back)
        
        if not new_files:
            logger.info("✅ No new files to process")
            return
        
        # Process each file
        success_count = 0
        failed_count = 0
        
        for blob in new_files:
            try:
                if await self.process_file(blob):
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"❌ Unexpected error processing {blob.name}: {e}")
                failed_count += 1
        
        # Print summary
        logger.info("\n" + "="*80)
        logger.info("📊 INGESTION SUMMARY")
        logger.info("="*80)
        logger.info(f"✅ Successfully processed: {success_count}")
        logger.info(f"❌ Failed: {failed_count}")
        logger.info(f"📁 Total files tracked: {len(self.processed_files)}")
        logger.info("="*80 + "\n")


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Daily GCS bucket ingestion into Pinecone',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process files from last 24 hours
  python daily_gcs_ingestion.py --bucket your-bucket-name
  
  # Process files from last 7 days
  python daily_gcs_ingestion.py --bucket your-bucket-name --days 7
  
  # Force reprocess all files
  python daily_gcs_ingestion.py --bucket your-bucket-name --days 365 --force
        """
    )
    
    parser.add_argument(
        '--bucket',
        required=True,
        help='GCS bucket name'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=1,
        help='Number of days to look back for new files (default: 1)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reprocess all files (clears tracking)'
    )
    
    args = parser.parse_args()
    
    # Create ingestion handler
    ingestion = DailyGCSIngestion(args.bucket)
    
    # Clear tracking if force flag is set
    if args.force:
        logger.warning("⚠️ Force flag set - clearing processed files tracking")
        ingestion.processed_files = {}
        ingestion.save_processed_files()
    
    # Run ingestion
    await ingestion.run_daily_ingestion(args.days)
    
    logger.info("✅ Daily ingestion completed!")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob