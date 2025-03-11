from flask import Flask, render_template
import requests

app = Flask(__name__)

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,ripple,cardano,solana&vs_currencies=usd"
    response = requests.get(url)
    return response.json()

@app.route('/')
def home():
    prices = get_crypto_prices()
    return render_template('index.html', prices=prices)

if __name__ == '__main__':
    app.run(debug=True)