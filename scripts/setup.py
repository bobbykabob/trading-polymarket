#!/usr/bin/env python3
"""
Setup script for the arbitrage platform
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.data.database import DatabaseManager
    from backend.core.config import config
    from backend.core.monitor import monitor
    print("✅ All backend modules loaded successfully")
except ImportError as e:
    print(f"❌ Error importing backend modules: {e}")
    print("Make sure you have installed all dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('arbitrage.log'),
            logging.StreamHandler()
        ]
    )

def setup_database():
    """Initialize the database"""
    print("🗄️  Setting up database...")
    try:
        db = DatabaseManager()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_apis():
    """Test API connections"""
    print("🔌 Testing API connections...")
    
    try:
        from backend.polymarket_api import PolymarketAPI
        from backend.kalshi_api import KalshiAPI
        
        # Test Polymarket API
        poly_api = PolymarketAPI()
        poly_markets = poly_api.get_markets(limit=2)
        if poly_markets:
            print("✅ Polymarket API connection successful")
        else:
            print("⚠️  Polymarket API connection failed or returned no data")
        
        # Test Kalshi API
        kalshi_api = KalshiAPI()
        kalshi_markets = kalshi_api.get_markets(limit=2)
        if kalshi_markets:
            print("✅ Kalshi API connection successful")
        else:
            print("⚠️  Kalshi API connection failed or returned no data")
            
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_market_matching():
    """Test market matching functionality"""
    print("🔗 Testing market matching...")
    
    try:
        from backend.core.market_matcher import MarketMatcher
        from backend.polymarket_api import PolymarketAPI
        from backend.kalshi_api import KalshiAPI
        
        # Get sample markets
        poly_api = PolymarketAPI()
        kalshi_api = KalshiAPI()
        
        poly_markets = poly_api.get_markets(limit=3)
        kalshi_markets = kalshi_api.get_markets(limit=3)
        
        if not poly_markets or not kalshi_markets:
            print("⚠️  Could not get sample markets for testing")
            return False
        
        # Test matching
        matcher = MarketMatcher()
        matches = matcher.find_equivalent_markets(poly_markets, kalshi_markets)
        
        print(f"✅ Market matching test successful: {len(matches)} matches found")
        
        for match in matches[:2]:  # Show first 2 matches
            print(f"   - {match.match_type} match: {match.confidence:.2f} confidence")
            print(f"     Polymarket: {match.polymarket_question[:40]}...")
            print(f"     Kalshi: {match.kalshi_question[:40]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Market matching test failed: {e}")
        return False

def test_arbitrage_detection():
    """Test arbitrage detection"""
    print("💰 Testing arbitrage detection...")
    
    try:
        from backend.core.arbitrage_detector import ArbitrageDetector
        from backend.core.market_matcher import MarketMatcher
        from backend.polymarket_api import PolymarketAPI
        from backend.kalshi_api import KalshiAPI
        
        # Get sample data
        poly_api = PolymarketAPI()
        kalshi_api = KalshiAPI()
        
        poly_markets = poly_api.get_markets(limit=5)
        kalshi_markets = kalshi_api.get_markets(limit=5)
        
        if not poly_markets or not kalshi_markets:
            print("⚠️  Could not get sample markets for testing")
            return False
        
        # Find matches
        matcher = MarketMatcher()
        matches = matcher.find_equivalent_markets(poly_markets, kalshi_markets)
        
        if not matches:
            print("⚠️  No market matches found for arbitrage testing")
            return False
        
        # Test arbitrage detection
        detector = ArbitrageDetector()
        
        # Prepare data dictionaries
        poly_data = {m.get('id'): m for m in poly_markets}
        kalshi_data = {m.get('id'): m for m in kalshi_markets}
        
        opportunities = detector.detect_opportunities(matches, poly_data, kalshi_data)
        
        print(f"✅ Arbitrage detection test successful: {len(opportunities)} opportunities found")
        
        for opp in opportunities[:2]:  # Show first 2 opportunities
            print(f"   - {opp.strategy} on {opp.outcome}: {opp.profit_percentage:.1%} profit")
            print(f"     Potential: ${opp.profit_potential:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Arbitrage detection test failed: {e}")
        return False

def test_monitoring():
    """Test monitoring system"""
    print("📊 Testing monitoring system...")
    
    try:
        # Test monitoring status
        status = monitor.get_monitoring_status()
        print(f"✅ Monitoring system accessible")
        print(f"   - Status: {'Running' if status['is_running'] else 'Stopped'}")
        print(f"   - Cycle count: {status['cycle_count']}")
        print(f"   - Update interval: {status['update_interval']}s")
        
        # Test forced update
        print("   Testing forced update...")
        opportunities = monitor.force_update()
        print(f"   - Forced update successful: {len(opportunities)} opportunities found")
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Arbitrage Platform...")
    print("=" * 50)
    
    setup_logging()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed - exiting")
        sys.exit(1)
    
    # Test APIs
    if not test_apis():
        print("⚠️  API tests failed - continuing anyway")
    
    # Test market matching
    if not test_market_matching():
        print("⚠️  Market matching test failed - continuing anyway")
    
    # Test arbitrage detection
    if not test_arbitrage_detection():
        print("⚠️  Arbitrage detection test failed - continuing anyway")
    
    # Test monitoring
    if not test_monitoring():
        print("⚠️  Monitoring test failed - continuing anyway")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run the dashboard: streamlit run frontend/app.py")
    print("2. Navigate to the Arbitrage Dashboard")
    print("3. Click 'Start Monitoring' to begin detecting opportunities")
    print("\nConfiguration files:")
    print("- config/settings.yaml - Main configuration")
    print("- config/market_pairs.yaml - Manual market pairs")
    print("\nLogs:")
    print("- arbitrage.log - Application logs")
    print("- data/arbitrage.db - SQLite database")

if __name__ == "__main__":
    main()
