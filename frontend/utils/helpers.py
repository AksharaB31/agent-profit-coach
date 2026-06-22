import streamlit as st

def inject_custom_css():
    """Reads custom.css and injects it into Streamlit."""
    import os
    css_path = os.path.join(os.path.dirname(__file__), "..", "styles", "custom.css")
    try:
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Could not find custom.css styling file.")

def safe_score(val) -> float:
    """
    Safely convert a score (e.g. 0-100 or 0.0-1.0) into a strictly 
    clamped 0.0-1.0 float to prevent StreamlitAPIException on st.progress().
    """
    val = float(val) if val is not None else 0.0
    val = val / 100.0 if val > 1.0 else val
    return max(0.0, min(val, 1.0))
