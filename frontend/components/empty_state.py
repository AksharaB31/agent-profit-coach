import streamlit as st

def render_empty_state():
    html = """<div style="text-align: center; padding: 40px; margin-top: 20px;">
<h2>✈️ Ready for Takeoff</h2>
<p style="margin-bottom: 30px;">Enter your route details in the sidebar and click <strong>Analyze Route</strong> to generate AI-powered airline intelligence.</p>
<div style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: left;">
<div style="flex: 1; min-width: 200px; padding: 20px; margin: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2);">
<h3>🔍 Live Analysis</h3>
<p>We analyze live pricing and historical margins to find the best options.</p>
</div>
<div style="flex: 1; min-width: 200px; padding: 20px; margin: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2);">
<h3>🛡️ Reliability</h3>
<p>We calculate supplier cancellation risks and conversion probabilities.</p>
</div>
<div style="flex: 1; min-width: 200px; padding: 20px; margin: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.2);">
<h3>💰 Max Profit</h3>
<p>Our AI ranks options to maximize your agency's bottom line.</p>
</div>
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)
