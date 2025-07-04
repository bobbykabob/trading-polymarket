#!/usr/bin/env python3
"""
Test script to debug Kalshi market history issues
"""

import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from kalshi_api import KalshiAPI

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_kalshi_history():
    """Test Kalshi market history functionality"""
    
    print("Testing Kalshi Market History...")
    print("=" * 50)
    
    # Initialize API
    kalshi = KalshiAPI()
    
    # First, get some markets to test with
    print("\n1. Fetching Kalshi markets...")
    try:
        markets = kalshi.get_markets(limit=5)
        if not markets:
            print("❌ No markets returned")
            return
        
        print(f"✅ Got {len(markets)} markets")
        for i, market in enumerate(markets[:3]):
            print(f"   {i+1}. {market['id']}: {market['question'][:60]}...")
        
    except Exception as e:
        print(f"❌ Error fetching markets: {e}")
        return
    
    # Test history for the first market
    test_market = markets[0]
    market_id = test_market['id']
    
    print(f"\n2. Testing history for market: {market_id}")
    print(f"   Question: {test_market['question']}")
    print("-" * 50)
    
    try:
        history = kalshi.get_market_history(market_id, days=7)
        
        if history:
            print("✅ History data received!")
            print(f"   Market ID: {history.get('market_id')}")
            
            token_histories = history.get('token_histories', {})
            print(f"   Token histories keys: {list(token_histories.keys())}")
            
            for token, data in token_histories.items():
                print(f"   {token}: {len(data)} data points")
                if data:
                    first_point = data[0]
                    last_point = data[-1]
                    print(f"     First: {first_point}")
                    print(f"     Last: {last_point}")
            
            outcome_map = history.get('outcome_token_map', {})
            print(f"   Outcome token map: {outcome_map}")
            
        else:
            print("❌ No history data returned")
            
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing with different market...")
    if len(markets) > 1:
        test_market2 = markets[1]
        market_id2 = test_market2['id']
        print(f"   Testing: {market_id2}")
        
        try:
            history2 = kalshi.get_market_history(market_id2, days=3)  # Try shorter period
            if history2:
                print("✅ Second market history worked!")
                token_histories = history2.get('token_histories', {})
                for token, data in token_histories.items():
                    print(f"   {token}: {len(data)} data points")
            else:
                print("❌ Second market history failed")
        except Exception as e:
            print(f"❌ Error with second market: {e}")

if __name__ == "__main__":
    test_kalshi_history()
