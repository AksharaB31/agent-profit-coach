import streamlit as st
import pandas as pd

def render_supplier_profitability(supplier_data: list):
    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True) 
    st.markdown("### 🏢 Supplier Profitability Analysis")
    
    if not supplier_data:
        st.info("No supplier data available.")
        st.markdown('</div>', unsafe_allow_html=True) 
        return
        
    df = pd.DataFrame(supplier_data)
    
    # Clean up display columns
    display_df = df.copy()
    display_df["Recommended"] = display_df["recommended"].apply(lambda x: "⭐ Yes" if x else "No")
    
    # Rename for professional table header
    display_df = display_df.rename(columns={
        "total_itineraries": "Total Itineraries",
        "average_agent_profit": "Avg Profit",
        "best_itinerary_profit": "Best Profit",
        "average_reliability": "Reliability Score",
        "best_conversion_probability": "Conversion Prob",
    })
    
    cols = ["Total Itineraries", "Avg Profit", "Best Profit", "Reliability Score", "Conversion Prob", "Recommended"]
    cols = [c for c in cols if c in display_df.columns]
    
    st.dataframe(
        display_df[cols],
        width="stretch",
        hide_index=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
