"""
Processore documenti normativi con chunking intelligente.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from loguru import logger

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredHTMLLoader,
    TextLoader
)
from langchain_core.documents import Document

from backend.config import CHUNKING_CONFIG


class NormativeDocumentProcessor:
    """Processore per documenti normativi."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNKING_CONFIG["chunk_size"],
            chunk_overlap=CHUNKING_CONFIG["chunk_overlap"],
            separators=CHUNKING_CONFIG["separators"],
            keep_separator=CHUNKING_CONFIG["keep_separator"]
        )
        
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Carica un documento normativo.
        
        Args:
            file_path: Path al file da caricare
            
        Returns:
            Lista di documenti LangChain
        """
        logger.info(f"Caricamento documento: {file_path}")
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif suffix in [".html", ".htm"]:
                loader = UnstructuredHTMLLoader(str(file_path))
            elif suffix == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                raise ValueError(f"Formato file non supportato: {suffix}")
            
            documents = loader.load()
            logger.success(f"Caricati {len(documents)} documenti da {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Errore nel caricamento di {file_path}: {e}")
            raise
    
    def extract_metadata(
        self,
        document: Document,
        normative_level: str,
        region: Optional[str] = None,
        province: Optional[str] = None,
        municipality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estrae metadati da un documento normativo.
        
        Args:
            document: Documento da cui estrarre metadati
            normative_level: Livello normativo (nazionale/regionale/comunale)
            region: Regione (per normative regionali/comunali)
            province: Provincia (per normative provinciali/comunali)
            municipality: Comune (per normative comunali)
            
        Returns:
            Dizionario con metadati estratti
        """
        metadata = {
            "normative_level": normative_level,
            "region": region,
            "province": province,
            "municipality": municipality,
            "processed_date": datetime.now().isoformat()
        }
        
        # Estrai numero articolo se presente
        text = document.page_content
        article_match = re.search(r'Art(?:icolo)?\s+(\d+)', text, re.IGNORECASE)
        if article_match:
            metadata["article"] = article_match.group(1)
        
        # Estrai riferimenti a leggi
        law_match = re.search(
            r'(L\.R\.|Legge Regionale|D\.P\.R\.|Decreto)\s+n?\s*(\d+)[/\s]+(\d{4})',
            text,
            re.IGNORECASE
        )
        if law_match:
            metadata["law_type"] = law_match.group(1)
            metadata["law_number"] = law_match.group(2)
            metadata["law_year"] = law_match.group(3)
        
        # Merge con metadati esistenti
        metadata.update(document.metadata)
        
        return metadata

    def chunk_document(
        self,
        document: Document,
        preserve_articles: bool = True
    ) -> List[Document]:
        """
        Divide un documento in chunk mantenendo la struttura degli articoli.
        
        Args:
            document: Documento da dividere
            preserve_articles: Se True, cerca di mantenere gli articoli integri
            
        Returns:
            Lista di chunk come documenti
        """
        if preserve_articles:
            # Prova a dividere per articoli
            chunks = self._split_by_articles(document)
            if chunks:
                logger.info(f"Documento diviso in {len(chunks)} articoli")
                return chunks
        
        # Fallback: chunking standard
        chunks = self.text_splitter.split_documents([document])
        logger.info(f"Documento diviso in {len(chunks)} chunk standard")
        return chunks
    
    def _split_by_articles(self, document: Document) -> List[Document]:
        """
        Divide un documento per articoli.
        
        Args:
            document: Documento da dividere
            
        Returns:
            Lista di documenti, uno per articolo
        """
        text = document.page_content
        
        # Pattern per identificare inizio articoli
        article_pattern = r'(Art(?:icolo)?\s+\d+[^\n]*)'
        
        # Trova tutti gli articoli
        matches = list(re.finditer(article_pattern, text, re.IGNORECASE))
        
        if len(matches) < 2:
            return []  # Non abbastanza articoli, usa chunking standard
        
        chunks = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            article_text = text[start:end].strip()
            
            # Se l'articolo è troppo lungo, dividilo ulteriormente
            if len(article_text) > CHUNKING_CONFIG["chunk_size"] * 1.5:
                sub_chunks = self.text_splitter.create_documents([article_text])
                for j, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.metadata = document.metadata.copy()
                    sub_chunk.metadata["article_part"] = j + 1
                    chunks.append(sub_chunk)
            else:
                chunk = Document(
                    page_content=article_text,
                    metadata=document.metadata.copy()
                )
                chunks.append(chunk)
        
        return chunks
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocessa il testo normativo.
        
        Args:
            text: Testo da preprocessare
            
        Returns:
            Testo preprocessato
        """
        # Rimuovi whitespace multipli
        text = re.sub(r'\s+', ' ', text)
        
        # Normalizza riferimenti ad articoli
        text = re.sub(r'art\.\s*', 'Articolo ', text, flags=re.IGNORECASE)
        
        # Normalizza riferimenti a commi
        text = re.sub(r'comma\s+', 'comma ', text, flags=re.IGNORECASE)
        
        # Rimuovi caratteri speciali problematici
        text = text.replace('\x00', '')
        
        return text.strip()
    
    def process_normative_file(
        self,
        file_path: Path,
        normative_level: str,
        region: Optional[str] = None,
        municipality: Optional[str] = None,
        province: Optional[str] = None
    ) -> List[Document]:
        """
        Processa completamente un file normativo.
        
        Args:
            file_path: Path al file
            normative_level: Livello normativo
            region: Regione (opzionale)
            municipality: Comune (opzionale)
            
        Returns:
            Lista di chunk processati e pronti per l'indicizzazione
        """
        logger.info(f"Inizio processing di {file_path.name}")
        
        # Carica documento
        documents = self.load_document(file_path)
        
        all_chunks = []
        for doc in documents:
            # Preprocessa testo
            doc.page_content = self.preprocess_text(doc.page_content)
            
            # Estrai metadati
            metadata = self.extract_metadata(
                doc,
                normative_level,
                region,
                municipality
            )
            doc.metadata = metadata
            
            # Chunking
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.success(
            f"Processing completato: {len(all_chunks)} chunk da {file_path.name}"
        )
        
        return all_chunks
    
    def process_directory(
        self,
        directory: Path,
        normative_level: str,
        region: Optional[str] = None,
        municipality: Optional[str] = None,
        recursive: bool = True
    ) -> List[Document]:
        """
        Processa tutti i file normativi in una directory.
        
        Args:
            directory: Directory da processare
            normative_level: Livello normativo
            region: Regione (opzionale)
            municipality: Comune (opzionale)
            recursive: Se True, processa anche le sottodirectory
            
        Returns:
            Lista di tutti i chunk processati
        """
        logger.info(f"Processing directory: {directory}")
        
        pattern = "**/*" if recursive else "*"
        all_chunks = []
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".html", ".htm", ".txt"]:
                try:
                    chunks = self.process_normative_file(
                        file_path,
                        normative_level,
                        region,
                        municipality
                    )
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Errore nel processing di {file_path}: {e}")
                    continue
        
        logger.success(
            f"Directory processing completato: {len(all_chunks)} chunk totali"
        )
        
        return all_chunks
