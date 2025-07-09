# 🔄 Polymarket-Kalshi Arbitrage Platform

A comprehensive arbitrage detection and execution platform that automatically identifies price discrepancies between Polymarket and Kalshi markets, enabling profitable trading opportunities.

## 🎯 Overview

This platform transforms the existing trading dashboard into an automated arbitrage detection system that:

- 🔍 **Continuously monitors** both Polymarket and Kalshi for price discrepancies
- 🤖 **Automatically matches** equivalent markets across platforms using AI/ML
- 📊 **Calculates profitability** after fees, slippage, and risk factors
- 🚨 **Provides real-time alerts** for actionable opportunities
- 📈 **Tracks performance** with comprehensive analytics
- ⚙️ **Configuration-driven** architecture for easy customization

## 🏗️ Architecture

### Backend Components

```
backend/
├── core/
│   ├── config.py              # Configuration management
│   ├── market_matcher.py      # AI-powered market matching
│   ├── arbitrage_detector.py  # Opportunity detection engine
│   └── monitor.py             # Real-time monitoring system
├── data/
│   └── database.py            # Database models and management
├── polymarket_api.py          # Polymarket API client
└── kalshi_api.py              # Kalshi API client
```

### Frontend Components

```
frontend/
├── pages/
│   └── arbitrage.py           # Arbitrage dashboard
├── components.py              # UI components
├── charts.py                  # Chart generation
├── data.py                    # Data fetching
└── app.py                     # Main application
```

### Configuration

```
config/
├── settings.yaml              # Main configuration
└── market_pairs.yaml          # Manual market pairs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
python scripts/setup.py
```

### 3. Start the Application

```bash
streamlit run frontend/app.py
```

### 4. Access the Dashboard

1. Navigate to the **Arbitrage Dashboard** in the sidebar
2. Click **Start Monitoring** to begin detecting opportunities
3. View real-time opportunities and performance metrics

## 📊 Core Features

### 🔍 Automated Market Matching

The system uses multiple matching algorithms:

- **Fuzzy String Matching**: Token-based similarity comparison
- **Semantic Matching**: AI-powered question understanding using sentence transformers
- **Keyword Matching**: Jaccard similarity with stop-word filtering
- **Manual Pairs**: User-defined high-confidence matches

```python
# Example: Add manual market pair
matcher.add_manual_pair(
    polymarket_id="21742633143462077347409894363331703050164692090159753447536090927577877651421",
    kalshi_id="PRES-24",
    confidence=1.0,
    notes="2024 Presidential Election"
)
```

### 💰 Arbitrage Detection

The detection engine calculates:

- **Profit Potential**: After fees and slippage
- **Risk Assessment**: Confidence scores and position sizing
- **Strategy Optimization**: Best execution path
- **Real-time Filtering**: Minimum profit thresholds

```python
# Example opportunity structure
ArbitrageOpportunity(
    strategy="buy_poly_sell_kalshi",
    outcome="yes",
    profit_percentage=0.087,  # 8.7% profit
    profit_potential=43.50,   # $43.50 potential profit
    confidence_score=0.89     # 89% confidence
)
```

### 📈 Real-time Monitoring

- **Background Processing**: Continuous market scanning
- **Rate Limit Management**: Intelligent API request batching
- **Performance Tracking**: Comprehensive metrics and logging
- **Alert System**: Configurable notifications

### 🎛️ Configuration Management

All settings are managed through YAML configuration files:

```yaml
arbitrage:
  min_profit_threshold: 0.05  # 5% minimum profit
  max_position_size: 1000     # $1000 max per trade
  slippage_buffer: 0.02       # 2% slippage buffer

platforms:
  polymarket:
    fee_rate: 0.02            # 2% fee rate
  kalshi:
    fee_rate: 0.01            # 1% fee rate

market_matching:
  similarity_threshold: 0.8   # 80% minimum similarity
  semantic_model: "all-MiniLM-L6-v2"

monitoring:
  update_interval: 30         # 30 seconds between updates
  batch_size: 20              # 20 markets per batch
```

## 🎮 Dashboard Features

### 📊 Control Panel

- **Start/Stop Monitoring**: Real-time control
- **Force Update**: Immediate opportunity scan
- **Configuration**: Live settings adjustment
- **Data Cleanup**: Historical data management

### 💰 Opportunities View

- **Live Opportunities**: Real-time arbitrage detection
- **Profit Calculations**: Detailed breakdown with fees
- **Risk Analysis**: Confidence scoring and position sizing
- **Execution Plans**: Step-by-step trading instructions

### 📈 Performance Analytics

- **Historical Tracking**: Opportunity trends over time
- **Strategy Breakdown**: Performance by strategy type
- **Profit Distribution**: Statistical analysis
- **System Metrics**: API usage and processing times

## 🛠️ Advanced Configuration

### Market Matching Settings

```yaml
market_matching:
  similarity_threshold: 0.8   # Minimum similarity for auto-matching
  fuzzy_threshold: 85         # Fuzzy string matching threshold
  semantic_model: "all-MiniLM-L6-v2"  # Sentence transformer model
```

### Risk Management

```yaml
arbitrage:
  min_profit_threshold: 0.05  # 5% minimum profit after fees
  max_position_size: 1000     # $1000 maximum per trade
  slippage_buffer: 0.02       # 2% slippage buffer
  alert_cooldown: 300         # 5 minutes between duplicate alerts
```

