"""
Trading Markets Dashboard
Main application entry point
"""

import streamlit as st
from datetime import datetime
import time

from styles import ULTRA_COMPACT_CSS
from data import fetch_market_data, process_markets
from components import render_controls, render_summary_stats, render_table_header, render_market_row
from charts import create_volume_chart, create_order_book_chart

# Configure Streamlit page
st.set_page_config(
    page_title="Top Markets Dashboard",
    page_icon="",
    layout="wide"
)

# Apply custom CSS
st.markdown(ULTRA_COMPACT_CSS, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    st.title("Top Markets by Volume")
    
    # Render controls
    platforms, num_markets, refresh_clicked, auto_refresh = render_controls()
    
    # Handle refresh
    if refresh_clicked:
        st.cache_data.clear()
        st.rerun()
    
    # Validate inputs
    if not platforms:
        st.warning("Please select at least one platform.")
        return
    
    # Fetch and process data
    with st.spinner("Loading..."):
        all_markets = fetch_market_data(platforms, num_markets)
    
    if not all_markets:
        st.error("No data available. Please refresh.")
        return
    
    top_markets = process_markets(all_markets, num_markets)
    
    # Render summary statistics
    render_summary_stats(top_markets)
    
    # Display markets table
    st.subheader(f"Top {num_markets} Markets")
    render_table_header()
    st.divider()
    
    for i, market in enumerate(top_markets, 1):
        render_market_row(market, i)
    
    # Volume chart
    st.markdown("---")
    st.subheader("Volume Chart")
    
    # Debug information
    st.caption(f"Number of markets with volume data: {sum(1 for m in top_markets if m.get('volume_24hr', 0) > 0)}")
    
    # Create and display volume chart
    try:
        volume_chart = create_volume_chart(top_markets)
        st.plotly_chart(volume_chart, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating volume chart: {str(e)}")
        st.write("Market data:", [{"name": m.get('question', 'Unknown')[:20], "volume": m.get('volume_24hr', 0)} for m in top_markets[:3]])
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(60)
        st.rerun()
    
    # Footer
    st.caption(f"*Updated: {datetime.now().strftime('%H:%M:%S')} | Data: Live APIs*")


if __name__ == "__main__":
    main()
