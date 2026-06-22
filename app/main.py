from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(api_router)


@app.get("/")
def root():
    return {
        "message": "Agent Profit Coach API Running"
    }

@app.get("/debug-db")
def debug_db():
    from app.infra.mysql.database import SessionLocal
    from app.services.agent_profit_coach.response_builder.enterprise_response_builder import EnterpriseResponseBuilder
    from app.api.schemas import ProfitCoachRequest
    
    db = SessionLocal()
    try:
        builder = EnterpriseResponseBuilder(db)
        payload = ProfitCoachRequest(
            origin="WAW",
            destination="BER",
            trip_type="oneway",
            departure_date="2026-04-09",
            agent_id=1
        )
        
        flight = {
            "supplier_code": "sup_f8a1",
            "airline": "LO",
            "price": 1127.44,
            "duration_minutes": 75,
            "stops": 0,
            "refundable": True
        }
        
        # Manually run Pass 1
        sup_code = flight.get("supplier_code", "UNKNOWN")
        air_code = flight.get("airline", "UNKNOWN")
        
        sup_details = builder.supplier_loader.get_supplier_details(sup_code)
        rel_data = builder.reliability_loader.get_supplier_reliability(sup_code)
        hist_profit = builder.profitability_loader.get_historical_agent_profit(sup_code, payload.origin, payload.destination)
        rec_markup = builder.profitability_loader.get_recommended_agent_markup(air_code)
        conv_prob_db = builder.conversion_loader.get_route_conversion_probability(sup_code, payload.origin, payload.destination)
        
        base_price = flight.get("price", 0.0)
        expected_agent_profit = hist_profit + (rec_markup if rec_markup else 0.0)
        
        features = {
            "price": base_price,
            "duration_minutes": flight.get("duration_minutes", 0),
            "stops": flight.get("stops", 0),
            "is_refundable": flight.get("refundable", False),
            "month": 4,
            "day_of_week": 3,
            "advance_purchase_days": 30
        }
        
        raw_conv_prob = builder.scoring_engine.ai_engine.predict_conversion_probability(features, 0.85)
        
        p_total = rel_data.get("process_total", 0)
        p_success = rel_data.get("process_success", 0)
        raw_success_prob = builder.scoring_engine.reliability.calculate_booking_success_probability(p_success, p_total)
        
        sup_avg_profit = builder.profitability_loader.get_supplier_avg_profit(sup_code)
        air_avg_profit = builder.profitability_loader.get_airline_avg_profit(air_code)

        return {
            "status": "Pass 1 successful",
            "hist_profit": hist_profit,
            "rel_data": rel_data,
            "p_total": p_total,
            "p_success": p_success
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
    finally:
        db.close()