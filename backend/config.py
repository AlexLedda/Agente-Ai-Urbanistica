"""
Configurazione centralizzata per l'agente AI di conformità urbanistica.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Configurazione applicazione caricata da variabili ambiente."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # LLM API Keys
    openai_api_key: str
    anthropic_api_key: str
    google_ai_api_key: str

    # Auth Configuration
    secret_key: str = "supersecretkeychangeinproduction"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database Configuration
    vector_db_path: Path = Path("./data/vectordb")
    vector_db_type: str = "chromadb"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    # Data Paths
    normative_data_path: Path = Path("./data/normative")
    upload_path: Path = Path("./data/uploads")
    cache_path: Path = Path("./data/cache")
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Scraper Configuration
    scraper_user_agent: str = "Mozilla/5.0 (compatible; UrbanisticaBot/1.0)"
    scraper_delay: int = 2
    scraper_max_retries: int = 3
    
    # Region/Municipality Configuration
    default_region: str = "Lazio"
    default_municipalities: str = "Tarquinia,Montalto di Castro"
    
    # Update Schedule
    normative_update_schedule: str = "0 2 * * 0"  # Every Sunday at 2 AM
    
    # LLM Router Configuration
    primary_llm: str = "gpt-4-vision-preview"
    secondary_llm: str = "gemini-pro-vision"
    tertiary_llm: str = "claude-3-sonnet-20240229"
    
    # Logging
    log_level: str = "INFO"
    log_file: Path = Path("./logs/urbanistica-ai.log")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Crea le directory necessarie
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        self.normative_data_path.mkdir(parents=True, exist_ok=True)
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Configurazioni specifiche per normative
NORMATIVE_SOURCES = {
    "nazionale": {
        "testo_unico": {
            "name": "Testo Unico Edilizia (DPR 380/2001)",
            "url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-06;380",
            "type": "pdf"
        }
    },
    "regionale": {
        "lazio": {
            "name": "Normativa Urbanistica Regione Lazio",
            "bur_url": "https://www.regione.lazio.it/bur",
            "leggi_principali": [
                {
                    "name": "LR 38/1999 - Norme sul governo del territorio",
                    "url": "https://www.regione.lazio.it/documenti/77609" # Placeholder per search logic
                }
            ]
        }
    },
    "comunale": {
        "tarquinia": {
            "name": "Comune di Tarquinia",
            "website": "https://www.comune.tarquinia.vt.it",
            "prg_url": "https://www.comune.tarquinia.vt.it/c056050/hh/index.php",  # Landing S.U.E.
            "regolamento_edilizio_url": "https://www.comune.tarquinia.vt.it/c056050/hh/index.php"  # Landing
        },
        "montalto_di_castro": {
            "name": "Comune di Montalto di Castro",
            "website": "https://www.comune.montaltodicastro.vt.it",
            "prg_url": "https://www.comune.montaltodicastro.vt.it/c056036/hh/index.php",
            "regolamento_edilizio_url": "https://www.comune.montaltodicastro.vt.it/c056036/hh/index.php"
        }
    }
}


# Configurazione chunking per RAG
CHUNKING_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "separators": ["\n\nArt.", "\n\nArticolo", "\n\n", "\n", ". ", " ", ""],
    "keep_separator": True
}


# Configurazione retrieval
RETRIEVAL_CONFIG = {
    "top_k": 5,
    "score_threshold": 0.7,
    "rerank": True,
    "hybrid_search": True,
    "keyword_weight": 0.3
}


# Template per prompt
PROMPT_TEMPLATES = {
    "normative_query": """Sei un esperto di urbanistica e diritto edilizio italiano.
Rispondi alla domanda effettuando un'ANALISI COMPARATA delle normative fornite.

Il contesto contiene normative di diversi livelli gerarchici:
- Nazionale (es. Testo Unico)
- Regionale
- Provinciale
- Comunale (es. PRG, NTA)

Contesto Normativo:
{context}

Domanda: {question}

Istruzioni per la risposta:
1. Analizza le norme rilevanti per OGNI livello disponibile.
2. CONFRONTA le norme:
   - Se la norma locale è più restrittiva, evidenzialo (di solito prevale).
   - Se c'è conflitto, spiega quale norma dovrebbe applicarsi secondo il principio di specialità e gerarchia.
3. Fornisci una conclusione sintetica basata sul livello più specifico applicabile (di solito il Comunale per parametri urbanistici).
4. Cita espressamente articoli e commi.

Se la risposta non è contenuta nelle normative fornite, dillo esplicitamente.
""",
    
    "compliance_check": """Sei un tecnico esperto in conformità urbanistica.
Analizza la seguente situazione e verifica la conformità alle normative.

Normative applicabili:
{normative}

Informazioni immobile:
{property_info}

Documenti analizzati:
{documents}

Verifica:
1. Conformità planimetrica
2. Rispetto indici urbanistici
3. Distanze e altezze
4. Eventuali difformità

Fornisci un'analisi dettagliata con citazioni normative precise.
""",
    
    "difformita_detection": """Analizza i seguenti documenti e rileva eventuali difformità:

Planimetria catastale: {planimetria}
Progetto urbanistico: {progetto}
Foto immobile: {foto}

Identifica:
1. Discrepanze dimensionali
2. Modifiche strutturali non autorizzate
3. Cambi di destinazione d'uso
4. Abusi edilizi visibili

Per ogni difformità rilevata, specifica:
- Tipo di difformità
- Gravità (lieve/media/grave)
- Normativa violata
- Possibile regolarizzazione
"""
}


# Singleton settings
settings = Settings()
