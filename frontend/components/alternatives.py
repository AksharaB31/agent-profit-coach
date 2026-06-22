import streamlit as st
from utils.formatters import render_badge, format_currency
from utils.helpers import safe_score

def render_alternatives(alternatives: list):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 🔄 Alternative Recommendations")
    
    if not alternatives:
        st.info("No alternative recommendations found for this route.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
        
    for i, alt in enumerate(alternatives):
        airline = alt.get('airline', 'Unknown')
        currency = alt.get('currency', 'EUR')
        price = alt.get('price', 0.0)
        
        with st.expander(f"Option {i+1} - {airline} | {format_currency(price, currency)}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Airline:** {airline}")
                
                profit = alt.get("expected_agent_profit", 0.0)
                st.markdown(f"**Price:** {format_currency(price, currency)}")
                st.markdown(f"**Expected Profit:** {format_currency(profit, currency)}")
                
                duration = alt.get("duration_minutes", 0)
                st.markdown(f"**Duration:** {duration // 60}h {duration % 60}m")
                st.markdown(f"**Stops:** {alt.get('stops', 0)}")
                
            with col2:
                rel = safe_score(alt.get("reliability_score", 0.0))
                conv = safe_score(alt.get("journey_convenience_score", 0.0))
                
                st.markdown(f"**Reliability:** {rel * 100:.1f}%")
                st.markdown(f"**Convenience:** {conv * 100:.1f}%")
                
                ref_badge = render_badge("Refundable", "success") if alt.get("refundable") else render_badge("Non-Refundable", "danger")
                meal_badge = render_badge("Meals", "primary") if alt.get("meals") else ""
                st.markdown(f"{ref_badge} {meal_badge}", unsafe_allow_html=True)
                
                st.markdown("**AI Reasons:**")
                for reason in alt.get("recommendation_reasons", []):
                    text = reason["reason"] if isinstance(reason, dict) else str(reason)
                    st.markdown(f"- {text}")
                    
    st.markdown('</div>', unsafe_allow_html=True)
