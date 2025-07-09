#!/usr/bin/env python3
"""
Demo script for the arbitrage platform
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_configuration():
    """Test configuration system"""
    print("🔧 Testing configuration system...")
    
    try:
        from backend.core.config import config
        
        # Test basic configuration access
        min_profit = config.get("arbitrage.min_profit_threshold", 0.05)
        print(f"   - Min profit threshold: {min_profit}")
        
        poly_fee = config.get("platforms.polymarket.fee_rate", 0.02)
        print(f"   - Polymarket fee rate: {poly_fee}")
        
        kalshi_fee = config.get("platforms.kalshi.fee_rate", 0.01)
        print(f"   - Kalshi fee rate: {kalshi_fee}")
        
        print("✅ Configuration system working")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_market_matching():
    """Test market matching with sample data"""
    print("🔗 Testing market matching...")
    
    try:
        from backend.core.market_matcher import MarketMatcher
        
        # Sample market data
        poly_markets = [
            {
                "id": "poly_1",
                "question": "Will Donald Trump win the 2024 US Presidential Election?",
                "volume_24hr": 1000
            },
            {
                "id": "poly_2", 
                "question": "Will the Democrats control the House after 2024?",
                "volume_24hr": 500
            }
        ]
        
        kalshi_markets = [
            {
                "id": "PRES-24",
                "question": "Will Trump be President in 2024?",
                "volume_24hr": 800
            },
            {
                "id": "HOUSE-24",
                "question": "Will Democrats control House in 2024?",
                "volume_24hr": 600
            }
        ]
        
        matcher = MarketMatcher()
        matches = matcher.find_equivalent_markets(poly_markets, kalshi_markets)
        
        print(f"   - Found {len(matches)} matches")
        for match in matches:
            print(f"     * {match.match_type} match (confidence: {match.confidence:.2f})")
            print(f"       Polymarket: {match.polymarket_question[:50]}...")
            print(f"       Kalshi: {match.kalshi_question[:50]}...")
        
        print("✅ Market matching working")
        return True
        
    except Exception as e:
        print(f"❌ Market matching test failed: {e}")
        return False

def test_arbitrage_detection():
    """Test arbitrage detection with sample data"""
    print("💰 Testing arbitrage detection...")
    
    try:
        from backend.core.arbitrage_detector import ArbitrageDetector
        from backend.core.market_matcher import MarketMatch
        
        # Sample data with price discrepancy
        poly_data = {
            "poly_1": {
                "id": "poly_1",
                "question": "Will Trump win 2024?",
                "yes_price": 0.45,
                "no_price": 0.55,
                "volume_24hr": 1000
            }
        }
        
        kalshi_data = {
            "PRES-24": {
                "id": "PRES-24",
                "question": "Will Trump be President in 2024?",
                "yes_price": 0.50,
                "no_price": 0.50,
                "volume_24hr": 800
            }
        }
        
        # Sample match
        matches = [
            MarketMatch(
                polymarket_id="poly_1",
                kalshi_id="PRES-24",
                polymarket_question="Will Trump win 2024?",
                kalshi_question="Will Trump be President in 2024?",
                confidence=0.9,
                match_type="manual",
                notes="Test match"
            )
        ]
        
        detector = ArbitrageDetector()
        opportunities = detector.detect_opportunities(matches, poly_data, kalshi_data)
        
        print(f"   - Found {len(opportunities)} opportunities")
        for opp in opportunities:
            print(f"     * {opp.strategy} on {opp.outcome}")
            print(f"       Profit: {opp.profit_percentage:.1%} (${opp.profit_potential:.2f})")
            print(f"       Confidence: {opp.confidence_score:.1%}")
        
        print("✅ Arbitrage detection working")
        return True
        
    except Exception as e:
        print(f"❌ Arbitrage detection test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("🗄️  Testing database...")
    
    try:
        from backend.data.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Test database connection
        session = db.get_session()
        session.close()
        
        print("   - Database connection successful")
        print("   - Tables created/verified")
        
        print("✅ Database working")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Main demo function"""
    print("🎯 Arbitrage Platform Demo")
    print("=" * 40)
    
    tests = [
        test_configuration,
        test_database,
        test_market_matching,
        test_arbitrage_detection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
            print()
    
    print("=" * 40)
    print("📊 Results Summary")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! System is ready.")
        print("\nTo run the full application:")
        print("   python scripts/setup.py")
        print("   streamlit run frontend/app.py")
    else:
        print("⚠️  Some tests failed. Check dependencies:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
