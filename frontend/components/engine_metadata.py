import streamlit as st

def render_engine_metadata(metadata: dict, full_response: dict):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Engine Metadata")
    
    metadata = metadata or {}
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Ranking Engine Version:** {metadata.get('ranking_engine_version', 'N/A')}")
        st.markdown(f"**Metrics Source:** {metadata.get('metrics_source', 'N/A').replace('_', ' ').title()}")
        st.markdown(f"**Search Source:** {metadata.get('search_source', 'N/A')}")
        
    with col2:
        db_enabled = "✅ Enabled" if metadata.get("database_analysis_enabled", False) else "❌ Disabled"
        live_enabled = "✅ Enabled" if metadata.get("live_search_analysis_enabled", False) else "❌ Disabled"
        st.markdown(f"**DB Analysis:** {db_enabled}")
        st.markdown(f"**Live Analysis:** {live_enabled}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("🛠️ View Raw JSON Response"):
        st.json(full_response)
        
    st.markdown('</div>', unsafe_allow_html=True)
