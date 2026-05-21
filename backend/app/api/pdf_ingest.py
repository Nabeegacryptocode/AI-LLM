"""
PDF Ingestion API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
import logging
import tempfile
import os
from pathlib import Path

from scraper.pdf_scraper import pdf_scraper
from app.utils.auth import verify_api_key

router = APIRouter(prefix="/pdf", tags=["pdf-ingestion"])
logger = logging.getLogger(__name__)


@router.post("/upload", dependencies=[Depends(verify_api_key)])
async def upload_pdf(
    file: UploadFile = File(...),
    namespace: str = Form(""),
    title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    source: Optional[str] = Form(None)
):
    """
    Upload and ingest a PDF file into Pinecone
    
    Args:
        file: PDF file to upload
        namespace: Pinecone namespace (optional)
        title: Custom title (optional, uses PDF metadata if not provided)
        author: Custom author (optional)
        source: Source information (optional)
        
    Returns:
        Ingestion results
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Prepare custom metadata
            custom_metadata = {}
            if title:
                custom_metadata['title'] = title
            if author:
                custom_metadata['author'] = author
            if source:
                custom_metadata['source'] = source
            
            # Process PDF
            result = await pdf_scraper.process_pdf(
                tmp_path,
                namespace=namespace,
                custom_metadata=custom_metadata if custom_metadata else None
            )
            
            if not result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process PDF: {result.get('error', 'Unknown error')}"
                )
            
            return {
                "status": "success",
                "message": f"Successfully ingested PDF: {file.filename}",
                "data": {
                    "filename": file.filename,
                    "chunks_created": result.get('chunks_created', 0),
                    "vectors_stored": result.get('vectors_stored', 0),
                    "namespace": namespace or "default",
                    "metadata": result.get('metadata', {})
                }
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-multiple", dependencies=[Depends(verify_api_key)])
async def upload_multiple_pdfs(
    files: List[UploadFile] = File(...),
    namespace: str = Form("")
):
    """
    Upload and ingest multiple PDF files into Pinecone
    
    Args:
        files: List of PDF files to upload
        namespace: Pinecone namespace (optional)
        
    Returns:
        Ingestion results for all files
    """
    try:
        results = {
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "total_vectors": 0,
            "files": []
        }
        
        for file in files:
            try:
                # Validate file type
                if not file.filename.lower().endswith('.pdf'):
                    results['failed'] += 1
                    results['files'].append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Not a PDF file"
                    })
                    continue
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    content = await file.read()
                    tmp_file.write(content)
                    tmp_path = tmp_file.name
                
                try:
                    # Process PDF
                    result = await pdf_scraper.process_pdf(
                        tmp_path,
                        namespace=namespace
                    )
                    
                    if result['success']:
                        results['processed'] += 1
                        results['total_chunks'] += result.get('chunks_created', 0)
                        results['total_vectors'] += result.get('vectors_stored', 0)
                    else:
                        results['failed'] += 1
                    
                    results['files'].append({
                        "filename": file.filename,
                        **result
                    })
                    
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {str(e)}")
                results['failed'] += 1
                results['files'].append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "message": f"Processed {results['processed']} of {results['total_files']} files",
            "data": results
        }
    
    except Exception as e:
        logger.error(f"Error uploading multiple PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest-from-path", dependencies=[Depends(verify_api_key)])
async def ingest_from_path(
    path: str = Form(...),
    namespace: str = Form(""),
    recursive: bool = Form(True)
):
    """
    Ingest PDF files from a server path
    
    Args:
        path: Path to PDF file or directory
        namespace: Pinecone namespace (optional)
        recursive: Search subdirectories (for directories only)
        
    Returns:
        Ingestion results
    """
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Path not found: {path}"
            )
        
        # Check if it's a file or directory
        if path_obj.is_file():
            if not path.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="File must be a PDF"
                )
            
            result = await pdf_scraper.process_pdf(
                path,
                namespace=namespace
            )
            
            if not result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process PDF: {result.get('error', 'Unknown error')}"
                )
            
            return {
                "status": "success",
                "message": f"Successfully ingested PDF from path",
                "data": result
            }
        
        elif path_obj.is_dir():
            result = await pdf_scraper.process_pdf_directory(
                path,
                namespace=namespace,
                recursive=recursive
            )
            
            if not result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process directory: {result.get('error', 'Unknown error')}"
                )
            
            return {
                "status": "success",
                "message": f"Successfully processed {result.get('processed', 0)} PDFs from directory",
                "data": result
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Path must be a file or directory"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting from path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Made with Bob