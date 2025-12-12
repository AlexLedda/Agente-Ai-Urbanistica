from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from backend.api.deps import get_current_active_user
from backend.models.user import User
from backend.rag.retriever import NormativeRetriever
from backend.rag.vector_store import MultiLevelVectorStore
from backend.models.llm_router import LLMRouter, TaskType
from backend.config import PROMPT_TEMPLATES

from backend.agents.urban_compliance_agent import UrbanComplianceAgent
from functools import lru_cache

router = APIRouter()

@lru_cache()
def get_agent():
    return UrbanComplianceAgent()

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    municipality: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    agent: UrbanComplianceAgent = Depends(get_agent)
):
    """
    Endpoint per chat con assistente urbanistico.
    """
    logger.info(f"Chat request da {current_user.username}: {request.message}")
    
    try:
        # Usa l'agente per gestire la richiesta
        # L'agente gestisce internamente retrieval, location extraction e prompt comparativo
        response_text = agent.chat(
            request.message,
            context={
                "municipality": request.municipality,
                "province": request.province,
                "region": request.region
            }
        )
        
        # Recupera le fonti usate dall'ultima query del retriever dell'agente
        # Nota: Idealmente l'agente dovrebbe restituire anche le fonti. 
        # Per ora recuperiamo dal retriever dell'agente (l'ultima query)
        # TODO: Refactor agente per restituire oggetto strutturato con fonti
        sources = []
        # Questo è un accesso "sporco" allo stato, ma per ora funzionale
        if hasattr(agent, 'retriever') and hasattr(agent.retriever, 'last_retrieved_docs'):
             for doc in agent.retriever.last_retrieved_docs:
                sources.append({
                    "filename": doc.metadata.get("filename", "Sconosciuto"),
                    "page": doc.metadata.get("page", 0),
                    "normative_level": doc.metadata.get("normative_level", "Generico"),
                    "content_preview": doc.page_content[:200] + "..."
                })
                
    except Exception as e:
        logger.error(f"Errore chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    return ChatResponse(
        response=response_text,
        sources=sources
    )
