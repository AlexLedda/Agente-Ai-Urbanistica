"""
Sistema di retrieval avanzato per normative.
Implementa hybrid search e re-ranking.
"""
from typing import List, Dict, Any, Optional
from loguru import logger

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import BM25Retriever
from langchain_openai import ChatOpenAI

from backend.rag.vector_store import MultiLevelVectorStore
from backend.config import settings, RETRIEVAL_CONFIG


class NormativeRetriever:
    """Retriever avanzato per normative con hybrid search e re-ranking."""
    
    def __init__(self, vector_store: MultiLevelVectorStore):
        """
        Inizializza il retriever.
        
        Args:
            vector_store: Vector store multi-livello
        """
        self.vector_store = vector_store
        self.config = RETRIEVAL_CONFIG
        
        # LLM per re-ranking (opzionale)
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        logger.info("Normative retriever inizializzato")
    
    def retrieve(
        self,
        query: str,
        municipality: Optional[str] = None,
        region: Optional[str] = None,
        province: Optional[str] = None,
        normative_level: Optional[str] = None,
        top_k: Optional[int] = None,
        use_rerank: Optional[bool] = None
    ) -> List[Document]:
        """
        Recupera documenti normativi rilevanti.
        
        Args:
            query: Query di ricerca
            municipality: Comune per ricerca gerarchica
            region: Regione per ricerca gerarchica
            province: Provincia per ricerca gerarchica
            normative_level: Livello specifico (se None, cerca gerarchicamente)
            top_k: Numero di risultati (default da config)
            use_rerank: Se True, applica re-ranking (default da config)
            
        Returns:
            Lista di documenti rilevanti ordinati per rilevanza
        """
        top_k = top_k or self.config["top_k"]
        use_rerank = use_rerank if use_rerank is not None else self.config["rerank"]
        
        logger.info(f"Retrieve: '{query}' (top_k={top_k}, rerank={use_rerank})")
        
        # Ricerca base
        if normative_level:
            # Ricerca su livello specifico
            documents = self._search_specific_level(
                query,
                normative_level,
                municipality,
                region,
                province,
                top_k
            )
        else:
            # Ricerca gerarchica
            documents = self.vector_store.search_hierarchical(
                query,
                municipality=municipality,
                region=region,
                province=province,
                k=top_k * 2  # Recupera più documenti per il re-ranking
            )
        
        # Hybrid search (combina semantico + keyword)
        if self.config["hybrid_search"]:
            documents = self._hybrid_search(query, documents, top_k)
        
        # Re-ranking
        if use_rerank and len(documents) > top_k:
            documents = self._rerank_documents(query, documents, top_k)
        
        # Filtra per score threshold
        if self.config["score_threshold"]:
            documents = self._filter_by_score(documents)
        
        logger.success(f"Recuperati {len(documents)} documenti rilevanti")
        return documents[:top_k]
    
    def _search_specific_level(
        self,
        query: str,
        level: str,
        municipality: Optional[str],
        region: Optional[str],
        province: Optional[str],
        k: int
    ) -> List[Document]:
        """Ricerca su un livello normativo specifico."""
        filter_dict = {}
        
        if municipality and level == "comunale":
            filter_dict["municipality"] = municipality
        elif province and (level in ["regionale", "provinciale", "comunale"]):
             filter_dict["province"] = province
        elif region and (level in ["regionale", "provinciale", "comunale"]):
            filter_dict["region"] = region
        
        # Map provinciale to regionale store
        target_store = level
        if level == "provinciale":
            target_store = "regionale"
            
        store = self.vector_store.stores.get(target_store)
        if not store:
             logger.warning(f"Livello store {level} non trovato, uso default nazionale")
             store = self.vector_store.stores["nazionale"]

        
        if filter_dict:
            return store.search(query, k=k, filter_dict=filter_dict)
        else:
            return store.search(query, k=k)
    
    def _hybrid_search(
        self,
        query: str,
        semantic_results: List[Document],
        top_k: int
    ) -> List[Document]:
        """
        Combina ricerca semantica con keyword search.
        
        Args:
            query: Query originale
            semantic_results: Risultati da ricerca semantica
            top_k: Numero di risultati finali
            
        Returns:
            Risultati combinati
        """
        # Estrai keyword dalla query
        keywords = self._extract_keywords(query)
        
        # Score semantico (normalizzato)
        semantic_scores = {
            i: 1.0 - (i / len(semantic_results))
            for i in range(len(semantic_results))
        }
        
        # Score keyword
        keyword_scores = {}
        for i, doc in enumerate(semantic_results):
            score = self._keyword_match_score(doc.page_content, keywords)
            keyword_scores[i] = score
        
        # Combina score
        keyword_weight = self.config["keyword_weight"]
        semantic_weight = 1.0 - keyword_weight
        
        combined_scores = {
            i: (semantic_weight * semantic_scores[i] + 
                keyword_weight * keyword_scores[i])
            for i in range(len(semantic_results))
        }
        
        # Ordina per score combinato
        sorted_indices = sorted(
            combined_scores.keys(),
            key=lambda i: combined_scores[i],
            reverse=True
        )
        
        return [semantic_results[i] for i in sorted_indices[:top_k]]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Estrae keyword rilevanti dalla query."""
        # Rimuovi stopwords italiane comuni
        stopwords = {
            'il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una',
            'di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra',
            'è', 'sono', 'sia', 'come', 'quale', 'quali', 'che', 'cosa'
        }
        
        words = query.lower().split()
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        return keywords
    
    def _keyword_match_score(self, text: str, keywords: List[str]) -> float:
        """Calcola score di match per keyword."""
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        
        return matches / len(keywords)
    
    def _rerank_documents(
        self,
        query: str,
        documents: List[Document],
        top_k: int
    ) -> List[Document]:
        """
        Re-ranking dei documenti usando LLM.
        
        Args:
            query: Query originale
            documents: Documenti da re-rankare
            top_k: Numero di documenti finali
            
        Returns:
            Documenti re-rankati
        """
        logger.debug(f"Re-ranking {len(documents)} documenti")
        
        try:
            # Usa LLMChainExtractor per compressione contestuale
            compressor = LLMChainExtractor.from_llm(self.llm)
            
            # Crea retriever base (mock)
            from langchain.retrievers import BaseRetriever
            
            class MockRetriever(BaseRetriever):
                def __init__(self, docs):
                    self.docs = docs
                
                def _get_relevant_documents(self, query: str) -> List[Document]:
                    return self.docs
            
            base_retriever = MockRetriever(documents)
            
            # Applica compressione
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=base_retriever
            )
            
            reranked = compression_retriever.get_relevant_documents(query)
            
            logger.debug(f"Re-ranking completato: {len(reranked)} documenti")
            return reranked[:top_k]
            
        except Exception as e:
            logger.warning(f"Errore nel re-ranking, uso ordine originale: {e}")
            return documents[:top_k]
    
    def _filter_by_score(self, documents: List[Document]) -> List[Document]:
        """Filtra documenti sotto la soglia di score."""
        # Nota: questo richiede che i documenti abbiano score nei metadata
        threshold = self.config["score_threshold"]
        
        filtered = [
            doc for doc in documents
            if doc.metadata.get("score", 1.0) >= threshold
        ]
        
        if len(filtered) < len(documents):
            logger.debug(
                f"Filtrati {len(documents) - len(filtered)} documenti "
                f"sotto soglia {threshold}"
            )
        
        return filtered
    
    def format_context(self, documents: List[Document]) -> str:
        """
        Formatta i documenti recuperati come contesto per LLM.
        
        Args:
            documents: Documenti da formattare
            
        Returns:
            Stringa formattata con contesto
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            
            # Costruisci riferimento normativo
            ref_parts = []
            
            if metadata.get("law_type") and metadata.get("law_number"):
                ref_parts.append(
                    f"{metadata['law_type']} {metadata['law_number']}/{metadata.get('law_year', '')}"
                )
            
            if metadata.get("article"):
                ref_parts.append(f"Art. {metadata['article']}")
            
            level = metadata.get("normative_level", "")
            if level == "comunale" and metadata.get("municipality"):
                ref_parts.append(f"Comune di {metadata['municipality']}")
            elif level == "regionale" and metadata.get("region"):
                ref_parts.append(f"Regione {metadata['region']}")
            
            reference = " - ".join(ref_parts) if ref_parts else f"Documento {i}"
            
            # Formatta chunk
            context_parts.append(
                f"[{reference}]\n{doc.page_content}\n"
            )
        
        return "\n---\n\n".join(context_parts)
    
    def get_citations(self, documents: List[Document]) -> List[Dict[str, str]]:
        """
        Estrae citazioni formattate dai documenti.
        
        Args:
            documents: Documenti da cui estrarre citazioni
            
        Returns:
            Lista di dizionari con informazioni citazione
        """
        citations = []
        
        for doc in documents:
            metadata = doc.metadata
            
            citation = {
                "level": metadata.get("normative_level", ""),
                "text": doc.page_content[:200] + "...",  # Preview
            }
            
            if metadata.get("law_type") and metadata.get("law_number"):
                citation["law"] = (
                    f"{metadata['law_type']} "
                    f"{metadata['law_number']}/{metadata.get('law_year', '')}"
                )
            
            if metadata.get("article"):
                citation["article"] = metadata["article"]
            
            if metadata.get("municipality"):
                citation["municipality"] = metadata["municipality"]
            elif metadata.get("region"):
                citation["region"] = metadata["region"]
            
            citations.append(citation)
        
        return citations
