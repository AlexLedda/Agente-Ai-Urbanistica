import asyncio
import shutil
from pathlib import Path
from loguru import logger
from backend.scrapers.testo_unico_scraper import TestoUnicoScraper

async def run():
    logger.info("Avvio download Testo Unico...")
    scraper = TestoUnicoScraper()
    files = scraper.scrape()
    
    # Destinazione library
    dest_dir = Path("data/library/nazionale")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for file_path in files:
        if file_path.suffix.lower() == '.pdf':
            dest_path = dest_dir / file_path.name
            shutil.copy2(file_path, dest_path)
            logger.info(f"Copiato {file_path.name} in {dest_dir}")
            count += 1
            
    if count == 0:
        logger.warning("Nessun PDF scaricato. Controllo se ci sono HTML utili...")
        # Fallback: se non c'è PDF, usiamo HTML (ma il processore preferisce PDF)
        # Per ora ci limitiamo al warning
    else:
        logger.success(f"Pronto per import: {count} file in {dest_dir}")

if __name__ == "__main__":
    asyncio.run(run())
