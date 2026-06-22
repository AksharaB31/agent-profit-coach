import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Main Container Styling */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Metric Cards */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #1e3a8a;
            font-weight: 700;
        }
        
        /* Custom Card styling for sections */
        .enterprise-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
        }
        
        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.75em;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
            margin-right: 5px;
        }
        .badge-success { background-color: #d1fae5; color: #065f46; }
        .badge-warning { background-color: #fef3c7; color: #92400e; }
        .badge-danger { background-color: #fee2e2; color: #991b1b; }
        .badge-primary { background-color: #dbeafe; color: #1e40af; }
        .badge-dark { background-color: #f3f4f6; color: #1f2937; }
        
        /* Headers */
        h1, h2, h3 {
            color: #111827;
            font-family: 'Inter', sans-serif;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
        }
        </style>
    """, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "primary"):
    """Render an HTML badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'

def format_currency(value: float, currency: str = "EUR") -> str:
    """Format float into currency string."""
    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "AED": "د.إ"}
    sym = symbols.get(currency, currency)
    return f"{sym}{value:,.2f}"
