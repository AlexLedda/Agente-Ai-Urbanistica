# Usa Python 3.12 slim per efficienza e compatibilità
FROM python:3.12-slim

# Imposta variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Imposta working directory
WORKDIR /app

# Installa dipendenze di sistema necessarie per OpenCV e OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-ita \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY backend/requirements.txt /app/backend/requirements.txt

# Installa dipendenze Python
# Aggiungiamo unstructured che abbiamo installato manualmente
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r backend/requirements.txt && \
    pip install --no-cache-dir unstructured langchain-community langchain-text-splitters chromadb

# Copia il codice sorgente
COPY . /app/

# Crea directory per i dati se non esistono
RUN mkdir -p /app/data/vectordb /app/data/normative /app/data/uploads /app/logs

# Espone la porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando di avvio
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
