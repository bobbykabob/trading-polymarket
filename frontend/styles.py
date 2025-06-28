"""
CSS styles for the trading markets dashboard
"""

ULTRA_COMPACT_CSS = """
<style>
    /* Overall app styling */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    /* Dark background and better contrast */
    .stApp {
        background-color: #121212;
    }
    
    /* Better styling for metrics */
    .metric-container {
        background-color: rgba(30, 30, 30, 0.6);
        padding: 0.2rem;
        border-radius: 0.3rem;
        margin-bottom: 0.2rem;
        border: 1px solid rgba(100,100,100,0.2);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Improve metrics display */
    .stMetric {
        background-color: rgba(30, 30, 30, 0.6);
        padding: 0.1rem;
        border-radius: 0.2rem;
        margin-bottom: 0.1rem;
    }
    
    /* Better expander styling */
    .stExpander {
        margin-bottom: 0.2rem;
        border-radius: 0.3rem !important;
        border: 1px solid rgba(100,100,100,0.2) !important;
        background-color: rgba(30, 30, 30, 0.6);
    }
    
    .stExpander > div > div > div {
        padding: 0.25rem !important;
    }
    
    /* Better metric styling */
    div[data-testid="metric-container"] {
        background-color: rgba(30, 30, 30, 0.6);
        border: 1px solid rgba(100,100,100,0.15);
        padding: 0.15rem;
        border-radius: 0.25rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    div[data-testid="metric-container"] > div {
        color: #FFFFFF;
    }
    
    /* Improved header styling */
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.3rem !important;
        color: #FFFFFF;
        font-weight: 600;
    }
    
    h2 {
        font-size: 1.2rem !important;
        margin-bottom: 0.2rem !important;
        margin-top: 0.5rem !important;
        color: #FFFFFF;
        font-weight: 500;
    }
    
    h3 {
        font-size: 1rem !important;
        color: #FFFFFF;
        margin-top: 0.4rem;
        margin-bottom: 0.3rem;
        font-weight: 500;
    }
    
    /* Improved tab styling */
    button[data-baseweb="tab"] {
        background-color: rgba(30, 30, 30, 0.6) !important;
        border-radius: 5px 5px 0 0 !important;
        border: 1px solid rgba(100,100,100,0.2) !important;
        border-bottom: none !important;
        padding: 0.5rem 1rem !important;
        margin-right: 0.3rem !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(70, 70, 70, 0.6) !important;
        border-bottom: 2px solid #8B5CF6 !important;
    }
    
    div[role="tablist"] {
        border-bottom: 1px solid rgba(100,100,100,0.2) !important;
    }
    
    /* Chart styling to match the screenshot */
    .js-plotly-plot .plotly .main-svg {
        background-color: transparent !important;
    }
    
    .plotly-chart-container {
        margin-top: 0.5rem;
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: rgba(15, 15, 15, 0.5);
        border: 1px solid rgba(100,100,100,0.15);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Better styling for tab content */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 10px 5px !important;
        background-color: rgba(15, 15, 15, 0.7);
        border-radius: 0 0 5px 5px;
        border: 1px solid rgba(100,100,100,0.2);
        border-top: none;
    }
    
    /* Fix chart control buttons */
    .modebar-container {
        background-color: rgba(30, 30, 30, 0.7) !important;
        border-radius: 4px;
    }
    
    .modebar-btn svg {
        fill: white !important;
    }
    
    /* Style the metrics to look like the screenshot */
    .stMetric {
        background-color: transparent !important;
        padding: 0.2rem 0 !important;
    }
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
