import React, { useState, useEffect } from 'react';

function Alerts() {
  const [coin, setCoin] = useState('');
  const [threshold, setThreshold] = useState('');
  const [pendingAlerts, setPendingAlerts] = useState({});
  const [triggeredAlerts, setTriggeredAlerts] = useState([]);

  useEffect(() => {
    fetch('/api/prices')
      .then(res => res.json())
      .then(data => {
        setPendingAlerts(data.pending_alerts);
        setTriggeredAlerts(data.triggered_alerts);
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/alert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin, threshold })
    }).then(() => {
      setCoin('');
      setThreshold('');
      fetch('/api/prices').then(res => res.json()).then(data => {
        setPendingAlerts(data.pending_alerts);
        setTriggeredAlerts(data.triggered_alerts);
      });
    });
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Price Alerts</h2>
      <form onSubmit={handleSubmit} className="flex space-x-4 mb-4">
        <input value={coin} onChange={e => setCoin(e.target.value)} placeholder="Coin (e.g., bitcoin)" className="bg-gray-700 p-2 rounded text-white w-1/3" />
        <input value={threshold} onChange={e => setThreshold(e.target.value)} type="number" step="1" placeholder="Price Threshold" className="bg-gray-700 p-2 rounded text-white w-1/3" />
        <button type="submit" className="bg-purple-600 p-2 rounded hover:bg-purple-700 w-1/3">Set Alert</button>
      </form>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="font-bold text-yellow-400 mb-2">Pending Alerts</h3>
          {Object.keys(pendingAlerts).length ? (
            <table className="w-full text-left">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b border-gray-700">Coin</th>
                  <th className="py-2 px-4 border-b border-gray-700">Threshold (USD)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(pendingAlerts).flatMap(([coin, thresholds]) =>
                  thresholds.map(threshold => (
                    <tr key={`${coin}-${threshold}`}>
                      <td className="py-2 px-4 border-b border-gray-700">{coin.charAt(0).toUpperCase() + coin.slice(1)}</td>
                      <td className="py-2 px-4 border-b border-gray-700">${threshold.toFixed(2)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-400">No pending alerts.</p>
          )}
        </div>
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="font-bold text-yellow-400 mb-2">Triggered Alerts</h3>
          {triggeredAlerts.length ? (
            <table className="w-full text-left">
              <thead>
                <tr>
                  <th className="py-2 px-4 border-b border-gray-700">Message</th>
                </tr>
              </thead>
              <tbody>
                {triggeredAlerts.map((alert, index) => (
                  <tr key={index}>
                    <td className="py-2 px-4 border-b border-gray-700">{alert}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-400">No triggered alerts yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Alerts;