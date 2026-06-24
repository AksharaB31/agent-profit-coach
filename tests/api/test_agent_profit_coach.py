import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_agent_profit_coach_unauthorized():
    # Attempt to access the endpoint without an API key
    payload = {
        "origin": "WAW",
        "destination": "BER",
        "trip_type": "oneway",
        "departure_date": "2026-04-15"
    }
    response = client.post("/api/v1/agent-profit-coach", json=payload)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}

def test_agent_profit_coach_invalid_api_key():
    # Attempt to access the endpoint with an invalid API key
    payload = {
        "origin": "WAW",
        "destination": "BER",
        "trip_type": "oneway",
        "departure_date": "2026-04-15"
    }
    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/api/v1/agent-profit-coach", json=payload, headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate API KEY"}

def test_agent_profit_coach_authorized():
    # The actual business logic needs DB access and ML models.
    # We will test if the auth successfully passes. If it returns 200 or 500 (due to lack of DB in test env), 
    # it means the auth barrier was passed.
    payload = {
        "origin": "WAW",
        "destination": "BER",
        "trip_type": "oneway",
        "departure_date": "2026-04-15"
    }
    # Mocking the settings API key in case it's missing in the test environment
    if not settings.API_KEY:
        settings.API_KEY = "test_key"
        
    headers = {"X-API-Key": settings.API_KEY}
    response = client.post("/api/v1/agent-profit-coach", json=payload, headers=headers)
    
    # It should not return 401 or 403
    assert response.status_code not in (401, 403)
