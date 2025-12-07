"""
Processore OCR per estrazione testo da documenti tecnici.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger
import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr

from backend.config import settings


class OCRProcessor:
    """Processore OCR con supporto multi-engine."""
    
    def __init__(self, primary_engine: str = "easyocr"):
        """
        Inizializza il processore OCR.
        
        Args:
            primary_engine: Engine primario ("easyocr" o "tesseract")
        """
        self.primary_engine = primary_engine
        
        # Inizializza EasyOCR per italiano
        if primary_engine == "easyocr":
            logger.info("Inizializzazione EasyOCR per italiano")
            self.reader = easyocr.Reader(['it', 'en'], gpu=False)
        
        logger.success(f"OCR Processor inizializzato con {primary_engine}")
    
    def preprocess_image(
        self,
        image_path: Path,
        enhance: bool = True
    ) -> np.ndarray:
        """
        Preprocessa l'immagine per migliorare l'OCR.
        
        Args:
            image_path: Path all'immagine
            enhance: Se True, applica enhancement
            
        Returns:
            Immagine preprocessata come array numpy
        """
        logger.debug(f"Preprocessing immagine: {image_path}")
        
        # Carica immagine
        img = cv2.imread(str(image_path))
        
        if img is None:
            raise ValueError(f"Impossibile caricare immagine: {image_path}")
        
        if not enhance:
            return img
        
        # Converti in grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Riduci rumore
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Aumenta contrasto (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Binarizzazione adattiva
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        logger.debug("Preprocessing completato")
        return binary
    
    def extract_text_easyocr(
        self,
        image: np.ndarray,
        detail_level: int = 0
    ) -> Dict[str, Any]:
        """
        Estrae testo con EasyOCR.
        
        Args:
            image: Immagine preprocessata
            detail_level: 0=solo testo, 1=con coordinate
            
        Returns:
            Dizionario con testo e metadati
        """
        logger.info("Estrazione testo con EasyOCR")
        
        results = self.reader.readtext(image, detail=detail_level)
        
        # Estrai testo
        if detail_level == 0:
            text = " ".join(results)
        else:
            # Con coordinate
            text_blocks = []
            for bbox, text, confidence in results:
                text_blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
            
            text = " ".join([block["text"] for block in text_blocks])
        
        return {
            "text": text,
            "engine": "easyocr",
            "blocks": text_blocks if detail_level > 0 else None
        }
    
    def extract_text_tesseract(
        self,
        image: np.ndarray,
        lang: str = "ita+eng"
    ) -> Dict[str, Any]:
        """
        Estrae testo con Tesseract.
        
        Args:
            image: Immagine preprocessata
            lang: Lingue per OCR
            
        Returns:
            Dizionario con testo e metadati
        """
        logger.info("Estrazione testo con Tesseract")
        
        # Configurazione Tesseract
        custom_config = r'--oem 3 --psm 6'
        
        # Estrai testo
        text = pytesseract.image_to_string(
            image,
            lang=lang,
            config=custom_config
        )
        
        # Estrai anche dati dettagliati
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            config=custom_config,
            output_type=pytesseract.Output.DICT
        )
        
        return {
            "text": text,
            "engine": "tesseract",
            "data": data
        }
    
    def extract_text(
        self,
        image_path: Path,
        preprocess: bool = True,
        fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Estrae testo da un'immagine con fallback automatico.
        
        Args:
            image_path: Path all'immagine
            preprocess: Se True, preprocessa l'immagine
            fallback: Se True, usa engine alternativo in caso di errore
            
        Returns:
            Dizionario con testo estratto e metadati
        """
        logger.info(f"Estrazione testo da: {image_path}")
        
        # Preprocessa immagine
        if preprocess:
            image = self.preprocess_image(image_path, enhance=True)
        else:
            image = cv2.imread(str(image_path))
        
        # Prova con engine primario
        try:
            if self.primary_engine == "easyocr":
                result = self.extract_text_easyocr(image, detail_level=1)
            else:
                result = self.extract_text_tesseract(image)
            
            logger.success(f"Estratto testo: {len(result['text'])} caratteri")
            return result
            
        except Exception as e:
            logger.warning(f"Errore con {self.primary_engine}: {e}")
            
            if not fallback:
                raise
            
            # Fallback su engine alternativo
            logger.info("Tentativo con engine alternativo")
            try:
                if self.primary_engine == "easyocr":
                    result = self.extract_text_tesseract(image)
                else:
                    result = self.extract_text_easyocr(image, detail_level=0)
                
                logger.success("Estrazione completata con fallback")
                return result
                
            except Exception as e2:
                logger.error(f"Errore anche con fallback: {e2}")
                raise
    
    def extract_measurements(self, text: str) -> List[Dict[str, Any]]:
        """
        Estrae misure e dimensioni dal testo OCR.
        
        Args:
            text: Testo da cui estrarre misure
            
        Returns:
            Lista di misure trovate
        """
        import re
        
        measurements = []
        
        # Pattern per misure (es: "3.50 m", "350 cm", "3,50 mt")
        patterns = [
            r'(\d+[.,]\d+)\s*(m|mt|metri|cm|centimetri)',
            r'(\d+)\s*x\s*(\d+[.,]?\d*)\s*(m|mt|cm)',  # es: "3 x 4.5 m"
            r'h\s*[=:]?\s*(\d+[.,]?\d*)\s*(m|mt|cm)',  # altezza
            r'(\d+[.,]\d+)\s*mq|m²',  # superficie
            r'(\d+[.,]\d+)\s*mc|m³'   # volume
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                measurements.append({
                    "value": match.group(1),
                    "unit": match.group(2) if len(match.groups()) > 1 else None,
                    "full_match": match.group(0)
                })
        
        logger.debug(f"Trovate {len(measurements)} misure")
        return measurements
    
    def extract_catasto_data(self, text: str) -> Dict[str, Optional[str]]:
        """
        Estrae dati catastali dal testo OCR.
        
        Args:
            text: Testo da cui estrarre dati catastali
            
        Returns:
            Dizionario con dati catastali
        """
        import re
        
        catasto_data = {
            "foglio": None,
            "particella": None,
            "subalterno": None,
            "categoria": None,
            "classe": None,
            "rendita": None
        }
        
        # Pattern per dati catastali
        foglio_match = re.search(r'foglio\s*[:\s]*(\d+)', text, re.IGNORECASE)
        if foglio_match:
            catasto_data["foglio"] = foglio_match.group(1)
        
        part_match = re.search(r'particella\s*[:\s]*(\d+)', text, re.IGNORECASE)
        if part_match:
            catasto_data["particella"] = part_match.group(1)
        
        sub_match = re.search(r'sub(?:alterno)?\s*[:\s]*(\d+)', text, re.IGNORECASE)
        if sub_match:
            catasto_data["subalterno"] = sub_match.group(1)
        
        cat_match = re.search(r'categoria\s*[:\s]*([A-F]/\d+)', text, re.IGNORECASE)
        if cat_match:
            catasto_data["categoria"] = cat_match.group(1)
        
        logger.debug(f"Dati catastali estratti: {catasto_data}")
        return catasto_data
    
    def process_planimetria(self, image_path: Path) -> Dict[str, Any]:
        """
        Processa una planimetria estraendo testo e dati strutturati.
        
        Args:
            image_path: Path alla planimetria
            
        Returns:
            Dizionario con tutti i dati estratti
        """
        logger.info(f"Processing planimetria: {image_path}")
        
        # Estrai testo
        ocr_result = self.extract_text(image_path, preprocess=True)
        text = ocr_result["text"]
        
        # Estrai informazioni strutturate
        measurements = self.extract_measurements(text)
        catasto_data = self.extract_catasto_data(text)
        
        result = {
            "raw_text": text,
            "measurements": measurements,
            "catasto_data": catasto_data,
            "ocr_engine": ocr_result["engine"],
            "image_path": str(image_path)
        }
        
        logger.success("Planimetria processata")
        return result
