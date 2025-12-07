from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from loguru import logger

from backend.api.deps import get_current_active_user
from backend.models.user import User
from backend.rag.retriever import NormativeRetriever
from backend.rag.vector_store import MultiLevelVectorStore
from backend.models.llm_router import LLMRouter, TaskType
from backend.config import settings, PROMPT_TEMPLATES

router = APIRouter()

# Istanze (singleton)
vector_store = MultiLevelVectorStore()
retriever = NormativeRetriever(vector_store)
llm_router = LLMRouter()

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    municipality: Optional[str] = None
    region: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint per chat con assistente urbanistico.
    """
    logger.info(f"Chat request da {current_user.username}: {request.message}")
    
    try:
        # 1. Retrieval
        # Cerca documenti rilevanti nel vector store
        docs = retriever.retrieve(
            query=request.message,
            municipality=request.municipality,
            region=request.region,
            top_k=3
        )
        
        # Estrai contesto e sorgenti
        context_text = "\n\n".join([doc.page_content for doc in docs])
        sources = []
        for doc in docs:
            sources.append({
                "filename": doc.metadata.get("filename", "Sconosciuto"),
                "page": doc.metadata.get("page", 0),
                "normative_level": doc.metadata.get("level", "Sconosciuto"),
                "content_preview": doc.page_content[:200] + "..."
            })
            
        # 2. Generazione Risposta con LLM
        # Costruisci prompt con contesto
        system_prompt = PROMPT_TEMPLATES["normative_query"].format(
            context=context_text,
            question=request.message
        )
        
        # Chiamata LLM
        try:
            response_text = llm_router.analyze_with_best_model(
                prompt=request.message,
                task_type=TaskType.NORMATIVE_ANALYSIS,
                system_message=system_prompt
            )
        except Exception as e:
            logger.warning(f"LLM fallito: {e}. Fallback a modalità offline.")
            response_text = (
                "**Modalità Offline**: Non posso generare una risposta completa perché "
                "il servizio di intelligenza artificiale non è raggiungibile o configurato.\n\n"
                "Tuttavia, ho trovato questi documenti rilevanti che potrebbero contenere la risposta:\n\n"
            )
            for src in sources:
                response_text += f"- **{src['filename']}** (Pag. {src.get('page', '?')})\n"
                
    except Exception as e:
        logger.error(f"Errore chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    return ChatResponse(
        response=response_text,
        sources=sources
    )
