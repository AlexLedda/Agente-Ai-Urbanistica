import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger

from langchain_core.messages import HumanMessage, SystemMessage

from backend.models.llm_router import LLMRouter, TaskType
from backend.models.prompt_templates import PromptTemplates
from backend.rag.vector_store import MultiLevelVectorStore
from backend.rag.retriever import NormativeRetriever
from backend.vision.comparator import DocumentComparator
from backend.agents.report_generator import ReportGenerator


class UrbanComplianceAgent:
    """Agente AI principale per verifica conformità urbanistica."""
    
    def __init__(self):
        """Inizializza l'agente."""
        self.router = LLMRouter()
        self.vector_store = MultiLevelVectorStore()
        self.retriever = NormativeRetriever(self.vector_store)
        self.comparator = DocumentComparator()
        self.report_generator = ReportGenerator(self.router)
        
        logger.info("Urban Compliance Agent inizializzato")
    
    def analyze_property(
        self,
        municipality: str,
        region: str = "Lazio",
        planimetria_catastale: Optional[Path] = None,
        progetto_urbanistico: Optional[Path] = None,
        foto_immobile: Optional[List[Path]] = None,
        property_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analizza un immobile per verificare la conformità urbanistica.
        
        Args:
            municipality: Comune
            region: Regione
            planimetria_catastale: Path planimetria catastale
            progetto_urbanistico: Path progetto urbanistico
            foto_immobile: Lista foto immobile
            property_info: Informazioni aggiuntive immobile
            
        Returns:
            Analisi completa con report
        """
        logger.info(f"Analisi immobile - {municipality}, {region}")
        
        # 1. Recupera normative applicabili
        logger.info("Recupero normative applicabili")
        normative_context = self._get_applicable_normative(municipality, region)
        
        # 2. Analizza documenti
        logger.info("Analisi documenti")
        document_analysis = self.comparator.compare_all_documents(
            planimetria_catastale=planimetria_catastale,
            progetto_urbanistico=progetto_urbanistico,
            foto_immobile=foto_immobile,
            normative_context=normative_context
        )
        
        # 3. Verifica conformità
        logger.info("Verifica conformità")
        compliance_result = self._verify_compliance(
            document_analysis,
            normative_context,
            municipality,
            region,
            property_info
        )
        
        # 4. Genera report
        logger.info("Generazione report")
        report = self.report_generator.generate_report(
            compliance_result,
            document_analysis,
            normative_context,
            municipality,
            region
        )
        
        result = {
            "municipality": municipality,
            "region": region,
            "normative_context": normative_context,
            "document_analysis": document_analysis,
            "compliance_result": compliance_result,
            "report": report
        }
        
        logger.success("Analisi immobile completata")
        return result
    
    def _get_applicable_normative(
        self,
        municipality: str,
        region: str
    ) -> str:
        """Recupera normative applicabili."""
        # Query per normative rilevanti
        queries = [
            "distanze minime dai confini",
            "altezze massime edifici",
            "indici urbanistici",
            "destinazioni d'uso",
            "regolamento edilizio"
        ]
        
        all_normative = []
        for query in queries:
            docs = self.retriever.retrieve(
                query,
                municipality=municipality,
                region=region,
                top_k=3
            )
            all_normative.extend(docs)
        
        # Formatta contesto
        context = self.retriever.format_context(all_normative)
        return context
    
    def _verify_compliance(
        self,
        document_analysis: Dict[str, Any],
        normative_context: str,
        municipality: str,
        region: str,
        property_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verifica conformità usando LLM."""
        # Prepara dati per verifica
        property_data = property_info or {}
        
        # Usa prompt template
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.COMPLIANCE_CHECK,
            normative=normative_context,
            municipality=municipality,
            region=region,
            property_type=property_data.get("type", "Residenziale"),
            property_info=str(property_data),
            documents=str(document_analysis)
        )
        
        # Analisi con LLM
        compliance_analysis = self.router.analyze_with_best_model(
            prompt,
            TaskType.COMPLIANCE_CHECK,
            system_message=PromptTemplates.get_system_message("urbanistica_expert")
        )
        
        return {
            "analysis": compliance_analysis,
            "difformita": document_analysis.get("difformita", []),
            "municipality": municipality,
            "region": region
        }
    
    def _extract_location_from_query(self, query: str) -> Dict[str, Optional[str]]:
        """
        Estrae regione e comune dalla query utente usando LLM.
        """
        try:
            prompt = f"""Analizza la seguente domanda tecnica e estrai il Comune e la Regione se menzionati esplicitamente o implicitamente.
            Domanda: {query}
            
            Rispondi ESCLUSIVAMENTE con un oggetto JSON valido nel seguente formato:
            {{"municipality": "Nome Comune" | null, "region": "Nome Regione" | null}}
            """
            
            # Usa il modello veloce per questa estrazione
            response = self.router.gpt35.invoke(prompt)
            content = response.content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content)
            logger.info(f"Location estratta dalla query: {data}")
            return data
            
        except Exception as e:
            logger.warning(f"Errore estrazione location da query: {e}")
            return {"municipality": None, "region": None}

    def ask_question(
        self,
        question: str,
        municipality: Optional[str] = None,
        region: Optional[str] = None
    ) -> str:
        """
        Risponde a domande su normative urbanistiche con analisi comparata.
        
        Args:
            question: Domanda dell'utente
            municipality: Comune (opzionale)
            region: Regione (opzionale)
            
        Returns:
            Risposta con citazioni normative
        """
        logger.info(f"Domanda: {question}")
        
        # 1. Se location non fornita, prova ad estrarla dalla query
        if not municipality and not region:
            extracted_loc = self._extract_location_from_query(question)
            municipality = extracted_loc.get("municipality")
            region = extracted_loc.get("region")
            
        logger.info(f"Contesto location: Comune={municipality}, Regione={region}")
        
        # 2. Recupera normative rilevanti (Gerarchico: Naz -> Reg -> Prov -> Com)
        # Il retriever gestisce la logica gerarchica se chiamiamo retrieve senza specificare un livello forzato
        # ma passando i parametri di location
        docs = self.retriever.retrieve(
            question,
            municipality=municipality,
            region=region,
            top_k=6  # Aumentiamo il context window per avere più livelli
        )
        
        context = self.retriever.format_context(docs)
        
        # 3. Usa prompt template per analisi comparativa
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.COMPARATIVE_NORMATIVE_ANALYSIS,
            context=context,
            question=question
        )
        
        # 4. Genera risposta usando un modello analitico (Claude opzionale o GPT-4)
        answer = self.router.analyze_with_best_model(
            prompt,
            TaskType.NORMATIVE_ANALYSIS,
            system_message=PromptTemplates.get_system_message("urbanistica_expert")
        )
        
        logger.success("Risposta generata")
        return answer
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Modalità chat conversazionale.
        
        Args:
            message: Messaggio utente
            context: Contesto opzionale (comune, regione, ecc.)
            
        Returns:
            Risposta dell'agente
        """
        logger.info(f"Chat message: {message}")
        
        # Normalizza context
        ctx = context or {}
        
        # Determina intent
        if any(word in message.lower() for word in ["conforme", "conformità", "verifica", "analizza l'immobile"]):
            # Intent: verifica conformità (richiede documenti)
            if ctx.get("documents"):
                return "Per verificare la conformità, usa il metodo analyze_property con i documenti."
            else:
                # Se l'utente chiede verifica ma è una domanda generale
                return self.ask_question(message, ctx.get("municipality"), ctx.get("region"))
        else:
            # Intent: domanda normativa / analisi comparata
            return self.ask_question(message, ctx.get("municipality"), ctx.get("region"))
