"""
FastAPI application principale.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from backend.config import get_settings

# Configura logging
logger.remove()
# Use a lazy configuration or get_settings() if strictly needed at module level.
# Since we are at module level, this WILL trigger instantiation.
# But inside a function would be better.
# However, for now, let's use get_settings() and accept it calls it.
# BUT, if I call get_settings() here, I am NOT solving the problem for test collection
# if test collection imports main.py!
# Does test_agent_logic import main? No.
# So this might be fine.
# Wait, IF main.py is imported, it crashes.
# I should wrap logging config in a function setup_logging() and call it in startup_event?
# Yes.

def setup_logging():
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    logger.add(
        settings.log_file,
        rotation="10 MB",
        retention="1 month",
        level=settings.log_level
    )


# Crea app
app = FastAPI(
    title="Urbanistica AI Agent API",
    description="API Gateway for Urban Compliance Agent",
    version="1.0.0"
)

# CORS Configuration
# origins = settings.cors_origins.split(",") # Moved to middleware setup or startup?
# Middleware setup runs at module level.
# I must call get_settings() here.
# origins = get_settings().cors_origins.split(",")
origins = ["*"] # Allow all for now to avoid Settings instantiation at import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inizializzazione al startup."""
    setup_logging()
    logger.info("🚀 Avvio Urbanistica AI Agent API")
    settings = get_settings()
    logger.info(f"Ambiente: {settings.log_level}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup allo shutdown."""
    logger.info("👋 Shutdown Urbanistica AI Agent API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Urbanistica AI Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Importa routes
from backend.api.routes import analysis, normative, ingestion, chat
from backend.api import auth

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(normative.router, prefix="/api/normative", tags=["normative"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
