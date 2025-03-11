from flask import Flask, render_template, request, redirect
import requests
import tweepy
from textblob import TextBlob

app = Flask(__name__)
portfolio = {}
fantasy_portfolio = {}  # New storage for fantasy game

# Replace with your Bearer Token (or use a placeholder for now)
client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN_HERE")

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    return requests.get(url).json()

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

@app.route('/')
def home():
    prices = get_crypto_prices()
    sentiments = {coin: get_sentiment(coin) for coin in prices.keys()}
    total_value = sum(float(amount) * prices[coin]['usd'] for coin, amount in portfolio.items())
    # Calculate fantasy gain/loss as a percentage
    if fantasy_portfolio:
        initial_value = sum(float(amount) for amount in fantasy_portfolio.values())
        current_value = sum(float(amount) * prices[coin]['usd'] / 10000 for coin, amount in fantasy_portfolio.items())
        fantasy_gain = ((current_value - initial_value) / initial_value) * 100 if initial_value else 0
    else:
        fantasy_gain = 0
    return render_template('index.html', prices=prices, portfolio=portfolio, total_value=total_value,
                          sentiments=sentiments, fantasy_portfolio=fantasy_portfolio, fantasy_gain=fantasy_gain)

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
    if total <= 10000:  # Cap at $10,000
        fantasy_portfolio.clear()
        fantasy_portfolio.update({k: float(v) for k, v in request.form.items() if v})
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)