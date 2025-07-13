import React, { useState } from 'react';
import OrderBookChart from '../components/OrderBookChart';

const availableSymbols = [
  { code: 'US.AAPL', name: '苹果' },
  { code: 'US.GOOGL', name: '谷歌' },
  { code: 'US.MSFT', name: '微软' },
  { code: 'US.TSLA', name: '特斯拉' },
  { code: 'US.AMZN', name: '亚马逊' },
  { code: 'US.NVDA', name: '英伟达' },
  { code: 'US.META', name: '元' },
  { code: 'US.NFLX', name: '奈飞' },
  { code: 'US.AMD', name: '超微' },
  { code: 'US.INTC', name: '英特尔' }
];

export default function OrderBookPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('US.AAPL');
  const [websocketUrl, setWebsocketUrl] = useState('ws://127.0.0.1:8000/ws');

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Real-Time Order Book Chart
          </h1>
          <p className="text-gray-600">
            Live order book visualization using data from the fake order book service
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Symbol Selection */}
            <div>
              <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-2">
                Select Symbol
              </label>
              <select
                id="symbol"
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {availableSymbols.map((symbol) => (
                  <option key={symbol.code} value={symbol.code}>
                    {symbol.name} ({symbol.code})
                  </option>
                ))}
              </select>
            </div>

            {/* WebSocket URL */}
            <div>
              <label htmlFor="websocketUrl" className="block text-sm font-medium text-gray-700 mb-2">
                WebSocket URL
              </label>
              <input
                type="text"
                id="websocketUrl"
                value={websocketUrl}
                onChange={(e) => setWebsocketUrl(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="ws://127.0.0.1:8000/ws"
              />
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <h3 className="text-sm font-medium text-blue-800 mb-2">Setup Instructions:</h3>
            <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
              <li>Start the WebSocket middleware: <code className="bg-blue-100 px-1 rounded">cd apps/websocket_middleware && python -m uvicorn app.main:app --reload</code></li>
              <li>Start the fake order book service: <code className="bg-blue-100 px-1 rounded">cd apps/websocket_middleware && python fake_orderbook_service.py</code></li>
              <li>Select a symbol above to view its real-time order book data</li>
            </ol>
          </div>
        </div>

        {/* Order Book Chart */}
        <div className="mb-8">
          <OrderBookChart 
            symbol={selectedSymbol} 
            websocketUrl={websocketUrl}
          />
        </div>

        {/* Multiple Charts View */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Multiple Symbols View
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {availableSymbols.slice(0, 4).map((symbol) => (
              <div key={symbol.code} className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {symbol.name} ({symbol.code})
                </h3>
                <div className="h-64">
                  <OrderBookChart 
                    symbol={symbol.code} 
                    websocketUrl={websocketUrl}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 