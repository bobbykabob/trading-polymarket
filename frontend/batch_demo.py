"""
Streamlit app for demonstrating batch order book fetching in the frontend
"""

import streamlit as st
import time
from datetime import datetime
import sys
import os

# Add project directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from data import fetch_market_data, process_markets, fetch_order_books_batch, get_api_clients
from charts import create_order_book_chart

# Page config
st.set_page_config(
    page_title="Batch Order Book Demo",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("🚀 Batch Order Book Fetching Demo")
st.write("This demo shows the performance difference between individual and batch order book requests")

# Initialize session state if needed
if 'demo_markets' not in st.session_state:
    st.session_state.demo_markets = None
    st.session_state.batch_time = None
    st.session_state.order_books_cache = {}
    st.session_state.individual_times = {}

# Controls
st.sidebar.header("Settings")
num_markets = st.sidebar.slider("Number of Markets", min_value=1, max_value=10, value=5)
auto_run = st.sidebar.checkbox("Auto-run Demo", value=False)

# Fetch markets button
fetch_markets = st.sidebar.button("Fetch Markets") or auto_run

# Main content
if fetch_markets or st.session_state.demo_markets is not None:
    if st.session_state.demo_markets is None:
        with st.spinner("Fetching markets..."):
            # Get markets from Polymarket
            polymarket_api, _ = get_api_clients()
            all_markets = polymarket_api.get_markets(limit=20)
            
            # Filter to only markets with token_ids
            valid_markets = []
            for market in all_markets:
                market_id = market.get('id')
                token_ids = polymarket_api.get_token_ids_for_market(market_id)
                if token_ids:
                    market['token_ids'] = token_ids  # Store token_ids for later use
                    valid_markets.append(market)
                    if len(valid_markets) >= num_markets:
                        break
            
            st.session_state.demo_markets = valid_markets[:num_markets]
    
    # Display markets
    st.subheader(f"Selected Markets ({len(st.session_state.demo_markets)})")
    
    for i, market in enumerate(st.session_state.demo_markets):
        st.write(f"{i+1}. **{market.get('question')}**")
        st.caption(f"Market ID: `{market.get('id')}`")
    
    # Batch fetch button
    col1, col2, col3 = st.columns(3)
    
    with col1:
        batch_fetch = st.button("1️⃣ Fetch Using Batch API") or auto_run
    
    with col2:
        individual_fetch = st.button("2️⃣ Fetch Individually")
    
    with col3:
        clear_cache = st.button("🗑️ Clear Cache")
        if clear_cache:
            st.session_state.order_books_cache = {}
            st.session_state.individual_times = {}
            st.session_state.batch_time = None
            st.success("Cache cleared!")
            st.rerun()
    
    # BATCH FETCHING
    if batch_fetch:
        st.subheader("Batch Order Book Fetching")
        
        with st.spinner("Fetching all order books in one batch request..."):
            start_time = time.time()
            
            # Use our batch fetching function
            order_books_cache = fetch_order_books_batch(
                st.session_state.demo_markets, 
                max_markets=len(st.session_state.demo_markets)
            )
            
            batch_time = time.time() - start_time
            st.session_state.batch_time = batch_time
            st.session_state.order_books_cache = order_books_cache
        
        # Show performance metrics
        if st.session_state.batch_time:
            st.success(f"✅ Batch fetching completed in **{st.session_state.batch_time:.3f} seconds**")
            st.info(f"📊 Retrieved {len(st.session_state.order_books_cache)} order books in a single API call")
        
        # Display the order books
        if st.session_state.order_books_cache:
            st.subheader("Order Book Charts (From Batch Request)")
            
            for market_id, order_book_data in st.session_state.order_books_cache.items():
                # Find market details
                market_info = next((m for m in st.session_state.demo_markets if m.get('id') == market_id), None)
                if market_info:
                    market_name = market_info.get('question', f"Market {market_id}")
                    
                    with st.expander(f"{market_name}", expanded=False):
                        fig = create_order_book_chart(order_book_data)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error("Could not create chart for this market")
    
    # INDIVIDUAL FETCHING
    if individual_fetch:
        st.subheader("Individual Order Book Fetching")
        polymarket_api, _ = get_api_clients()
        
        for i, market in enumerate(st.session_state.demo_markets):
            market_id = market.get('id')
            market_name = market.get('question')
            
            with st.spinner(f"Fetching order book for market {i+1}/{len(st.session_state.demo_markets)}..."):
                start_time = time.time()
                
                # Direct API call for each market
                order_book_data = polymarket_api.get_order_book(market_id)
                
                fetch_time = time.time() - start_time
                st.session_state.individual_times[market_id] = fetch_time
                
                if order_book_data:
                    st.success(f"✅ Fetched order book for {market_name} in **{fetch_time:.3f} seconds**")
                    
                    # Store in cache for comparison
                    st.session_state.order_books_cache[market_id] = order_book_data
                else:
                    st.error(f"❌ Failed to fetch order book for {market_name}")
    
    # COMPARISON
    if st.session_state.batch_time and st.session_state.individual_times:
        st.subheader("Performance Comparison")
        
        # Calculate total individual time
        total_individual_time = sum(st.session_state.individual_times.values())
        speedup = total_individual_time / st.session_state.batch_time if st.session_state.batch_time > 0 else 0
        
        comparison_cols = st.columns(2)
        
        with comparison_cols[0]:
            st.metric("Batch Request Time", f"{st.session_state.batch_time:.3f} sec")
            st.caption("Time to fetch all markets in one request")
        
        with comparison_cols[1]:
            st.metric("Individual Requests Time", f"{total_individual_time:.3f} sec")
            st.caption("Sum of individual request times")
        
        st.info(f"🚀 **Speed Improvement**: Batch requests are **{speedup:.1f}x faster**")
        st.info(f"📉 **API Calls**: Reduced from **{len(st.session_state.individual_times)}** to **1** API call")
        
        # Performance visualization
        import pandas as pd
        import plotly.express as px
        
        # Prepare comparison data
        comparison_data = [
            {"Method": "Batch Request", "Time": st.session_state.batch_time, "API Calls": 1},
            {"Method": "Individual Requests", "Time": total_individual_time, 
             "API Calls": len(st.session_state.individual_times)}
        ]
        
        # Create bar chart
        df = pd.DataFrame(comparison_data)
        fig = px.bar(df, x="Method", y="Time", 
                     title="Request Time Comparison",
                     color="Method", 
                     text=[f"{t:.3f}s" for t in df.Time],
                     labels={"Time": "Time (seconds)"})
        
        fig.update_layout(
            height=400,
            xaxis_title="Method",
            yaxis_title="Time (seconds)",
            plot_bgcolor="white",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Set the number of markets and click 'Fetch Markets' to begin the demo")

# Footer
st.markdown("---")
st.caption(f"Demo updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
