import React, { useState, useEffect } from 'react';

function PriceTable() {
  const [data, setData] = useState({ prices: {}, sentiments: {}, predictions: {} });

  const fetchPrices = () => {
    fetch('/refresh_prices')
      .then(res => res.json())
      .then(data => setData(data));
  };

  useEffect(() => {
    fetchPrices();
    const interval = setInterval(fetchPrices, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Live Prices</h2>
        <button onClick={fetchPrices} className="bg-blue-600 p-2 rounded hover:bg-blue-700">Refresh</button>
      </div>
      <div className="grid grid-cols-4 gap-4 bg-gray-800 p-4 rounded-lg">
        <div className="font-bold text-gray-300">Coin</div>
        <div className="font-bold text-gray-300">Price (USD)</div>
        <div className="font-bold text-gray-300">Sentiment</div>
        <div className="font-bold text-gray-300">Next Hour Prediction</div>
        {Object.entries(data.prices).map(([coin, info]) => (
          <React.Fragment key={coin}>
            <div>{coin.charAt(0).toUpperCase() + coin.slice(1)}</div>
            <div>${info.usd.toFixed(2)}</div>
            <div className={data.sentiments[coin] > 0 ? 'text-green-400' : data.sentiments[coin] < 0 ? 'text-red-400' : 'text-gray-400'}>
              {data.sentiments[coin]}
            </div>
            <div className={data.predictions[coin] > info.usd ? 'text-green-400' : data.predictions[coin] < info.usd ? 'text-red-400' : 'text-gray-400'}>
              ${data.predictions[coin].toFixed(2)}
              {info.usd !== 0 && ` (${(((data.predictions[coin] - info.usd) / info.usd) * 100).toFixed(1)}%)`}
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export default PriceTable;