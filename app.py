from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)
portfolio = {}  # Temporary storage for portfolio

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    return requests.get(url).json()

@app.route('/')
def home():
    prices = get_crypto_prices()
    total_value = sum(float(amount) * prices[coin]['usd'] for coin, amount in portfolio.items())
    return render_template('index.html', prices=prices, portfolio=portfolio, total_value=total_value)

@app.route('/portfolio', methods=['POST'])
def add_to_portfolio():
    coin = request.form['coin'].lower()
    amount = float(request.form['amount'])
    prices = get_crypto_prices()
    if coin in prices:
        portfolio[coin] = portfolio.get(coin, 0) + amount  # Add or update amount
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)