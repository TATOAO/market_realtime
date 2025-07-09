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