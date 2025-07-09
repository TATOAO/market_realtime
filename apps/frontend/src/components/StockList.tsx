import { useState, useEffect } from 'react';

interface Stock {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  changePercent?: number;
}

interface StockListProps {
  onStockSelect: (symbol: string) => void;
}

export default function StockList({ onStockSelect }: StockListProps) {
  const [stocks, setStocks] = useState<Stock[]>([
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' },
  ]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // TODO: Fetch real stock data from API
    fetchStockData();
  }, []);

  const fetchStockData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      // TODO: Replace with actual API call
      // const response = await fetch('/api/stocks');
      // const data = await response.json();
      // setStocks(data);
    } catch (error) {
      console.error('Error fetching stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2">
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        stocks.map((stock) => (
          <div
            key={stock.symbol}
            className="stock-card cursor-pointer"
            onClick={() => onStockSelect(stock.symbol)}
          >
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-semibold text-gray-900">{stock.symbol}</h3>
                <p className="text-sm text-gray-500">{stock.name}</p>
              </div>
              <div className="text-right">
                {stock.price ? (
                  <>
                    <p className="font-medium text-gray-900">${stock.price.toFixed(2)}</p>
                    {stock.change && (
                      <p className={`text-sm ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent?.toFixed(2)}%)
                      </p>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-gray-400">Loading...</p>
                )}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
} 