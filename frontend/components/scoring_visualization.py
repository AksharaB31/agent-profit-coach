import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_scoring_visualization(itinerary: dict):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 AI Scoring Breakdown")
    
    scores = {
        "Profit": itinerary.get("profit_score", 0.0),
        "Reliability": itinerary.get("reliability_score", 0.0),
        "Convenience": itinerary.get("journey_convenience_score", 0.0),
        "Conversion Prob": itinerary.get("conversion_probability", 0.0),
        "Booking Success": itinerary.get("booking_success_probability", 0.0)
    }
    
    def safe_score(val):
        val = float(val) if val is not None else 0.0
        val = val / 100.0 if val > 1.0 else val
        return max(0.0, min(val, 1.0))

    normalized_scores = {k: safe_score(v) for k, v in scores.items()}
    
    df = pd.DataFrame(dict(
        r=list(normalized_scores.values()),
        theta=list(normalized_scores.keys())
    ))
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig = go.Figure(data=go.Scatterpolar(
            r=df['r'],
            theta=df['theta'],
            fill='toself',
            marker_color='#1e40af',
            line_color='#1e40af'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("#### Score Details")
        for k, v in scores.items():
            val = float(v) if v is not None else 0.0
            val = val / 100.0 if val > 1.0 else val
            val = max(0.0, min(val, 1.0))
            
            st.markdown(f"**{k}:** {val * 100:.1f}%")
            st.progress(val)
            
    st.markdown('</div>', unsafe_allow_html=True)
