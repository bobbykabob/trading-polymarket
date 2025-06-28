"""
Data fetching and processing functions
"""

import streamlit as st
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from polymarket_api import PolymarketAPI
from kalshi_api import KalshiAPI


@st.cache_resource
def get_api_clients():
    """Initialize and cache API clients"""
    polymarket_api = PolymarketAPI()
    kalshi_api = KalshiAPI()
    return polymarket_api, kalshi_api


def fetch_market_data(platforms, num_markets):
    """Fetch market data from selected platforms"""
    polymarket_api, kalshi_api = get_api_clients()
    all_markets = []
    
    # Get data from selected platforms
    if "Polymarket" in platforms:
        try:
            poly_markets = polymarket_api.get_markets(limit=max(num_markets * 2, 20))
            all_markets.extend(poly_markets)
        except Exception as e:
            st.error(f"Polymarket error: {e}")
    
    if "Kalshi" in platforms:
        try:
            kalshi_markets = kalshi_api.get_markets(limit=max(num_markets * 2, 20))
            all_markets.extend(kalshi_markets)
        except Exception as e:
            st.error(f"Kalshi error: {e}")
    
    return all_markets


def process_markets(all_markets, num_markets):
    """Sort and filter markets by volume"""
    if not all_markets:
        return []
    
    # Sort by volume and take top N
    all_markets.sort(key=lambda x: x.get('volume_24hr', 0), reverse=True)
    return all_markets[:num_markets]
