import pytest
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Global Mock of chromadb to prevent import crash due to Pydantic V2 incompatibility
mock_chromadb = MagicMock()
sys.modules["chromadb"] = mock_chromadb
sys.modules["chromadb.config"] = MagicMock()

# Pre-set environment variables for Pydantic validation at import time
os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["ANTHROPIC_API_KEY"] = "dummy"
os.environ["GOOGLE_AI_API_KEY"] = "dummy"

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock environment settings."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "dummy")
    monkeypatch.setenv("VECTOR_DB_PATH", "/tmp/chroma_test")
    
@pytest.fixture
def mock_llm_chain():
    """Mock LangChain LLM Chain."""
    mock = MagicMock()
    mock.invoke.return_value.content = '{"municipality": "Tarquinia", "region": "Lazio", "topic": "vincoli"}'
    return mock

@pytest.fixture
def mock_vector_store():
    """Mock Vector Store retriever."""
    mock = MagicMock()
    # Mock retrieval results
    mock.search_hierarchical.return_value = [
        MagicMock(page_content="Vincolo paesaggistico a Tarquinia...", metadata={"source": "NTA Tarquinia", "level": "comunale"})
    ]
    return mock
