"""
Router intelligente per selezione LLM basata sul task.
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import base64
from pathlib import Path
from loguru import logger

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from backend.config import get_settings


class TaskType(Enum):
    """Tipi di task per routing LLM."""
    NORMATIVE_ANALYSIS = "normative_analysis"  # Analisi testi normativi
    VISION_ANALYSIS = "vision_analysis"  # Analisi immagini/planimetrie
    COMPLIANCE_CHECK = "compliance_check"  # Verifica conformità
    REPORT_GENERATION = "report_generation"  # Generazione report
    GENERAL_QUERY = "general_query"  # Query generiche


class LLMRouter:
    """Router per selezione intelligente del modello LLM."""
    
    def __init__(self):
        """Inizializza i client per tutti i modelli LLM."""
        
        settings = get_settings()
        
        # OpenAI GPT-4
        self.gpt4 = ChatOpenAI(
            model=settings.primary_llm,
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        self.gpt4_turbo = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        # Google Gemini
        self.gemini = ChatGoogleGenerativeAI(
            model=settings.secondary_llm,
            temperature=0,
            google_api_key=settings.google_ai_api_key
        )
        
        # Anthropic Claude
        self.claude = ChatAnthropic(
            model=settings.tertiary_llm,
            temperature=0,
            anthropic_api_key=settings.anthropic_api_key
        )
        
        # Modello economico per task semplici
        self.gpt35 = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        logger.info("LLM Router inizializzato con tutti i modelli")
    
    def select_model(self, task_type: TaskType, has_images: bool = False):
        """
        Seleziona il modello ottimale per il task.
        
        Args:
            task_type: Tipo di task
            has_images: Se True, serve un vision model
            
        Returns:
            Modello LLM selezionato
        """
        if has_images:
            settings = get_settings()
            # Per task con immagini, usa vision models
            logger.info(f"Task con immagini: usando {settings.primary_llm}")
            return self.gpt4  # GPT-4V
        
        # Routing basato sul tipo di task
        if task_type == TaskType.NORMATIVE_ANALYSIS:
            # Claude eccelle nell'analisi di testi lunghi e legali
            logger.info("Task normative analysis: usando Claude")
            return self.claude
        
        elif task_type == TaskType.COMPLIANCE_CHECK:
            # GPT-4 per reasoning complesso
            logger.info("Task compliance check: usando GPT-4")
            return self.gpt4_turbo
        
        elif task_type == TaskType.REPORT_GENERATION:
            # Gemini per generazione testi lunghi
            logger.info("Task report generation: usando Gemini")
            return self.gemini
        
        elif task_type == TaskType.VISION_ANALYSIS:
            # GPT-4V per analisi visiva
            logger.info("Task vision analysis: usando GPT-4V")
            return self.gpt4
        
        else:
            # Task generici: usa modello economico
            logger.info("Task generico: usando GPT-3.5")
            return self.gpt35
    
    def invoke_with_fallback(
        self,
        messages: List[BaseMessage],
        task_type: TaskType,
        has_images: bool = False,
        **kwargs
    ) -> str:
        """
        Invoca LLM con fallback automatico in caso di errore.
        
        Args:
            messages: Messaggi da inviare
            task_type: Tipo di task
            has_images: Se il task include immagini
            **kwargs: Parametri aggiuntivi per LLM
            
        Returns:
            Risposta del modello
        """
        # Seleziona modello primario
        primary_model = self.select_model(task_type, has_images)
        
        # Lista di fallback
        fallback_models = self._get_fallback_models(primary_model, has_images)
        
        # Prova con modello primario
        try:
            logger.debug(f"Invocazione modello primario")
            response = primary_model.invoke(messages, **kwargs)
            return response.content
        
        except Exception as e:
            logger.warning(f"Errore con modello primario: {e}")
            
            # Prova con fallback
            for i, fallback_model in enumerate(fallback_models):
                try:
                    logger.info(f"Tentativo fallback {i+1}/{len(fallback_models)}")
                    response = fallback_model.invoke(messages, **kwargs)
                    return response.content
                
                except Exception as e:
                    logger.warning(f"Errore con fallback {i+1}: {e}")
                    continue
            
            # Se tutti i modelli falliscono
            logger.error("Tutti i modelli hanno fallito")
            raise Exception("Impossibile ottenere risposta da nessun modello LLM")
    
    def _get_fallback_models(self, primary_model, has_images: bool) -> List:
        """Ottiene lista di modelli fallback."""
        all_models = [self.gpt4_turbo, self.gemini, self.claude, self.gpt35]
        
        # Rimuovi il modello primario
        fallback = [m for m in all_models if m != primary_model]
        
        # Se servono immagini, filtra solo vision models
        if has_images:
            fallback = [m for m in fallback if m in [self.gpt4, self.gemini]]
        
        return fallback
    
    def multi_model_consensus(
        self,
        messages: List[BaseMessage],
        models: Optional[List] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Ottiene risposte da più modelli per confronto/consenso.
        Utile per decisioni critiche.
        
        Args:
            messages: Messaggi da inviare
            models: Lista di modelli (se None, usa tutti)
            **kwargs: Parametri aggiuntivi
            
        Returns:
            Dizionario {nome_modello: risposta}
        """
        if models is None:
            models = [
                ("GPT-4", self.gpt4_turbo),
                ("Gemini", self.gemini),
                ("Claude", self.claude)
            ]
        
        responses = {}
        
        for name, model in models:
            try:
                logger.info(f"Richiesta consenso a {name}")
                response = model.invoke(messages, **kwargs)
                responses[name] = response.content
            except Exception as e:
                logger.warning(f"Errore con {name}: {e}")
                responses[name] = f"[ERRORE: {str(e)}]"
        
        return responses
    
    def analyze_with_best_model(
        self,
        prompt: str,
        task_type: TaskType,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Analizza un prompt con il modello migliore per il task.
        
        Args:
            prompt: Prompt utente
            task_type: Tipo di task
            system_message: Messaggio di sistema (opzionale)
            **kwargs: Parametri aggiuntivi
            
        Returns:
            Risposta del modello
        """
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        messages.append(HumanMessage(content=prompt))
        
        return self.invoke_with_fallback(
            messages,
            task_type=task_type,
            **kwargs
        )


class VisionAnalyzer:
    """Analizzatore specializzato per documenti con immagini."""
    
    def __init__(self, router: LLMRouter):
        """
        Inizializza l'analizzatore vision.
        
        Args:
            router: Router LLM
        """
        self.router = router
        logger.info("Vision Analyzer inizializzato")
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str,
        detail_level: str = "high"
    ) -> str:
        """
        Analizza un'immagine con vision model.
        
        Args:
            image_path: Path all'immagine
            prompt: Prompt per l'analisi
            detail_level: Livello di dettaglio ("low", "high", "auto")
            
        Returns:
            Analisi dell'immagine
        """
        logger.info(f"Analisi immagine: {image_path}")
        
        # Prepara messaggio con immagine
        import base64
        from pathlib import Path
        
        # Leggi e codifica immagine
        image_data = Path(image_path).read_bytes()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determina tipo MIME
        suffix = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(suffix, 'image/jpeg')
        
        # Crea messaggio con immagine
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}",
                        "detail": detail_level
                    }
                }
            ]
        )
        
        # Usa GPT-4V
        try:
            response = self.router.gpt4.invoke([message])
            return response.content
        except Exception as e:
            logger.error(f"Errore nell'analisi immagine: {e}")
            raise
    
    def compare_images(
        self,
        image1_path: str,
        image2_path: str,
        comparison_prompt: str
    ) -> str:
        """
        Confronta due immagini.
        
        Args:
            image1_path: Path prima immagine
            image2_path: Path seconda immagine
            comparison_prompt: Prompt per il confronto
            
        Returns:
            Analisi comparativa
        """
        logger.info(f"Confronto immagini: {image1_path} vs {image2_path}")
        
        import base64
        from pathlib import Path
        
        # Codifica entrambe le immagini
        images_data = []
        for img_path in [image1_path, image2_path]:
            image_data = Path(img_path).read_bytes()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            suffix = Path(img_path).suffix.lower()
            mime_type = 'image/jpeg' if suffix in ['.jpg', '.jpeg'] else 'image/png'
            
            images_data.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}",
                    "detail": "high"
                }
            })
        
        # Crea messaggio con entrambe le immagini
        message = HumanMessage(
            content=[
                {"type": "text", "text": comparison_prompt},
                images_data[0],
                images_data[1]
            ]
        )
        
        try:
            response = self.router.gpt4.invoke([message])
            return response.content
        except Exception as e:
            logger.error(f"Errore nel confronto immagini: {e}")
            raise
