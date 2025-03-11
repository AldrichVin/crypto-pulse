# Crypto Pulse
A cryptocurrency tracker with live prices, portfolio management, sentiment analysis, a fantasy league, and predictive alerts.

## Features
- Live prices from CoinGecko for BTC, ETH, XRP, ADA, SOL (refreshed every minute)
- Portfolio tracking with total value
- Sentiment analysis from X posts
- Fantasy league: Invest $10,000 and track gains/losses
- Price predictions and user-set alerts (trigger on crossing)

## Setup
1. Clone: `git clone https://github.com/AldrichVin/crypto-pulse.git`
2. Install: `pip install -r requirements.txt`
3. Add X Bearer Token to `app.py` (replace "INSERT_TOKEN_HERE")
4. Run: `python app.py`