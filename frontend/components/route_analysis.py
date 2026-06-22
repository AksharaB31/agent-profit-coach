import streamlit as st

def render_route_analysis(route_data: dict):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.subheader("📍 Route Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Origin", route_data.get("origin", "N/A"))
    with col2:
        st.metric("Destination", route_data.get("destination", "N/A"))
    with col3:
        st.metric("Trip Type", route_data.get("trip_type", "N/A").title())
    with col4:
        st.metric("Departure", route_data.get("departure_date", "N/A"))
        
    st.markdown('</div>', unsafe_allow_html=True)
