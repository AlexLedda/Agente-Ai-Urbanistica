"""
Tool per consultazione normative.
"""
from typing import Dict, Any
from loguru import logger

from backend.rag.retriever import NormativeRetriever


class NormativeTool:
    """Tool per ricerca e consultazione normative."""
    
    def __init__(self, retriever: NormativeRetriever):
        """
        Inizializza il tool.
        
        Args:
            retriever: Retriever normative
        """
        self.retriever = retriever
        logger.info("Normative Tool inizializzato")
    
    def search(self, query: str, **kwargs) -> str:
        """
        Cerca normative rilevanti.
        
        Args:
            query: Query di ricerca
            **kwargs: Parametri aggiuntivi (municipality, region, ecc.)
            
        Returns:
            Normative formattate
        """
        logger.info(f"Ricerca normative: {query}")
        
        # Estrai parametri
        municipality = kwargs.get("municipality")
        region = kwargs.get("region")
        top_k = kwargs.get("top_k", 5)
        
        # Recupera documenti
        docs = self.retriever.retrieve(
            query,
            municipality=municipality,
            region=region,
            top_k=top_k
        )
        
        # Formatta risultati
        if not docs:
            return "Nessuna normativa trovata per la query specificata."
        
        result = self.retriever.format_context(docs)
        
        # Aggiungi citazioni
        citations = self.retriever.get_citations(docs)
        citations_text = "\n\nCitazioni:\n"
        for i, cit in enumerate(citations, 1):
            citations_text += f"{i}. {cit.get('law', 'N/A')} - {cit.get('level', 'N/A')}\n"
        
        return result + citations_text
