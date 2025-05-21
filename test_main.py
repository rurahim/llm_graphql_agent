import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

# Test root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "LLM GraphQL Agent" in response.json()["service"]

# Test health check endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Test query endpoint with valid input
def test_query_valid():
    with patch("main.query_agent") as mock_query_agent:
        mock_query_agent.return_value = "Found 3 Python jobs in Berlin"
        
        response = client.post("/query", json={"q": "Show me Python jobs in Berlin"})
        
        assert response.status_code == 200
        assert response.json()["answer"] == "Found 3 Python jobs in Berlin"
        mock_query_agent.assert_called_once_with("Show me Python jobs in Berlin")

# Test query endpoint with empty input
def test_query_empty():
    response = client.post("/query", json={"q": ""})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

# Test query endpoint with agent error
def test_query_agent_error():
    with patch("main.query_agent") as mock_query_agent:
        mock_query_agent.side_effect = Exception("Test error")
        
        response = client.post("/query", json={"q": "Show me Python jobs in Berlin"})
        
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()
        mock_query_agent.assert_called_once()