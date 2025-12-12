import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.agents.urban_compliance_agent import UrbanComplianceAgent

@pytest.mark.asyncio
async def test_location_extraction(mock_settings, mock_llm_chain, mock_vector_store):
    """Test correctly extracting location from extraction chain."""
    
    # Mock dependencies
    # Mock dependencies
    with patch('backend.agents.urban_compliance_agent.LLMRouter') as MockLLMRouter:
        with patch('backend.agents.urban_compliance_agent.MultiLevelVectorStore') as MockVectorStore:
            
            # Setup mock router
            mock_router_instance = MockLLMRouter.return_value
            # Mock gpt35 response for location extraction
            mock_router_instance.gpt35.invoke.return_value.content = '{"municipality": "Tarquinia", "region": "Lazio"}'
            
            # Setup agent mock
            agent = UrbanComplianceAgent()
            agent.retriever = mock_vector_store      # Uses fixture

            # Run extraction
            query = "Quali sono i vincoli a Tarquinia?"
            location = agent._extract_location_from_query(query)

            # Assertions
            assert location['municipality'] == "Tarquinia"
            assert location['region'] == "Lazio"

@pytest.mark.asyncio
async def test_agent_flow(mock_settings, mock_llm_chain, mock_vector_store):
    """Test full agent flow with mocked retrieval."""
    
    with patch('backend.agents.urban_compliance_agent.LLMRouter') as MockLLMRouter:
        with patch('backend.agents.urban_compliance_agent.MultiLevelVectorStore') as MockVectorStore:
            
            # Setup mock router
            mock_router_instance = MockLLMRouter.return_value
            # Mock analyze_with_best_model response
            mock_router_instance.analyze_with_best_model.return_value = "Analisi: Il vincolo a Tarquinia impedisce nuove costruzioni."
            # Mock gpt35 for location extraction inside ask_question
            mock_router_instance.gpt35.invoke.return_value.content = '{"municipality": "Tarquinia", "region": "Lazio"}'
            
            agent = UrbanComplianceAgent()
            agent.retriever.vector_store = mock_vector_store # Fix: Mock the internal vector_store, not the retriever itself
            
            # Run Chat
            response = agent.chat("Quali sono i vincoli a Tarquinia?")

            # Assertions
            assert "Analisi" in response
            mock_vector_store.search_hierarchical.assert_called_once()
