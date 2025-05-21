import pytest
import os
from unittest.mock import patch, MagicMock
from agent import GraphQLTool, setup_llm, query_agent

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "GRAPHQL_API_URL": "https://test-api.example.com/graphql",
        "OPENAI_API_KEY": "test-openai-key"
    }):
        yield

# Test GraphQLTool initialization
@pytest.mark.parametrize("endpoint,headers", [
    ("https://test-api.com/graphql", None),
    ("https://test-api.com/graphql", {"Authorization": "Bearer token"})
])
def test_graphql_tool_init(endpoint, headers):
    with patch("agent.Client") as mock_client:
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        tool = GraphQLTool(endpoint=endpoint, headers=headers)
        
        assert tool.endpoint == endpoint
        assert isinstance(tool.headers, dict)
        assert tool.name == "GraphQLJobsAPI"
        assert "query job listings" in tool.description.lower()

# Test GraphQLTool query execution
def test_graphql_tool_run():
    with patch("agent.Client") as mock_client:
        mock_client_instance = MagicMock()
        mock_client_instance.execute.return_value = {"data": {"jobs": [{"title": "Python Developer"}]}}
        mock_client.return_value = mock_client_instance
        
        tool = GraphQLTool(endpoint="https://test-api.com/graphql")
        result = tool._run("query { jobs { title } }")
        
        assert "Python Developer" in result
        mock_client_instance.execute.assert_called_once()

# Test LLM setup with OpenAI
def test_setup_llm_openai():
    with patch("agent.ChatOpenAI") as mock_openai:
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance
        
        llm = setup_llm()
        
        assert llm == mock_openai_instance
        mock_openai.assert_called_once()

# Test query_agent function with a successful query
def test_query_agent_success():
    with patch("agent.init_agent") as mock_init_agent:
        mock_agent = MagicMock()
        mock_agent.run.return_value = "Found 5 Python jobs in Berlin"
        mock_init_agent.return_value = mock_agent
        
        result = query_agent("Show me Python jobs in Berlin")
        
        assert "Found 5 Python jobs" in result
        mock_agent.run.assert_called_once()

# Test query_agent function with an error
def test_query_agent_error():
    with patch("agent.init_agent") as mock_init_agent:
        mock_agent = MagicMock()
        mock_agent.run.side_effect = Exception("Test error")
        mock_init_agent.return_value = mock_agent
        
        result = query_agent("Show me Python jobs in Berlin")
        
        assert "error occurred" in result.lower()
        assert "Test error" in result
        mock_agent.run.assert_called_once()