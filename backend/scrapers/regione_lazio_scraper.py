"""
Scraper per normative Regione Lazio.
"""
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

from backend.scrapers.base_scraper import BaseScraper


class RegioneLazioScraper(BaseScraper):
    """Scraper per normative urbanistiche Regione Lazio."""
    
    def __init__(self):
        super().__init__("regione_lazio")
        self.bur_url = "https://www.regione.lazio.it/bur"
        self.urbanistica_url = "https://www.regione.lazio.it/rl_urbanistica"
    
    def scrape(self) -> List[Path]:
        """
        Scarica normative urbanistiche Regione Lazio.
        
        Returns:
            Lista di file scaricati
        """
        logger.info("Scraping normative Regione Lazio")
        
        downloaded_files = []
        
        # Scarica legge regionale principale (LR 38/1999)
        lr_38_file = self._scrape_lr_38_1999()
        if lr_38_file:
            downloaded_files.append(lr_38_file)
        
        # Scarica ultimi BUR con contenuti urbanistici
        bur_files = self._scrape_recent_bur()
        downloaded_files.extend(bur_files)
        
        logger.success(f"Scaricati {len(downloaded_files)} file Regione Lazio")
        return downloaded_files
    
    def _scrape_lr_38_1999(self) -> Path:
        """Scarica LR 38/1999 - Norme sul governo del territorio."""
        logger.info("Download LR 38/1999")
        
        # URL diretto alla legge (da verificare/aggiornare)
        lr_url = "https://www.regione.lazio.it/rl_urbanistica/?vw=leggiRegionali"
        
        response = self.fetch_url(lr_url)
        if not response:
            logger.warning("Impossibile scaricare LR 38/1999")
            return None
        
        # Salva HTML
        html_file = self.save_document(
            response.text,
            "lr_38_1999_governo_territorio.html",
            metadata={
                "source": "Regione Lazio",
                "law": "LR 38/1999",
                "title": "Norme sul governo del territorio",
                "region": "Lazio",
                "download_date": str(datetime.now().date())
            }
        )
        
        return html_file
    
    def _scrape_recent_bur(self, num_issues: int = 5) -> List[Path]:
        """
        Scarica ultimi numeri del BUR con contenuti urbanistici.
        
        Args:
            num_issues: Numero di BUR da scaricare
            
        Returns:
            Lista di file scaricati
        """
        logger.info(f"Download ultimi {num_issues} BUR")
        
        downloaded_files = []
        
        response = self.fetch_url(self.bur_url)
        if not response:
            return downloaded_files
        
        soup = self.parse_html(response.text)
        
        # Cerca link ai BUR (struttura da adattare al sito reale)
        bur_links = soup.find_all('a', href=lambda x: x and 'bur' in x.lower())
        
        for i, link in enumerate(bur_links[:num_issues]):
            bur_url = link.get('href')
            if not bur_url.startswith('http'):
                bur_url = "https://www.regione.lazio.it" + bur_url
            
            bur_response = self.fetch_url(bur_url)
            if bur_response:
                filename = f"bur_lazio_{i+1}.html"
                file_path = self.save_document(
                    bur_response.text,
                    filename,
                    metadata={
                        "source": "BUR Lazio",
                        "region": "Lazio",
                        "download_date": str(datetime.now().date()),
                        "url": bur_url
                    }
                )
                downloaded_files.append(file_path)
        
        return downloaded_files
    
    def check_updates(self) -> List[Dict[str, Any]]:
        """
        Controlla aggiornamenti normativi Regione Lazio.
        
        Returns:
            Lista di aggiornamenti
        """
        logger.info("Controllo aggiornamenti Regione Lazio")
        
        updates = []
        
        # Controlla ultimo BUR
        response = self.fetch_url(self.bur_url)
        if response:
            soup = self.parse_html(response.text)
            
            # Cerca data ultimo BUR
            date_elements = soup.find_all(text=lambda x: x and '202' in x)
            if date_elements:
                updates.append({
                    "type": "bur_update",
                    "description": "Nuovo BUR disponibile",
                    "url": self.bur_url,
                    "check_date": str(datetime.now().date())
                })
        
        return updates
