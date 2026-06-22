from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ProfitCoachRequest(BaseModel):     
    trip_type: str
    origin: str
    destination: str
    departure_date: str
    agent_id: Optional[int] = None

class RouteAnalysis(BaseModel):    
    origin: str
    destination: str
    trip_type: str
    departure_date: str

class BestOverallItinerary(BaseModel):
    supplier: str
    airline: str
    flight_numbers: List[str]
    price: float
    currency: str
    expected_agent_profit: float
    historical_agent_profit: float
    profit_score: float
    duration_minutes: int
    stops: int
    baggage: str
    refundable: bool
    meals: bool
    reliability_score: float
    conversion_probability: float
    booking_success_probability: float 
    cancellation_risk: float
    journey_convenience_score: float
    expected_revenue: float = 0.0
    profit_opportunity_score: float = 0.0
    recommendation_reasons: List[Dict[str, Any]]
    score_breakdown: Dict[str, float] = {}

class SupplierRouteProfitability(BaseModel):   
    supplier: str
    supplier_name: str
    total_itineraries: int
    best_itinerary_profit: float
    average_agent_profit: float
    average_reliability: float
    best_conversion_probability: float
    recommended: bool

class MarketInsights(BaseModel):
    cheapest_supplier: Optional[str] = None
    fastest_supplier: Optional[str] = None
    most_reliable_supplier: Optional[str] = None
    best_value_supplier: Optional[str] = None
    highest_profit_supplier: Optional[str] = None 

class EngineMetadata(BaseModel):
    search_source: str = "unknown"
    database_analysis_enabled: bool = True
    live_search_analysis_enabled: bool = True
    total_itineraries_analyzed: int = 0
    total_suppliers_analyzed: int = 0
    ranking_engine_version: str = "enterprise_v2"
    metrics_source: str = "database_only"
    pass_1_errors: Optional[List[str]] = None

class EnterpriseProfitCoachResponse(BaseModel):
    route_analysis: RouteAnalysis
    best_overall_itinerary: Optional[BestOverallItinerary] = None
    supplier_route_profitability: List[SupplierRouteProfitability]
    market_insights: MarketInsights
    alternative_recommendations: List[BestOverallItinerary] 
    engine_metadata: EngineMetadata

