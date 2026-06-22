import streamlit as st

def render_header(payload: dict = None):
    st.title("🌐 Agent Profit Coach")
    st.markdown("#### Next-Generation Airline Profitability & Route Intelligence")
    
    if payload:
        html = f"""<div class="enterprise-card" style="padding: 15px; margin-top: 20px; display: flex; justify-content: space-between; flex-wrap: wrap;">
<div><strong>Route:</strong> {payload.get('origin')} ➔ {payload.get('destination')}</div>
<div><strong>Date:</strong> {payload.get('departure_date')}</div>
<div><strong>Type:</strong> {str(payload.get('trip_type')).title()}</div>
</div>"""
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("---")
