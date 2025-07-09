"""
UI components for the trading markets dashboard
"""

import streamlit as st
from frontend.utils import format_volume, format_price, get_platform_icon, get_trend_icon, format_end_date
from frontend.charts import create_price_history_chart, create_order_book_chart
from frontend.data import get_api_clients


def render_controls():
    """Render the control panel"""
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        platforms = st.multiselect(
            "Platforms",
            ["Polymarket", "Kalshi"],
            default=["Polymarket"],
            help="Choose platforms"
        )
    
    with col2:
        num_markets = st.selectbox(
            "Markets",
            options=[5, 10, 15, 20, 25],
            index=0,
            help="Number of markets to display"
        )
    
    with col3:
        refresh_clicked = st.button("Refresh", type="primary")
    
    with col4:
        auto_refresh = st.checkbox("Auto-refresh")
    
    with col5:
        st.caption("*Live data*")
    
    return platforms, num_markets, refresh_clicked, auto_refresh


def render_summary_stats(top_markets):
    """Render summary statistics"""
    total_volume = sum(market.get('volume_24hr', 0) for market in top_markets)
    avg_volume = total_volume / len(top_markets) if top_markets else 0
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Markets", len(top_markets))
    
    with summary_col2:
        st.metric("Total Volume", format_volume(total_volume))
    
    with summary_col3:
        st.metric("Avg Volume", format_volume(avg_volume))
    
    with summary_col4:
        highest_vol = max((market.get('volume_24hr', 0) for market in top_markets), default=0)
        st.metric("Highest", format_volume(highest_vol))


def render_table_header():
    """Render the table header"""
    header_cols = st.columns([0.3, 2.5, 0.6, 0.6, 0.4, 0.4, 0.5, 0.3])
    with header_cols[0]:
        st.markdown("**#**")
    with header_cols[1]:
        st.markdown("**Market Question**")
    with header_cols[2]:
        st.markdown("**Volume**")
    with header_cols[3]:
        st.markdown("**Yes**")
    with header_cols[4]:
        st.markdown("**No**")
    with header_cols[5]:
        st.markdown("**Platform**")
    with header_cols[6]:
        st.markdown("**End Date**")
    with header_cols[7]:
        st.markdown("**Trend**")


def render_market_row(market, rank):
    """Render a single market row"""
    yes_price = market.get('yes_price', 0) or 0
    no_price = market.get('no_price', 0) or 0
    volume = market.get('volume_24hr', 0)
    platform = market.get('platform', 'Unknown')
    question = market.get('question', 'Unknown Market')
    
    # Ultra-condensed single row
    cols = st.columns([0.3, 2.5, 0.6, 0.6, 0.4, 0.4, 0.5, 0.3])
    
    with cols[0]:
        st.markdown(f"**{rank}**")
    
    with cols[1]:
        with st.expander(f"{question[:45]}{'...' if len(question) > 45 else ''}", expanded=False):
            render_market_details(market)
    
    with cols[2]:
        st.markdown(f"**{format_volume(volume)}**")
    with cols[3]:
        st.markdown(f"🟢 **{format_price(yes_price)}**")
    with cols[4]:
        st.markdown(f"🔴 **{format_price(no_price)}**")
    with cols[5]:
        st.markdown(f"{get_platform_icon(platform)}")
    with cols[6]:
        st.markdown(f"**{format_end_date(market.get('end_date', 'Unknown'))}**")
    with cols[7]:
        st.markdown(get_trend_icon(yes_price))


