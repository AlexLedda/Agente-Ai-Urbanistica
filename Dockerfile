# Multi-stage build per applicazione completa
# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend + Serve Frontend
FROM python:3.11-slim

# Installa nginx e dipendenze di sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libyaml-dev \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-ita \
    tesseract-ocr-eng \
    nginx \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /app

# Copia e installa dipendenze Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --upgrade pip setuptools wheel Cython PyYAML && \
    pip install --no-cache-dir -r requirements.txt

# Copia backend
COPY backend/ /app/backend/
ENV PYTHONPATH=/app

# Copia frontend build da stage precedente
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copia configurazione nginx
COPY nginx-eb.conf /etc/nginx/sites-available/default

# Crea directory necessarie
RUN mkdir -p /app/data/vectordb /app/data/normative /app/data/uploads /app/logs

# Configurazione Supervisor per gestire nginx e uvicorn
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Espone porta 80 (nginx)
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Avvia supervisor che gestisce nginx e uvicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
