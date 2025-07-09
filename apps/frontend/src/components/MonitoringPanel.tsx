import { useState } from 'react';

interface Alert {
  id: string;
  symbol: string;
  price: number;
  type: 'above' | 'below';
  isActive: boolean;
}

export default function MonitoringPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [newAlert, setNewAlert] = useState({
    symbol: '',
    price: '',
    type: 'above' as 'above' | 'below'
  });

  const addAlert = () => {
    if (newAlert.symbol && newAlert.price) {
      const alert: Alert = {
        id: Date.now().toString(),
        symbol: newAlert.symbol.toUpperCase(),
        price: parseFloat(newAlert.price),
        type: newAlert.type,
        isActive: true
      };
      setAlerts([...alerts, alert]);
      setNewAlert({ symbol: '', price: '', type: 'above' });
    }
  };

  const toggleAlert = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, isActive: !alert.isActive } : alert
    ));
  };

  const removeAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Add New Alert */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Add Price Alert</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Stock Symbol (e.g., AAPL)"
            value={newAlert.symbol}
            onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <input
            type="number"
            placeholder="Price"
            value={newAlert.price}
            onChange={(e) => setNewAlert({ ...newAlert, price: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <select
            value={newAlert.type}
            onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value as 'above' | 'below' })}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="above">Above</option>
            <option value="below">Below</option>
          </select>
          <button
            onClick={addAlert}
            className="btn-primary"
          >
            Add Alert
          </button>
        </div>
      </div>

      {/* Active Alerts */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Active Alerts</h3>
        {alerts.length === 0 ? (
          <p className="text-gray-500">No alerts set. Add an alert above to get started.</p>
        ) : (
          <div className="space-y-2">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${alert.isActive ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <div>
                    <span className="font-semibold text-gray-900">{alert.symbol}</span>
                    <span className="text-gray-500 ml-2">
                      {alert.type} ${alert.price.toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => toggleAlert(alert.id)}
                    className={`px-3 py-1 rounded text-sm ${
                      alert.isActive 
                        ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' 
                        : 'bg-green-100 text-green-800 hover:bg-green-200'
                    }`}
                  >
                    {alert.isActive ? 'Pause' : 'Resume'}
                  </button>
                  <button
                    onClick={() => removeAlert(alert.id)}
                    className="px-3 py-1 rounded text-sm bg-red-100 text-red-800 hover:bg-red-200"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 