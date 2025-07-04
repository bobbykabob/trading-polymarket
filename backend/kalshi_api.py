"""
Kalshi API Client
Handles interactions with Kalshi's trading API
"""

import requests
import logging
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

# Ensure INFO logs are shown
logging.basicConfig(level=logging.DEBUG)
load_dotenv()

class KalshiAPI:
    def __init__(self):
        # the Base URL is guaranteed correct as per Kalshi's API documentation
        self.base_url = "https://api.elections.kalshi.com/trade-api/v2"
        self.api_key = os.getenv("KALSHI_API_KEY", "")
        self.api_secret = os.getenv("KALSHI_API_SECRET", "")
        self.session = requests.Session()
        
        # Set up authentication headers if credentials are available
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def get_markets(self, limit: int = 10, archived: bool = False, offset: int = 0, 
                   order_by: str = "volume", ascending: bool = False) -> List[Dict[str, Any]]:
        """
        Get markets from Kalshi API
        Returns markets based on specified ordering and limit
        
        Args:
            limit: Maximum number of markets to return (default: 10)
            archived: Whether to include archived markets (default: False)
            offset: Number of records to skip (default: 0)
            order_by: Field to order results by (default: "volume")
                      Options: "volume", "liquidity", "close_time", etc.
            ascending: Sort direction (default: False = descending order)
        
        Returns:
            List of market dictionaries
        """
        try:
            url = f"{self.base_url}/markets"
            params = {
                "limit": limit,
                "cursor": offset,
                "status": "open" if not archived else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            markets_data = data.get("markets", [])
            
            # Process and clean the market data
            processed_markets = []
            for market in markets_data:
                processed_market = {
                    "id": market.get("ticker"),
                    "question": market.get("title"),
                    "description": market.get("subtitle", ""),
                    "end_date": market.get("close_time"),
                    "volume_24hr": market.get("volume_24h", 0),
                    "volume": market.get("volume", 0),
                    "liquidity": market.get("liquidity", 0),
                    "yes_price": market.get("yes_bid", 0) / 100 if market.get("yes_bid") else None,  # Convert cents to dollars
                    "no_price": market.get("no_bid", 0) / 100 if market.get("no_bid") else None,   # Convert cents to dollars
                    "platform": "Kalshi"
                }
                processed_markets.append(processed_market)
            
            # Sort by specified field
            if order_by == "volume":
                processed_markets.sort(key=lambda x: x.get('volume_24hr', 0), reverse=not ascending)
            elif order_by == "liquidity":
                processed_markets.sort(key=lambda x: x.get('liquidity', 0), reverse=not ascending)
            elif order_by == "close_time":
                processed_markets.sort(key=lambda x: x.get('end_date', ''), reverse=not ascending)
            
            return processed_markets
            
        except requests.RequestException as e:
            logging.error(f"Error fetching markets from Kalshi: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in get_markets: {e}")
            raise
    
    def get_market_by_id(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific market details by ID (ticker)
        """
        try:
            url = f"{self.base_url}/markets/{market_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            market = data.get("market", {})
            
            return {
                "id": market.get("ticker"),
                "question": market.get("title"),
                "description": market.get("subtitle", ""),
                "end_date": market.get("close_time"),
                "volume_24hr": market.get("volume_24h", 0),
                "volume": market.get("volume", 0),
                "liquidity": market.get("liquidity", 0),
                "yes_price": market.get("yes_bid", 0) / 100 if market.get("yes_bid") else None,
                "no_price": market.get("no_bid", 0) / 100 if market.get("no_bid") else None,
                "platform": "Kalshi",
                "status": market.get("status"),
                "can_close_early": market.get("can_close_early"),
                "category": market.get("category"),
                "yes_ask": market.get("yes_ask", 0) / 100 if market.get("yes_ask") else None,
                "no_ask": market.get("no_ask", 0) / 100 if market.get("no_ask") else None,
            }
            
        except requests.RequestException as e:
            logging.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_market_history(self, market_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Get historical price data for a market using the candlesticks endpoint
        Reference: https://trading-api.readme.io/reference/getmarketcandlesticks-1
        """
        try:
            logging.debug(f"Getting market history for {market_id}, days: {days}")
            
            # First get market details to get the event_ticker (which is the series_ticker)
            url = f"{self.base_url}/markets/{market_id}"
            logging.debug(f"Fetching market details from: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            logging.debug(f"Market details response: {data}")
            
            market = data.get("market", {})
            series_ticker = market.get("event_ticker")
            logging.debug(f"Extracted series_ticker: {series_ticker}")
            
            if not series_ticker:
                logging.error(f"Could not get event_ticker for market {market_id}")
                return None
            
            # Now get candlesticks data
            candlesticks_url = f"{self.base_url}/series/{series_ticker}/markets/{market_id}/candlesticks"
            logging.debug(f"Fetching candlesticks from: {candlesticks_url}")
            
            # Calculate time range for the last N days
            from datetime import datetime, timedelta
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            params = {
                "start_ts": int(start_time.timestamp()),
                "end_ts": int(end_time.timestamp()),
                "period_interval": 60,  # 1 hour intervals (in minutes)
            }
            logging.debug(f"Candlesticks request params: {params}")
            logging.debug(f"Time range: {start_time} to {end_time}")
            
            candlesticks_response = self.session.get(candlesticks_url, params=params)
            logging.debug(f"Candlesticks response status: {candlesticks_response.status_code}")
            candlesticks_response.raise_for_status()
            
            candlesticks_data = candlesticks_response.json()
            logging.debug(f"Candlesticks response data: {candlesticks_data}")
            
            candlesticks = candlesticks_data.get("candlesticks", [])
            logging.debug(f"Number of candlesticks retrieved: {len(candlesticks)}")
            
            # Process candlestick data to match expected format
            processed_history = {
                "market_id": market_id,
                "token_histories": {
                    "yes": [],
                    "no": []
                },
                "outcome_token_map": {
                    "yes": "yes_token",
                    "no": "no_token"
                }
            }
            
            # Convert candlestick data to price points
            for i, candle in enumerate(candlesticks):
                logging.debug(f"Processing candlestick {i}: {candle}")
                
                # Kalshi uses 'end_period_ts' for timestamp, not 'ts'
                timestamp = candle.get("end_period_ts")  # Unix timestamp
                
                # Try to get price from multiple sources in order of preference
                close_price = None
                
                # 1. Try actual traded price first
                price_data = candle.get("price", {})
                if price_data and price_data.get("close") is not None:
                    close_price = price_data.get("close") / 100  # Convert cents to dollars
                
                # 2. If no traded price, use midpoint of bid/ask
                if close_price is None:
                    yes_bid = candle.get("yes_bid", {})
                    yes_ask = candle.get("yes_ask", {})
                    
                    bid_close = yes_bid.get("close") if yes_bid else None
                    ask_close = yes_ask.get("close") if yes_ask else None
                    
                    if bid_close is not None and ask_close is not None and bid_close > 0 and ask_close > 0:
                        # Use midpoint of bid/ask spread
                        midpoint_cents = (bid_close + ask_close) / 2
                        close_price = midpoint_cents / 100  # Convert cents to dollars
                        logging.debug(f"Using bid/ask midpoint: bid={bid_close}, ask={ask_close}, midpoint={close_price}")
                    else:
                        logging.debug(f"Skipping candle due to invalid bid/ask data: bid={bid_close}, ask={ask_close}")
                
                logging.debug(f"Timestamp: {timestamp}, Close price: {close_price}")
                
                if close_price is not None and timestamp:
                    # For Kalshi, we have a single price that represents the "yes" probability
                    # The "no" probability is 1 - yes_probability
                    yes_price = close_price
                    no_price = 1.0 - close_price if close_price <= 1.0 else None
                    
                    logging.debug(f"Yes price: {yes_price}, No price: {no_price}")
                    
                    processed_history["token_histories"]["yes"].append({
                        "t": timestamp * 1000,  # Convert to milliseconds for consistency with Polymarket
                        "p": yes_price
                    })
                    
                    if no_price is not None:
                        processed_history["token_histories"]["no"].append({
                            "t": timestamp * 1000,
                            "p": no_price
                        })
            
            logging.debug(f"Final processed history: yes points={len(processed_history['token_histories']['yes'])}, no points={len(processed_history['token_histories']['no'])}")
            
            return processed_history
            
        except requests.RequestException as e:
            logging.error(f"Error fetching historical data for market {market_id}: {e}")
            logging.debug(f"Request exception details: {type(e).__name__}: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error fetching historical data for market {market_id}: {e}")
            logging.debug(f"Exception details: {type(e).__name__}: {str(e)}", exc_info=True)
            return None
    
    def get_order_book(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order book data for a market
        Returns bid/ask data for yes/no outcomes
        """
        try:
            url = f"{self.base_url}/markets/{market_id}/orderbook"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            logging.debug(f"Kalshi order book response for {market_id}: {data}")
            orderbook = data.get("orderbook", {})
            
            # Ensure orderbook is not None
            if not orderbook:
                orderbook = {}
            
            # Process order book data
            yes_bids = []
            yes_asks = []
            no_bids = []
            no_asks = []
            
            # Process yes side orders - Kalshi format is [[price_cents, size], ...]
            yes_orders = orderbook.get("yes")
            if yes_orders and isinstance(yes_orders, list):
                # In Kalshi, the orders are in format [[price_cents, size], ...]
                # We need to separate bids and asks, but Kalshi might not distinguish them clearly
                # For now, let's treat all yes orders as bids (best available price)
                for order in yes_orders:
                    if len(order) >= 2:
                        price_cents, size = order[0], order[1]
                        yes_bids.append([
                            str(price_cents / 100),  # Convert cents to dollars
                            str(size)
                        ])
            
            # Process no side orders
            no_orders = orderbook.get("no")
            if no_orders and isinstance(no_orders, list):
                for order in no_orders:
                    if len(order) >= 2:
                        price_cents, size = order[0], order[1]
                        no_bids.append([
                            str(price_cents / 100),  # Convert cents to dollars
                            str(size)
                        ])
            
            return {
                'market_id': market_id,
                'order_books': {
                    'Yes': {
                        'token_id': 'yes_token',
                        'bids': yes_bids,
                        'asks': yes_asks
                    },
                    'No': {
                        'token_id': 'no_token',
                        'bids': no_bids,
                        'asks': no_asks
                    }
                }
            }
            
        except requests.RequestException as e:
            logging.error(f"Error fetching order book for market {market_id}: {e}")
            return None
    
    def get_books(self, market_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get multiple order books at once
        Note: Kalshi doesn't have a batch endpoint, so we'll make individual requests
        
        Args:
            market_ids: List of market IDs to fetch order books for
            
        Returns:
            Dictionary containing order books for the requested markets
        """
        if not market_ids:
            logging.error("No market IDs provided to get_books")
            return None
        
        try:
            results = {}
            
            for market_id in market_ids:
                order_book = self.get_order_book(market_id)
                if order_book:
                    results[market_id] = order_book
                    
            return results
                
        except Exception as e:
            logging.error(f"Error fetching order books: {e}")
            return None
    
    def get_token_ids_for_market(self, market_id: str) -> Optional[List[str]]:
        """
        Get token IDs for a market
        For Kalshi, this returns symbolic tokens (yes/no) since they use a different structure
        """
        try:
            # For Kalshi, we return symbolic token identifiers
            return ["yes_token", "no_token"]
        except Exception as e:
            logging.error(f"Error fetching token IDs for market {market_id}: {e}")
            return None
