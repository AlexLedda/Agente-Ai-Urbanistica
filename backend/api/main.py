"""
FastAPI application principale.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from backend.config import settings

# Configura logging
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
    description="API per agente AI di conformità urbanistica",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Inizializzazione al startup."""
    logger.info("🚀 Avvio Urbanistica AI Agent API")
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
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Importa routes
from backend.api.routes import analysis, normative

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
