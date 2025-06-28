"""
Trading Markets Dashboard
Main application entry point
"""

import streamlit as st
from datetime import datetime
import time

from styles import ULTRA_COMPACT_CSS
from data import fetch_market_data, process_markets, fetch_order_books_batch
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
    
    # Pre-fetch order book data for all top markets in a single batch request
    import time
    with st.spinner("Preparing market data..."):
        start_time = time.time()
        
        # Only fetch for Polymarket markets since we implemented the batch endpoint for Polymarket only
        poly_markets = [m for m in top_markets if m.get('platform') == 'Polymarket']
        
        # Explicitly fetch ALL markets in one batch (no limit)
        order_books_cache = fetch_order_books_batch(
            markets=poly_markets, 
            max_markets=len(poly_markets)  # Fetch ALL Polymarket markets in one batch
        )
        
        # Store in session state for components to use
        st.session_state.order_books_cache = order_books_cache
        
        # Store performance metrics
        batch_time = time.time() - start_time
        st.session_state.batch_fetch_time = batch_time
        st.session_state.batch_fetch_count = len(order_books_cache)
        
        # Calculate estimated time savings compared to individual requests
        # Assume each individual request takes about 0.5 seconds on average
        if len(order_books_cache) > 0:
            estimated_individual_time = len(order_books_cache) * 0.5  # 0.5 seconds per request is a conservative estimate
            st.session_state.time_savings = estimated_individual_time - batch_time
    
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
    
    # Performance metrics
    if hasattr(st.session_state, 'batch_fetch_time') and hasattr(st.session_state, 'batch_fetch_count') and st.session_state.batch_fetch_count > 0:
        st.markdown("---")
        st.subheader("Performance Metrics")
        
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Batch API Calls", "1", help="All markets fetched in a single batch API call")
        
        with metrics_cols[1]:
            st.metric("Markets Fetched", st.session_state.batch_fetch_count, 
                     help=f"All {st.session_state.batch_fetch_count} markets fetched in one request")
        
        with metrics_cols[2]:
            st.metric("Batch Time", f"{st.session_state.batch_fetch_time:.2f} sec", 
                     help="Time taken for the batch request")
            
        with metrics_cols[3]:
            if hasattr(st.session_state, 'time_savings'):
                time_saved = st.session_state.time_savings
                st.metric("Time Saved", f"{time_saved:.2f} sec", 
                         help=f"Estimated time saved vs. {st.session_state.batch_fetch_count} individual requests")
        
        # Add detailed explanation        
        st.info("⚡ **Batch API Optimization**: All order books are fetched in a single API call instead of making separate requests for each market. This reduces API rate limiting issues and improves load times.")
        
        # Add a technical note
        st.caption("Technical note: Using the `/books` batch endpoint instead of multiple `/book` requests")
    
    # Footer
    st.caption(f"*Updated: {datetime.now().strftime('%H:%M:%S')} | Data: Live APIs*")


if __name__ == "__main__":
    main()
