from flask import Flask, render_template, request, redirect
import requests
import tweepy
from textblob import TextBlob

app = Flask(__name__)
portfolio = {}

# Replace with your Bearer Token
client = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAAEB3zwEAAAAAwraw8ATm1CX99VGlNLwKsm5iEDs%3D8pBSimxnpXGnI1hnTtmHoPNAnBdPKmb8KNBhyNwNDvpGHhZEIb")

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    return requests.get(url).json()

def get_sentiment(coin):
    try:
        # Map coin names to X-friendly tags
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
    return render_template('index.html', prices=prices, portfolio=portfolio, total_value=total_value, sentiments=sentiments)

@app.route('/portfolio', methods=['POST'])
def add_to_portfolio():
    coin = request.form['coin'].lower()
    amount = float(request.form['amount'])
    prices = get_crypto_prices()
    if coin in prices:
        portfolio[coin] = portfolio.get(coin, 0) + amount
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)