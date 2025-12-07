# Urbanistica AI Agent

Sistema AI multimodale per la verifica della conformità urbanistica degli immobili attraverso l'analisi di normative, planimetrie, progetti urbanistici e fotografie.

## 🎯 Caratteristiche Principali

- **Sistema RAG** per normative (Testo Unico Edilizia, Regione Lazio, normative comunali)
- **Multi-LLM Integration** (GPT-4V, Gemini Pro Vision, Claude 3.5 Sonnet)
- **Analisi Multimodale** con OCR (EasyOCR, Tesseract) e Computer Vision (OpenCV)
- **Web Scraping Automatico** per aggiornamenti normativi
- **Interfacce Multiple**: CLI interattiva e Web API (FastAPI)
- **Rilevamento Difformità** automatico confrontando planimetrie, progetti e foto

## 📋 Requisiti

- Python 3.9+
- API Keys per:
  - OpenAI (GPT-4V)
  - Google AI (Gemini)
  - Anthropic (Claude)

## 🚀 Installazione

### 1. Clona e configura ambiente

```bash
cd urbanistica-ai-agent
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 2. Configura variabili ambiente

Copia `.env.example` in `.env` e inserisci le tue API keys:

```bash
cp .env.example .env
```

Modifica `.env`:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...
```

### 3. Scarica e indicizza normative

```bash
# Scarica normative
python cli/urban_cli.py update-norms

# Indicizza Testo Unico
python cli/urban_cli.py index-norms ./data/normative/testo_unico --level nazionale

# Indicizza Regione Lazio
python cli/urban_cli.py index-norms ./data/normative/regione_lazio --level regionale --regione Lazio

# Indicizza Comune Tarquinia
python cli/urban_cli.py index-norms ./data/normative/comune_tarquinia --level comunale --regione Lazio --comune Tarquinia
```

## 💻 Utilizzo

### CLI Interattiva

#### Fai una domanda sulle normative

```bash
python cli/urban_cli.py ask "Quali sono le distanze minime dai confini?" --comune Tarquinia
```

#### Analizza un immobile

```bash
python cli/urban_cli.py analyze \
  --comune Tarquinia \
  --planimetria ./documenti/planimetria_catastale.pdf \
  --progetto ./documenti/progetto_urbanistico.pdf \
  --foto ./documenti/foto1.jpg \
  --foto ./documenti/foto2.jpg
```

#### Modalità chat

```bash
python cli/urban_cli.py chat
```

#### Visualizza statistiche

```bash
python cli/urban_cli.py stats
```

### Web API

#### Avvia il server

```bash
cd backend
python -m api.main
```

Il server sarà disponibile su `http://localhost:8000`

#### Documentazione API

Visita `http://localhost:8000/docs` per la documentazione interattiva Swagger.

#### Esempi API

**Crea nuova analisi:**
```bash
curl -X POST "http://localhost:8000/api/analysis/new" \
  -H "Content-Type: application/json" \
  -d '{"municipality": "Tarquinia", "region": "Lazio"}'
```

**Upload documenti:**
```bash
curl -X POST "http://localhost:8000/api/analysis/{analysis_id}/upload" \
  -F "planimetria_catastale=@planimetria.pdf" \
  -F "foto_immobile=@foto1.jpg"
```

**Esegui analisi:**
```bash
curl -X POST "http://localhost:8000/api/analysis/{analysis_id}/run"
```

**Ottieni report:**
```bash
curl "http://localhost:8000/api/analysis/{analysis_id}/report"
```

**Cerca normative:**
```bash
curl "http://localhost:8000/api/normative/search?query=distanze+minime&municipality=Tarquinia"
```

## 📁 Struttura Progetto

```
urbanistica-ai-agent/
├── backend/
│   ├── agents/          # Agente principale e tools
│   ├── rag/            # Sistema RAG (vector store, retriever)
│   ├── vision/         # OCR e Computer Vision
│   ├── scrapers/       # Web scraping normative
│   ├── models/         # LLM router e prompt templates
│   └── api/            # FastAPI endpoints
├── cli/                # CLI interattiva
├── data/
│   ├── normative/      # Normative scaricate
│   └── vectordb/       # Database vettoriale
└── docs/               # Documentazione
```

## 🔧 Configurazione Avanzata

### Aggiungere un nuovo comune

1. Crea uno scraper personalizzato in `backend/scrapers/comune_scraper.py`:

```python
def create_nuovo_comune_scraper() -> ComuneScraper:
    return ComuneScraper(
        comune_name="Nuovo Comune",
        website_url="https://www.comune.nuovocomune.it",
        prg_url="URL_AL_PRG",
        regolamento_url="URL_AL_REGOLAMENTO"
    )
```

2. Scarica e indicizza:

```bash
python cli/urban_cli.py update-norms
python cli/urban_cli.py index-norms ./data/normative/comune_nuovo_comune \
  --level comunale --regione Lazio --comune "Nuovo Comune"
```

### Aggiungere una nuova regione

Crea un nuovo scraper in `backend/scrapers/` seguendo il pattern di `regione_lazio_scraper.py`.

## 📊 Funzionalità Principali

### Sistema RAG

- **Document Processing**: Chunking intelligente rispettando articoli e commi
- **Vector Store Multi-Livello**: Separazione nazionale/regionale/comunale
- **Hybrid Search**: Combinazione ricerca semantica + keyword
- **Re-ranking**: LLM-based per risultati ottimali

### Analisi Multimodale

- **OCR**: Estrazione testo da planimetrie con EasyOCR/Tesseract
- **Computer Vision**: Rilevamento stanze e layout
- **Vision AI**: Analisi planimetrie e foto con GPT-4V/Gemini
- **Comparazione**: Confronto automatico planimetria vs progetto vs foto

### Rilevamento Difformità

- Discrepanze dimensionali
- Modifiche strutturali
- Cambi destinazione d'uso
- Abusi edilizi visibili
- Classificazione gravità (lieve/media/grave)
- Suggerimenti regolarizzazione

## ⚠️ Disclaimer

Questo sistema fornisce analisi automatizzate basate su AI e **NON sostituisce una perizia tecnica professionale**. Per decisioni legali o amministrative, consultare sempre un tecnico abilitato (architetto, ingegnere, geometra).

## 📝 Licenza

MIT License

## 🤝 Contributi

Contributi benvenuti! Apri una issue o una pull request.

## 📧 Supporto

Per domande o supporto, apri una issue su GitHub.

---

**Sviluppato con ❤️ per semplificare la verifica della conformità urbanistica**
