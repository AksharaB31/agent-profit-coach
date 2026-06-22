import streamlit as st
import pandas as pd
import plotly.express as px

def render_supplier_analysis(supplier_data: list):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Supplier Profitability Analysis")
    
    if not supplier_data:
        st.info("No supplier data available.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
        
    df = pd.DataFrame(supplier_data)
    df = df.reset_index().rename(columns={"index": "#"})
    
    # Format for display
    display_df = df.copy()
    display_df["Recommended"] = display_df["recommended"].apply(lambda x: "⭐ Yes" if x else "No")
    
    # Show interactive table (no supplier identifiers)
    st.dataframe(
        display_df[["total_itineraries", "average_agent_profit", "best_itinerary_profit", "average_reliability", "best_conversion_probability", "Recommended"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### Visual Insights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Profitability Chart
        fig_profit = px.bar(
            df, 
            x="#", 
            y="average_agent_profit", 
            title="Avg Agent Profit",
            labels={"average_agent_profit": "Avg Profit", "#": "Supplier"}
        )
        fig_profit.update_layout(showlegend=False, xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_profit, use_container_width=True)
        
    with col2:
        # Reliability Chart
        fig_rel = px.bar(
            df, 
            x="#", 
            y="average_reliability", 
            color="average_reliability",
            color_continuous_scale="Blues",
            title="Avg Reliability",
            labels={"average_reliability": "Reliability Score", "#": "Supplier"}
        )
        fig_rel.update_layout(showlegend=False, xaxis=dict(showticklabels=False))
        st.plotly_chart(fig_rel, use_container_width=True)
        
    with col3:
        # Conversion Chart
        fig_conv = px.bar(
            df, 
            x="#", 
            y="best_conversion_probability", 
            color="best_conversion_probability",
            color_continuous_scale="Greens",
            title="Conversion Prob.",
            labels={"best_conversion_probability": "Conversion %", "#": "Supplier"}
        )
        fig_conv.update_layout(showlegend=False, xaxis=dict(showticklabels=False))
        
    st.markdown('</div>', unsafe_allow_html=True)
