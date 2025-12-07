"""
Tool per verifica conformità.
"""
from typing import Dict, Any
from loguru import logger

from backend.rag.retriever import NormativeRetriever
from backend.vision.comparator import DocumentComparator


class ComplianceChecker:
    """Tool per verifica conformità urbanistica."""
    
    def __init__(
        self,
        retriever: NormativeRetriever,
        comparator: DocumentComparator
    ):
        """
        Inizializza il checker.
        
        Args:
            retriever: Retriever normative
            comparator: Comparatore documenti
        """
        self.retriever = retriever
        self.comparator = comparator
        logger.info("Compliance Checker inizializzato")
    
    def check(self, data: Dict[str, Any]) -> str:
        """
        Verifica conformità.
        
        Args:
            data: Dati immobile e documenti
            
        Returns:
            Risultato verifica
        """
        logger.info("Verifica conformità")
        
        municipality = data.get("municipality")
        region = data.get("region", "Lazio")
        
        # Recupera normative
        normative_docs = self.retriever.retrieve(
            "conformità urbanistica regolamento edilizio",
            municipality=municipality,
            region=region,
            top_k=5
        )
        
        normative_context = self.retriever.format_context(normative_docs)
        
        # Risultato
        result = f"=== VERIFICA CONFORMITÀ ===\n\n"
        result += f"Comune: {municipality}\n"
        result += f"Regione: {region}\n\n"
        result += f"Normative applicabili:\n{normative_context[:500]}...\n\n"
        result += "Per una verifica completa, fornire planimetrie e foto dell'immobile.\n"
        
        return result
