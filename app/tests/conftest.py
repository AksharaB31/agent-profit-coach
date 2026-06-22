import pytest


@pytest.fixture
def sample_flight():

    return {
        "baggage": 25,
        "stops": 0,
        "duration": 300,
        "refundable": True,
        "departure_hour": 9,
        "supplier_reliability": 0.92,
        "success_rate": 0.95,
        "price_score": 0.8,
        "commission": 1000,
        "markup": 500,
        "incentives": 200
    }