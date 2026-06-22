from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_agent_profit_coach():

    response = client.post(
        "/api/v1/agent-profit-coach",
        json={
            "trip_type": "oneway",
            "origin": "DXB",
            "destination": "DEL",
            "departure_date": "2026-06-20"
        }
    )
    assert response.status_code == 200