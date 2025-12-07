"""
Tool per analisi documenti.
"""
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

from backend.vision.comparator import DocumentComparator


class AnalysisTool:
    """Tool per analisi documenti tecnici."""
    
    def __init__(self, comparator: DocumentComparator):
        """
        Inizializza il tool.
        
        Args:
            comparator: Comparatore documenti
        """
        self.comparator = comparator
        logger.info("Analysis Tool inizializzato")
    
    def analyze(self, documents: Dict[str, Any]) -> str:
        """
        Analizza documenti forniti.
        
        Args:
            documents: Dizionario con path ai documenti
            
        Returns:
            Analisi formattata
        """
        logger.info("Analisi documenti")
        
        # Estrai path
        planimetria_catastale = documents.get("planimetria_catastale")
        progetto_urbanistico = documents.get("progetto_urbanistico")
        foto_immobile = documents.get("foto_immobile", [])
        
        # Converti stringhe in Path
        if planimetria_catastale:
            planimetria_catastale = Path(planimetria_catastale)
        if progetto_urbanistico:
            progetto_urbanistico = Path(progetto_urbanistico)
        if foto_immobile:
            foto_immobile = [Path(f) for f in foto_immobile]
        
        # Analizza
        analysis = self.comparator.compare_all_documents(
            planimetria_catastale=planimetria_catastale,
            progetto_urbanistico=progetto_urbanistico,
            foto_immobile=foto_immobile if foto_immobile else None
        )
        
        # Formatta risultati
        result = "=== ANALISI DOCUMENTI ===\n\n"
        
        if analysis.get("planimetria_catastale_analysis"):
            plan_data = analysis["planimetria_catastale_analysis"]
            result += f"Planimetria Catastale:\n"
            result += f"- Stanze rilevate: {plan_data.get('rooms_detected', 'N/A')}\n"
            result += f"- Dati catastali: {plan_data.get('dimensions', {}).get('catasto_data', {})}\n\n"
        
        if analysis.get("difformita"):
            result += f"Difformità rilevate: {len(analysis['difformita'])}\n"
            for i, diff in enumerate(analysis['difformita'][:5], 1):  # Max 5
                result += f"{i}. {diff.get('descrizione', 'N/A')[:200]}...\n"
        
        return result
