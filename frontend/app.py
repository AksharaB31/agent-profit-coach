import streamlit as st
import sys
from pathlib import Path

# Add frontend directory to path for absolute imports
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from config import config
from utils.helpers import inject_custom_css
from api.client import fetch_itinerary_intelligence
from components.sidebar import render_sidebar
from components.header import render_header
from components.metrics_cards import render_metrics_cards
from components.best_itinerary import render_best_itinerary
from components.supplier_profitability import render_supplier_profitability

from components.alternatives import render_alternatives
from components.empty_state import render_empty_state

st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT
)

def main():
    inject_custom_css()
    
    # 2. Sidebar Filters
    payload = render_sidebar()
    
    # 1. Header
    render_header(payload)
    
    # Check if form submitted
    if not payload:
        render_empty_state()
        return
        
    # Fetch Data
    with st.spinner("Analyzing live pricing and supplier reliability..."):
        response_data = fetch_itinerary_intelligence(payload)
        
    if not response_data:
        # Client handles displaying error messages
        return
        
    # Parse Safe Lookups
    metadata = response_data.get("engine_metadata", {})
    best_itinerary = response_data.get("best_overall_itinerary", {})
    supplier_data = response_data.get("supplier_route_profitability", [])
    alternatives = response_data.get("alternative_recommendations", [])
    
    # 3. KPI Metric Cards
    render_metrics_cards(metadata, best_itinerary)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Best Overall Itinerary
    if best_itinerary:
        render_best_itinerary(best_itinerary)
    else:
        st.warning("No itineraries available for this route.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Supplier Profitability Analysis
    render_supplier_profitability(supplier_data)
    

    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 7. Alternative Recommendations
    render_alternatives(alternatives)
    
    st.markdown("<br>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