### Platform Settings

```yaml
platforms:
  polymarket:
    fee_rate: 0.02            # 2% transaction fee
    api_rate_limit: 100       # 100 requests per minute
    min_volume: 100           # $100 minimum volume
    
  kalshi:
    fee_rate: 0.01            # 1% transaction fee
    api_rate_limit: 50        # 50 requests per minute
    min_volume: 50            # $50 minimum volume
```

## 🗄️ Database Schema

The system uses SQLite by default with the following key tables:

### ArbitrageOpportunities
- **Opportunity Data**: Prices, volumes, profits
- **Strategy Information**: Execution plans and outcomes
- **Risk Metrics**: Confidence scores and adjustments
- **Timestamps**: Detection and expiration times

### MarketPairs
- **Matching Data**: Polymarket ↔ Kalshi pairs
- **Confidence Scores**: Match quality metrics
- **Match Types**: Manual, fuzzy, semantic, keyword

### MonitoringLogs
- **Performance Data**: Processing times and API calls
- **System Status**: Success/error rates
- **Market Statistics**: Counts and analysis results

## 🚨 Alert System

Configure alerts for high-value opportunities:

```yaml
alerts:
  email_enabled: false
  sms_enabled: false
  webhook_enabled: false
  min_profit_for_alert: 0.1   # 10% minimum profit for alerts
```

## 📝 Usage Examples

### Basic Monitoring

```python
from backend.core.monitor import monitor

# Start monitoring
monitor.start_monitoring()

# Get current opportunities
opportunities = monitor.get_current_opportunities()

# Get performance metrics
metrics = monitor.get_performance_metrics(timeframe_hours=24)
```

### Manual Market Matching

```python
from backend.core.market_matcher import MarketMatcher

matcher = MarketMatcher()

# Add manual pair
matcher.add_manual_pair(
    polymarket_id="poly_market_id",
    kalshi_id="kalshi_market_id",
    confidence=1.0,
    notes="High confidence match"
)
```

### Custom Arbitrage Detection

```python
from backend.core.arbitrage_detector import ArbitrageDetector

detector = ArbitrageDetector()

# Detect opportunities
opportunities = detector.detect_opportunities(
    market_matches=matches,
    polymarket_data=poly_data,
    kalshi_data=kalshi_data
)

# Get summary
summary = detector.get_opportunity_summary(opportunities)
```

## 🔧 Development

### Project Structure

```
trading-polymarket/
├── backend/           # Core arbitrage logic
├── frontend/          # Streamlit dashboard
├── config/            # Configuration files
├── data/              # Database and cache
├── scripts/           # Setup and utility scripts
└── requirements.txt   # Python dependencies
```

### Testing

```bash
# Run demo tests
python scripts/demo.py

# Run full setup
python scripts/setup.py

# Start dashboard
streamlit run frontend/app.py
```

### Adding New Features

1. **Market Matching**: Extend `MarketMatcher` class
2. **Detection Logic**: Modify `ArbitrageDetector` algorithms
3. **UI Components**: Add to `frontend/pages/arbitrage.py`
4. **Configuration**: Update `config/settings.yaml`

## 🔒 Security & Risk

### Risk Management Features

- **Position Sizing**: Maximum capital limits
- **Slippage Protection**: Configurable buffers
- **Confidence Scoring**: Multi-factor risk assessment
- **Rate Limiting**: API protection

### Data Protection

- **Local Storage**: SQLite database
- **Configuration Security**: YAML-based settings
- **API Key Management**: Environment variables
- **Audit Logging**: Complete operation tracking

## 📈 Performance Optimization

### Efficient Data Fetching

- **Batch API Requests**: Minimize rate limit impact
- **Intelligent Caching**: Reduce redundant calls
- **Concurrent Processing**: Multi-threaded operations
- **Database Optimization**: Indexed queries

### Monitoring Efficiency

- **Configurable Intervals**: Balance speed vs. resources
- **Selective Updates**: Only fetch changed data
- **Background Processing**: Non-blocking operations
- **Memory Management**: Automatic cleanup

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run setup: `python scripts/setup.py`
4. Start development: `streamlit run frontend/app.py`

### Code Style

- **Type Hints**: All functions should include type annotations
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Graceful failure management
- **Configuration**: Use YAML for all settings

## 📊 Success Metrics

- **Opportunity Detection Rate**: >95% of profitable opportunities identified
- **False Positive Rate**: <10% of alerts are unprofitable
- **Response Time**: <5 seconds from price change to alert
- **Platform Uptime**: >99.5% monitoring availability

## 🔮 Future Enhancements

### Phase 2 Features

- **Execution Framework**: Semi-automated trading
- **Machine Learning**: Predictive price modeling
- **Mobile Alerts**: Push notifications
- **Multi-Platform**: Additional exchanges

### Advanced Analytics

- **Backtesting**: Historical performance analysis
- **Risk Modeling**: Advanced portfolio theory
- **Market Microstructure**: Order book analysis
- **Sentiment Integration**: Social media signals

## 📞 Support

For questions or issues:

1. Check the configuration in `config/settings.yaml`
2. Review logs in `arbitrage.log`
3. Run diagnostic: `python scripts/demo.py`
4. Check database: `data/arbitrage.db`

