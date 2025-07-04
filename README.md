# Trading Markets Dashboard

A Streamlit dashboard displaying **top prediction markets by volume** from Polymarket and Kalshi, focusing on **actively tradeable markets only**.

## 🚀 Quick Start

```bash
# Run the main application
streamlit run frontend/app.py

# Run the batch order book demo
streamlit run frontend/batch_demo.py

# Run the batch vs. individual performance test
python demo_batch_fetching.py
```

Visit: http://localhost:8501

## 📁 Project Structure

```
trading-polymarket/
├── backend/
│   ├── polymarket_api.py    # Polymarket API client with batch order book support
│   └── kalshi_api.py        # Kalshi API client
├── frontend/
│   ├── app.py               # Main Streamlit dashboard
│   ├── batch_demo.py        # Demo of batch order book fetching
│   ├── charts.py            # Chart generation functions
│   ├── components.py        # UI components
│   ├── data.py              # Data fetching and processing
│   ├── styles.py            # CSS styling
│   └── utils.py             # Utility functions
├── demo_batch_fetching.py   # Performance test for batch vs individual requests
├── test_get_books.py        # Tests for batch order book fetching
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## 📈 Features

- **Top Markets by Volume**: Shows highest volume tradeable markets from both platforms  
- **Active Markets Only**: Kalshi integration filters to only show open/tradeable markets (not settled)
- **Real-time Data**: Live market data via Polymarket Gamma API and Kalshi Trade API
- **Platform Selection**: Choose between Polymarket and Kalshi
- **Market Details**: Prices, volumes, end dates, descriptions with order book depth
- **Interactive Charts**: Volume comparisons, price history, and order book visualizations
- **Auto-refresh**: Manual refresh button to get latest data
- **Dark Mode**: Auto-enabled dark theme for better viewing
- **Compact Design**: Dense layout to see more information at once
- **Batch API Requests**: Optimized order book fetching using batch endpoints
- **Performance Metrics**: Shows the efficiency of batch vs individual requests

## 📊 What You'll See

1. **Summary Metrics**: Total markets, combined volume, averages
2. **Market Cards**: Detailed info for each top market including:
   - Market question/title
   - 24-hour trading volume
   - Yes/No prices (in cents)
   - End date and Market ID
   - Price visualization charts
   - Expandable descriptions
3. **Volume Chart**: Bar chart comparing trading volumes across platforms

## 🌙 Dark Mode Setup

Dark mode is automatically enabled! The configuration is set in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#8B5CF6"        # Purple accent
backgroundColor = "#0E1117"      # Dark background  
secondaryBackgroundColor = "#262730"  # Card backgrounds
textColor = "#FAFAFA"           # Light text
```

The dashboard automatically loads with:
- Dark background theme
- High contrast text
- Custom purple accent color
- Dark-optimized charts and components

## 🔧 Dependencies

Install required packages:
```bash
pip install streamlit pandas plotly requests python-dotenv
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## 📡 Data Sources

- **Polymarket**: Live data from Gamma API (https://gamma-api.polymarket.com/markets)
- **Kalshi**: Live data from Kalshi Trade API (https://api.elections.kalshi.com/trade-api/v2)
  - *Note: Only shows open/tradeable markets (not settled ones)*
  - *Open market volumes are typically lower (~$500-$3K) as high-volume markets have often settled*

## 🎯 Simple & Clean

- Clean folder structure: `backend/` and `frontend/`
- No complex launchers or src wrappers
- Just run `streamlit run frontend/app.py` and go!

---

## 📊 Volume Analysis Summary

**Understanding Kalshi Volume Data:**
- **Volume Type**: Total cumulative trading volume in USD (not daily average)
- **24h Volume**: Trading volume in the last 24 hours  
- **Open vs Settled Markets**: 
  - Open markets (tradeable): Typically $500-$3,275 volume
  - Settled markets (not tradeable): Can exceed $350,000+ volume
  - **Why?** High-volume markets often settle after major events conclude

**Current Market State**: The ~$3K max volume in open Kalshi markets is typical and represents genuinely tradeable opportunities. Higher volumes are usually found in settled (non-tradeable) markets.

---

*Last updated: July 3, 2025*