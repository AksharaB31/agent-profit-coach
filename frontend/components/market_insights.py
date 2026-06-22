import streamlit as st

def render_market_insights(insights: dict):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 💡 Market Insights")
    
    insights = insights or {}
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    def _check(val):
        return "✓" if val and val != "N/A" else "—"
    
    with col1:
        st.metric("💰 Cheapest", _check(insights.get("cheapest_supplier")))
    with col2:
        st.metric("⚡ Fastest", _check(insights.get("fastest_supplier")))
    with col3:
        st.metric("🛡️ Most Reliable", _check(insights.get("most_reliable_supplier")))
    with col4:
        st.metric("💎 Best Value", _check(insights.get("best_value_supplier")))
    with col5:
        st.metric("🤑 Highest Profit", _check(insights.get("highest_profit_supplier")))
        
    st.markdown('</div>', unsafe_allow_html=True)
