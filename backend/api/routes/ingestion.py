from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from pathlib import Path
import shutil
from loguru import logger

from backend.api.deps import get_current_active_user
from backend.models.user import User
from backend.rag.document_processor import NormativeDocumentProcessor
from backend.rag.vector_store import MultiLevelVectorStore
from backend.config import get_settings

router = APIRouter()

# Assicurati che la directory di upload esista
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/files")
async def list_files(current_user: User = Depends(get_current_active_user)):
    """Lista i file caricati."""
    settings = get_settings() # Get settings inside the function
    upload_dir = Path(settings.upload_path) # Use settings for upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    
    files = []
    if upload_dir.exists(): # Use upload_dir
        # Ordina per data di modifica (più recenti prima)
        paths = sorted(upload_dir.glob("*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)
        for p in paths:
            files.append({
                "name": p.name,
                "size": p.stat().st_size,
                "date": p.stat().st_mtime
            })
    return files

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    normative_level: str = Form("comunale"), 
    region: Optional[str] = Form(None),
    province: Optional[str] = Form(None),
    municipality: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Carica file normativi (PDF, HTML, TXT) e li indicizza.
    """
    settings = get_settings() # Get settings inside the function
    temp_upload_dir = Path(settings.temp_upload_path) # Use settings for temp_upload_path
    temp_upload_dir.mkdir(exist_ok=True) # Ensure temp directory exists
    
    results = []
    
    for file in files:
        # Salva file temporaneamente
        temp_path = Path("temp_uploads") / file.filename
        temp_path.parent.mkdir(exist_ok=True)
        
        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Determina store level
            store_level = "nazionale"
            if normative_level == "regionale" or normative_level == "provinciale":
                store_level = "regionale"
            elif normative_level == "comunale":
                store_level = "comunale"
            
            # Processa e indicizza
            processor = NormativeDocumentProcessor()
            processed_chunks = processor.process_normative_file(
                temp_path,
                normative_level,
                region,
                municipality,
                province  # Pass province to processor
            )
            
            # Inserisci nel vector store appropriato
            vector_store = MultiLevelVectorStore()
            ids = vector_store.add_documents(processed_chunks, store_level)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks": len(processed_chunks),
                "ids": len(ids)
            })
            
        except Exception as e:
            logger.error(f"Errore caricamento {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    return {"results": results}
