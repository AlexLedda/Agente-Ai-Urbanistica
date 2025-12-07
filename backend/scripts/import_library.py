import asyncio
import os
from pathlib import Path
from loguru import logger
from typing import List

from backend.rag.document_processor import NormativeDocumentProcessor
from backend.rag.vector_store import MultiLevelVectorStore

# Configurazione path
LIBRARY_DIR = Path("data/library")
DIRS = {
    "nazionale": LIBRARY_DIR / "nazionale",
    "regionale": LIBRARY_DIR / "regionale",
    "comunale": LIBRARY_DIR / "comunale"
}

async def import_library():
    """Importa tutti i documenti presenti nella cartella library."""
    logger.info("Avvio importazione libreria normativa...")
    
    processor = NormativeDocumentProcessor()
    vector_store = MultiLevelVectorStore()
    
    total_files = 0
    
    for level, dir_path in DIRS.items():
        if not dir_path.exists():
            logger.warning(f"Directory non trovata: {dir_path}")
            continue
            
        files = list(dir_path.glob("*.pdf"))
        if not files:
            logger.info(f"Nessun PDF trovato in {level}")
            continue
            
        logger.info(f"Trovati {len(files)} file in {level}")
        
        for file_path in files:
            try:
                logger.info(f"Processando: {file_path.name}")
                
                # Metadata base
                # Se è comunale, cerchiamo di indovinare il comune dal nome file o cartella
                # Per ora usiamo valori generici se non specificati
                municipality = None
                region = None
                
                if level == "comunale":
                    # Esempio banale: data/library/comunale/tarquinia_prg.pdf
                    # Potremmo implementare logica più smart qui
                    pass
                elif level == "regionale":
                    region = "Lazio" # Default per ora
                
                chunks = processor.process_normative_file(
                    file_path=file_path,
                    normative_level=level,
                    region=region,
                    municipality=municipality
                )
                
                ids = vector_store.add_documents(chunks, level=level)
                logger.success(f"Indicizzato {file_path.name}: {len(ids)} chunks")
                total_files += 1
                
            except Exception as e:
                logger.error(f"Errore su {file_path.name}: {e}")
                
    logger.info(f"Importazione completata. Totale file processati: {total_files}")

if __name__ == "__main__":
    # Configura logger per script
    import sys
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    asyncio.run(import_library())
