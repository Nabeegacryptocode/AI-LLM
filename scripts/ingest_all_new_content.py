"""
Master script to ingest ALL new information into the vector database
Simplified version that uses existing ingestion scripts
"""
import sys
import os
import subprocess
import argparse
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MasterIngestionOrchestrator:
    """Orchestrates ingestion from all sources using existing scripts"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    def run_script(self, script_name: str, args: list = None) -> bool:
        """Run a Python script and return success status"""
        try:
            cmd = [sys.executable, os.path.join(self.scripts_dir, script_name)]
            if args:
                cmd.extend(args)
            
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ {script_name} completed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout[-500:]}")  # Last 500 chars
                return True
            else:
                logger.error(f"❌ {script_name} failed with code {result.returncode}")
                if result.stderr:
                    logger.error(f"STDERR: {result.stderr[-1000:]}")  # Last 1000 chars
                if result.stdout:
                    logger.error(f"STDOUT: {result.stdout[-1000:]}")  # Last 1000 chars
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running {script_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def ingest_ibm_cloud(self, max_pages: int = 20):
        """Ingest IBM Cloud documentation"""
        logger.info("\n" + "="*80)
        logger.info("🌩️  INGESTING IBM CLOUD DOCUMENTATION")
        logger.info("="*80 + "\n")
        
        success = self.run_script('ingest_all_docs.py', [
            '--source', 'cloud',
            '--sections', 'all',
            '--max-pages', str(max_pages)
        ])
        self.results['ibm_cloud'] = 'success' if success else 'failed'
    
    def ingest_ibm_mas(self, max_pages: int = 20):
        """Ingest IBM Maximo Application Suite documentation"""
        logger.info("\n" + "="*80)
        logger.info("🏭 INGESTING IBM MAXIMO APPLICATION SUITE DOCUMENTATION")
        logger.info("="*80 + "\n")
        
        success = self.run_script('ingest_all_docs.py', [
            '--source', 'mas',
            '--sections', 'all',
            '--max-pages', str(max_pages)
        ])
        self.results['ibm_mas'] = 'success' if success else 'failed'
    
    def ingest_ibm_gdp(self, max_pages: int = 20):
        """Ingest IBM Guardium Data Protection documentation"""
        logger.info("\n" + "="*80)
        logger.info("🛡️  INGESTING IBM GUARDIUM DATA PROTECTION DOCUMENTATION")
        logger.info("="*80 + "\n")
        
        success = self.run_script('ingest_all_docs.py', [
            '--source', 'gdp',
            '--sections', 'all',
            '--max-pages', str(max_pages)
        ])
        self.results['ibm_gdp'] = 'success' if success else 'failed'
    
    def ingest_ibm_maas360(self):
        """Ingest IBM MaaS360 documentation"""
        logger.info("\n" + "="*80)
        logger.info("📱 INGESTING IBM MAAS360 DOCUMENTATION")
        logger.info("="*80 + "\n")
        
        success = self.run_script('ingest_ibm_maas360.py')
        self.results['ibm_maas360'] = 'success' if success else 'failed'
    
    def ingest_fahm_partners(self):
        """Ingest FAHM Partners website content"""
        logger.info("\n" + "="*80)
        logger.info("🏢 INGESTING FAHM PARTNERS WEBSITE CONTENT")
        logger.info("="*80 + "\n")
        
        success = self.run_script('ingest_fahm_partners.py')
        self.results['fahm_partners'] = 'success' if success else 'failed'
    
    def ingest_pdfs(self, pdf_directory: str = None):
        """Ingest PDF documents"""
        logger.info("\n" + "="*80)
        logger.info("📄 INGESTING PDF DOCUMENTS")
        logger.info("="*80 + "\n")
        
        if not pdf_directory:
            logger.info("⏭️  No PDF directory specified, skipping...")
            self.results['pdfs'] = 'skipped'
            return
        
        if not os.path.exists(pdf_directory):
            logger.warning(f"⚠️  PDF directory not found: {pdf_directory}")
            self.results['pdfs'] = 'not_found'
            return
        
        # Find all PDF files
        pdf_files = []
        for root, dirs, files in os.walk(pdf_directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if not pdf_files:
            logger.warning("⚠️  No PDF files found")
            self.results['pdfs'] = 'no_files'
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        # Ingest each PDF
        success_count = 0
        for pdf_file in pdf_files:
            logger.info(f"📄 Processing: {os.path.basename(pdf_file)}")
            if self.run_script('ingest_pdf.py', [pdf_file]):
                success_count += 1
        
        self.results['pdfs'] = f'success ({success_count}/{len(pdf_files)})'
    
    def ingest_pptx(self, pptx_directory: str = None, gcs_bucket: str = None):
        """Ingest PowerPoint presentations"""
        logger.info("\n" + "="*80)
        logger.info("📊 INGESTING POWERPOINT PRESENTATIONS")
        logger.info("="*80 + "\n")
        
        if not pptx_directory and not gcs_bucket:
            logger.info("⏭️  No PPTX directory or GCS bucket specified, skipping...")
            self.results['pptx'] = 'skipped'
            return
        
        success = False
        
        # Process GCS bucket if specified
        if gcs_bucket:
            logger.info(f"📦 Processing PPTX files from GCS bucket: {gcs_bucket}")
            success = self.run_script('ingest_gcs_pptx.py', ['--bucket', gcs_bucket])
        
        # Process local directory if specified
        if pptx_directory:
            if os.path.exists(pptx_directory):
                pptx_files = []
                for root, dirs, files in os.walk(pptx_directory):
                    for file in files:
                        if file.lower().endswith('.pptx'):
                            pptx_files.append(os.path.join(root, file))
                
                logger.info(f"Found {len(pptx_files)} PPTX files locally")
                
                for pptx_file in pptx_files:
                    logger.info(f"📊 Processing: {os.path.basename(pptx_file)}")
                    if self.run_script('ingest_pdf.py', [pptx_file]):  # Can reuse PDF script
                        success = True
            else:
                logger.warning(f"⚠️  PPTX directory not found: {pptx_directory}")
        
        self.results['pptx'] = 'success' if success else 'failed'
    
    def run_full_ingestion(
        self,
        sources: list = None,
        max_pages: int = 20,
        pdf_dir: str = None,
        pptx_dir: str = None,
        gcs_bucket: str = None
    ):
        """Run full ingestion pipeline"""
        logger.info("\n" + "="*80)
        logger.info("🚀 STARTING MASTER INGESTION PIPELINE")
        logger.info(f"⏰ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")
        
        # Determine which sources to ingest
        all_sources = ['ibm_cloud', 'ibm_mas', 'ibm_gdp', 'ibm_maas360', 'fahm_partners', 'pdfs', 'pptx']
        sources_to_ingest = sources if sources else all_sources
        
        # Run ingestion for each source
        if 'ibm_cloud' in sources_to_ingest:
            self.ingest_ibm_cloud(max_pages)
        
        if 'ibm_mas' in sources_to_ingest:
            self.ingest_ibm_mas(max_pages)
        
        if 'ibm_gdp' in sources_to_ingest:
            self.ingest_ibm_gdp(max_pages)
        
        if 'ibm_maas360' in sources_to_ingest:
            self.ingest_ibm_maas360()
        
        if 'fahm_partners' in sources_to_ingest:
            self.ingest_fahm_partners()
        
        if 'pdfs' in sources_to_ingest:
            self.ingest_pdfs(pdf_dir)
        
        if 'pptx' in sources_to_ingest:
            self.ingest_pptx(pptx_dir, gcs_bucket)
        
        # Print final summary
        self.print_summary()
    
    def print_summary(self):
        """Print ingestion summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        logger.info("\n" + "="*80)
        logger.info("📊 INGESTION SUMMARY")
        logger.info("="*80)
        logger.info(f"⏰ Duration: {duration}")
        logger.info("")
        
        for source, status in self.results.items():
            status_emoji = {
                'success': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'not_found': '🔍',
                'no_files': '📭'
            }.get(status if not status.startswith('success') else 'success', '❓')
            
            logger.info(f"{status_emoji} {source.upper().replace('_', ' ')}: {status}")
        
        logger.info("="*80 + "\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Master script to ingest ALL new information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest everything (default)
  python ingest_all_new_content.py
  
  # Ingest specific sources
  python ingest_all_new_content.py --sources ibm_gdp ibm_maas360 fahm_partners
  
  # Ingest with custom page limits
  python ingest_all_new_content.py --max-pages 50
  
  # Include PDFs and PPTX files
  python ingest_all_new_content.py --pdf-dir ./pdfs --pptx-dir ./presentations
  
  # Include GCS bucket for PPTX
  python ingest_all_new_content.py --gcs-bucket your-bucket-name
        """
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['ibm_cloud', 'ibm_mas', 'ibm_gdp', 'ibm_maas360', 'fahm_partners', 'pdfs', 'pptx'],
        help='Specific sources to ingest (default: all)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Maximum pages per section for web scraping (default: 20)'
    )
    parser.add_argument(
        '--pdf-dir',
        type=str,
        help='Directory containing PDF files to ingest'
    )
    parser.add_argument(
        '--pptx-dir',
        type=str,
        help='Directory containing PPTX files to ingest'
    )
    parser.add_argument(
        '--gcs-bucket',
        type=str,
        help='Google Cloud Storage bucket name for PPTX files'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator and run ingestion
    orchestrator = MasterIngestionOrchestrator()
    
    orchestrator.run_full_ingestion(
        sources=args.sources,
        max_pages=args.max_pages,
        pdf_dir=args.pdf_dir,
        pptx_dir=args.pptx_dir,
        gcs_bucket=args.gcs_bucket
    )
    
    logger.info("✅ Master ingestion pipeline completed!")


if __name__ == "__main__":
    main()

# Made with Bob