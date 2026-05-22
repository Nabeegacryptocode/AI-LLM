"""
Dynamic Document Ingestion Service
Automatically downloads and ingests PPTX and PDF files found by Discovery Engine
"""
import logging
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from scraper.pptx_scraper import pptx_scraper
from scraper.pdf_scraper import pdf_scraper
from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class DynamicPPTXIngestionService:
    """Service for dynamically ingesting PPTX and PDF files from GCS"""
    
    def __init__(self):
        """Initialize dynamic ingestion service"""
        self.service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.service_account_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        self.ingested_files_cache = set()  # Track already ingested files
        
    def _get_file_hash(self, gcs_url: str) -> str:
        """Generate hash for GCS URL to track ingested files"""
        return hashlib.md5(gcs_url.encode()).hexdigest()
    
    def _is_pptx_file(self, url: str) -> bool:
        """Check if URL points to a PPTX file"""
        return url.lower().endswith(('.pptx', '.ppt'))
    
    def _is_pdf_file(self, url: str) -> bool:
        """Check if URL points to a PDF file"""
        return url.lower().endswith('.pdf')
    
    def _is_supported_file(self, url: str) -> bool:
        """Check if URL points to a supported file type (PPTX or PDF)"""
        return self._is_pptx_file(url) or self._is_pdf_file(url)
    
    def _parse_gcs_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse GCS URL to extract bucket and blob name
        
        Args:
            url: GCS URL (gs://bucket/path/to/file.pptx)
            
        Returns:
            Dict with bucket and blob_name, or None if invalid
        """
        if not url.startswith('gs://'):
            return None
        
        # Remove gs:// prefix
        path = url[5:]
        parts = path.split('/', 1)
        
        if len(parts) != 2:
            return None
        
        return {
            'bucket': parts[0],
            'blob_name': parts[1]
        }
    
    async def download_and_ingest_pptx(
        self,
        gcs_url: str,
        namespace: str = "",
        chunk_by_slide: bool = True
    ) -> Dict[str, Any]:
        """
        Download PPTX from GCS and ingest into Pinecone
        
        Args:
            gcs_url: GCS URL (gs://bucket/path/to/file.pptx)
            namespace: Pinecone namespace
            chunk_by_slide: Whether to chunk by slide
            
        Returns:
            Ingestion result
        """
        try:
            # Check if already ingested
            file_hash = self._get_file_hash(gcs_url)
            if file_hash in self.ingested_files_cache:
                logger.info(f"File already ingested: {gcs_url}")
                return {
                    'success': True,
                    'cached': True,
                    'message': 'File already ingested'
                }
            
            # Parse GCS URL
            gcs_info = self._parse_gcs_url(gcs_url)
            if not gcs_info:
                logger.error(f"Invalid GCS URL: {gcs_url}")
                return {
                    'success': False,
                    'error': 'Invalid GCS URL format'
                }
            
            if not GCS_AVAILABLE:
                logger.error("google-cloud-storage not installed")
                return {
                    'success': False,
                    'error': 'google-cloud-storage not installed'
                }
            
            logger.info(f"Downloading PPTX from: {gcs_url}")
            
            # Set credentials
            if self.service_account_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.service_account_path
            
            # Download file
            storage_client = storage.Client()
            bucket = storage_client.bucket(gcs_info['bucket'])
            blob = bucket.blob(gcs_info['blob_name'])
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as temp_file:
                temp_path = temp_file.name
            
            try:
                # Download to temp file
                blob.download_to_filename(temp_path)
                logger.info(f"Downloaded to: {temp_path}")
                
                # Process and ingest
                filename = Path(gcs_info['blob_name']).name
                result = await pptx_scraper.process_pptx(
                    temp_path,
                    namespace=namespace,
                    custom_metadata={
                        'gcs_bucket': gcs_info['bucket'],
                        'gcs_path': gcs_info['blob_name'],
                        'gcs_url': gcs_url,
                        'source': 'Google Cloud Storage',
                        'original_filename': filename,
                        'dynamically_ingested': True
                    },
                    chunk_by_slide=chunk_by_slide
                )
                
                if result['success']:
                    # Mark as ingested
                    self.ingested_files_cache.add(file_hash)
                    logger.info(
                        f"Successfully ingested {filename}: "
                        f"{result['vectors_stored']} vectors from {result['total_slides']} slides"
                    )
                
                return result
                
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error downloading and ingesting PPTX: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download_and_ingest_pdf(
        self,
        gcs_url: str,
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Download PDF from GCS and ingest into Pinecone
        
        Args:
            gcs_url: GCS URL (gs://bucket/path/to/file.pdf)
            namespace: Pinecone namespace
            
        Returns:
            Ingestion result
        """
        try:
            # Check if already ingested
            file_hash = self._get_file_hash(gcs_url)
            if file_hash in self.ingested_files_cache:
                logger.info(f"File already ingested: {gcs_url}")
                return {
                    'success': True,
                    'cached': True,
                    'message': 'File already ingested'
                }
            
            # Parse GCS URL
            gcs_info = self._parse_gcs_url(gcs_url)
            if not gcs_info:
                logger.error(f"Invalid GCS URL: {gcs_url}")
                return {
                    'success': False,
                    'error': 'Invalid GCS URL format'
                }
            
            if not GCS_AVAILABLE:
                logger.error("google-cloud-storage not installed")
                return {
                    'success': False,
                    'error': 'google-cloud-storage not installed'
                }
            
            logger.info(f"Downloading PDF from: {gcs_url}")
            
            # Set credentials
            if self.service_account_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.service_account_path
            
            # Download file
            storage_client = storage.Client()
            bucket = storage_client.bucket(gcs_info['bucket'])
            blob = bucket.blob(gcs_info['blob_name'])
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name
            
            try:
                # Download to temp file
                blob.download_to_filename(temp_path)
                logger.info(f"Downloaded to: {temp_path}")
                
                # Process and ingest
                filename = Path(gcs_info['blob_name']).name
                result = await pdf_scraper.process_pdf(
                    temp_path,
                    namespace=namespace,
                    custom_metadata={
                        'gcs_bucket': gcs_info['bucket'],
                        'gcs_path': gcs_info['blob_name'],
                        'gcs_url': gcs_url,
                        'source': 'Google Cloud Storage',
                        'original_filename': filename,
                        'dynamically_ingested': True
                    }
                )
                
                if result['success']:
                    # Mark as ingested
                    self.ingested_files_cache.add(file_hash)
                    logger.info(
                        f"Successfully ingested {filename}: "
                        f"{result['vectors_stored']} vectors from {result['total_pages']} pages"
                    )
                
                return result
                
            finally:
                # Clean up temp file
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error downloading and ingesting PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def download_and_ingest_document(
        self,
        gcs_url: str,
        namespace: str = "",
        chunk_by_slide: bool = True
    ) -> Dict[str, Any]:
        """
        Download and ingest document (PPTX or PDF) from GCS
        
        Args:
            gcs_url: GCS URL (gs://bucket/path/to/file)
            namespace: Pinecone namespace
            chunk_by_slide: Whether to chunk by slide (for PPTX only)
            
        Returns:
            Ingestion result
        """
        if self._is_pptx_file(gcs_url):
            return await self.download_and_ingest_pptx(gcs_url, namespace, chunk_by_slide)
        elif self._is_pdf_file(gcs_url):
            return await self.download_and_ingest_pdf(gcs_url, namespace)
        else:
            return {
                'success': False,
                'error': f'Unsupported file type: {gcs_url}'
            }
    
    async def process_discovery_results(
        self,
        discovery_results: List[Dict[str, Any]],
        namespace: str = "",
        chunk_by_slide: bool = True,
        max_files: int = 3
    ) -> Dict[str, Any]:
        """
        Process Discovery Engine results and ingest PPTX and PDF files
        
        Args:
            discovery_results: Results from Discovery Engine
            namespace: Pinecone namespace
            chunk_by_slide: Whether to chunk by slide (for PPTX only)
            max_files: Maximum number of files to ingest
            
        Returns:
            Summary of ingestion results
        """
        logger.info(f"Processing {len(discovery_results)} Discovery Engine results")
        
        results = {
            'total_results': len(discovery_results),
            'pptx_files_found': 0,
            'pdf_files_found': 0,
            'supported_files_found': 0,
            'ingested': 0,
            'cached': 0,
            'failed': 0,
            'total_vectors': 0,
            'files': []
        }
        
        ingested_count = 0
        
        for result in discovery_results:
            url = result.get('url', '')
            
            # Check if it's a supported file type
            if not self._is_supported_file(url):
                continue
            
            # Track file types
            if self._is_pptx_file(url):
                results['pptx_files_found'] += 1
                file_type = 'PPTX'
            elif self._is_pdf_file(url):
                results['pdf_files_found'] += 1
                file_type = 'PDF'
            else:
                continue
            
            results['supported_files_found'] += 1
            
            # Stop if we've reached max files
            if ingested_count >= max_files:
                logger.info(f"Reached max files limit ({max_files})")
                break
            
            # Download and ingest
            logger.info(f"Processing {file_type}: {result.get('title', 'Unknown')}")
            ingest_result = await self.download_and_ingest_document(
                url,
                namespace=namespace,
                chunk_by_slide=chunk_by_slide
            )
            
            if ingest_result.get('success'):
                if ingest_result.get('cached'):
                    results['cached'] += 1
                else:
                    results['ingested'] += 1
                    results['total_vectors'] += ingest_result.get('vectors_stored', 0)
                    ingested_count += 1
                
                # Get page/slide count based on file type
                page_count = ingest_result.get('total_slides', ingest_result.get('total_pages', 0))
                
                results['files'].append({
                    'title': result.get('title', 'Unknown'),
                    'url': url,
                    'file_type': file_type,
                    'status': 'cached' if ingest_result.get('cached') else 'ingested',
                    'vectors': ingest_result.get('vectors_stored', 0),
                    'pages': page_count
                })
            else:
                results['failed'] += 1
                results['files'].append({
                    'title': result.get('title', 'Unknown'),
                    'url': url,
                    'file_type': file_type,
                    'status': 'failed',
                    'error': ingest_result.get('error', 'Unknown error')
                })
        
        logger.info(
            f"Dynamic ingestion complete: {results['ingested']} ingested, "
            f"{results['cached']} cached, {results['failed']} failed "
            f"({results['pptx_files_found']} PPTX, {results['pdf_files_found']} PDF)"
        )
        
        return results
    
    async def get_content_from_discovery_results(
        self,
        discovery_results: List[Dict[str, Any]],
        query: str,
        namespace: str = "",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Ingest PPTX files from Discovery results and retrieve relevant content
        
        Args:
            discovery_results: Results from Discovery Engine
            query: Original query
            namespace: Pinecone namespace
            top_k: Number of results to return
            
        Returns:
            List of relevant content chunks
        """
        # First, ingest any PPTX files found (only top document)
        ingestion_results = await self.process_discovery_results(
            discovery_results,
            namespace=namespace,
            chunk_by_slide=True,
            max_files=1
        )
        
        logger.info(
            f"Ingested {ingestion_results['ingested']} new files, "
            f"{ingestion_results['cached']} were cached"
        )
        
        # Now search for relevant content in Pinecone
        if ingestion_results['ingested'] > 0 or ingestion_results['cached'] > 0:
            logger.info(f"Searching Pinecone for: {query}")
            results = await embedding_service.search_similar(
                query=query,
                namespace=namespace,
                top_k=top_k
            )
            return results
        
        return []


# Global instance
dynamic_pptx_ingestion_service = DynamicPPTXIngestionService()

# Made with Bob
