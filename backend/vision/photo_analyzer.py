"""
Analizzatore foto immobili per rilevamento difformità.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

from backend.models.llm_router import VisionAnalyzer, LLMRouter
from backend.models.prompt_templates import PromptTemplates


class PhotoAnalyzer:
    """Analizzatore foto immobili con AI vision."""
    
    def __init__(self):
        """Inizializza l'analizzatore."""
        self.router = LLMRouter()
        self.vision = VisionAnalyzer(self.router)
        logger.info("Photo Analyzer inizializzato")
    
    def analyze_single_photo(
        self,
        photo_path: Path,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analizza una singola foto dell'immobile.
        
        Args:
            photo_path: Path alla foto
            context: Contesto aggiuntivo (es. "facciata principale")
            
        Returns:
            Analisi della foto
        """
        logger.info(f"Analisi foto: {photo_path}")
        
        # Prepara prompt
        prompt = PromptTemplates.PHOTO_ANALYSIS
        if context:
            prompt = f"Contesto: {context}\n\n{prompt}"
        
        # Analisi con vision AI
        analysis = self.vision.analyze_image(
            str(photo_path),
            prompt,
            detail_level="high"
        )
        
        return {
            "photo_path": str(photo_path),
            "context": context,
            "analysis": analysis
        }
    
    def analyze_photo_set(
        self,
        photo_paths: List[Path],
        contexts: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analizza un set di foto dell'immobile.
        
        Args:
            photo_paths: Lista di path alle foto
            contexts: Contesti per ogni foto (opzionale)
            
        Returns:
            Lista di analisi
        """
        logger.info(f"Analisi set di {len(photo_paths)} foto")
        
        if contexts is None:
            contexts = [None] * len(photo_paths)
        
        analyses = []
        for photo_path, context in zip(photo_paths, contexts):
            try:
                analysis = self.analyze_single_photo(photo_path, context)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Errore nell'analisi di {photo_path}: {e}")
                analyses.append({
                    "photo_path": str(photo_path),
                    "context": context,
                    "error": str(e)
                })
        
        logger.success(f"Analizzate {len(analyses)} foto")
        return analyses
    
    def detect_modifications(
        self,
        photo_paths: List[Path],
        planimetria_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rileva modifiche e potenziali abusi dalle foto.
        
        Args:
            photo_paths: Foto dell'immobile
            planimetria_info: Info dalla planimetria per confronto
            
        Returns:
            Modifiche rilevate
        """
        logger.info("Rilevamento modifiche da foto")
        
        # Analizza tutte le foto
        photo_analyses = self.analyze_photo_set(photo_paths)
        
        # Prompt per rilevamento modifiche
        combined_analysis = "\n\n".join([
            f"Foto {i+1}: {a.get('analysis', a.get('error', 'N/A'))}"
            for i, a in enumerate(photo_analyses)
        ])
        
        planimetria_context = ""
        if planimetria_info:
            planimetria_context = f"""
Informazioni dalla planimetria catastale:
- Stanze: {planimetria_info.get('rooms_detected', 'N/A')}
- Superficie: {planimetria_info.get('dimensions', {}).get('ocr_measurements', 'N/A')}
- Dati catastali: {planimetria_info.get('dimensions', {}).get('catasto_data', 'N/A')}
"""
        
        detection_prompt = f"""Analizza le seguenti foto dell'immobile e rileva potenziali modifiche o abusi edilizi.

{planimetria_context}

Analisi foto:
{combined_analysis}

Identifica:
1. Chiusure di balconi/verande
2. Aperture modificate (finestre, porte)
3. Ampliamenti o sopraelevazioni
4. Cambi destinazione d'uso visibili
5. Installazioni non autorizzate
6. Modifiche strutturali evidenti

Per ogni modifica rilevata, specifica:
- Tipo di modifica
- Livello di certezza (alto/medio/basso)
- Potenziale gravità
- Necessità di verifica tecnica"""
        
        from langchain.schema import HumanMessage
        modification_analysis = self.router.gpt4_turbo.invoke([
            HumanMessage(content=detection_prompt)
        ]).content
        
        return {
            "photo_analyses": photo_analyses,
            "modifications_detected": modification_analysis,
            "total_photos": len(photo_paths)
        }
    
    def compare_with_planimetria(
        self,
        photo_path: Path,
        planimetria_path: Path,
        element_type: str = "facciata"
    ) -> Dict[str, Any]:
        """
        Confronta una foto con la planimetria.
        
        Args:
            photo_path: Foto dell'immobile
            planimetria_path: Planimetria
            element_type: Tipo di elemento da confrontare
            
        Returns:
            Risultati del confronto
        """
        logger.info(f"Confronto foto-planimetria: {element_type}")
        
        comparison_prompt = f"""Confronta questa foto dell'immobile con la planimetria.

Elemento da verificare: {element_type}

Verifica:
1. Corrispondenza numero e posizione aperture (finestre/porte)
2. Corrispondenza dimensioni e proporzioni
3. Elementi presenti in foto ma non in planimetria
4. Elementi in planimetria ma non visibili in foto
5. Modifiche evidenti

Fornisci un'analisi dettagliata delle corrispondenze e discrepanze."""
        
        comparison = self.vision.compare_images(
            str(photo_path),
            str(planimetria_path),
            comparison_prompt
        )
        
        return {
            "photo_path": str(photo_path),
            "planimetria_path": str(planimetria_path),
            "element_type": element_type,
            "comparison": comparison
        }
    
    def assess_compliance(
        self,
        photo_analyses: List[Dict[str, Any]],
        normative_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valuta la conformità basandosi sulle foto analizzate.
        
        Args:
            photo_analyses: Analisi delle foto
            normative_context: Contesto normativo applicabile
            
        Returns:
            Valutazione di conformità
        """
        logger.info("Valutazione conformità da foto")
        
        # Combina tutte le analisi
        combined = "\n\n".join([
            f"Foto {i+1}: {a.get('analysis', 'N/A')}"
            for i, a in enumerate(photo_analyses)
        ])
        
        normative_section = ""
        if normative_context:
            normative_section = f"\nNormative applicabili:\n{normative_context}\n"
        
        assessment_prompt = f"""Basandoti sulle analisi delle foto, valuta la conformità dell'immobile.

{normative_section}
Analisi foto:
{combined}

Valuta:
1. Conformità estetica e decoro urbano
2. Rispetto vincoli paesaggistici (se applicabili)
3. Conformità regolamento edilizio
4. Potenziali violazioni rilevabili visivamente

Per ogni aspetto, fornisci:
- Valutazione (CONFORME / DUBBIO / NON CONFORME)
- Motivazione
- Normativa di riferimento (se nota)
- Raccomandazioni"""
        
        from langchain.schema import HumanMessage
        assessment = self.router.claude.invoke([
            HumanMessage(content=assessment_prompt)
        ]).content
        
        return {
            "compliance_assessment": assessment,
            "photos_analyzed": len(photo_analyses),
            "normative_context_provided": normative_context is not None
        }
