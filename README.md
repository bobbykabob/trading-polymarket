# 🔄 Polymarket-Kalshi Arbitrage Platform

A comprehensive arbitrage detection and analysis platform for identifying profitable trading opportunities between Polymarket and Kalshi prediction markets.

## 🎯 Overview

This platform transforms the original trading dashboard into a sophisticated arbitrage detection system that:

- **Automatically matches equivalent markets** across Polymarket and Kalshi
- **Detects profitable arbitrage opportunities** in real-time
- **Calculates risk-adjusted profits** after fees and slippage
- **Provides comprehensive analytics** and historical tracking
- **Offers configurable monitoring** with customizable alerts

## 📊 Key Features

### 🔍 Automated Market Matching
- **Fuzzy String Matching**: Identifies similar market questions
- **Semantic Analysis**: Uses AI to understand market equivalence
- **Manual Override System**: Allows confirmed market pairs
- **Confidence Scoring**: Rates match quality for better decisions
- **Interactive Correlation Analysis**: Visualize similarities during batching

### 🔗 Market Correlations & Similarities
- **Real-time Similarity Scoring**: Multiple algorithms analyze market pairs
- **Interactive Filtering**: Filter by score, match type, and exclusion status
- **Detailed Breakdowns**: Fuzzy, semantic, and keyword scores
- **Visual Analytics**: Charts showing score distributions and comparisons
- **Common Keywords**: Extract and display shared terms
- **Similarity Reasons**: Human-readable explanations for matches
- **Price Comparisons**: Side-by-side market price analysis

### 💰 Arbitrage Detection
- **Real-time Opportunity Scanning**: Continuous monitoring of price discrepancies
- **Fee-Adjusted Calculations**: Accounts for platform fees (Polymarket 2%, Kalshi 1%)
- **Slippage Modeling**: Includes realistic trading costs
- **Risk Assessment**: Confidence scoring for each opportunity

### 📈 Performance Analytics
- **Historical Tracking**: Database storage of all opportunities
- **Success Rate Metrics**: Monitor detection accuracy
- **Profit Distribution Analysis**: Understand opportunity patterns
- **API Performance Monitoring**: Track system efficiency

### ⚙️ Configuration-Driven
- **YAML Configuration**: Easy settings management
- **Live Updates**: Change parameters without code changes
- **Platform-Specific Settings**: Customizable for each exchange
- **Alert Thresholds**: Configurable notification levels

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd trading-polymarket

# Install dependencies
pip install -r requirements.txt

# Run setup script
python scripts/setup.py
```

### 2. Configuration

Edit `config/settings.yaml` to customize:

```yaml
arbitrage:
  min_profit_threshold: 0.05  # 5% minimum profit
  max_position_size: 1000     # $1000 max per trade
  
platforms:
  polymarket:
    fee_rate: 0.02            # 2% fee rate
  kalshi:
    fee_rate: 0.01            # 1% fee rate
```

### 3. Launch the Dashboard

```bash
streamlit run frontend/app.py
```

Navigate to the **Arbitrage Dashboard** tab to start monitoring.

### 4. Analyze Market Correlations

Click **"Analyze Correlations"** in the dashboard to see:

- **Similarity Scores**: How markets are matched during batching
- **Interactive Filters**: Customize view by score and match type
- **Detailed Analysis**: Drill down into specific market pairs
- **Visual Charts**: Score distributions and comparisons
- **Common Keywords**: Shared terms between markets

This intermediate step shows the correlation analysis before final arbitrage detection.

## 🏗️ Architecture

```
trading-polymarket/
├── 📁 backend/
│   ├── 🔧 core/
│   │   ├── config.py           # Configuration management
│   │   ├── market_matcher.py   # Market matching engine
│   │   ├── arbitrage_detector.py # Arbitrage detection
│   │   └── monitor.py          # Real-time monitoring
│   ├── 📊 data/
│   │   └── database.py         # Database management
│   ├── 🔌 polymarket_api.py    # Polymarket API client
│   └── 🔌 kalshi_api.py        # Kalshi API client
├── 🖥️ frontend/
│   ├── 📱 pages/
│   │   └── arbitrage.py        # Arbitrage dashboard
│   ├── 🎨 components.py        # UI components
│   └── 📊 charts.py            # Chart generation
├── ⚙️ config/
│   ├── settings.yaml           # Main configuration
│   └── market_pairs.yaml       # Manual market pairs
├── 📜 scripts/
│   ├── setup.py               # System setup
│   └── demo.py                # Demo/testing script
└── 📂 data/
    └── arbitrage.db           # SQLite database
