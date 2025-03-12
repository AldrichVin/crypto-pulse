from flask import Flask, render_template, request, redirect, jsonify, flash
from flask import url_for
import requests
import tweepy
from textblob import TextBlob
import numpy as np
from sklearn.linear_model import LinearRegression
import time
import logging
import os

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'

# Global variables
portfolio = {}
fantasy_portfolio = {}  # Stores invested amounts (e.g., {'bitcoin': 5000})
fantasy_initial_prices = {}  # Stores prices at the time of investment (e.g., {'bitcoin': 80000})
pending_alerts = {}
triggered_alerts = []
last_known_prices = {}
last_prices = {}
last_predictions = {}
last_api_call_time = 0

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER_TOKEN", "your_token_here"))

def get_crypto_prices():
    global last_known_prices, last_api_call_time
    current_time = time.time()
    if current_time - last_api_call_time < 10 and last_known_prices:
        logger.warning(f"Rate limit delay: {current_time - last_api_call_time}s since last call. Using last known prices.")
        return last_known_prices

    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    for attempt in range(3):
        try:
            logger.debug("Fetching prices from CoinGecko")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            prices = response.json()
            for coin in ['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana']:
                if coin in prices and isinstance(prices[coin].get('usd'), (int, float)) and prices[coin]['usd'] > 0:
                    last_known_prices[coin] = {'usd': prices[coin]['usd']}
            logger.debug(f"Successfully fetched prices: {prices}")
            last_api_call_time = current_time
            return prices
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit hit on attempt {attempt + 1}: {e} - Retrying")
                time.sleep(2 ** attempt)
                continue
            logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
            break
        except Exception as e:
            logger.error(f"General error on attempt {attempt + 1}: {e}")
            break
    logger.error("All attempts failed - Using last known prices or fallback")
    return last_known_prices if last_known_prices else {
        'bitcoin': {'usd': 0}, 'ethereum': {'usd': 0}, 'ripple': {'usd': 0},
        'cardano': {'usd': 0}, 'solana': {'usd': 0}
    }

def get_sentiment(coin):
    try:
        coin_tags = {'bitcoin': '#BTC', 'ethereum': '#ETH', 'ripple': '#XRP', 'cardano': '#ADA', 'solana': '#SOL'}
        tweets = client.search_recent_tweets(coin_tags[coin], max_results=10).data or []
        polarity = sum(TextBlob(tweet.text).sentiment.polarity for tweet in tweets) / len(tweets) if tweets else 0
        return round(polarity, 1)
    except Exception as e:
        logger.error(f"Sentiment error for {coin}: {e}")
        return 0

