import streamlit as st
from utils.formatters import format_currency

def render_metrics_cards(metadata: dict, best_itinerary: dict):
    st.markdown("### 📊 Top Level KPIs")
    
    best_itinerary = best_itinerary or {}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Suppliers", metadata.get("total_suppliers_analyzed", 0))
    with col2:
        st.metric("Total Itineraries", metadata.get("total_itineraries_analyzed", 0))
    with col3:
        currency = best_itinerary.get("currency", "EUR")
        profit = best_itinerary.get("expected_agent_profit", 0.0)
        st.metric("Best Expected Profit", format_currency(profit, currency))
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    with col4:
        rel = best_itinerary.get("reliability_score", 0.0) * 100
        st.metric("Best Reliability", f"{rel:.1f}%")
    with col5:
        conv = best_itinerary.get("conversion_probability", 0.0) * 100
        st.metric("Best Conversion Prob", f"{conv:.1f}%")
    with col6:
        convenience = best_itinerary.get("journey_convenience_score", 0.0) * 100
        st.metric("Best Convenience", f"{convenience:.1f}%")
