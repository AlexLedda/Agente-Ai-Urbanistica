import sys
import os
from pathlib import Path

# Aggiungi root al path
sys.path.insert(0, str(Path.cwd()))

from backend.scrapers.comune_scraper import create_montalto_scraper
from loguru import logger

def test_montalto():
    logger.info("Avvio test scraper Montalto...")
    
    # Test Montalto
    try:
        scraper_montalto = create_montalto_scraper()
        files = scraper_montalto.scrape()
        if files:
            logger.success(f"Montalto: Scaricati {len(files)} file")
        else:
            logger.warning("Montalto: Nessun file trovato")
    except Exception as e:
        logger.error(f"Errore Montalto: {e}")

if __name__ == "__main__":
    test_montalto()
