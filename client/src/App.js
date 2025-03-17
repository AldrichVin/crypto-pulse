import React, { useState } from 'react';
import PriceTable from './components/PriceTable';

function App() {
  const [activeTab, setActiveTab] = useState('prices');

  return (
    <div className="bg-gray-900 text-white font-sans min-h-screen">
      <header className="bg-gray-800 p-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold">Crypto Pulse</h1>
      </header>
      <main className="p-6 max-w-6xl mx-auto">
        <div className="flex border-b border-gray-700 mb-6">
          {['prices', 'portfolio', 'fantasy', 'alerts'].map(tab => (
            <button
              key={tab}
              className={`px-4 py-2 text-gray-300 font-semibold border-b-2 ${activeTab === tab ? 'border-blue-500' : 'border-transparent'} hover:border-blue-500`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
        <div className="tab-content">
          {activeTab === 'prices' && <PriceTable />}
          {activeTab === 'portfolio' && <div>Portfolio Tab</div>}
          {activeTab === 'fantasy' && <div>Fantasy Tab</div>}
          {activeTab === 'alerts' && <div>Alerts Tab</div>}
        </div>
      </main>
    </div>
  );
}

export default App;