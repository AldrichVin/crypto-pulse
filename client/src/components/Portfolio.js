import React, { useState, useEffect } from 'react';

function Portfolio({ setMessages }) {
  const [coin, setCoin] = useState('');
  const [amount, setAmount] = useState('');
  const [portfolio, setPortfolio] = useState({});
  const [totalValue, setTotalValue] = useState(0);

  useEffect(() => {
    fetch('/api/prices')
      .then(res => res.json())
      .then(data => {
        setPortfolio(data.portfolio);
        setTotalValue(data.total_value);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/portfolio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin, amount })
    })
      .then(res => res.json())
      .then(data => {
        setMessages(prev => [...prev, { message: data.message, category: data.category }]);
        setCoin('');
        setAmount('');
        fetch('/api/prices').then(res => res.json()).then(data => {
          setPortfolio(data.portfolio);
          setTotalValue(data.total_value);
        });
      });
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Your Portfolio</h2>
      <form onSubmit={handleSubmit} className="flex space-x-4 mb-4">
        <input value={coin} onChange={e => setCoin(e.target.value)} placeholder="Coin (e.g., bitcoin)" className="bg-gray-700 p-2 rounded text-white w-1/3" />
        <input value={amount} onChange={e => setAmount(e.target.value)} type="number" step="0.01" placeholder="Amount" className="bg-gray-700 p-2 rounded text-white w-1/3" />
        <button type="submit" className="bg-blue-600 p-2 rounded hover:bg-blue-700 w-1/3">Add to Portfolio</button>
      </form>
      <div className="bg-gray-800 p-4 rounded-lg">
        {Object.keys(portfolio).length ? (
          <>
            {Object.entries(portfolio).map(([coin, amount]) => (
              <div key={coin} className="flex justify-between py-1">
                <span>{coin.charAt(0).toUpperCase() + coin.slice(1)}: {amount}</span>
              </div>
            ))}
            <div className="mt-2 text-lg font-semibold">
              Total Value: ${totalValue.toFixed(2)}
            </div>
          </>
        ) : (
          <p className="text-gray-400">No holdings yet. Add some coins!</p>
        )}
      </div>
    </div>
  );
}

export default Portfolio;