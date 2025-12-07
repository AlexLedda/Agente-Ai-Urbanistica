"""
Analizzatore planimetrie con computer vision e AI.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import cv2
import numpy as np

from backend.vision.ocr_processor import OCRProcessor
from backend.models.llm_router import VisionAnalyzer, LLMRouter
from backend.models.prompt_templates import PromptTemplates


class PlanimetriaAnalyzer:
    """Analizzatore specializzato per planimetrie."""
    
    def __init__(self):
        """Inizializza l'analizzatore."""
        self.ocr = OCRProcessor()
        self.router = LLMRouter()
        self.vision = VisionAnalyzer(self.router)
        logger.info("Planimetria Analyzer inizializzato")
    
    def detect_rooms(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Rileva stanze e ambienti nella planimetria usando computer vision.
        
        Args:
            image_path: Path alla planimetria
            
        Returns:
            Lista di stanze rilevate con coordinate
        """
        logger.info("Rilevamento stanze con computer vision")
        
        # Carica immagine
        img = cv2.imread(str(image_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Rileva contorni (stanze)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        rooms = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filtra contorni troppo piccoli (rumore)
            if area < 1000:
                continue
            
            # Calcola bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calcola centro
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w//2, y + h//2
            
            rooms.append({
                "id": i,
                "bbox": {"x": x, "y": y, "width": w, "height": h},
                "center": {"x": cx, "y": cy},
                "area_pixels": area,
                "contour": contour.tolist()
            })
        
        logger.success(f"Rilevate {len(rooms)} stanze")
        return rooms
    
    def extract_dimensions(self, image_path: Path) -> Dict[str, Any]:
        """
        Estrae dimensioni dalla planimetria combinando OCR e vision AI.
        
        Args:
            image_path: Path alla planimetria
            
        Returns:
            Dizionario con dimensioni estratte
        """
        logger.info("Estrazione dimensioni")
        
        # OCR per testo e misure
        ocr_data = self.ocr.process_planimetria(image_path)
        
        # Vision AI per analisi semantica
        prompt = PromptTemplates.PLANIMETRIA_ANALYSIS
        vision_analysis = self.vision.analyze_image(
            str(image_path),
            prompt,
            detail_level="high"
        )
        
        return {
            "ocr_measurements": ocr_data["measurements"],
            "catasto_data": ocr_data["catasto_data"],
            "ai_analysis": vision_analysis,
            "raw_ocr_text": ocr_data["raw_text"]
        }
    
    def analyze_layout(self, image_path: Path) -> Dict[str, Any]:
        """
        Analizza il layout completo della planimetria.
        
        Args:
            image_path: Path alla planimetria
            
        Returns:
            Analisi completa del layout
        """
        logger.info(f"Analisi layout planimetria: {image_path}")
        
        # Rileva stanze con CV
        rooms = self.detect_rooms(image_path)
        
        # Estrai dimensioni e dati
        dimensions = self.extract_dimensions(image_path)
        
        # Analisi AI completa
        ai_analysis = dimensions["ai_analysis"]
        
        result = {
            "rooms_detected": len(rooms),
            "rooms": rooms,
            "dimensions": dimensions,
            "layout_analysis": ai_analysis,
            "image_path": str(image_path)
        }
        
        logger.success("Analisi layout completata")
        return result
    
    def compare_planimetrie(
        self,
        planimetria1_path: Path,
        planimetria2_path: Path,
        comparison_type: str = "catastale_vs_progetto"
    ) -> Dict[str, Any]:
        """
        Confronta due planimetrie per rilevare differenze.
        
        Args:
            planimetria1_path: Prima planimetria
            planimetria2_path: Seconda planimetria
            comparison_type: Tipo di confronto
            
        Returns:
            Risultati del confronto
        """
        logger.info(f"Confronto planimetrie: {comparison_type}")
        
        # Analizza entrambe
        layout1 = self.analyze_layout(planimetria1_path)
        layout2 = self.analyze_layout(planimetria2_path)
        
        # Confronto con Vision AI
        comparison_prompt = f"""Confronta queste due planimetrie e identifica le differenze:

Planimetria 1 ({comparison_type.split('_')[0]}):
- Stanze rilevate: {layout1['rooms_detected']}
- Dati: {layout1['dimensions']['catasto_data']}

Planimetria 2 ({comparison_type.split('_')[-1]}):
- Stanze rilevate: {layout2['rooms_detected']}
- Dati: {layout2['dimensions']['catasto_data']}

Identifica:
1. Differenze nel numero di stanze
2. Modifiche dimensionali
3. Aperture aggiunte/rimosse
4. Cambi di destinazione d'uso
5. Modifiche strutturali

Fornisci un'analisi dettagliata delle difformità."""

        ai_comparison = self.vision.compare_images(
            str(planimetria1_path),
            str(planimetria2_path),
            comparison_prompt
        )
        
        # Confronto numerico stanze
        room_diff = layout2['rooms_detected'] - layout1['rooms_detected']
        
        result = {
            "planimetria1": layout1,
            "planimetria2": layout2,
            "room_difference": room_diff,
            "ai_comparison": ai_comparison,
            "comparison_type": comparison_type
        }
        
        logger.success("Confronto completato")
        return result
    
    def calculate_indices(
        self,
        layout_data: Dict[str, Any],
        lotto_superficie: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calcola indici urbanistici dalla planimetria.
        
        Args:
            layout_data: Dati layout da analyze_layout
            lotto_superficie: Superficie lotto in mq (opzionale)
            
        Returns:
            Indici urbanistici calcolati
        """
        logger.info("Calcolo indici urbanistici")
        
        # Estrai superfici dalle misure OCR
        measurements = layout_data["dimensions"]["ocr_measurements"]
        
        # Cerca superficie totale
        superficie_totale = None
        for m in measurements:
            if m.get("unit") in ["mq", "m²"]:
                try:
                    superficie_totale = float(m["value"].replace(",", "."))
                    break
                except:
                    continue
        
        indices = {
            "superficie_utile": superficie_totale,
            "numero_vani": layout_data["rooms_detected"]
        }
        
        # Calcola indici se abbiamo superficie lotto
        if lotto_superficie and superficie_totale:
            indices["rapporto_copertura"] = superficie_totale / lotto_superficie
            indices["superficie_lotto"] = lotto_superficie
        
        logger.debug(f"Indici calcolati: {indices}")
        return indices