```

## 📱 Dashboard Features

### 🎛️ Control Panel
- **Start/Stop Monitoring**: Real-time opportunity detection
- **Force Update**: Immediate scan for opportunities
- **Market Correlation Analysis**: Interactive similarity batching
- **Configuration Settings**: Live parameter adjustments
- **Data Cleanup**: Manage historical data

### 📊 Live Monitoring
- **Market Correlations**: Interactive similarity analysis during batching
- **Current Opportunities**: Real-time arbitrage detection
- **Performance Metrics**: Success rates and API performance
- **Historical Analysis**: Trends and patterns over time
- **Detailed Analytics**: Per-opportunity breakdown

### 💡 Opportunity Analysis
- **Profit Calculations**: Fee and slippage-adjusted returns
- **Risk Assessment**: Confidence scoring and volume analysis
- **Execution Strategy**: Step-by-step trading instructions
- **Market Comparison**: Side-by-side market details

## 🔧 Configuration Guide

### Core Settings (`config/settings.yaml`)

```yaml
arbitrage:
  min_profit_threshold: 0.05    # Minimum 5% profit required
  max_position_size: 1000       # Maximum $1000 per trade
  slippage_buffer: 0.02         # 2% slippage allowance
  
market_matching:
  similarity_threshold: 0.8     # 80% similarity required
  semantic_model: "all-MiniLM-L6-v2"  # AI model for matching
  
monitoring:
  update_interval: 30           # Check every 30 seconds
  batch_size: 20               # Process 20 markets at once
  
alerts:
  min_profit_for_alert: 0.1    # Alert for 10%+ opportunities
```

### Manual Market Pairs (`config/market_pairs.yaml`)

```yaml
pairs:
  - polymarket_id: "market_id_1"
    kalshi_id: "MARKET-24"
    confidence: 1.0
    notes: "2024 Presidential Election"
```

## 📊 How It Works

### 1. Market Data Collection
- Fetches top markets from both platforms
- Retrieves real-time price and volume data
- Caches data for efficient processing

### 2. Market Matching
- Compares market questions using multiple algorithms
- Assigns confidence scores to matches
- **Displays detailed correlations during batching**
- **Shows fuzzy, semantic, and keyword similarity scores**
- **Provides interactive analysis of market similarities**
- Stores validated pairs for future use

### 3. Arbitrage Detection
- Calculates profit potential for each matched pair
- Applies fee and slippage adjustments
- Filters opportunities by minimum thresholds

### 4. Opportunity Ranking
- Scores opportunities by profit, confidence, and volume
- Presents ranked list for decision making
- Provides detailed analysis for each opportunity

## 🔍 Example Opportunity

```
📊 Arbitrage Opportunity Detected!

Markets:
  Polymarket: "Will Trump win the 2024 election?"
  Kalshi: "Will Trump be President in 2024?"

Strategy: Buy Kalshi, Sell Polymarket (YES tokens)
  Kalshi YES Price: $0.45
  Polymarket YES Price: $0.52
  
Profit Analysis:
  Gross Profit: $0.07 per share (15.6%)
  Platform Fees: $0.015 (Kalshi 1% + Polymarket 2%)
  Net Profit: $0.055 per share (12.2%)
  
