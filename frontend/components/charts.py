import streamlit as st
import pandas as pd
import plotly.express as px

def render_charts(supplier_data: list):
    if not supplier_data:
        return
        
    df = pd.DataFrame(supplier_data)
    df = df.reset_index().rename(columns={"index": "#"})
    
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Visual Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_profit = px.bar(
            df, 
            x="#", 
            y="average_agent_profit", 
            title="Avg Profit Comparison",
            labels={"average_agent_profit": "Avg Profit", "#": "Supplier"}
        )
        fig_profit.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_profit, use_container_width=True)
        
    with col2:
        fig_rel = px.bar(
            df, 
            x="#", 
            y="average_reliability", 
            color="average_reliability",
            color_continuous_scale="Blues",
            title="Reliability Comparison",
            labels={"average_reliability": "Reliability", "#": "Supplier"}
        )
        fig_rel.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_rel, use_container_width=True)
        
    with col3:
        fig_conv = px.bar(
            df, 
            x="#", 
            y="best_conversion_probability", 
            color="best_conversion_probability",
            color_continuous_scale="Greens",
            title="Conversion Probability",
            labels={"best_conversion_probability": "Conversion Prob", "#": "Supplier"}
        )
        fig_conv.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(showticklabels=False))
        
    st.markdown('</div>', unsafe_allow_html=True)
