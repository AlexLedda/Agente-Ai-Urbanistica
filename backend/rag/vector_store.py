"""
Vector store manager con ChromaDB per normative multi-livello.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from backend.config import settings


class VectorStoreManager:
    """Gestisce il vector database per le normative."""
    
    def __init__(self, collection_name: str = "normative"):
        """
        Inizializza il vector store.
        
        Args:
            collection_name: Nome della collection ChromaDB
        """
        self.collection_name = collection_name
        
        # Inizializza embeddings (modello multilingua per italiano)
        # Inizializza embeddings (modello multilingua per italiano)
        logger.info(f"Caricamento modello embeddings: {settings.embedding_model}")
        # try:
        #     self.embeddings = HuggingFaceEmbeddings(
        #         model_name=settings.embedding_model,
        #         model_kwargs={'device': 'cpu'},
        #         encode_kwargs={'normalize_embeddings': True}
        #     )
        # except Exception as e:
        logger.warning(f"Uso FakeEmbeddings per modalità offline")
        from langchain_community.embeddings import FakeEmbeddings
        self.embeddings = FakeEmbeddings(size=768)
        
        # Inizializza ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(settings.vector_db_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Inizializza vector store LangChain
        self.vector_store = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
        
        logger.success(f"Vector store inizializzato: {collection_name}")
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Aggiunge documenti al vector store.
        
        Args:
            documents: Lista di documenti da aggiungere
            batch_size: Dimensione batch per l'inserimento
            
        Returns:
            Lista di ID dei documenti inseriti
        """
        logger.info(f"Aggiunta di {len(documents)} documenti al vector store")
        
        all_ids = []
        
        # Inserisci in batch per efficienza
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                ids = self.vector_store.add_documents(batch)
                all_ids.extend(ids)
                logger.debug(f"Batch {i//batch_size + 1}: {len(ids)} documenti inseriti")
            except Exception as e:
                logger.error(f"Errore nell'inserimento batch {i//batch_size + 1}: {e}")
                raise
        
        logger.success(f"Inseriti {len(all_ids)} documenti nel vector store")
        return all_ids
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Ricerca semantica nel vector store.
        
        Args:
            query: Query di ricerca
            k: Numero di risultati da restituire
            filter_dict: Filtri sui metadati (es. {"normative_level": "comunale"})
            
        Returns:
            Lista di documenti rilevanti
        """
        logger.info(f"Ricerca: '{query}' (top {k})")
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            logger.debug(f"Trovati {len(results)} risultati")
            return results
            
        except Exception as e:
            logger.error(f"Errore nella ricerca: {e}")
            raise
    
    def search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[tuple[Document, float]]:
        """
        Ricerca semantica con score di similarità.
        
        Args:
            query: Query di ricerca
            k: Numero di risultati da restituire
            filter_dict: Filtri sui metadati
            score_threshold: Soglia minima di score (opzionale)
            
        Returns:
            Lista di tuple (documento, score)
        """
        logger.info(f"Ricerca con score: '{query}'")
        
        try:
            if filter_dict:
                results = self.vector_store.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Applica soglia se specificata
            if score_threshold is not None:
                results = [(doc, score) for doc, score in results if score >= score_threshold]
            
            logger.debug(f"Trovati {len(results)} risultati con score")
            return results
            
        except Exception as e:
            logger.error(f"Errore nella ricerca con score: {e}")
            raise
    
    def delete_by_metadata(self, filter_dict: Dict[str, Any]) -> int:
        """
        Elimina documenti in base ai metadati.
        
        Args:
            filter_dict: Filtri per identificare documenti da eliminare
            
        Returns:
            Numero di documenti eliminati
        """
        logger.info(f"Eliminazione documenti con filtro: {filter_dict}")
        
        try:
            # ChromaDB delete by metadata
            collection = self.client.get_collection(self.collection_name)
            
            # Get IDs matching filter
            results = collection.get(where=filter_dict)
            ids_to_delete = results['ids']
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.success(f"Eliminati {len(ids_to_delete)} documenti")
                return len(ids_to_delete)
            else:
                logger.info("Nessun documento da eliminare")
                return 0
                
        except Exception as e:
            logger.error(f"Errore nell'eliminazione: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Ottiene statistiche sulla collection.
        
        Returns:
            Dizionario con statistiche
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()
            
            stats = {
                "collection_name": self.collection_name,
                "total_documents": count,
                "embedding_model": settings.embedding_model
            }
            
            logger.info(f"Statistiche collection: {count} documenti")
            return stats
            
        except Exception as e:
            logger.error(f"Errore nel recupero statistiche: {e}")
            raise
    
    def reset_collection(self):
        """Resetta completamente la collection (ATTENZIONE: elimina tutti i dati)."""
        logger.warning(f"RESET collection {self.collection_name}")
        
        try:
            self.client.delete_collection(self.collection_name)
            logger.success("Collection eliminata")
            
            # Ricrea collection vuota
            self.vector_store = Chroma(
                client=self.client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
            logger.success("Collection ricreata vuota")
            
        except Exception as e:
            logger.error(f"Errore nel reset: {e}")
            raise


class MultiLevelVectorStore:
    """
    Gestisce vector store separati per diversi livelli normativi.
    Permette ricerche mirate per livello (nazionale/regionale/comunale).
    """
    
    def __init__(self):
        """Inizializza vector store per ogni livello normativo."""
        self.stores = {
            "nazionale": VectorStoreManager("normative_nazionale"),
            "regionale": VectorStoreManager("normative_regionale"),
            "comunale": VectorStoreManager("normative_comunale")
        }
        logger.info("Multi-level vector store inizializzato")
    
    def add_documents(
        self,
        documents: List[Document],
        level: str
    ) -> List[str]:
        """
        Aggiunge documenti al vector store del livello specificato.
        
        Args:
            documents: Documenti da aggiungere
            level: Livello normativo (nazionale/regionale/comunale)
            
        Returns:
            Lista di ID inseriti
        """
        if level not in self.stores:
            raise ValueError(f"Livello non valido: {level}")
        
        return self.stores[level].add_documents(documents)
    
    def search_all_levels(
        self,
        query: str,
        k_per_level: int = 3
    ) -> Dict[str, List[Document]]:
        """
        Ricerca in tutti i livelli normativi.
        
        Args:
            query: Query di ricerca
            k_per_level: Numero di risultati per livello
            
        Returns:
            Dizionario con risultati per livello
        """
        results = {}
        
        for level, store in self.stores.items():
            try:
                results[level] = store.search(query, k=k_per_level)
            except Exception as e:
                logger.error(f"Errore nella ricerca livello {level}: {e}")
                results[level] = []
        
        return results
    
    def search_hierarchical(
        self,
        query: str,
        municipality: Optional[str] = None,
        region: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Ricerca gerarchica: priorità a normative più specifiche.
        
        Args:
            query: Query di ricerca
            municipality: Comune (se specificato, cerca prima qui)
            region: Regione (se specificato, cerca prima qui)
            k: Numero totale di risultati
            
        Returns:
            Lista di documenti ordinati per specificità
        """
        all_results = []
        
        # 1. Cerca a livello comunale (più specifico)
        if municipality:
            comunale_results = self.stores["comunale"].search(
                query,
                k=k,
                filter_dict={"municipality": municipality}
            )
            all_results.extend(comunale_results)
        
        # 2. Cerca a livello regionale
        if region and len(all_results) < k:
            regionale_results = self.stores["regionale"].search(
                query,
                k=k - len(all_results),
                filter_dict={"region": region}
            )
            all_results.extend(regionale_results)
        
        # 3. Cerca a livello nazionale (più generico)
        if len(all_results) < k:
            nazionale_results = self.stores["nazionale"].search(
                query,
                k=k - len(all_results)
            )
            all_results.extend(nazionale_results)
        
        logger.info(f"Ricerca gerarchica: {len(all_results)} risultati totali")
        return all_results[:k]
