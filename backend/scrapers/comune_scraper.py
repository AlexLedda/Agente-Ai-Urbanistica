"""
Scraper configurabile per comuni.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from backend.scrapers.base_scraper import BaseScraper


class ComuneScraper(BaseScraper):
    """Scraper configurabile per normative comunali."""
    
    def __init__(
        self,
        comune_name: str,
        website_url: str,
        prg_url: Optional[str] = None,
        regolamento_url: Optional[str] = None
    ):
        """
        Inizializza scraper per un comune.
        
        Args:
            comune_name: Nome del comune
            website_url: URL sito web comunale
            prg_url: URL Piano Regolatore Generale (opzionale)
            regolamento_url: URL Regolamento Edilizio (opzionale)
        """
        super().__init__(f"comune_{comune_name.lower().replace(' ', '_')}")
        self.comune_name = comune_name
        self.website_url = website_url
        self.prg_url = prg_url
        self.regolamento_url = regolamento_url
    
    def scrape(self) -> List[Path]:
        """
        Scarica normative comunali.
        
        Returns:
            Lista di file scaricati
        """
        logger.info(f"Scraping normative Comune di {self.comune_name}")
        
        downloaded_files = []
        
        # Scarica PRG se URL disponibile
        if self.prg_url:
            prg_files = self._scrape_prg()
            downloaded_files.extend(prg_files)
        
        # Scarica Regolamento Edilizio se URL disponibile
        if self.regolamento_url:
            reg_files = self._scrape_regolamento()
            downloaded_files.extend(reg_files)
        
        # Se non ci sono URL specifici, cerca nella sezione urbanistica
        if not self.prg_url and not self.regolamento_url:
            generic_files = self._scrape_urbanistica_section()
            downloaded_files.extend(generic_files)
        
        logger.success(
            f"Scaricati {len(downloaded_files)} file per Comune di {self.comune_name}"
        )
        return downloaded_files
    
    def _scrape_prg(self) -> List[Path]:
        """Scarica Piano Regolatore Generale."""
        logger.info(f"Download PRG - {self.comune_name}")
        
        downloaded_files = []
        
        response = self.fetch_url(self.prg_url)
        if not response:
            return downloaded_files
        
        # Salva HTML
        html_file = self.save_document(
            response.text,
            f"prg_{self.comune_name.lower().replace(' ', '_')}.html",
            metadata={
                "source": f"Comune di {self.comune_name}",
                "type": "Piano Regolatore Generale",
                "municipality": self.comune_name,
                "region": "Lazio",
                "download_date": str(datetime.now().date()),
                "url": self.prg_url
            }
        )
        downloaded_files.append(html_file)
        
        # Cerca PDF allegati
        soup = self.parse_html(response.text)
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        
        for i, link in enumerate(pdf_links[:10]):  # Max 10 PDF
            pdf_url = link.get('href')
            if not pdf_url.startswith('http'):
                # URL relativo
                from urllib.parse import urljoin
                pdf_url = urljoin(self.prg_url, pdf_url)
            
            pdf_file = self.download_pdf(
                pdf_url,
                f"prg_{self.comune_name.lower().replace(' ', '_')}_{i+1}.pdf"
            )
            if pdf_file:
                downloaded_files.append(pdf_file)
        
        return downloaded_files
    
    def _scrape_regolamento(self) -> List[Path]:
        """Scarica Regolamento Edilizio Comunale."""
        logger.info(f"Download Regolamento Edilizio - {self.comune_name}")
        
        downloaded_files = []
        
        response = self.fetch_url(self.regolamento_url)
        if not response:
            return downloaded_files
        
        # Salva HTML
        html_file = self.save_document(
            response.text,
            f"regolamento_edilizio_{self.comune_name.lower().replace(' ', '_')}.html",
            metadata={
                "source": f"Comune di {self.comune_name}",
                "type": "Regolamento Edilizio Comunale",
                "municipality": self.comune_name,
                "region": "Lazio",
                "download_date": str(datetime.now().date()),
                "url": self.regolamento_url
            }
        )
        downloaded_files.append(html_file)
        
        # Cerca PDF
        soup = self.parse_html(response.text)
        pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())
        
        for i, link in enumerate(pdf_links[:5]):
            pdf_url = link.get('href')
            if not pdf_url.startswith('http'):
                from urllib.parse import urljoin
                pdf_url = urljoin(self.regolamento_url, pdf_url)
            
            pdf_file = self.download_pdf(
                pdf_url,
                f"regolamento_edilizio_{self.comune_name.lower().replace(' ', '_')}_{i+1}.pdf"
            )
            if pdf_file:
                downloaded_files.append(pdf_file)
        
        return downloaded_files
    
    def _scrape_urbanistica_section(self) -> List[Path]:
        """Cerca e scarica dalla sezione urbanistica generica."""
        logger.info(f"Ricerca sezione urbanistica - {self.comune_name}")
        
        downloaded_files = []
        
        # Prova URL comuni per sezione urbanistica
        possible_urls = [
            f"{self.website_url}/urbanistica",
            f"{self.website_url}/servizi/urbanistica",
            f"{self.website_url}/area-urbanistica",
        ]
        
        for url in possible_urls:
            response = self.fetch_url(url)
            if response and response.status_code == 200:
                # Trovata sezione urbanistica
                html_file = self.save_document(
                    response.text,
                    f"urbanistica_{self.comune_name.lower().replace(' ', '_')}.html",
                    metadata={
                        "source": f"Comune di {self.comune_name}",
                        "type": "Sezione Urbanistica",
                        "municipality": self.comune_name,
                        "region": "Lazio",
                        "download_date": str(datetime.now().date()),
                        "url": url
                    }
                )
                downloaded_files.append(html_file)
                break
        
        return downloaded_files
    
    def check_updates(self) -> List[Dict[str, Any]]:
        """
        Controlla aggiornamenti normativi comunali.
        
        Returns:
            Lista di aggiornamenti
        """
        logger.info(f"Controllo aggiornamenti Comune di {self.comune_name}")
        
        updates = []
        
        # Controlla PRG
        if self.prg_url:
            response = self.fetch_url(self.prg_url)
            if response:
                # Cerca date di modifica
                soup = self.parse_html(response.text)
                date_text = soup.find(text=lambda x: x and 'aggiorn' in x.lower())
                if date_text:
                    updates.append({
                        "type": "prg_update",
                        "description": f"Possibile aggiornamento PRG {self.comune_name}",
                        "url": self.prg_url,
                        "check_date": str(datetime.now().date())
                    })
        
        return updates


# Factory per comuni specifici
def create_tarquinia_scraper() -> ComuneScraper:
    """Crea scraper per Comune di Tarquinia."""
    return ComuneScraper(
        comune_name="Tarquinia",
        website_url="https://www.comune.tarquinia.vt.it",
        # URL da configurare con quelli reali
        prg_url=None,
        regolamento_url=None
    )


def create_montalto_scraper() -> ComuneScraper:
    """Crea scraper per Comune di Montalto di Castro."""
    return ComuneScraper(
        comune_name="Montalto di Castro",
        website_url="https://www.comune.montaldodicastro.vt.it",
        # URL da configurare con quelli reali
        prg_url=None,
        regolamento_url=None
    )
