"""
Routes per normative.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from backend.rag.vector_store import MultiLevelVectorStore
from backend.rag.retriever import NormativeRetriever

router = APIRouter()

# Istanze (singleton)
vector_store = MultiLevelVectorStore()
retriever = NormativeRetriever(vector_store)


@router.get("/search")
async def search_normative(
    query: str = Query(..., description="Query di ricerca"),
    municipality: Optional[str] = Query(None, description="Comune"),
    region: Optional[str] = Query("Lazio", description="Regione"),
    top_k: int = Query(5, description="Numero risultati")
):
    """
    Cerca normative urbanistiche.
    
    Args:
        query: Query di ricerca
        municipality: Comune (opzionale)
        region: Regione
        top_k: Numero di risultati
        
    Returns:
        Normative rilevanti
    """
    logger.info(f"Ricerca normative: {query}")
    
    try:
        # Recupera documenti
        docs = retriever.retrieve(
            query,
            municipality=municipality,
            region=region,
            top_k=top_k
        )
        
        # Formatta risultati
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata
            })
        
        # Citazioni
        citations = retriever.get_citations(docs)
        
        return {
            "query": query,
            "results": results,
            "citations": citations,
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Errore nella ricerca: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/updates")
async def get_normative_updates():
    """
    Ottiene ultimi aggiornamenti normativi.
    
    Returns:
        Lista aggiornamenti
    """
    logger.info("Richiesta aggiornamenti normativi")
    
    # TODO: implementare sistema di tracking aggiornamenti
    return {
        "updates": [],
        "message": "Sistema di tracking aggiornamenti in sviluppo"
    }


@router.post("/refresh")
async def refresh_normative():
    """
    Trigger aggiornamento normative (esegue scraper).
    
    Returns:
        Stato aggiornamento
    """
    logger.info("Refresh normative richiesto")
    
    try:
        from backend.scrapers.testo_unico_scraper import TestoUnicoScraper
        from backend.scrapers.regione_lazio_scraper import RegioneLazioScraper
        from backend.scrapers.comune_scraper import (
            create_tarquinia_scraper,
            create_montalto_scraper
        )
        
        scrapers = [
            TestoUnicoScraper(),
            RegioneLazioScraper(),
            create_tarquinia_scraper(),
            create_montalto_scraper()
        ]
        
        downloaded_files = []
        for scraper in scrapers:
            try:
                files = scraper.scrape()
                downloaded_files.extend(files)
            except Exception as e:
                logger.error(f"Errore con scraper {scraper.name}: {e}")
        
        return {
            "status": "completed",
            "files_downloaded": len(downloaded_files),
            "message": f"Scaricati {len(downloaded_files)} file normativi"
        }
        
    except Exception as e:
        logger.error(f"Errore nel refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_normative_stats():
    """
    Statistiche sul database normative.
    
    Returns:
        Statistiche
    """
    try:
        stats = {}
        for level, store in vector_store.stores.items():
            stats[level] = store.get_collection_stats()
        
        return {
            "stats": stats,
            "total_documents": sum(s["total_documents"] for s in stats.values())
        }
        
    except Exception as e:
        logger.error(f"Errore nel recupero statistiche: {e}")
        raise HTTPException(status_code=500, detail=str(e))