Position Sizing:
  Max Position: $500 (based on volume)
  Total Profit: $61.11
  Required Capital: $225

Risk Assessment:
  Match Confidence: 95%
  Slippage Risk: Low
  Overall Confidence: 87%
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Internet connection for API access

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Setup Script**
```bash
python scripts/setup.py
```

3. **Test Installation**
```bash
python scripts/demo.py
```

4. **Start Application**
```bash
streamlit run frontend/app.py
```

### Troubleshooting
- **Import Errors**: Ensure all dependencies are installed
- **API Issues**: Check network connectivity
- **Database Problems**: Re-run setup script
- **Performance Issues**: Adjust monitoring intervals

## 📈 Performance & Monitoring

### System Status
- **API Health**: Monitor connection to both platforms
- **Database Performance**: Track storage efficiency
- **Processing Speed**: Monitor cycle times
- **Memory Usage**: Track resource consumption

### Key Metrics
- **Opportunities/Hour**: Detection rate
- **Success Rate**: Accuracy of opportunities
- **Profit Potential**: Total value detected
- **Response Time**: Speed of detection

## 🔐 Security & Risk Management

### Built-in Risk Controls
- **Position Sizing**: Automatic capital limits
- **Slippage Protection**: Built-in cost buffers
- **Volume Validation**: Liquidity requirements
- **Confidence Thresholds**: Quality filtering

### Data Security
- **Local Storage**: All data stored locally
- **API Security**: Secure credential management
- **Error Handling**: Robust failure recovery

## 📚 Technical Details

### Core Dependencies
- **Backend**: Python 3.8+, SQLAlchemy, PyYAML
- **Frontend**: Streamlit, Plotly, Pandas
- **AI/ML**: sentence-transformers, fuzzywuzzy
- **APIs**: requests, aiohttp

### Database Schema
- **ArbitrageOpportunities**: Detected opportunities
- **MarketPairs**: Matched markets
- **MonitoringLogs**: System audit trail
- **PerformanceMetrics**: Historical analytics

## 🎯 Success Metrics

### Performance Targets
- **Detection Rate**: >95% of opportunities found
- **False Positive Rate**: <10% of alerts
- **Response Time**: <5 seconds detection
- **System Uptime**: >99.5% availability

### Profitability Tracking
- **Average Profit**: Historical returns
- **Risk-Adjusted Returns**: Sharpe ratios
- **Capital Efficiency**: ROI tracking
- **Opportunity Frequency**: Detection patterns

## 🔮 Future Enhancements

### Planned Features
- **Automated Execution**: Paper trading
- **Mobile Alerts**: SMS/email notifications
- **Advanced Analytics**: ML predictions
- **Portfolio Management**: Position tracking

### Potential Expansions
- **Multi-Platform**: Additional exchanges
- **Cross-Asset**: Different asset classes
- **Geographic**: International markets
- **Predictive**: Time-series analysis

## 📞 Support

### Common Issues
1. **Import Errors**: Run `pip install -r requirements.txt`
2. **API Failures**: Check network connectivity
3. **Database Issues**: Run setup script again
4. **Performance**: Adjust monitoring intervals

### Getting Help
- **Logs**: Check `arbitrage.log` for details
- **Test**: Run `python scripts/demo.py`
- **Config**: Review `config/settings.yaml`
- **Database**: Inspect `data/arbitrage.db`

---

## 🏆 Getting Started

**Ready to detect arbitrage opportunities?**

1. **Setup**: `python scripts/setup.py`
2. **Launch**: `streamlit run frontend/app.py`
3. **Navigate**: Go to Arbitrage Dashboard
4. **Monitor**: Click "Start Monitoring"

The system will begin scanning for profitable opportunities across both platforms!

---

*Polymarket-Kalshi Arbitrage Platform*
*Version 1.0.0 - July 2025*
