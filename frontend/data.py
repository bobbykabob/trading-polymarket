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


@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_order_books_batch(markets, max_markets=None):
    """
    Fetch order books for multiple markets in batch to improve efficiency
    
    Args:
        markets: List of markets to fetch order books for
        max_markets: Maximum number of markets to process in one batch.
                     If None or equal to number of markets, fetches ALL markets in a single batch.
    
    Returns:
        Dictionary mapping market_id to order book data
    """
    polymarket_api, _ = get_api_clients()
    
    # Process only Polymarket markets with IDs
    poly_markets = [m for m in markets if m.get('platform') == 'Polymarket' and m.get('id')]
    
    # Limit the number of markets to process (if max_markets is None, process all)
    if max_markets is None or max_markets >= len(poly_markets):
        markets_to_process = poly_markets  # Process ALL markets in one batch
    else:
        markets_to_process = poly_markets[:max_markets]
    
    if not markets_to_process:
        return {}
    
    # Get all token IDs for all markets
    all_token_ids = []
    market_token_map = {}  # Maps token_ids back to their market_id
    market_outcome_map = {}  # Maps market_id to outcome names
    
    for market in markets_to_process:
        market_id = market.get('id')
        
        # Get token IDs for this market
        token_ids = polymarket_api.get_token_ids_for_market(market_id)
        if not token_ids:
            continue
            
        # Get market details for outcome names
        market_details = polymarket_api.get_market_by_id(market_id)
        outcome_names = []
        if market_details:
            outcomes = market_details.get('outcomes')
            import json
            if outcomes:
                if isinstance(outcomes, str):
                    try:
                        outcome_names = json.loads(outcomes)
                    except Exception:
                        outcome_names = []
                else:
                    outcome_names = outcomes
                    
        market_outcome_map[market_id] = outcome_names
        
        # Track which token belongs to which market
        for token_id in token_ids:
            all_token_ids.append(token_id)
            market_token_map[token_id] = market_id
    
    if not all_token_ids:
        return {}
    
    # Fetch all books in a single batch request
    all_books_data = polymarket_api.get_books(all_token_ids)
    if not all_books_data:
        return {}
    
    # Organize results by market
    results = {}
    
    for token_id, book_data in all_books_data.items():
        market_id = market_token_map.get(token_id)
        if not market_id:
            continue
            
        # Initialize market entry if needed
        if market_id not in results:
            results[market_id] = {
                'market_id': market_id,
                'order_books': {}
            }
            
        # Get outcome names for this market
        outcome_names = market_outcome_map.get(market_id, [])
        
        # Find index of this token in the market's token list
        token_ids = polymarket_api.get_token_ids_for_market(market_id)
        if token_ids:
            try:
                idx = token_ids.index(token_id)
                outcome_name = outcome_names[idx] if idx < len(outcome_names) else f"Token_{idx}"
            except ValueError:
                outcome_name = f"Unknown_{token_id[-4:]}"
                
            # Add this book to the market's order books
            results[market_id]['order_books'][outcome_name] = {
                'token_id': token_id,
                'bids': book_data.get('bids', []),
                'asks': book_data.get('asks', [])
            }
    
    return results
