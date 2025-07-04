#!/usr/bin/env python3
"""
Test script for Kalshi API implementation
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from kalshi_api import KalshiAPI

def test_kalshi_api():
    """Test the Kalshi API implementation"""
    print("Testing Kalshi API implementation...")
    
    # Initialize API client
    kalshi_api = KalshiAPI()
    
    # Test get_markets
    print("\n1. Testing get_markets()...")
    markets = kalshi_api.get_markets(limit=5)
    print(f"   Retrieved {len(markets)} markets")
    
    if markets:
        market = markets[0]
        print(f"   Sample market: {market['question']}")
        print(f"   Platform: {market['platform']}")
        print(f"   ID: {market['id']}")
        print(f"   Volume 24hr: ${market['volume_24hr']:,}")
        
        # Test get_market_by_id
        print(f"\n2. Testing get_market_by_id() with ID: {market['id']}...")
        market_details = kalshi_api.get_market_by_id(market['id'])
        if market_details:
            print(f"   Retrieved market details successfully")
            print(f"   Question: {market_details['question']}")
        else:
            print(f"   Market details returned None (expected for mock data)")
        
        # Test get_market_history
        print(f"\n3. Testing get_market_history() with ID: {market['id']}...")
        history = kalshi_api.get_market_history(market['id'], days=7)
        if history:
            print(f"   Retrieved market history successfully")
            print(f"   Market ID: {history['market_id']}")
            print(f"   Token histories keys: {list(history['token_histories'].keys())}")
        else:
            print(f"   Market history returned None (expected for mock data)")
        
        # Test get_order_book
        print(f"\n4. Testing get_order_book() with ID: {market['id']}...")
        order_book = kalshi_api.get_order_book(market['id'])
        if order_book:
            print(f"   Retrieved order book successfully")
            print(f"   Market ID: {order_book['market_id']}")
            print(f"   Order book keys: {list(order_book['order_books'].keys())}")
        else:
            print(f"   Order book returned None (expected for mock data)")
        
        # Test get_token_ids_for_market
        print(f"\n5. Testing get_token_ids_for_market() with ID: {market['id']}...")
        token_ids = kalshi_api.get_token_ids_for_market(market['id'])
        if token_ids:
            print(f"   Retrieved token IDs: {token_ids}")
        else:
            print(f"   Token IDs returned None")
        
        # Test get_books
        print(f"\n6. Testing get_books() with multiple market IDs...")
        market_ids = [m['id'] for m in markets[:3]]
        books = kalshi_api.get_books(market_ids)
        if books:
            print(f"   Retrieved order books for {len(books)} markets")
            for market_id in books:
                print(f"     - {market_id}: {list(books[market_id]['order_books'].keys()) if 'order_books' in books[market_id] else 'No order books'}")
        else:
            print(f"   Books returned None (expected for mock data)")
    
    print("\n✅ Kalshi API test completed!")

if __name__ == "__main__":
    test_kalshi_api()
