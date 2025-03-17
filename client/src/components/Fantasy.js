import React, { useState, useEffect } from 'react';

function Fantasy({ setMessages }) {
  const [formData, setFormData] = useState({});
  const [fantasyPortfolio, setFantasyPortfolio] = useState({});
  const [fantasyGain, setFantasyGain] = useState(0);
  const [fantasyInitialPrices, setFantasyInitialPrices] = useState({}); // New state

  useEffect(() => {
    fetch('/api/prices')
      .then(res => res.json())
      .then(data => {
        setFantasyPortfolio(data.fantasy_portfolio);
        setFantasyGain(data.fantasy_gain);
        setFantasyInitialPrices(data.fantasy_initial_prices); // Fetch initial prices
      });
  }, []);

  const handleChange = (coin, value) => {
    setFormData({ ...formData, [coin]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/fantasy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })
      .then(res => res.json())
      .then(data => {
        setMessages(prev => [...prev, { message: data.message, category: data.category }]);
        setFormData({});
        fetch('/api/prices').then(res => res.json()).then(data => {
          setFantasyPortfolio(data.fantasy_portfolio);
          setFantasyGain(data.fantasy_gain);
          setFantasyInitialPrices(data.fantasy_initial_prices);
        });
      });
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Fantasy League ($10,000)</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4 mb-4">
        {['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana'].map(coin => (
          <div key={coin}>
            <label className="block text-gray-300">{coin.charAt(0).toUpperCase() + coin.slice(1)}</label>
            <input
              value={formData[coin] || ''}
              onChange={e => handleChange(coin, e.target.value)}
              type="number"
              step="1"
              placeholder="$"
              className="bg-gray-700 p-2 rounded text-white w-full"
            />
          </div>
        ))}
        <button type="submit" className="bg-green-600 p-2 rounded hover:bg-green-700 col-span-2">Start Fantasy Game</button>
      </form>
      {Object.keys(fantasyPortfolio).length > 0 && (
        <div className="bg-gray-800 p-4 rounded-lg">
          {Object.entries(fantasyPortfolio).map(([coin, amount]) => (
            <div key={coin} className="flex justify-between py-1">
              <span>
                {coin.charAt(0).toUpperCase() + coin.slice(1)}: ${amount} 
                {fantasyInitialPrices[coin] && ` (Initial: $${fantasyInitialPrices[coin].usd.toFixed(2)})`}
              </span>
            </div>
          ))}
          <div className="mt-2 text-lg font-semibold">
            Fantasy Gain: <span className={fantasyGain >= 0 ? 'text-green-400' : 'text-red-400'}>{fantasyGain.toFixed(1)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Fantasy;