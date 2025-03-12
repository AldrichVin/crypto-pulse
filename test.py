import tweepy

client = tweepy.Client(bearer_token="AAAAAAAAAAAAAAAAAAAAAEB3zwEAAAAAwraw8ATm1CX99VGlNLwKsm5iEDs%3D8pBSimxnpXGnI1hnTtmHoPNAnBdPKmb8KNBhyNwNDvpGHhZEIb")
tweets = client.search_recent_tweets("#BTC", max_results=10).data or []
print(tweets)