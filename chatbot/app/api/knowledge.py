from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import aiofiles
from pathlib import Path
from app.database.config import get_db
from app.schemas.schemas import (
    KnowledgeDocumentResponse, 
    KnowledgeDocumentCreate, 
    KnowledgeDocumentUpdate,
    FileUploadResponse
)
from app.services import crud
from app.services.document_processor import process_uploaded_file

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/documents", response_model=List[KnowledgeDocumentResponse])
def get_documents(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get knowledge documents with optional search"""
    return crud.get_knowledge_documents(db, skip=skip, limit=limit, search=search)

@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific knowledge document"""
    document = crud.get_knowledge_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/documents/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new knowledge document"""
    
    # Validate file type
    allowed_types = {".pdf", ".docx", ".doc", ".txt"}
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create document record
        document_data = KnowledgeDocumentCreate(
            title=title or file.filename,
            file_name=file.filename,
            file_type=file_extension,
            file_size=len(content),
            file_path=str(file_path),
            tags=tags,
            content=""  # Will be processed later
        )
        
        document = crud.create_knowledge_document(db, document_data)
        
        # Process file asynchronously (in background)
        # For now, we'll mark it as processing and handle it later
        try:
            processed_content = await process_uploaded_file(file_path, file_extension)
            
            # Update document with processed content
            update_data = KnowledgeDocumentUpdate(
                content=processed_content,
                status="ready"
            )
            crud.update_knowledge_document(db, document.id, update_data)
            
            # Create document chunks for better search
            chunks = split_content_into_chunks(processed_content)
            crud.create_document_chunks(db, document.id, chunks)
            
        except Exception as processing_error:
            # Mark document as error
            update_data = KnowledgeDocumentUpdate(
                status="error",
                error_message=str(processing_error)
            )
            crud.update_knowledge_document(db, document.id, update_data)
        
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            document_id=document.id,
            filename=file.filename
        )
        
    except Exception as e:
        # Clean up file if database operation failed
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.put("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
def update_document(
    document_id: int,
    update_data: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update a knowledge document"""
    document = crud.update_knowledge_document(db, document_id, update_data)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a knowledge document"""
    success = crud.delete_knowledge_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@router.get("/search")
def search_knowledge(query: str, limit: int = 5, db: Session = Depends(get_db)):
    """Search knowledge base content"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    chunks = crud.search_knowledge_content(db, query, limit=limit)
    
    results = []
    for chunk in chunks:
        results.append({
            "document_id": chunk.document.id,
            "document_title": chunk.document.title,
            "content": chunk.content,
            "chunk_index": chunk.chunk_index
        })
    
    return {"query": query, "results": results}

def split_content_into_chunks(content: str, chunk_size: int = 1000) -> List[str]:
    """Split content into smaller chunks for better search"""
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
        
        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0
    
    # Add remaining words as final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks