"""
PDF Scraper for extracting and ingesting PDF documents into Pinecone
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from scraper.document_processor import DocumentProcessor
from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class PDFScraper:
    """Scraper for PDF documents"""
    
    def __init__(self):
        """Initialize PDF scraper"""
        self.document_processor = DocumentProcessor()
        
        # Check available PDF libraries
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            logger.warning(
                "No PDF library available. Install PyPDF2 or pdfplumber: "
                "pip install PyPDF2 pdfplumber"
            )
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        try:
            text_content = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {num_pages} pages using PyPDF2")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        text_content.append(text)
                        logger.debug(f"Extracted {len(text)} characters from page {page_num + 1}")
            
            full_text = '\n\n'.join(text_content)
            logger.info(f"Total extracted text: {len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {str(e)}")
            raise
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text from PDF using pdfplumber (better for complex PDFs)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber not installed. Install with: pip install pdfplumber")
        
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"Extracting text from {num_pages} pages using pdfplumber")
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text:
                        text_content.append(text)
                        logger.debug(f"Extracted {len(text)} characters from page {page_num + 1}")
            
            full_text = '\n\n'.join(text_content)
            logger.info(f"Total extracted text: {len(full_text)} characters")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber: {str(e)}")
            raise
    
    def extract_text(self, pdf_path: str, method: str = 'auto') -> str:
        """
        Extract text from PDF using available method
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ('auto', 'pypdf2', 'pdfplumber')
            
        Returns:
            Extracted text
        """
        if method == 'auto':
            # Try pdfplumber first (better quality), fallback to PyPDF2
            if PDFPLUMBER_AVAILABLE:
                try:
                    return self.extract_text_pdfplumber(pdf_path)
                except Exception as e:
                    logger.warning(f"pdfplumber failed, trying PyPDF2: {str(e)}")
            
            if PYPDF2_AVAILABLE:
                return self.extract_text_pypdf2(pdf_path)
            
            raise ImportError("No PDF library available")
        
        elif method == 'pypdf2':
            return self.extract_text_pypdf2(pdf_path)
        
        elif method == 'pdfplumber':
            return self.extract_text_pdfplumber(pdf_path)
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'filename': Path(pdf_path).name,
            'filepath': str(pdf_path),
            'file_size': Path(pdf_path).stat().st_size,
            'source_type': 'PDF Document',
            'ingestion_date': datetime.utcnow().isoformat()
        }
        
        # Try to extract PDF metadata
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    metadata['num_pages'] = len(pdf_reader.pages)
                    
                    # Extract PDF info
                    if pdf_reader.metadata:
                        pdf_info = pdf_reader.metadata
                        metadata['title'] = pdf_info.get('/Title', metadata['filename'])
                        metadata['author'] = pdf_info.get('/Author', 'Unknown')
                        metadata['subject'] = pdf_info.get('/Subject', '')
                        metadata['creator'] = pdf_info.get('/Creator', '')
                        metadata['producer'] = pdf_info.get('/Producer', '')
                        
                        # Parse creation date if available
                        if '/CreationDate' in pdf_info:
                            metadata['creation_date'] = pdf_info['/CreationDate']
                    else:
                        metadata['title'] = metadata['filename']
                        
            except Exception as e:
                logger.warning(f"Could not extract PDF metadata: {str(e)}")
                metadata['title'] = metadata['filename']
        else:
            metadata['title'] = metadata['filename']
        
        return metadata
    
    async def process_pdf(
        self,
        pdf_path: str,
        namespace: str = "",
        custom_metadata: Optional[Dict[str, Any]] = None,
        method: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Process a PDF file and ingest into Pinecone
        
        Args:
            pdf_path: Path to PDF file
            namespace: Pinecone namespace
            custom_metadata: Additional metadata to include
            method: Extraction method
            
        Returns:
            Processing results
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Check if file exists
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Extract text
            text = self.extract_text(pdf_path, method=method)
            
            if not text or len(text.strip()) < 100:
                logger.warning(f"Extracted text too short ({len(text)} chars), skipping")
                return {
                    'success': False,
                    'error': 'Extracted text too short or empty',
                    'file': pdf_path
                }
            
            # Extract metadata
            metadata = self.extract_metadata(pdf_path)
            
            # Add custom metadata
            if custom_metadata:
                metadata.update(custom_metadata)
            
            # Create document
            document = {
                'content': text,
                'metadata': metadata
            }
            
            # Create chunks
            chunks = self.document_processor.create_chunks_with_metadata(document)
            
            if not chunks:
                logger.warning(f"No chunks created from PDF: {pdf_path}")
                return {
                    'success': False,
                    'error': 'No chunks created',
                    'file': pdf_path
                }
            
            logger.info(f"Created {len(chunks)} chunks from PDF")
            
            # Ingest into Pinecone
            results = await embedding_service.ingest_documents(
                chunks,
                namespace=namespace
            )
            
            return {
                'success': True,
                'file': pdf_path,
                'chunks_created': len(chunks),
                'vectors_stored': results.get('stored', 0),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file': pdf_path
            }
    
    async def process_pdf_directory(
        self,
        directory_path: str,
        namespace: str = "",
        recursive: bool = True,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process all PDFs in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            namespace: Pinecone namespace
            recursive: Whether to search subdirectories
            custom_metadata: Additional metadata for all PDFs
            
        Returns:
            Processing results summary
        """
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            # Find all PDF files
            if recursive:
                pdf_files = list(directory.rglob('*.pdf'))
            else:
                pdf_files = list(directory.glob('*.pdf'))
            
            logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
            
            if not pdf_files:
                return {
                    'success': True,
                    'message': 'No PDF files found',
                    'total_files': 0,
                    'processed': 0,
                    'failed': 0
                }
            
            results = {
                'total_files': len(pdf_files),
                'processed': 0,
                'failed': 0,
                'total_chunks': 0,
                'total_vectors': 0,
                'files': []
            }
            
            # Process each PDF
            for pdf_file in pdf_files:
                logger.info(f"Processing {pdf_file.name}...")
                
                result = await self.process_pdf(
                    str(pdf_file),
                    namespace=namespace,
                    custom_metadata=custom_metadata
                )
                
                if result['success']:
                    results['processed'] += 1
                    results['total_chunks'] += result.get('chunks_created', 0)
                    results['total_vectors'] += result.get('vectors_stored', 0)
                else:
                    results['failed'] += 1
                
                results['files'].append(result)
            
            logger.info(
                f"Completed processing: {results['processed']} successful, "
                f"{results['failed']} failed, {results['total_vectors']} vectors stored"
            )
            
            return {
                'success': True,
                **results
            }
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'directory': directory_path
            }


# Global instance
pdf_scraper = PDFScraper()

# Made with Bob