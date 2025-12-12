"""
Routes per analisi immobili.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from pathlib import Path
import uuid
from loguru import logger

from backend.agents.urban_compliance_agent import UrbanComplianceAgent
from backend.api.models.schemas import AnalysisRequest, AnalysisResponse
from backend.config import get_settings

router = APIRouter()

from functools import lru_cache
from fastapi import Depends

@lru_cache()
def get_agent():
    return UrbanComplianceAgent()

# Storage analisi in corso
analyses = {}


@router.post("/new", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    """
    Crea una nuova analisi di conformità.
    
    Args:
        request: Dati richiesta analisi
        
    Returns:
        ID analisi e stato
    """
    logger.info(f"Nuova analisi per {request.municipality}")
    
    # Genera ID
    analysis_id = str(uuid.uuid4())
    
    # Salva in storage
    analyses[analysis_id] = {
        "id": analysis_id,
        "municipality": request.municipality,
        "region": request.region,
        "status": "created",
        "documents": {},
        "result": None
    }
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="created",
        message="Analisi creata. Carica i documenti per procedere."
    )


@router.post("/{analysis_id}/upload")
async def upload_documents(
    analysis_id: str,
    planimetria_catastale: Optional[UploadFile] = File(None),
    progetto_urbanistico: Optional[UploadFile] = File(None),
    foto_immobile: Optional[List[UploadFile]] = File(None)
):
    """
    Upload documenti per un'analisi.
    
    Args:
        analysis_id: ID analisi
        planimetria_catastale: Planimetria catastale
        progetto_urbanistico: Progetto urbanistico
        foto_immobile: Lista foto immobile
        
    Returns:
        Stato upload
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
    
    logger.info(f"Upload documenti per analisi {analysis_id}")
    
    # Directory upload per questa analisi
    settings = get_settings()
    upload_dir = settings.upload_path / analysis_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = {}
    
    # Salva planimetria catastale
    if planimetria_catastale:
        plan_path = upload_dir / f"planimetria_catastale_{planimetria_catastale.filename}"
        with plan_path.open("wb") as f:
            content = await planimetria_catastale.read()
            f.write(content)
        uploaded_files["planimetria_catastale"] = str(plan_path)
        logger.info(f"Salvata planimetria: {plan_path}")
    
    # Salva progetto
    if progetto_urbanistico:
        prog_path = upload_dir / f"progetto_{progetto_urbanistico.filename}"
        with prog_path.open("wb") as f:
            content = await progetto_urbanistico.read()
            f.write(content)
        uploaded_files["progetto_urbanistico"] = str(prog_path)
        logger.info(f"Salvato progetto: {prog_path}")
    
    # Salva foto
    if foto_immobile:
        foto_paths = []
        for i, foto in enumerate(foto_immobile):
            foto_path = upload_dir / f"foto_{i}_{foto.filename}"
            with foto_path.open("wb") as f:
                content = await foto.read()
                f.write(content)
            foto_paths.append(str(foto_path))
        uploaded_files["foto_immobile"] = foto_paths
        logger.info(f"Salvate {len(foto_paths)} foto")
    
    # Aggiorna analisi
    analyses[analysis_id]["documents"] = uploaded_files
    analyses[analysis_id]["status"] = "documents_uploaded"
    
    return {
        "analysis_id": analysis_id,
        "status": "documents_uploaded",
        "uploaded_files": list(uploaded_files.keys())
    }


@router.post("/{analysis_id}/run")
async def run_analysis(
    analysis_id: str,
    agent: UrbanComplianceAgent = Depends(get_agent)
):
    """
    Esegue l'analisi.
    
    Args:
        analysis_id: ID analisi
        
    Returns:
        Risultati analisi
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
    
    analysis_data = analyses[analysis_id]
    
    if analysis_data["status"] != "documents_uploaded":
        raise HTTPException(
            status_code=400,
            detail="Documenti non ancora caricati"
        )
    
    logger.info(f"Esecuzione analisi {analysis_id}")
    
    # Aggiorna stato
    analyses[analysis_id]["status"] = "running"
    
    try:
        # Prepara path documenti
        docs = analysis_data["documents"]
        planimetria = Path(docs["planimetria_catastale"]) if "planimetria_catastale" in docs else None
        progetto = Path(docs["progetto_urbanistico"]) if "progetto_urbanistico" in docs else None
        foto = [Path(f) for f in docs.get("foto_immobile", [])]
        
        # Esegui analisi
        result = agent.analyze_property(
            municipality=analysis_data["municipality"],
            region=analysis_data["region"],
            planimetria_catastale=planimetria,
            progetto_urbanistico=progetto,
            foto_immobile=foto if foto else None
        )
        
        # Salva risultato
        analyses[analysis_id]["result"] = result
        analyses[analysis_id]["status"] = "completed"
        
        logger.success(f"Analisi {analysis_id} completata")
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Errore nell'analisi {analysis_id}: {e}")
        analyses[analysis_id]["status"] = "error"
        analyses[analysis_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """
    Ottiene lo stato di un'analisi.
    
    Args:
        analysis_id: ID analisi
        
    Returns:
        Stato analisi
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
    
    analysis = analyses[analysis_id]
    
    return {
        "analysis_id": analysis_id,
        "status": analysis["status"],
        "municipality": analysis["municipality"],
        "region": analysis["region"]
    }


@router.get("/{analysis_id}/report")
async def get_analysis_report(analysis_id: str):
    """
    Ottiene il report di un'analisi.
    
    Args:
        analysis_id: ID analisi
        
    Returns:
        Report completo
    """
    if analysis_id not in analyses:
        raise HTTPException(status_code=404, detail="Analisi non trovata")
    
    analysis = analyses[analysis_id]
    
    if analysis["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analisi non completata (stato: {analysis['status']})"
        )
    
    return analysis["result"]["report"]
