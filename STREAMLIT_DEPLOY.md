# Quick Streamlit Community Cloud Deployment

## 🚀 Deploy Your Trading Dashboard in 5 Minutes

### Step 1: Test Locally
```bash
streamlit run streamlit_app.py
```
If it works locally, it will work on Streamlit Cloud!

### Step 2: Push to GitHub
```bash
# If you haven't initialized git yet:
git init
git add .
git commit -m "Ready for Streamlit Cloud deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/trading-polymarket.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `yourusername/trading-polymarket`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose something like `harris-song-arbitrage`
5. Click **"Deploy!"**

### Step 4: Add API Keys (Optional)
Your app works without API keys, but they provide more data:

1. In your app dashboard, click **"Settings"** → **"Secrets"**
2. Add (if you have them):
```toml
KALSHI_API_KEY = "your_key_here"
KALSHI_API_SECRET = "your_secret_here"
POLYMARKET_API_KEY = "your_key_here"
```

### That's it! 🎉

Your app will be live at: `https://harris-song-arbitrage.streamlit.app`

## ✅ Ready-to-Deploy Files
- ✅ `streamlit_app.py` - Entry point
- ✅ `requirements.txt` - Dependencies  
- ✅ `.streamlit/config.toml` - Configuration
- ✅ All imports fixed for deployment

## 🔧 Troubleshooting
- **Import errors**: All fixed for you!
- **Slow loading**: Normal on first visit (cold start)
- **API limits**: App includes smart caching
- **Need help**: Check the Streamlit Community Cloud logs
