"""
Comparatore documenti per rilevamento difformità.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

from backend.vision.plan_analyzer import PlanimetriaAnalyzer
from backend.vision.photo_analyzer import PhotoAnalyzer
from backend.models.llm_router import LLMRouter, TaskType
from backend.models.prompt_templates import PromptTemplates


class DocumentComparator:
    """Comparatore multi-documento per rilevamento difformità."""
    
    def __init__(self):
        """Inizializza il comparatore."""
        self.plan_analyzer = PlanimetriaAnalyzer()
        self.photo_analyzer = PhotoAnalyzer()
        self.router = LLMRouter()
        logger.info("Document Comparator inizializzato")
    
    def compare_all_documents(
        self,
        planimetria_catastale: Optional[Path] = None,
        progetto_urbanistico: Optional[Path] = None,
        foto_immobile: Optional[List[Path]] = None,
        normative_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confronta tutti i documenti disponibili per rilevare difformità.
        
        Args:
            planimetria_catastale: Path planimetria catastale
            progetto_urbanistico: Path progetto urbanistico
            foto_immobile: Lista foto immobile
            normative_context: Contesto normativo
            
        Returns:
            Analisi completa con difformità rilevate
        """
        logger.info("Confronto completo documenti")
        
        results = {
            "planimetria_catastale_analysis": None,
            "progetto_urbanistico_analysis": None,
            "foto_analysis": None,
            "comparisons": {},
            "difformita": []
        }
        
        # Analizza planimetria catastale
        if planimetria_catastale:
            logger.info("Analisi planimetria catastale")
            results["planimetria_catastale_analysis"] = \
                self.plan_analyzer.analyze_layout(planimetria_catastale)
        
        # Analizza progetto urbanistico
        if progetto_urbanistico:
            logger.info("Analisi progetto urbanistico")
            results["progetto_urbanistico_analysis"] = \
                self.plan_analyzer.analyze_layout(progetto_urbanistico)
        
        # Analizza foto
        if foto_immobile:
            logger.info("Analisi foto immobile")
            results["foto_analysis"] = \
                self.photo_analyzer.detect_modifications(
                    foto_immobile,
                    results.get("planimetria_catastale_analysis")
                )
        
        # Confronti incrociati
        if planimetria_catastale and progetto_urbanistico:
            logger.info("Confronto planimetria catastale vs progetto")
            results["comparisons"]["catastale_vs_progetto"] = \
                self.plan_analyzer.compare_planimetrie(
                    planimetria_catastale,
                    progetto_urbanistico,
                    "catastale_vs_progetto"
                )
        
        if foto_immobile and planimetria_catastale:
            logger.info("Confronto foto vs planimetria")
            # Confronta prima foto con planimetria
            results["comparisons"]["foto_vs_planimetria"] = \
                self.photo_analyzer.compare_with_planimetria(
                    foto_immobile[0],
                    planimetria_catastale,
                    "facciata"
                )
        
        # Genera analisi difformità completa
        difformita_analysis = self._generate_difformita_report(
            results,
            normative_context
        )
        results["difformita"] = difformita_analysis
        
        logger.success("Confronto documenti completato")
        return results
    
    def _generate_difformita_report(
        self,
        analysis_results: Dict[str, Any],
        normative_context: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Genera report difformità basato su tutte le analisi.
        
        Args:
            analysis_results: Risultati delle analisi
            normative_context: Contesto normativo
            
        Returns:
            Lista di difformità rilevate
        """
        logger.info("Generazione report difformità")
        
        # Prepara contesto per LLM
        planimetria_info = ""
        if analysis_results.get("planimetria_catastale_analysis"):
            plan_data = analysis_results["planimetria_catastale_analysis"]
            planimetria_info = f"""
Planimetria Catastale:
- Stanze rilevate: {plan_data.get('rooms_detected', 'N/A')}
- Dati catastali: {plan_data.get('dimensions', {}).get('catasto_data', {})}
- Misure: {plan_data.get('dimensions', {}).get('ocr_measurements', [])}
"""
        
        progetto_info = ""
        if analysis_results.get("progetto_urbanistico_analysis"):
            prog_data = analysis_results["progetto_urbanistico_analysis"]
            progetto_info = f"""
Progetto Urbanistico:
- Stanze rilevate: {prog_data.get('rooms_detected', 'N/A')}
- Misure: {prog_data.get('dimensions', {}).get('ocr_measurements', [])}
"""
        
        foto_info = ""
        if analysis_results.get("foto_analysis"):
            foto_data = analysis_results["foto_analysis"]
            foto_info = f"""
Analisi Foto:
{foto_data.get('modifications_detected', 'N/A')}
"""
        
        # Usa prompt template per difformità
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.DIFFORMITA_DETECTION,
            planimetria=planimetria_info,
            progetto=progetto_info,
            foto=foto_info
        )
        
        if normative_context:
            prompt += f"\n\nNormative applicabili:\n{normative_context}"
        
        # Genera analisi con LLM
        difformita_text = self.router.analyze_with_best_model(
            prompt,
            TaskType.COMPLIANCE_CHECK,
            system_message=PromptTemplates.get_system_message("perito_tecnico")
        )
        
        # Parsing strutturato (semplificato)
        difformita_list = self._parse_difformita(difformita_text)
        
        logger.success(f"Rilevate {len(difformita_list)} difformità")
        return difformita_list
    
    def _parse_difformita(self, difformita_text: str) -> List[Dict[str, Any]]:
        """
        Parsing del testo difformità in struttura dati.
        
        Args:
            difformita_text: Testo analisi difformità
            
        Returns:
            Lista strutturata di difformità
        """
        # Parsing semplificato - in produzione usare parsing più sofisticato
        difformita_list = []
        
        # Cerca sezioni numerate
        import re
        sections = re.split(r'\n\d+\.\s+', difformita_text)
        
        for section in sections[1:]:  # Salta intestazione
            difformita = {
                "descrizione": section.strip(),
                "tipo": "da_classificare",
                "gravita": "da_valutare",
                "normativa_violata": None,
                "regolarizzabile": None
            }
            
            # Cerca indicatori di gravità
            if any(word in section.lower() for word in ["grave", "abuso", "demolizione"]):
                difformita["gravita"] = "grave"
            elif any(word in section.lower() for word in ["lieve", "sanabile", "cila"]):
                difformita["gravita"] = "lieve"
            else:
                difformita["gravita"] = "media"
            
            # Cerca tipo
            if "planimetri" in section.lower():
                difformita["tipo"] = "planimetrica"
            elif "struttura" in section.lower():
                difformita["tipo"] = "strutturale"
            elif "destinazione" in section.lower():
                difformita["tipo"] = "destinazione_uso"
            
            difformita_list.append(difformita)
        
        return difformita_list
    
    def generate_visual_comparison(
        self,
        planimetria1_path: Path,
        planimetria2_path: Path,
        output_path: Path
    ) -> Path:
        """
        Genera immagine di confronto visivo tra planimetrie.
        
        Args:
            planimetria1_path: Prima planimetria
            planimetria2_path: Seconda planimetria
            output_path: Path output immagine
            
        Returns:
            Path all'immagine generata
        """
        logger.info("Generazione confronto visivo")
        
        import cv2
        import numpy as np
        
        # Carica immagini
        img1 = cv2.imread(str(planimetria1_path))
        img2 = cv2.imread(str(planimetria2_path))
        
        # Ridimensiona alla stessa dimensione
        height = max(img1.shape[0], img2.shape[0])
        width = max(img1.shape[1], img2.shape[1])
        
        img1_resized = cv2.resize(img1, (width, height))
        img2_resized = cv2.resize(img2, (width, height))
        
        # Crea confronto side-by-side
        comparison = np.hstack([img1_resized, img2_resized])
        
        # Aggiungi etichette
        cv2.putText(
            comparison,
            "Planimetria 1",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )
        cv2.putText(
            comparison,
            "Planimetria 2",
            (width + 50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )
        
        # Salva
        cv2.imwrite(str(output_path), comparison)
        
        logger.success(f"Confronto visivo salvato: {output_path}")
        return output_path
