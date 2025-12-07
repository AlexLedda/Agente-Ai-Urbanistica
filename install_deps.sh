#!/bin/bash
# Script di installazione completa con Python 3.12

set -e

echo "🔧 Installazione completa Urbanistica AI Agent (Python 3.12)"
echo "============================================================="

# Attiva virtual environment
source venv/bin/activate

echo ""
echo "📦 Stage 1: Aggiornamento pip..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📦 Stage 2: Core LLM Clients..."
pip install openai anthropic google-generativeai

echo ""
echo "📦 Stage 3: LangChain ecosystem..."
pip install langchain langchain-community langchain-openai langchain-anthropic langchain-google-genai

echo ""
echo "📦 Stage 4: Vector DB..."
pip install chromadb sentence-transformers

echo ""
echo "📦 Stage 5: Web Framework..."
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-multipart

echo ""
echo "📦 Stage 6: OCR e Computer Vision..."
pip install easyocr pytesseract opencv-python "Pillow>=10.4.0"

echo ""
echo "📦 Stage 7: Web Scraping..."
pip install requests beautifulsoup4 lxml scrapy selenium

echo ""
echo "📦 Stage 8: Utilities..."
pip install python-dotenv PyPDF2 pyyaml numpy pandas rich typer loguru aiofiles httpx

echo ""
echo "✅ Installazione completata con successo!"
echo ""
echo "Verifica installazione:"
python3 -c "import langchain; import openai; import chromadb; print('✓ Tutti i pacchetti importati con successo!')"
