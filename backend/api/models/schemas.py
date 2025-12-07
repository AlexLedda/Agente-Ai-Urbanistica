"""
Pydantic schemas per API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Richiesta creazione analisi."""
    municipality: str = Field(..., description="Comune")
    region: str = Field(default="Lazio", description="Regione")
    property_type: Optional[str] = Field(None, description="Tipologia immobile")
    property_info: Optional[Dict[str, Any]] = Field(None, description="Info aggiuntive")


class AnalysisResponse(BaseModel):
    """Risposta creazione analisi."""
    analysis_id: str = Field(..., description="ID analisi")
    status: str = Field(..., description="Stato analisi")
    message: Optional[str] = Field(None, description="Messaggio")


class DocumentUpload(BaseModel):
    """Metadata upload documento."""
    filename: str
    file_type: str
    size: int


class NormativeQuery(BaseModel):
    """Query ricerca normative."""
    query: str = Field(..., description="Query di ricerca")
    municipality: Optional[str] = Field(None, description="Comune")
    region: str = Field(default="Lazio", description="Regione")
    top_k: int = Field(default=5, description="Numero risultati")


class NormativeResult(BaseModel):
    """Risultato ricerca normativa."""
    content: str
    metadata: Dict[str, Any]


class ComplianceReport(BaseModel):
    """Report di conformità."""
    analysis_id: str
    municipality: str
    region: str
    generation_date: datetime
    difformita_count: int
    content: str
    format: str = "markdown"


class DifformitaItem(BaseModel):
    """Singola difformità rilevata."""
    tipo: str = Field(..., description="Tipo difformità")
    descrizione: str = Field(..., description="Descrizione")
    gravita: str = Field(..., description="Gravità (lieve/media/grave)")
    normativa_violata: Optional[str] = Field(None, description="Normativa violata")
    regolarizzabile: Optional[bool] = Field(None, description="Se regolarizzabile")


class AnalysisResult(BaseModel):
    """Risultato completo analisi."""
    analysis_id: str
    municipality: str
    region: str
    status: str
    difformita: List[DifformitaItem]
    report: ComplianceReport
    created_at: datetime
    completed_at: Optional[datetime] = None
