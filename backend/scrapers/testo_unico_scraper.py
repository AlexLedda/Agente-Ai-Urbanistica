"""
Scraper per Testo Unico dell'Edilizia (DPR 380/2001).
"""
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from backend.scrapers.base_scraper import BaseScraper


class TestoUnicoScraper(BaseScraper):
    """Scraper per il Testo Unico Edilizia da Normattiva."""
    
    def __init__(self):
        super().__init__("testo_unico")
        self.base_url = "https://www.normattiva.it"
        self.testo_unico_url = (
            "https://www.normattiva.it/uri-res/N2Ls?"
            "urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-06;380"
        )
    
    def scrape(self) -> List[Path]:
        """
        Scarica il Testo Unico dell'Edilizia.
        
        Returns:
            Lista di file scaricati
        """
        logger.info("Scraping Testo Unico Edilizia (DPR 380/2001)")
        
        downloaded_files = []
        
        # Fetch pagina principale
        response = self.fetch_url(self.testo_unico_url)
        if not response:
            logger.error("Impossibile scaricare Testo Unico")
            return downloaded_files
        
        soup = self.parse_html(response.text)
        
        # Salva HTML
        html_file = self.save_document(
            response.text,
            "testo_unico_edilizia_dpr_380_2001.html",
            metadata={
                "source": "Normattiva",
                "law": "DPR 380/2001",
                "title": "Testo Unico Edilizia",
                "download_date": str(datetime.now().date())
            }
        )
        downloaded_files.append(html_file)
        
        # Cerca link al PDF se disponibile
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        for link in pdf_links:
            pdf_url = link.get('href')
            if not pdf_url.startswith('http'):
                pdf_url = self.base_url + pdf_url
            
            pdf_file = self.download_pdf(
                pdf_url,
                "testo_unico_edilizia_dpr_380_2001.pdf"
            )
            if pdf_file:
                downloaded_files.append(pdf_file)
                break
        
        logger.success(f"Scaricati {len(downloaded_files)} file per Testo Unico")
        return downloaded_files
    
    def check_updates(self) -> List[Dict[str, Any]]:
        """
        Controlla aggiornamenti al Testo Unico.
        
        Returns:
            Lista di aggiornamenti
        """
        logger.info("Controllo aggiornamenti Testo Unico")
        
        # Fetch pagina
        response = self.fetch_url(self.testo_unico_url)
        if not response:
            return []
        
        soup = self.parse_html(response.text)
        
        # Cerca indicazioni di modifiche/aggiornamenti
        updates = []
        
        # Cerca sezione "Modifiche"
        modifiche_section = soup.find(text=lambda x: x and 'modific' in x.lower())
        if modifiche_section:
            updates.append({
                "type": "modification",
                "description": "Rilevate possibili modifiche",
                "url": self.testo_unico_url,
                "check_date": str(datetime.now().date())
            })
        
        return updates


from datetime import datetime
