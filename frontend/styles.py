"""
CSS styles for the trading markets dashboard
"""

ULTRA_COMPACT_CSS = """
<style>
    .main .block-container {
        padding-top: 0.3rem;
        padding-bottom: 0.3rem;
    }
    .metric-container {
        background-color: rgba(255, 255, 255, 0.01);
        padding: 0.1rem;
        border-radius: 0.2rem;
        margin-bottom: 0.1rem;
        border: none;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.01);
        padding: 0.05rem 0.1rem;
        border-radius: 0.1rem;
        margin-bottom: 0.05rem;
    }
    .stExpander {
        margin-bottom: 0.1rem;
        border-radius: 0.15rem !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    .stExpander > div > div > div {
        padding: 0.1rem !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.01);
        border: none;
        padding: 0.05rem;
        border-radius: 0.1rem;
        box-shadow: none;
    }
    div[data-testid="metric-container"] > div {
        color: #FAFAFA;
    }
    h1 {
        font-size: 1.3rem !important;
        margin-bottom: 0.1rem !important;
        color: #FAFAFA;
    }
    h2 {
        font-size: 1rem !important;
        margin-bottom: 0.1rem !important;
        margin-top: 0.3rem !important;
        color: #FAFAFA;
    }
    h3 {
        font-size: 0.9rem !important;
        margin-bottom: 0.05rem !important;
        margin-top: 0.1rem !important;
        color: #FAFAFA;
    }
    .stSelectbox > div > div {
        padding: 0.05rem;
        background-color: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stButton > button {
        background-color: #8B5CF6;
        color: white;
        border: none;
        border-radius: 0.1rem;
        padding: 0.1rem 0.4rem;
        font-size: 0.9rem;
    }
    .stButton > button:hover {
        background-color: #7C3AED;
        border: none;
    }
    .stCheckbox > label {
        color: #FAFAFA;
        font-size: 0.9rem;
    }
    /* Dark mode plotly charts */
    .js-plotly-plot .plotly .modebar {
        background-color: rgba(255, 255, 255, 0.05);
    }
    /* Custom divider */
    hr {
        border-color: rgba(255, 255, 255, 0.05);
        margin: 0.1rem 0;
    }
    /* Make text smaller and more condensed */
    p {
        font-size: 0.85rem !important;
        line-height: 1.1 !important;
        margin: 0.05rem 0 !important;
    }
    /* Compact table-like rows */
    div[data-testid="column"] {
        padding: 0.05rem !important;
    }
</style>"""
