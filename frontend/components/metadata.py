import streamlit as st
import json

def render_metadata(metadata: dict, full_response: dict):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Engine Metadata")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Itineraries Analyzed", metadata.get("total_itineraries_analyzed", 0))
        st.metric("Suppliers Analyzed", metadata.get("total_suppliers_analyzed", 0))
    with col2:
        st.metric("Engine Version", metadata.get("ranking_engine_version", "N/A"))
        st.metric("Metrics Source", metadata.get("metrics_source", "N/A").replace("_", " ").title())
    with col3:
        st.metric("Search Source", metadata.get("search_source", "N/A"))
        db_enabled = "✅ Yes" if metadata.get("database_analysis_enabled", False) else "❌ No"
        live_enabled = "✅ Yes" if metadata.get("live_search_analysis_enabled", False) else "❌ No"
        st.markdown(f"**DB Analysis:** {db_enabled}")
        st.markdown(f"**Live Analysis:** {live_enabled}")
        
    st.markdown("---")
    
    with st.expander("🛠️ View Raw JSON Response"):
        st.json(full_response)
        
    st.markdown('</div>', unsafe_allow_html=True)
