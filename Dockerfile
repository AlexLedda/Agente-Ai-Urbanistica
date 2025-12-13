FROM python:3.11-slim

# Installa dipendenze sistema essenziali
RUN apt-get update && apt-get install -y \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e installa tutte le dipendenze dal requirements.txt
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia backend
COPY backend/ /app/backend/
ENV PYTHONPATH=/app

# Configurazione nginx semplificata
RUN echo 'server { \
    listen 80; \
    location /health { \
    proxy_pass http://127.0.0.1:8000/health; \
    } \
    location /docs { \
    proxy_pass http://127.0.0.1:8000/docs; \
    } \
    location /api/ { \
    proxy_pass http://127.0.0.1:8000/; \
    } \
    location / { \
    return 200 "Agente AI Urbanistica - Backend Running"; \
    add_header Content-Type text/plain; \
    } \
    }' > /etc/nginx/sites-available/default

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/

# Crea directory
RUN mkdir -p /app/data /app/logs

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
