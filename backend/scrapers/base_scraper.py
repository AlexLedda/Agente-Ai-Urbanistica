"""
Classe base per web scraper di normative.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from loguru import logger

from backend.config import settings


class BaseScraper(ABC):
    """Classe base astratta per scraper normative."""
    
    def __init__(self, name: str):
        """
        Inizializza lo scraper.
        
        Args:
            name: Nome dello scraper
        """
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.scraper_user_agent
        })
        self.delay = settings.scraper_delay
        self.max_retries = settings.scraper_max_retries
        
        logger.info(f"Scraper inizializzato: {name}")
    
    def fetch_url(
        self,
        url: str,
        retry_count: int = 0
    ) -> Optional[requests.Response]:
        """
        Fetch URL con retry logic.
        
        Args:
            url: URL da fetchare
            retry_count: Contatore retry
            
        Returns:
            Response o None se fallisce
        """
        try:
            logger.debug(f"Fetching: {url}")
            time.sleep(self.delay)  # Rate limiting
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response
            
        except requests.RequestException as e:
            logger.warning(f"Errore nel fetch di {url}: {e}")
            
            if retry_count < self.max_retries:
                logger.info(f"Retry {retry_count + 1}/{self.max_retries}")
                time.sleep(self.delay * 2)  # Backoff
                return self.fetch_url(url, retry_count + 1)
            else:
                logger.error(f"Fallito dopo {self.max_retries} tentativi")
                return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parsing HTML con BeautifulSoup.
        
        Args:
            html: HTML da parsare
            
        Returns:
            Oggetto BeautifulSoup
        """
        return BeautifulSoup(html, 'lxml')
    
    def save_document(
        self,
        content: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Salva documento scaricato.
        
        Args:
            content: Contenuto del documento
            filename: Nome file
            metadata: Metadati opzionali
            
        Returns:
            Path al file salvato
        """
        # Crea directory per questo scraper
        scraper_dir = settings.normative_data_path / self.name
        scraper_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva contenuto
        file_path = scraper_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        # Salva metadati se forniti
        if metadata:
            import json
            metadata_path = file_path.with_suffix('.meta.json')
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        
        logger.success(f"Documento salvato: {file_path}")
        return file_path
    
    def download_pdf(self, url: str, filename: str) -> Optional[Path]:
        """
        Download PDF.
        
        Args:
            url: URL del PDF
            filename: Nome file di destinazione
            
        Returns:
            Path al PDF scaricato o None
        """
        logger.info(f"Download PDF: {url}")
        
        response = self.fetch_url(url)
        if not response:
            return None
        
        # Verifica che sia un PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower():
            logger.warning(f"Content-Type non è PDF: {content_type}")
        
        # Salva
        scraper_dir = settings.normative_data_path / self.name
        scraper_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = scraper_dir / filename
        file_path.write_bytes(response.content)
        
        logger.success(f"PDF salvato: {file_path}")
        return file_path
    
    @abstractmethod
    def scrape(self) -> List[Path]:
        """
        Metodo principale di scraping (da implementare nelle sottoclassi).
        
        Returns:
            Lista di file scaricati
        """
        pass
    
    @abstractmethod
    def check_updates(self) -> List[Dict[str, Any]]:
        """
        Controlla se ci sono aggiornamenti (da implementare nelle sottoclassi).
        
        Returns:
            Lista di aggiornamenti disponibili
        """
        pass
