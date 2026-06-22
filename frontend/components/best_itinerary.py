import streamlit as st
from utils.formatters import render_badge, format_currency
from utils.helpers import safe_score

def render_best_itinerary(itinerary: dict):
    st.markdown('<div class="enterprise-card hero-card">', unsafe_allow_html=True)
    st.markdown("### ⭐ BEST OVERALL OPTION")
    
    itinerary = itinerary or {}
    
    col_main, col_metrics = st.columns([2, 1])
    
    with col_main:
        airline = itinerary.get("airline", "Unknown")
        flights = ", ".join(itinerary.get("flight_numbers", []))
        
        st.markdown(f"**Airline:** {airline}")
        st.markdown(f"**Flights:** {flights}")
        
        # Badges
        stops = itinerary.get("stops", 0)
        duration = itinerary.get("duration_minutes", 0)
        
        stop_badge = render_badge("✈ Non-stop", "success") if stops == 0 else render_badge(f"{stops} Stops", "warning")
        baggage_badge = render_badge(f"👜 {itinerary.get('baggage', '0KG')}", "dark")
        ref_badge = render_badge("✅ Refundable", "success") if itinerary.get("refundable") else render_badge("❌ Non-Refundable", "danger")
        meal_badge = render_badge("🍽️ Meals", "primary") if itinerary.get("meals") else ""
        
        st.markdown(f"{stop_badge} {baggage_badge} {ref_badge} {meal_badge}", unsafe_allow_html=True)
        st.markdown(f"**Duration:** {duration // 60}h {duration % 60}m")
        
        st.markdown("#### Recommendation Reasons:")
        reasons = itinerary.get("recommendation_reasons", [])
        if reasons:
            reason_texts = [r["reason"] if isinstance(r, dict) else str(r) for r in reasons]
            pills = " ".join([render_badge(t, "primary") for t in reason_texts])
            st.markdown(pills, unsafe_allow_html=True)
            
    with col_metrics:
        currency = itinerary.get("currency", "EUR")
        st.metric("Price", format_currency(itinerary.get("price", 0.0), currency))
        st.metric("Expected Profit", format_currency(itinerary.get("expected_agent_profit", 0.0), currency))
        
        profit_score = safe_score(itinerary.get("profit_score", 0.0))
        rel_score = safe_score(itinerary.get("reliability_score", 0.0))
        success_prob = safe_score(itinerary.get("booking_success_probability", 0.0))
        cancel_risk = safe_score(itinerary.get("cancellation_risk", 0.0))
        
        st.caption(f"Profit Score: {profit_score * 100:.1f}/100")
        st.progress(profit_score)
        
        st.caption(f"Reliability Score: {rel_score * 100:.1f}/100")
        st.progress(rel_score)
        
        st.caption(f"Booking Success Prob: {success_prob * 100:.1f}%")
        st.progress(success_prob)
        
        st.caption(f"Cancellation Risk: {cancel_risk * 100:.1f}%")
        st.progress(cancel_risk)
        
        score_breakdown = itinerary.get("score_breakdown", {})
        if score_breakdown:
            with st.expander("📊 Score Breakdown"):
                for key, val in score_breakdown.items():
                    label = key.replace("_", " ").title()
                    st.markdown(f"**{label}:** {val:.2f}")
        
    st.markdown('</div>', unsafe_allow_html=True)
