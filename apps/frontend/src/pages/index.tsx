import { useState, useEffect } from 'react';
import Head from 'next/head';
import StockList from '@/components/StockList';
import StockChart from '@/components/StockChart';
import MonitoringPanel from '@/components/MonitoringPanel';

export default function Home() {
  const [selectedStock, setSelectedStock] = useState<string>('');

  return (
    <>
      <Head>
        <title>Futu Helper - Stock Market Analysis</title>
        <meta name="description" content="Real-time stock market analysis and monitoring" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">Futu Helper</h1>
              </div>
              <div className="flex items-center space-x-4">
                <a 
                  href="/orderbook" 
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Order Book Charts
                </a>
                <span className="text-sm text-gray-500">Real-time Stock Analysis</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Stock List */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Stock List</h2>
                <StockList onStockSelect={setSelectedStock} />
              </div>
            </div>

            {/* Stock Chart */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  {selectedStock ? `${selectedStock} Chart` : 'Select a Stock'}
                </h2>
                {selectedStock ? (
                  <StockChart symbol={selectedStock} />
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">
                    Choose a stock from the list to view its chart
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Monitoring Panel */}
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Monitoring & Alerts</h2>
              <MonitoringPanel />
            </div>
          </div>
        </main>
      </div>
    </>
  );
} 