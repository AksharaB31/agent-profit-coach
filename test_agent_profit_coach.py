from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200


def test_version():

    response = client.get(
        "/api/v1/version"
    )

    assert response.status_code == 200


def test_agent_profit_coach():

    payload = {
        "trip_type": "oneway",
        "origin": "DEL",
        "destination": "DXB",
        "departure_date": "2026-06-10",
        "agent_id": 1001
    }

    response = client.post(
        "/api/v1/agent-profit-coach",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "engine_metadata" in data

def test_booking_probability_no_double_counting():
    from app.services.agent_profit_coach.scorers.itinerary_scoring_engine import ItineraryScoringEngine
    from app.services.agent_profit_coach.analyzers.score_normalization_service import ScoreNormalizationService
    from unittest.mock import MagicMock
    
    # Setup mock scoring engine
    engine = ItineraryScoringEngine()
    engine.ai_engine = MagicMock()
    engine.profitability = MagicMock()
    engine.reliability = MagicMock()
    engine.convenience = MagicMock()
    
    # Mock some static inputs
    engine.profitability.calculate_profitability.return_value = {
        "expected_agent_profit": 1000.0,
        "sell_price": 2000.0,
        "profit_score": 1.0,
        "profit_margin_percent": 50.0
    }
    engine.reliability.calculate_booking_success_probability.return_value = 0.90
    engine.reliability.calculate_supplier_reliability.return_value = 0.80
    engine.convenience.calculate_score.return_value = 70.0
    
    # Test Example A: 0.90 Booking Probability
    engine.ai_engine.predict_conversion_probability.return_value = 0.90
    engine.ai_engine.predict_expected_profit.return_value = -1.0  # fallback to heuristic
    score_a = engine.score_itinerary(
        flight={}, supplier_data={}, rel_data={}, 
        historical_agent_profit=1000.0, recommended_markup=0.0,
        min_price=100, max_price=2000, avg_price=1000,
        min_duration=60, max_duration=600,
        conversion_data={}, max_revenue_cohort=1000.0, departure_date="2026-06-10"
    )
    
    expected_revenue_a = score_a["pricing"]["expected_revenue"]
    assert expected_revenue_a == 900.0  # 1000 * 0.90
    
    # Test Example B: 0.50 Booking Probability
    engine.reliability.calculate_booking_success_probability.return_value = 0.50
    engine.ai_engine.predict_conversion_probability.return_value = 0.50
    score_b = engine.score_itinerary(
        flight={}, supplier_data={}, rel_data={}, 
        historical_agent_profit=1000.0, recommended_markup=0.0,
        min_price=100, max_price=2000, avg_price=1000,
        min_duration=60, max_duration=600,
        conversion_data={}, max_revenue_cohort=1000.0, departure_date="2026-06-10"
    )
    
    expected_revenue_b = score_b["pricing"]["expected_revenue"]
    assert expected_revenue_b == 500.0  # 1000 * 0.50
    
    # Verify ranking logic is driven by expected revenue
    # Score A should be significantly higher than Score B because 900 revenue vs 500 revenue
    assert score_a["scores"]["profit_opportunity_score"] > score_b["scores"]["profit_opportunity_score"]
    
    # Verify ranking driven by expected revenue with configurable weights
    from app.core.config import settings
    pw = settings.PROFIT_WEIGHT
    rw = settings.RELIABILITY_WEIGHT
    cw = settings.CONVENIENCE_WEIGHT
    remaining = 1.0 - pw - rw - cw
    pw += remaining * 0.5
    cw += remaining * 0.5

    # conv_score is overwritten by conv_prob * 100 in the scoring engine
    expected_score_a = 90.0 * pw + 80.0 * rw + 90.0 * cw
    expected_score_b = 50.0 * pw + 80.0 * rw + 50.0 * cw
    assert abs(score_a["scores"]["profit_opportunity_score"] - expected_score_a) < 0.1
    assert abs(score_b["scores"]["profit_opportunity_score"] - expected_score_b) < 0.1