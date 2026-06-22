import streamlit as st

def render_summary(metadata: dict):
    if not metadata:
        return
        
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Enterprise Analysis Summary")
    
    metrics = metadata.get("pipeline_metrics", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Itineraries Analyzed", f"{metrics.get('raw_itineraries', 0)}") 
        
    with col2:
        st.metric("Suppliers Analyzed", f"{metadata.get('total_suppliers_analyzed', 0)}")
        
    with col3:
        version = metadata.get('ranking_engine_version', 'N/A').replace('_', ' ').title()
        st.metric("Engine Version", f"{version}")
        
    with col4:
        source = metadata.get('metrics_source', 'N/A').replace('_', ' ').title()
        st.metric("Metrics Source", f"{source}")
        
    st.markdown('</div>', unsafe_allow_html=True)
