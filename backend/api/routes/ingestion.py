from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from pathlib import Path
import shutil
from loguru import logger

from backend.api.deps import get_current_active_user
from backend.models.user import User
from backend.rag.document_processor import NormativeDocumentProcessor
from backend.rag.vector_store import MultiLevelVectorStore
from backend.config import settings

router = APIRouter()

# Assicurati che la directory di upload esista
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/files")
async def list_files(current_user: User = Depends(get_current_active_user)):
    """Lista i file caricati."""
    files = []
    if UPLOAD_DIR.exists():
        # Ordina per data di modifica (più recenti prima)
        paths = sorted(UPLOAD_DIR.glob("*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)
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
    normative_level: str = Form("comunale"), # Default a comunale
    municipality: Optional[str] = Form(None),
    region: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Carica file normativi, li processa e li indicizza.
    """
    logger.info(f"Ricevuti {len(files)} file da utente {current_user.username}")
    
    processor = NormativeDocumentProcessor()
    vector_store = MultiLevelVectorStore()
    
    results = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"File saltato (non PDF): {file.filename}")
            continue
            
        file_path = UPLOAD_DIR / file.filename
        
        try:
            # Salva il file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File salvato: {file_path}")
            
            # Processa il file
            chunks = processor.process_normative_file(
                file_path=file_path,
                normative_level=normative_level,
                region=region,
                municipality=municipality
            )
            
            # Aggiungi al vector store
            # Mappa livello normativo a key del vector store
            store_level = normative_level # Deve corrispondere a keys in MultiLevelVectorStore
            if store_level not in ["nazionale", "regionale", "comunale"]:
                 store_level = "comunale" # Fallback
            
            ids = vector_store.add_documents(chunks, level=store_level)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "chunks": len(chunks),
                "ids_count": len(ids)
            })
            
        except Exception as e:
            logger.error(f"Errore processando {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
            
    return {"results": results}
