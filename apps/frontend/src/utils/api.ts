const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const MONITORING_URL = process.env.NEXT_PUBLIC_MONITORING_URL || 'http://localhost:8001';

export const api = {
  // Stock data endpoints
  async getStocks(): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/stocks`);
    if (!response.ok) throw new Error('Failed to fetch stocks');
    return response.json();
  },

  async getStockData(symbol: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}`);
    if (!response.ok) throw new Error(`Failed to fetch data for ${symbol}`);
    return response.json();
  },

  async getStockChart(symbol: string, period: string = '1d'): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/chart?period=${period}`);
    if (!response.ok) throw new Error(`Failed to fetch chart for ${symbol}`);
    return response.json();
  },

  // Monitoring endpoints
  async getAlerts(): Promise<any[]> {
    const response = await fetch(`${MONITORING_URL}/alerts`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return response.json();
  },

  async createAlert(alert: { symbol: string; price: number; type: string }): Promise<any> {
    const response = await fetch(`${MONITORING_URL}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(alert),
    });
    if (!response.ok) throw new Error('Failed to create alert');
    return response.json();
  },

  async updateAlert(id: string, updates: any): Promise<any> {
    const response = await fetch(`${MONITORING_URL}/alerts/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update alert');
    return response.json();
  },

  async deleteAlert(id: string): Promise<void> {
    const response = await fetch(`${MONITORING_URL}/alerts/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete alert');
  },
}; 