"""
Script to ingest PDF files into Pinecone database
"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scraper.pdf_scraper import pdf_scraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def ingest_single_pdf(pdf_path: str, namespace: str = ""):
    """
    Ingest a single PDF file
    
    Args:
        pdf_path: Path to PDF file
        namespace: Pinecone namespace
    """
    logger.info(f"Ingesting PDF: {pdf_path}")
    
    result = await pdf_scraper.process_pdf(
        pdf_path,
        namespace=namespace
    )
    
    if result['success']:
        print(f"\n✅ Successfully ingested: {pdf_path}")
        print(f"   Chunks created: {result['chunks_created']}")
        print(f"   Vectors stored: {result['vectors_stored']}")
        print(f"   Title: {result['metadata'].get('title', 'N/A')}")
        print(f"   Pages: {result['metadata'].get('num_pages', 'N/A')}")
    else:
        print(f"\n❌ Failed to ingest: {pdf_path}")
        print(f"   Error: {result.get('error', 'Unknown error')}")


async def ingest_directory(directory_path: str, namespace: str = "", recursive: bool = True):
    """
    Ingest all PDFs in a directory
    
    Args:
        directory_path: Path to directory
        namespace: Pinecone namespace
        recursive: Search subdirectories
    """
    logger.info(f"Ingesting PDFs from directory: {directory_path}")
    
    result = await pdf_scraper.process_pdf_directory(
        directory_path,
        namespace=namespace,
        recursive=recursive
    )
    
    if result['success']:
        print(f"\n✅ Successfully processed directory: {directory_path}")
        print(f"   Total files: {result['total_files']}")
        print(f"   Processed: {result['processed']}")
        print(f"   Failed: {result['failed']}")
        print(f"   Total chunks: {result['total_chunks']}")
        print(f"   Total vectors: {result['total_vectors']}")
        
        print("\n📄 File Details:")
        for file_result in result['files']:
            status = "✅" if file_result['success'] else "❌"
            print(f"   {status} {Path(file_result['file']).name}")
            if file_result['success']:
                print(f"      Chunks: {file_result.get('chunks_created', 0)}, "
                      f"Vectors: {file_result.get('vectors_stored', 0)}")
            else:
                print(f"      Error: {file_result.get('error', 'Unknown')}")
    else:
        print(f"\n❌ Failed to process directory: {directory_path}")
        print(f"   Error: {result.get('error', 'Unknown error')}")


async def main():
    """Main function"""
    print("="*80)
    print("PDF Ingestion Script")
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python ingest_pdf.py <path> [namespace] [--no-recursive]")
        print("\nExamples:")
        print("  python ingest_pdf.py document.pdf")
        print("  python ingest_pdf.py document.pdf my-namespace")
        print("  python ingest_pdf.py /path/to/pdfs/")
        print("  python ingest_pdf.py /path/to/pdfs/ my-namespace --no-recursive")
        sys.exit(1)
    
    path = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else ""
    recursive = '--no-recursive' not in sys.argv
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        print(f"\n❌ Error: Path not found: {path}")
        sys.exit(1)
    
    try:
        if path_obj.is_file():
            if not path.lower().endswith('.pdf'):
                print(f"\n❌ Error: File must be a PDF: {path}")
                sys.exit(1)
            
            await ingest_single_pdf(path, namespace)
        
        elif path_obj.is_dir():
            await ingest_directory(path, namespace, recursive)
        
        else:
            print(f"\n❌ Error: Path must be a file or directory: {path}")
            sys.exit(1)
        
        print("\n" + "="*80)
        print("Ingestion Complete!")
        print("="*80 + "\n")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Ingestion failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
