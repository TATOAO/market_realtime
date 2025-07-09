import { useState, useEffect } from 'react';

interface StockChartProps {
  symbol: string;
}

export default function StockChart({ symbol }: StockChartProps) {
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    if (symbol) {
      fetchChartData();
    }
  }, [symbol]);

  const fetchChartData = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call to get chart data
      // const response = await fetch(`/api/stocks/${symbol}/chart`);
      // const data = await response.json();
      // setChartData(data);
      
      // Simulate loading
      await new Promise(resolve => setTimeout(resolve, 1000));
      setChartData({ symbol, data: 'mock data' });
    } catch (error) {
      console.error('Error fetching chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-2">{symbol} Chart</h3>
        <p className="text-gray-500">Chart component will be implemented with a charting library</p>
        <p className="text-sm text-gray-400 mt-2">(e.g., Chart.js, Recharts, or TradingView)</p>
      </div>
    </div>
  );
} 