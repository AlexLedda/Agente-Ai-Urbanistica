# Guida al Deployment - Urbanistica AI Agent

Questa guida spiega come mettere online l'agente AI per la conformità urbanistica utilizzando Docker.

## Prerequisiti

- [Docker](https://www.docker.com/get-started) installato sulla macchina.
- API Keys per OpenAI, Anthropic e Google (configurate nel file `.env`).

## Deployment Locale con Docker

Il metodo più rapido per avviare l'applicazione è utilizzare Docker Compose.

### 1. Configura le Variabili d'Ambiente

Assicurati che il file `.env` sia presente nella root del progetto e configurato correttamente:

```bash
cp .env.example .env
# Modifica .env con le tue chiavi
```

### 2. Avvia l'Applicazione

Esegui il comando:

```bash
docker-compose up --build -d
```

- L'opzione `--build` ricostruisce l'immagine per includere le ultime modifiche.
- L'opzione `-d` avvia il container in background (detached mode).

### 3. Verifica lo Stato

Controlla che il container sia attivo e "healthy":

```bash
docker ps
```

Dovresti vedere `urban-ai-backend` con status `healthy`.

L'API sarà accessibile su: `http://localhost:8000`
Documentazione Swagger: `http://localhost:8000/docs`

### 4. Gestione Logs

Per vedere i log in tempo reale:

```bash
docker-compose logs -f
```

### 5. Stop dell'Applicazione

```bash
docker-compose down
```

## Deployment su Cloud (Render/Railway/Fly.io)

L'applicazione è pronta per essere deployata su piattaforme PaaS che supportano Docker.

### Esempio: Render.com

1. Crea un nuovo **Web Service**.
2. Collega il tuo repository GitHub.
3. Seleziona **Docker** come Environment.
4. Render rileverà automaticamente il `Dockerfile`.
5. Nella sezione **Environment Variables**, aggiungi tutte le chiavi dal tuo `.env` (`OPENAI_API_KEY`, ecc.).
6. **Importante**: Per la persistenza del Vector DB (`./data`), dovrai aggiungere un **Disk** (Persistent Storage) su Render e montarlo su `/app/data`.
   - Mount Path: `/app/data`

### Esempio: Railway

1. Nuovo progetto -> Deploy from GitHub repo.
2. Railway rileverà il `Dockerfile`.
3. Aggiungi le variabili d'ambiente nella tab **Variables**.
4. Imposta un volume persistente per `/app/data` se vuoi conservare l'indice vettoriale tra i riavvii.

## Note sui Dati Persistenti

Il Dockerfile è configurato per salvare i dati in `/app/data`.
- In locale, `docker-compose.yml` mappa questa cartella alla tua cartella `./data` locale.
- In produzione, assicurati di configurare un volume persistente se non vuoi dover re-indicizzare le normative ad ogni deploy.

## Troubleshooting

**Errore "Port already allocated"**:
La porta 8000 è occupata. Modifica la mappatura in `docker-compose.yml`:
```yaml
ports:
  - "8080:8000" # Espone su 8080 invece di 8000
```
