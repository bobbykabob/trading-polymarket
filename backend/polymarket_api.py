"""
Polymarket API Client
Handles interactions with Polymarket's CLOB API and Markets API
"""

import requests
import logging
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv


# Ensure INFO logs are shown
load_dotenv()

class PolymarketAPI:
    def get_token_ids_for_market(self, market_id: str) -> Optional[list]:
        """
        Fetch the clobTokenIds (token IDs) for a given market_id from the Gamma API.
        Returns a list of token IDs (as strings) or None if not found.
        """
        try:
            details = self.get_market_by_id(market_id)
            if details and 'clobTokenIds' in details:
                token_ids = details['clobTokenIds']
                # If it's a JSON string, parse it
                import json
                if isinstance(token_ids, str):
                    token_ids = json.loads(token_ids)
                return token_ids
            else:
                logging.warning(f"No clobTokenIds found for market_id {market_id}")
                return None
        except Exception as e:
            logging.error(f"Error fetching token IDs for market {market_id}: {e}")
            return None
    def __init__(self):
        self.host = "https://clob.polymarket.com"
        self.gamma_api_url = "https://gamma-api.polymarket.com"
        self.key = os.getenv("PRIVATE_KEY", "")
        self.chain_id = 137
        self.proxy_address = os.getenv("PROXY_ADDRESS", "")
    
    def get_markets(self, limit: int = 10, archived: bool = False, offset: int = 0, 
               order_by: str = "volume24hr", ascending: bool = False) -> List[Dict[str, Any]]:
        """
        Get markets from Polymarket Gamma API
        Returns markets based on specified ordering and limit
        
        Args:
            limit: Maximum number of markets to return (default: 10)
            archived: Whether to include archived markets (default: False)
            offset: Number of records to skip (default: 0)
            order_by: Field to order results by (default: "volume24hr")
                      Options: "volume24hr", "volume", "liquidity", "endDate", etc.
            ascending: Sort direction (default: False = descending order)
        
        Returns:
            List of market dictionaries
        """
        try:
            url = f"{self.gamma_api_url}/markets"
            params = {
                "limit": limit,
                "archived": archived,
                "offset": offset,
                "order": order_by,
                "ascending": str(ascending).lower(),  # Convert bool to 'true'/'false' string
                "closed": "false",  # Only fetch open markets,
                "active": "true"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            markets_data = response.json()
            
            # Process and clean the market data
            processed_markets = []
            for market in markets_data:
                # Handle string/float conversion for volume fields
                volume_24hr = market.get("volume24hr", 0)
                volume = market.get("volume", 0)
                liquidity = market.get("liquidity", 0)
                
                # Convert strings to floats if needed
                if isinstance(volume_24hr, str):
                    volume_24hr = float(volume_24hr) if volume_24hr else 0
                if isinstance(volume, str):
                    volume = float(volume) if volume else 0
                if isinstance(liquidity, str):
                    liquidity = float(liquidity) if liquidity else 0
                
                processed_market = {
                    "id": market.get("id"),
                    "question": market.get("question"),
                    "description": market.get("description", ""),
                    "end_date": market.get("endDateIso"),
                    "volume_24hr": volume_24hr,
                    "volume": volume,
                    "liquidity": liquidity,
                    "yes_price": None,
                    "no_price": None,
                    "platform": "Polymarket"
                }
                
                # Extract prices from outcomePrices field
                outcome_prices = market.get("outcomePrices")
                outcomes = market.get("outcomes")
                
                if outcome_prices and outcomes:
                    try:
                        # Parse the JSON strings
                        import json
                        if isinstance(outcome_prices, str):
                            prices = json.loads(outcome_prices)
                        else:
                            prices = outcome_prices
                            
                        if isinstance(outcomes, str):
                            outcome_names = json.loads(outcomes)
                        else:
                            outcome_names = outcomes
                        
                        # Map outcomes to prices
                        for i, outcome in enumerate(outcome_names):
                            if i < len(prices):
                                price = float(prices[i])
                                if outcome.lower() == "yes":
                                    processed_market["yes_price"] = price
                                elif outcome.lower() == "no":
                                    processed_market["no_price"] = price
                    except (json.JSONDecodeError, ValueError, IndexError) as e:
                        logging.warning(f"Error parsing prices for market {market.get('id')}: {e}")
                
                processed_markets.append(processed_market)
            
            return processed_markets
            
        except requests.RequestException as e:
            logging.error(f"Error fetching markets from Polymarket: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in get_markets: {e}")
            return []
    
    def get_market_by_id(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get specific market details by ID
        """
        try:
            url = f"{self.gamma_api_url}/markets/{market_id}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_market_history(self, market_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Get historical price data for a market using CLOB timeseries API
        """
        try:
            # Get token IDs for the given market_id
            token_ids = self.get_token_ids_for_market(market_id)
            if not token_ids:
                logging.error(f"No token IDs found for market {market_id}")
                return None
            results = {}
            outcome_map = {}
            # Try to get outcome names for mapping
            details = self.get_market_by_id(market_id)
            outcome_names = None
            if details:
                outcomes = details.get('outcomes')
                import json
                if outcomes:
                    if isinstance(outcomes, str):
                        try:
                            outcome_names = json.loads(outcomes)
                        except Exception:
                            outcome_names = None
                    else:
                        outcome_names = outcomes
            base_url = f"{self.host}/prices-history"
            interval = "max"
            fidelity = 10
            for idx, token_id in enumerate(token_ids):
                params = {
                    "market": token_id,  # Use token_id as the market param
                    "interval": interval,
                    "fidelity": fidelity
                }
                try:
                    response = requests.get(base_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json().get("history", [])
                        results[token_id] = data
                        # Map token_id to outcome name if available
                        if outcome_names and idx < len(outcome_names):
                            outcome_map[outcome_names[idx].lower()] = token_id
                    else:
                        results[token_id] = None
                except Exception:
                    results[token_id] = None
            return {
                "market_id": market_id,
                "token_histories": results,
                "outcome_token_map": outcome_map
            }
        except Exception as e:
            logging.error(f"Error fetching historical data for market {market_id}: {e}")
            return None
        
    def get_order_book(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get order book data for a market using CLOB API
        Returns bid/ask data for each token in the market
        
        Uses the batch endpoint (get_books) to fetch multiple order books at once
        instead of making individual requests for each token
        """
        try:
            # Get token IDs for the given market_id
            token_ids = self.get_token_ids_for_market(market_id)
            if not token_ids:
                logging.error(f"No token IDs found for market {market_id}")
                return None
            
            # Get market details for outcome names
            market_details = self.get_market_by_id(market_id)
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
            
            # Get all order books in a single request using the batch endpoint
            books_data = self.get_books(token_ids)
            if not books_data:
                logging.error(f"Failed to get order books for market {market_id}")
                # Fallback to individual requests if batch request fails
                logging.info(f"Falling back to individual requests for {market_id}")
                
                order_books = {}
                for idx, token_id in enumerate(token_ids):
                    try:
                        url = f"{self.host}/book"
                        params = {"token_id": token_id}
                        
                        response = requests.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            book_data = response.json()
                            
                            # Determine outcome name
                            outcome_name = outcome_names[idx] if idx < len(outcome_names) else f"Token_{idx}"
                            
                            order_books[outcome_name] = {
                                'token_id': token_id,
                                'bids': book_data.get('bids', []),
                                'asks': book_data.get('asks', [])
                            }
                        else:
                            logging.warning(f"Failed to get order book for token {token_id}: {response.status_code}")
                            
                    except Exception as e:
                        logging.error(f"Error fetching order book for token {token_id}: {e}")
                        continue
                
                return {
                    'market_id': market_id,
                    'order_books': order_books
                }
            
            order_books = {}
            
            # Process the books data
            for idx, token_id in enumerate(token_ids):
                book_data = books_data.get(token_id)
                if book_data:
                    # Determine outcome name
                    outcome_name = outcome_names[idx] if idx < len(outcome_names) else f"Token_{idx}"
                    
                    order_books[outcome_name] = {
                        'token_id': token_id,
                        'bids': book_data.get('bids', []),
                        'asks': book_data.get('asks', [])
                    }
                else:
                    logging.warning(f"No order book data for token {token_id}")
            
            return {
                'market_id': market_id,
                'order_books': order_books
            }
            
        except Exception as e:
            logging.error(f"Error fetching order book for market {market_id}: {e}")
            return None
        
    def get_books(self, token_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get multiple order books at once using the batch endpoint
        https://docs.polymarket.com/developers/CLOB/prices-books/get-books
        
        Args:
            token_ids: List of token IDs to fetch order books for
            
        Returns:
            Dictionary containing order books for the requested tokens.
            Returns an empty dict if no order books exist (which can happen for resolved markets).
        """
        if not token_ids:
            logging.error("No token IDs provided to get_books")
            return None
        
        try:
            url = f"{self.host}/books"
            
            # According to docs, need to format each token ID as a BookParams object
            # Format: [{"token_id": "123"}, {"token_id": "456"}, ...]
            params = [{"token_id": token_id} for token_id in token_ids]
            
            headers = {"Content-Type": "application/json"}
            logging.debug(f"Sending request to {url} with params: {params}")
            
            response = requests.post(url, json=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                books_data = response.json()
                
                # Handle case where the API returns an empty list (no active order books)
                # This happens for markets that have closed/resolved
                if not books_data and isinstance(books_data, list):
                    logging.info(f"No active order books available for tokens {token_ids[:2]}... (likely resolved market)")
                    return {}
                
                # Convert list of books to dictionary keyed by token_id
                result = {}
                for book in books_data:
                    # The token_id field may be in "asset_id" or "tokenId" based on docs
                    token_id = book.get("asset_id") or book.get("tokenId")
                    if token_id:
                        result[token_id] = {"bids": book.get("bids", []), "asks": book.get("asks", [])}
                return result
            else:
                logging.warning(f"Failed to get order books: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching order books: {e}")
            return None
