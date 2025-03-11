from flask import Flask, render_template, request, redirect, jsonify, flash
from flask import url_for
import requests
import tweepy
from textblob import TextBlob
import numpy as np
from sklearn.linear_model import LinearRegression
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'
portfolio = {}
fantasy_portfolio = {}
alerts = []
pending_alerts = {}
last_known_prices = {}
last_prices = {}
last_predictions = {}  # Cache predictions to avoid rate limits

# Replace with your Bearer Token
client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN_HERE")

def get_crypto_prices():
    global last_known_prices
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        prices = response.json()
        for coin in ['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana']:
            if coin in prices and isinstance(prices[coin].get('usd'), (int, float)) and prices[coin]['usd'] > 0:
                last_known_prices[coin] = {'usd': prices[coin]['usd']}
        return prices
    except Exception as e:
        print(f"Price fetch error: {e} - Using last known prices or fallback")
        if last_known_prices:
            return last_known_prices
        else:
            return {
                'bitcoin': {'usd': 0},
                'ethereum': {'usd': 0},
                'ripple': {'usd': 0},
                'cardano': {'usd': 0},
                'solana': {'usd': 0}
            }

def get_sentiment(coin):
    try:
        coin_tags = {
            'bitcoin': '#BTC', 'ethereum': '#ETH', 'ripple': '#XRP',
            'cardano': '#ADA', 'solana': '#SOL'
        }
        tweets = client.search_recent_tweets(coin_tags[coin], max_results=10).data or []
        polarity = sum(TextBlob(tweet.text).sentiment.polarity for tweet in tweets) / len(tweets) if tweets else 0
        return round(polarity, 1)
    except Exception as e:
        print(f"Sentiment error for {coin}: {e}")
        return 0

def predict_price(coin):
    global last_predictions
    # Check if we have a recent prediction
    if coin in last_predictions:
        prediction_time, prediction_value = last_predictions[coin]
        if time.time() - prediction_time < 300:  # Cache for 5 minutes
            return prediction_value
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=1"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        history = response.json().get('prices', [])
        if not history or len(history) < 2:
            print(f"Prediction error for {coin}: Insufficient price history data")
            current_price = last_known_prices.get(coin, {}).get('usd', 0)
            last_predictions[coin] = (time.time(), current_price)
            return current_price
        X = np.array(range(len(history))).reshape(-1, 1)
        y = np.array([price[1] for price in history])
        model = LinearRegression().fit(X, y)
        next_hour = model.predict([[len(history)]])[0]
        prediction = round(next_hour, 2)
        last_predictions[coin] = (time.time(), prediction)
        return prediction
    except Exception as e:
        print(f"Prediction error for {coin}: {e}")
        current_price = last_known_prices.get(coin, {}).get('usd', 0)
        last_predictions[coin] = (time.time(), current_price)
        return current_price

@app.route('/')
def home():
    prices = get_crypto_prices()
    sentiments = {coin: get_sentiment(coin) for coin in prices.keys()}
    predictions = {coin: predict_price(coin) for coin in prices.keys()}
    total_value = sum(float(amount) * prices[coin].get('usd', 0) for coin, amount in portfolio.items())
    if fantasy_portfolio:
        initial_value = sum(float(amount) for amount in fantasy_portfolio.values())
        current_value = sum(float(amount) * prices[coin].get('usd', 0) / 10000 for coin, amount in fantasy_portfolio.items())
        fantasy_gain = ((current_value - initial_value) / initial_value * 100) if initial_value else 0
    else:
        fantasy_gain = 0
    
    # Update last prices
    for coin in prices.keys():
        last_prices[coin] = last_prices.get(coin, prices[coin].get('usd', 0))
    
    # Check pending alerts
    global alerts, pending_alerts
    for coin, threshold in list(pending_alerts.items()):
        current_price = prices[coin].get('usd', 0)
        last_price = last_prices.get(coin, 0)
        if last_price < threshold <= current_price and coin in pending_alerts:
            alerts.append(f"{coin.capitalize()} hit ${threshold}!")
            del pending_alerts[coin]
    
    for coin in prices.keys():
        last_prices[coin] = prices[coin].get('usd', 0)
    
    return render_template('index.html', prices=prices, portfolio=portfolio, total_value=total_value,
                          sentiments=sentiments, fantasy_portfolio=fantasy_portfolio, fantasy_gain=fantasy_gain,
                          predictions=predictions, alerts=alerts)

@app.route('/refresh_prices')
def refresh_prices():
    prices = get_crypto_prices()
    sentiments = {coin: get_sentiment(coin) for coin in prices.keys()}
    predictions = {coin: predict_price(coin) for coin in prices.keys()}
    return jsonify({
        'prices': prices,
        'sentiments': sentiments,
        'predictions': predictions
    })

@app.route('/portfolio', methods=['POST'])
def add_to_portfolio():
    coin = request.form['coin'].lower()
    amount = float(request.form['amount'])
    prices = get_crypto_prices()
    if coin in prices:
        portfolio[coin] = portfolio.get(coin, 0) + amount
    return redirect('/')

@app.route('/fantasy', methods=['POST'])
def start_fantasy():
    total = sum(float(v) for v in request.form.values() if v)
    if total <= 10000:
        fantasy_portfolio.clear()
        fantasy_portfolio.update({k: float(v) for k, v in request.form.items() if v})
    return redirect('/')

@app.route('/alert', methods=['POST'])
def set_alert():
    coin = request.form['coin'].lower()
    threshold = request.form['threshold'].strip()
    if not threshold or not threshold.replace('.', '').isdigit():
        flash('Please enter a valid price threshold.', category='error')
        return redirect(url_for('home'))
    threshold = float(threshold)
    pending_alerts[coin] = threshold
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)