def render_market_details(market):
    """Render detailed market information inside expander"""
    question = market.get('question', 'Unknown Market')
    
    # Full details inside expander
    st.markdown(f"**{question}**")
    
    # Description
    description = market.get('description', '')
    if description and len(description) > 10:
        st.caption(description)
    st.caption(f"**ID:** `{market.get('id', 'Unknown')}`")
    
    # Historical price chart and order book
    market_id = market.get('id')
    platform = market.get('platform', 'Unknown')
    
    if market_id:
        try:
            polymarket_api, kalshi_api = get_api_clients()
            
            # Determine which API to use based on the market's platform
            if platform == "Kalshi":
                api_client = kalshi_api
                st.caption(f"🔵 Kalshi Market Data")
            else:
                api_client = polymarket_api
                st.caption(f"🟣 Polymarket Data")
            
            # Use container to give charts more space in the UI
            with st.container():
                # Create tabs with better styling
                tab_style = """
                <style>
                button[data-baseweb="tab"] {
                    font-size: 1.1rem;
                    font-weight: 500;
                }
                </style>
                """
                st.markdown(tab_style, unsafe_allow_html=True)
                
                price_tab, depth_tab = st.tabs(["Price History", "Order Book Depth"])
                
                with price_tab:
                    st.markdown("### 7-Day Price History")
                    with st.spinner("Loading price history data..."):
                        historical_data = api_client.get_market_history(market_id, days=7)
                        
                        if historical_data:
                            fig = create_price_history_chart(historical_data)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                            else:
                                st.info("No historical price data available for this market")
                        else:
                            st.info("No historical data available")
                
                with depth_tab:
                    st.markdown("## Order Book Depth Chart")
                    with st.spinner("Loading order book data..."):
                        # Import the batch fetching function
                        from frontend.data import fetch_order_books_batch
                        
                        # Check if we have pre-fetched order book data in session state
                        order_book_data = None
                        if hasattr(st.session_state, 'order_books_cache') and market_id in st.session_state.order_books_cache:
                            order_book_data = st.session_state.order_books_cache[market_id]
                            st.caption("⚡ Using pre-fetched order book data from batch request")
                        else:
                            # Cache miss - we need to fetch this market's order book
                            st.caption("📡 Fetching order book data for this market")
                            
                            # Fetch using the batch function but only for this one market
                            # This will still use the more efficient batch endpoint for supported platforms
                            order_books_cache = fetch_order_books_batch([market], max_markets=1)
                            if market_id in order_books_cache:
                                order_book_data = order_books_cache[market_id]
                                
                                # Update the session state cache
                                if not hasattr(st.session_state, 'order_books_cache'):
                                    st.session_state.order_books_cache = {}
                                st.session_state.order_books_cache[market_id] = order_book_data
                            else:
                                # Last resort fallback to individual API request
                                st.warning(f"⚠️ Falling back to individual {platform} API request")
                                order_book_data = api_client.get_order_book(market_id)
                        
                        if order_book_data and order_book_data.get('order_books'):
                            # Add a summary of the order book
                            total_bids = 0
                            total_asks = 0
                            
                            for outcome, data in order_book_data['order_books'].items():
                                # Handle different formats between Polymarket and Kalshi
                                bids = data.get('bids', [])
                                asks = data.get('asks', [])
                                
                                # Process bids - handle both formats
                                for bid in bids:
                                    try:
                                        if isinstance(bid, list) and len(bid) >= 2:
                                            # Kalshi format: [price, size] 
                                            total_bids += float(bid[1])
                                        elif isinstance(bid, dict):
                                            # Polymarket format: {'price': ..., 'size': ...}
                                            total_bids += float(bid.get('size', 0))
                                    except (ValueError, TypeError):
                                        pass
                                
                                # Process asks - handle both formats  
                                for ask in asks:
                                    try:
                                        if isinstance(ask, list) and len(ask) >= 2:
                                            # Kalshi format: [price, size]
                                            total_asks += float(ask[1])
                                        elif isinstance(ask, dict):
                                            # Polymarket format: {'price': ..., 'size': ...}
                                            total_asks += float(ask.get('size', 0))
                                    except (ValueError, TypeError):
                                        pass
                            
                            # Large formatted dollar values for metrics
                            formatted_bids = f"${total_bids/1000000:.1f}M" if total_bids >= 1000000 else f"${total_bids/1000:.1f}K" 
                            formatted_asks = f"${total_asks/1000000:.1f}M" if total_asks >= 1000000 else f"${total_asks/1000:.1f}K"
                            
                            # Custom metric styling
                            metric_style = """
                            <style>
                            [data-testid="stMetricValue"] {
                                font-size: 2rem !important;
                                font-weight: 700 !important;
                                color: white !important;
                            }
                            [data-testid="stMetricLabel"] {
                                font-size: 1rem !important;
                                font-weight: 600 !important;
                            }
                            </style>
                            """
                            st.markdown(metric_style, unsafe_allow_html=True)
                            
                            # Display summary metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Bid Volume", formatted_bids)
                            with col2:
                                st.metric("Total Ask Volume", formatted_asks)
                            
                            # Create and display the chart
                            fig = create_order_book_chart(order_book_data)
                            if fig:
                                st.plotly_chart(fig, use_container_width=True, config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    "modeBarButtonsToAdd": ["zoom2d", "pan2d", "resetScale2d"],
                                    "modeBarButtonsToRemove": ["lasso2d", "select2d", "toggleSpikelines", "autoScale2d"]
                                })
                            else:
                                st.info("Could not generate order book chart with the available data")
                        else:
                            st.info(f"No order book data available for this {platform} market")
                
        except Exception as e:
            st.caption(f"Chart unavailable: {str(e)[:30]}...")
    else:
        st.caption("No market ID available")
