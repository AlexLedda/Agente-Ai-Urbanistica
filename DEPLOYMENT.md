# Guida al Deployment

Questa guida spiega come mettere in opera l'Agente Urbanistico AI su un server (VPS, Cloud o locale).

## Prerequisiti
- **Docker** e **Docker Compose** installati sul server.
- File del progetto copiati sul server.

## Struttura
Il progetto è configurato con due container:
1.  **backend**: API Python (FastAPI) su porta 8000.
2.  **frontend**: Web App (React/Nginx) su porta 80.

## Comandi Rapidi

### 1. Avvio
Dalla cartella principale del progetto:

```bash
docker-compose up -d --build
```
Questo comando costruisce le immagini e avvia i container in background.

### 2. Stop
```bash
docker-compose down
```

### 3. Log
Per vedere cosa succede:
```bash
docker-compose logs -f
```

## Configurazione
Assicurati che il file `.env` sia presente nella root e contenga le chiavi API:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_AI_API_KEY=...
SECRET_KEY=...
```

## Dati
- Tipo istanza: **t3.medium** (2vCPU, 4GB RAM).
- Volume (Disco): **Minimo 20GB** (8GB di default NON bastano per le librerie AI).
I dati sono salvati in volumi Docker mappati sulle cartelle locali:
- `./data`: Contiene il database vettoriale e i file caricati/libreria.
- `./logs`: Log del sistema.

Quindi, se copi dei file in `data/library` sul server, saranno visibili al container.

## Deployment su AWS

Il metodo più semplice ed economico è usare **AWS EC2** (o AWS Lightsail).

1.  **Crea istanza EC2**: Scegli 'Ubuntu' (t2.medium o t2.large raccomandato per AI).
2.  **Installa Docker**:
    ```bash
    sudo apt update
    sudo apt install docker.io docker-compose
    ```
3.  **Copia i file**: Usa `scp` dal tuo computer per caricare il progetto:
    ```bash
    scp -r /path/to/project ubuntu@tuo-ip-aws:/home/ubuntu/urban-ai
    ```
4.  **Avvia**:
    ```bash
    cd urban-ai
    sudo docker-compose up -d --build
    ```

Per production, assicurati di configurare il Security Group per aprire le porte 80 (HTTP) e 22 (SSH).