def predict_price(coin, prices):
    global last_predictions
    if coin in last_predictions:
        prediction_time, prediction_value = last_predictions[coin]
        if time.time() - prediction_time < 300 and prediction_value > 0:
            logger.debug(f"Using cached prediction for {coin}: {prediction_value}")
            return prediction_value
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=1"
        logger.debug(f"Fetching prediction data for {coin}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        history = response.json().get('prices', [])
        if not history or len(history) < 2:
            logger.warning(f"Insufficient data for {coin}: {len(history)} points")
            current_price = prices.get(coin, {}).get('usd', 0)
            last_predictions[coin] = (time.time(), current_price)
            return current_price
        X = np.array(range(len(history))).reshape(-1, 1)
        y = np.array([price[1] for price in history])
        model = LinearRegression().fit(X, y)
        next_hour = model.predict([[len(history)]])[0]
        prediction = round(next_hour, 2)
        last_predictions[coin] = (time.time(), prediction)
        logger.debug(f"New prediction for {coin}: {prediction}")
        return prediction
    except Exception as e:
        logger.error(f"Prediction error for {coin}: {e}")
        current_price = prices.get(coin, {}).get('usd', 0)
        last_predictions[coin] = (time.time(), current_price)
        return current_price

@app.route('/', methods=['GET'])
@app.route('/<active_tab>', methods=['GET'])
def home(active_tab='prices'):
    prices = get_crypto_prices()
    sentiments = {coin: get_sentiment(coin) for coin in prices.keys()}
    predictions = {coin: predict_price(coin, prices) for coin in prices.keys()}
    total_value = sum(float(amount) * prices[coin].get('usd', 0) for coin, amount in portfolio.items())
    if fantasy_portfolio:
        # Calculate initial value using stored initial prices
        initial_value = sum(float(amount) for amount in fantasy_portfolio.values())  # Total invested dollars
        # Calculate current value based on the number of coins bought initially
        current_value = 0
        for coin, amount in fantasy_portfolio.items():
            if coin in fantasy_initial_prices and fantasy_initial_prices[coin]['usd'] > 0:
                # Number of coins bought at initial price
                num_coins = float(amount) / fantasy_initial_prices[coin]['usd']
                # Current value of those coins at the latest price
                current_value += num_coins * prices[coin].get('usd', 0)
        fantasy_gain = ((current_value - initial_value) / initial_value * 100) if initial_value else 0
    else:
        fantasy_gain = 0

    global triggered_alerts
    for coin in prices.keys():
        current_price = prices[coin].get('usd', 0)
        last_price = last_prices.get(coin, 0)
        if coin in pending_alerts:
            remaining_thresholds = []
            for threshold in pending_alerts[coin]:
                if last_price < threshold <= current_price:
                    triggered_alerts.append(f"{coin.capitalize()} hit ${threshold}!")
                    logger.info(f"Alert triggered: {coin} at ${threshold}")
                else:
                    remaining_thresholds.append(threshold)
            if remaining_thresholds:
                pending_alerts[coin] = remaining_thresholds
            else:
                del pending_alerts[coin]
        last_prices[coin] = current_price

    logger.debug(f"Pending alerts: {pending_alerts}, Triggered alerts: {triggered_alerts}")
    return render_template('index.html', prices=prices, portfolio=portfolio, total_value=total_value,
                          sentiments=sentiments, fantasy_portfolio=fantasy_portfolio, fantasy_gain=fantasy_gain,
                          predictions=predictions, pending_alerts=pending_alerts, triggered_alerts=triggered_alerts,
                          fantasy_initial_prices=fantasy_initial_prices,  # Added this line
                          active_tab=active_tab)

@app.route('/refresh_prices')
def refresh_prices():
    logger.debug("Refreshing prices endpoint called")
    prices = get_crypto_prices()
    sentiments = {coin: get_sentiment(coin) for coin in prices.keys()}
    predictions = {coin: predict_price(coin, prices) for coin in prices.keys()}
    is_cached = (time.time() - last_api_call_time < 10)
    return jsonify({
        'prices': prices, 'sentiments': sentiments, 'predictions': predictions, 'is_cached': is_cached
    })

@app.route('/portfolio', methods=['POST'])
def add_to_portfolio():
    coin = request.form['coin'].lower()
    amount = float(request.form['amount'])
    prices = get_crypto_prices()
    if coin in prices:
        portfolio[coin] = portfolio.get(coin, 0) + amount
        flash(f"Added {amount} {coin.capitalize()} to portfolio", 'success')
    else:
        flash(f"Invalid coin: {coin}", 'error')
    return redirect(url_for('home', active_tab='portfolio'))

@app.route('/fantasy', methods=['POST'])
def start_fantasy():
    global fantasy_initial_prices
    total = 0
    # Only consider non-empty values for total calculation
    for value in request.form.values():
        if value.strip():  # Check if the value is not empty or just whitespace
            total += float(value)
    if total <= 10000:
        fantasy_portfolio.clear()
        fantasy_initial_prices.clear()
        # Store the current prices at the time of starting the fantasy game
        current_prices = get_crypto_prices()
        for coin in request.form.keys():
            value = request.form[coin].strip()
            if value and float(value) > 0:  # Only process if value is non-empty and positive
                if coin in current_prices:
                    fantasy_initial_prices[coin] = {'usd': current_prices[coin]['usd']}
                    fantasy_portfolio[coin] = float(value)
        flash("Fantasy league started!", 'success')
    else:
        flash("Total exceeds $10,000 limit", 'error')
    return redirect(url_for('home', active_tab='fantasy'))

@app.route('/alert', methods=['POST'])
def set_alert():
    coin = request.form.get('coin', '').lower()
    threshold = request.form.get('threshold', '').strip()
    valid_coins = ['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana']
    if not coin or coin not in valid_coins:
        flash(f"Invalid coin. Use: {', '.join(valid_coins)}", 'error')
    elif not threshold or not threshold.replace('.', '').isdigit():
        flash("Invalid threshold. Enter a number.", 'error')
    else:
        threshold = float(threshold)
        if coin not in pending_alerts:
            pending_alerts[coin] = []
        if threshold not in pending_alerts[coin]:
            pending_alerts[coin].append(threshold)
            flash(f"Alert set for {coin.capitalize()} at ${threshold}", 'success')
        else:
            flash(f"Alert for {coin.capitalize()} at ${threshold} already exists", 'error')
    return redirect(url_for('home', active_tab='alerts'))

if __name__ == '__main__':
    app.run(debug=True)