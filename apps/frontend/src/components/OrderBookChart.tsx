import React, { useState, useEffect, useMemo } from 'react';
import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';
import { OrderBookData, OrderBookChartData } from '../types';

interface OrderBookChartProps {
  symbol: string;
  websocketUrl?: string;
}

export default function OrderBookChart({ 
  symbol, 
  websocketUrl = "ws://127.0.0.1:8000/ws" 
}: OrderBookChartProps) {
  const [orderBookData, setOrderBookData] = useState<OrderBookData | null>(null);
  const [chartDataHistory, setChartDataHistory] = useState<OrderBookChartData[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingHistorical, setIsLoadingHistorical] = useState(true);

  // WebSocket connection
  useEffect(() => {
    let ws: WebSocket | null = null;

    const connectWebSocket = () => {
      try {
        // Use the simple WebSocket endpoint that auto-generates client ID
        ws = new WebSocket(websocketUrl);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setError(null);
          
          // Subscribe to the symbol
          if (ws && ws.readyState === WebSocket.OPEN) {
            console.log('Sending subscription for symbol:', symbol);
            ws.send(JSON.stringify({
              action: 'subscribe',
              symbol: symbol
            }));
          }
        };

        ws.onmessage = (event) => {
          try {
            console.log('Received WebSocket message:', event.data);
            const data = JSON.parse(event.data);
            
            if (data.type === 'historical_data' && data.symbol === symbol) {
              // Handle historical data
              console.log('Received historical data:', data.data.length, 'points');
              const historicalData = data.data.map((item: any) => {
                const orderBookData = item.data || item;
                return transformOrderBookToChartData(orderBookData);
              }).filter(Boolean);
              
              setChartDataHistory(historicalData);
              setIsLoadingHistorical(false);
            }
            else if (data.type === 'orderbook_update' && data.symbol === symbol) {
              setOrderBookData(data.data);
              
              // Transform and add to history
              const newDataPoint = transformOrderBookToChartData(data.data);
              if (newDataPoint) {
                setChartDataHistory(prev => {
                  const updated = [...prev, newDataPoint];
                  // Keep only last 100 data points
                  return updated.slice(-100);
                });
              }
              
              // Mark historical loading as complete
              setIsLoadingHistorical(false);
            }
            else if (data.type === 'connected') {
              console.log('Connection confirmed with client ID:', data.client_id);
            } else if (data.type === 'subscription_confirmed') {
              console.log('Subscription confirmed for symbol:', data.symbol);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection failed');
          setIsConnected(false);
        };
      } catch (err) {
        console.error('Error creating WebSocket:', err);
        setError('Failed to create WebSocket connection');
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [symbol, websocketUrl]);

  // Helper function to transform order book data to chart data
  const transformOrderBookToChartData = (orderBookData: OrderBookData): OrderBookChartData | null => {
    try {
      const validBids = orderBookData.Bid
        .filter((level: any) => Array.isArray(level) && level.length >= 2 && typeof level[0] === 'number' && typeof level[1] === 'number');
      const validAsks = orderBookData.Ask
        .filter((level: any) => Array.isArray(level) && level.length >= 2 && typeof level[0] === 'number' && typeof level[1] === 'number');

      if (validBids.length > 0 && validAsks.length > 0) {
        const bestBid = Math.max(...validBids.map((level: any) => level[0]));
        const bestAsk = Math.min(...validAsks.map((level: any) => level[0]));
        const midPrice = (bestBid + bestAsk) / 2;
        const bidVolume = validBids.reduce((sum: number, level: any) => sum + level[1], 0);
        const askVolume = validAsks.reduce((sum: number, level: any) => sum + level[1], 0);
        const totalVolume = bidVolume + askVolume;
        const timestamp = new Date(orderBookData.timestamp).getTime();

        return {
          timestamp,
          midPrice,
          bestBid,
          bestAsk,
          bidVolume,
          askVolume,
          totalVolume,
        };
      }
      return null;
    } catch (error) {
      console.error('Error transforming order book data:', error);
      return null;
    }
  };

  // Use chart data history for visualization
  const chartData = useMemo(() => {
    return chartDataHistory;
  }, [chartDataHistory]);

  // Calculate mid price
  const midPrice = useMemo(() => {
    if (!orderBookData || orderBookData.Bid.length === 0 || orderBookData.Ask.length === 0) {
      return null;
    }
    
    const validBids = orderBookData.Bid.filter(level => Array.isArray(level) && level.length >= 1 && typeof level[0] === 'number');
    const validAsks = orderBookData.Ask.filter(level => Array.isArray(level) && level.length >= 1 && typeof level[0] === 'number');
    
    if (validBids.length === 0 || validAsks.length === 0) {
      return null;
    }
    
    const bestBid = Math.max(...validBids.map(level => level[0]));
    const bestAsk = Math.min(...validAsks.map(level => level[0]));
    return (bestBid + bestAsk) / 2;
  }, [orderBookData]);

  // Calculate spread
  const spread = useMemo(() => {
    if (!orderBookData || orderBookData.Bid.length === 0 || orderBookData.Ask.length === 0) {
      return null;
    }
    
    const validBids = orderBookData.Bid.filter(level => Array.isArray(level) && level.length >= 1 && typeof level[0] === 'number');
    const validAsks = orderBookData.Ask.filter(level => Array.isArray(level) && level.length >= 1 && typeof level[0] === 'number');
    
    if (validBids.length === 0 || validAsks.length === 0) {
      return null;
    }
    
    const bestBid = Math.max(...validBids.map(level => level[0]));
    const bestAsk = Math.min(...validAsks.map(level => level[0]));
    return bestAsk - bestBid;
  }, [orderBookData]);

  // Calculate spread percentage
  const spreadPercentage = useMemo(() => {
    if (!spread || !midPrice) return null;
    return (spread / midPrice) * 100;
  }, [spread, midPrice]);

  // Calculate total volume
  const totalVolume = useMemo(() => {
    if (!orderBookData) return null;
    
    const bidVolume = orderBookData.Bid
      .filter(level => Array.isArray(level) && level.length >= 2)
      .reduce((sum, level) => sum + (level[1] || 0), 0);
    
    const askVolume = orderBookData.Ask
      .filter(level => Array.isArray(level) && level.length >= 2)
      .reduce((sum, level) => sum + (level[1] || 0), 0);
    
    return bidVolume + askVolume;
  }, [orderBookData]);

  // Format order book levels for display
  const formatOrderBookLevels = (levels: any[], isBid: boolean) => {
    return levels
      .filter(level => Array.isArray(level) && level.length >= 2)
      .sort((a, b) => isBid ? b[0] - a[0] : a[0] - b[0]) // Bids descending, asks ascending
      .slice(0, 10) // Show top 10 levels
      .map((level, index) => ({
        price: level[0],
        quantity: level[1],
        total: level[2] || 0,
        orders: level[3] || 0,
        key: `${isBid ? 'bid' : 'ask'}-${index}`
      }));
  };

  const bidLevels = useMemo(() => formatOrderBookLevels(orderBookData?.Bid || [], true), [orderBookData]);
  const askLevels = useMemo(() => formatOrderBookLevels(orderBookData?.Ask || [], false), [orderBookData]);

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">{symbol}</h2>
          <p className="text-sm text-gray-500">Real-time Order Book</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center">
            <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Loading Indicator */}
          {isLoadingHistorical && (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              <span className="text-sm text-gray-600">Loading historical data...</span>
            </div>
          )}
        </div>
      </div>

      {/* Price Information */}
      {midPrice && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Mid Price</div>
            <div className="text-lg font-semibold text-gray-900">${midPrice.toFixed(2)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Spread</div>
            <div className="text-lg font-semibold text-gray-900">
              ${spread?.toFixed(4)} ({spreadPercentage?.toFixed(2)}%)
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Total Volume</div>
            <div className="text-lg font-semibold text-gray-900">
              {totalVolume ? totalVolume.toLocaleString() : 'N/A'}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-500">Data Points</div>
            <div className="text-lg font-semibold text-gray-900">{chartData.length}</div>
          </div>
        </div>
      )}

      {/* Chart */}
      {chartData.length > 0 ? (
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Price Chart</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  type="number"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  formatter={(value: any) => [`$${value.toFixed(2)}`, 'Mid Price']}
                />
                <Area 
                  type="monotone" 
                  dataKey="midPrice" 
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      ) : (
        <div className="mb-6">
          <div className="bg-gray-50 rounded-lg p-8 text-center">
            <div className="text-gray-500">
              {isLoadingHistorical ? 'Loading historical data...' : 'No chart data available'}
            </div>
          </div>
        </div>
      )}

      {/* Order Book Table */}
      {orderBookData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bids */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Bids</h3>
            <div className="bg-gray-50 rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700">
                <div>Price</div>
                <div>Quantity</div>
                <div>Total</div>
                <div>Orders</div>
              </div>
              {bidLevels.map((level) => (
                <div key={level.key} className="grid grid-cols-4 px-4 py-2 text-sm border-t border-gray-200">
                  <div className="text-green-600 font-medium">${level.price.toFixed(2)}</div>
                  <div>{level.quantity.toLocaleString()}</div>
                  <div>{level.total.toLocaleString()}</div>
                  <div>{level.orders}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Asks */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Asks</h3>
            <div className="bg-gray-50 rounded-lg overflow-hidden">
              <div className="grid grid-cols-4 bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700">
                <div>Price</div>
                <div>Quantity</div>
                <div>Total</div>
                <div>Orders</div>
              </div>
              {askLevels.map((level) => (
                <div key={level.key} className="grid grid-cols-4 px-4 py-2 text-sm border-t border-gray-200">
                  <div className="text-red-600 font-medium">${level.price.toFixed(2)}</div>
                  <div>{level.quantity.toLocaleString()}</div>
                  <div>{level.total.toLocaleString()}</div>
                  <div>{level.orders}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 