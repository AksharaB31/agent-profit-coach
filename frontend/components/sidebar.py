import streamlit as st
from datetime import date

def render_sidebar():
    st.sidebar.title("Search Filters")

    origin = st.sidebar.text_input("Origin (IATA)", "DXB").upper()
    destination = st.sidebar.text_input("Destination (IATA)", "DEL").upper()

    trip_type = st.sidebar.selectbox(
        "Trip Type",
        ["oneway", "roundtrip"]
    )

    departure_date = st.sidebar.date_input(
        "Departure Date",
        value=date.today() 
    )

    agent_id = st.sidebar.number_input(
        "Agent ID (optional)",
        min_value=0,
        value=0,
        step=1
    )

    if st.sidebar.button("Analyze Route", use_container_width=True):
        
        # Validation rules
        if not origin or not destination:
            st.sidebar.error("Origin and Destination are required.")
            return None
            
        if origin == destination:
            st.sidebar.error("Origin and Destination cannot be the same.")
            return None
            
        if departure_date is None:
            st.sidebar.error("Departure date is required.")
            return None

        payload = {
            "origin": origin,
            "destination": destination,
            "trip_type": trip_type,
            "departure_date": departure_date.strftime("%Y-%m-%d"),
            "agent_id": agent_id if agent_id > 0 else None
        }

        return payload

    return None
