# Trading Markets Dashboard

A simple Streamlit dashboard displaying the **top 5 prediction markets by volume** from Polymarket and Kalshi.

## 🚀 Quick Start

```bash
streamlit run frontend/app.py
```

Visit: http://localhost:8501

## 📁 Project Structure

```
trading-polymarket/
├── backend/
│   ├── polymarket_api.py    # Polymarket API client
│   └── kalshi_api.py        # Kalshi API client
├── frontend/
│   └── app.py               # Streamlit dashboard
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 📈 Features

- **Top 5 Markets**: Shows highest volume markets from both platforms
- **Real-time Data**: Live market data via Polymarket Gamma API  
- **Platform Selection**: Choose between Polymarket and Kalshi
- **Market Details**: Prices, volumes, end dates, descriptions
- **Interactive Charts**: Volume comparisons and price visualizations
- **Auto-refresh**: Manual refresh button to get latest data
- **Dark Mode**: Auto-enabled dark theme for better viewing
- **Compact Design**: Dense layout to see more information at once

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
- **Kalshi**: Mock data (ready for real API integration)

## 🎯 Simple & Clean

- Clean folder structure: `backend/` and `frontend/`
- No complex launchers or src wrappers
- Just run `streamlit run frontend/app.py` and go!

---

*Last updated: 2025-06-28*