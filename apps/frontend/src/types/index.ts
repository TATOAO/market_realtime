export interface Stock {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
}

export interface StockPrice {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Alert {
  id: string;
  symbol: string;
  price: number;
  type: 'above' | 'below';
  isActive: boolean;
  createdAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Order Book Types
export type OrderBookLevel = [number, number, number, Record<string, any>]; // [price, quantity, numOrders, metadata]

export interface OrderBookData {
  code: string;
  name: string;
  svr_recv_time_bid: string;
  svr_recv_time_ask: string;
  Bid: OrderBookLevel[];
  Ask: OrderBookLevel[];
  timestamp: string;
}

export interface OrderBookChartData {
  timestamp: number;
  midPrice: number;
  bestBid: number;
  bestAsk: number;
  bidVolume: number;
  askVolume: number;
  totalVolume: number;
} 