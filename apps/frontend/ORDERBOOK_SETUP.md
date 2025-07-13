# Order Book Chart Component Setup Guide

This guide explains how to set up and use the real-time order book chart component that displays order book data from the fake order book service.

## Components Created

1. **OrderBookChart.tsx** - Main component that displays real-time order book data
2. **orderbook.tsx** - Demo page showcasing the component
3. **Updated types/index.ts** - Added order book related TypeScript interfaces

## Features

- Real-time WebSocket connection to receive order book updates
- Interactive area chart showing bid and ask quantities
- Live price and spread calculations
- Order book table showing top 10 bids and asks
- Connection status indicator
- Support for multiple symbols
- Responsive design with Tailwind CSS

## Prerequisites

1. **WebSocket Middleware** - Must be running on `http://localhost:8000`
2. **Fake Order Book Service** - Must be running to generate test data
3. **Frontend Dependencies** - Recharts library for charting

## Setup Instructions

### 1. Install Frontend Dependencies

```bash
cd apps/frontend
npm install recharts
```

### 2. Start the WebSocket Middleware

```bash
cd apps/websocket_middleware
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the Fake Order Book Service

```bash
cd apps/websocket_middleware
python fake_orderbook_service.py
```

### 4. Start the Frontend Development Server

```bash
cd apps/frontend
npm run dev
```

### 5. Access the Order Book Page

Navigate to `http://localhost:3000/orderbook` to view the order book charts.

## Usage

### Basic Usage

```tsx
import OrderBookChart from '../components/OrderBookChart';

function MyComponent() {
  return (
    <OrderBookChart 
      symbol="US.AAPL" 
      websocketUrl="ws://localhost:8000/ws"
    />
  );
}
```

### Props

- `symbol` (string, required): The stock symbol to display (e.g., "US.AAPL")
- `websocketUrl` (string, optional): WebSocket server URL (default: "ws://localhost:8000/ws")

### Available Symbols

The fake service generates data for these symbols:

- US.AAPL (苹果)
- US.GOOGL (谷歌)
- US.MSFT (微软)
- US.TSLA (特斯拉)
- US.AMZN (亚马逊)
- US.NVDA (英伟达)
- US.META (元)
- US.NFLX (奈飞)
- US.AMD (超微)
- US.INTC (英特尔)

## Data Format

The component expects order book data in this format:

```typescript
interface OrderBookData {
  code: string;
  name: string;
  svr_recv_time_bid: string;
  svr_recv_time_ask: string;
  Bid: OrderBookLevel[];
  Ask: OrderBookLevel[];
  timestamp: string;
}

interface OrderBookLevel {
  price: number;
  quantity: number;
  numOrders: number;
  metadata: Record<string, any>;
}
```

## WebSocket Message Format

The component subscribes to WebSocket messages with this format:

```json
{
  "type": "orderbook_update",
  "symbol": "US.AAPL",
  "data": { /* OrderBookData */ },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## Testing

Run the integration test to verify everything is working:

```bash
cd apps/websocket_middleware
python test_orderbook_integration.py
```

## Troubleshooting

### Connection Issues

1. **WebSocket connection failed**: Ensure the WebSocket middleware is running on port 8000
2. **No data received**: Check that the fake order book service is running and sending data
3. **CORS errors**: The middleware should have CORS enabled for localhost:3000

### Chart Not Displaying

1. **No chart library**: Ensure Recharts is installed (`npm install recharts`)
2. **Data format issues**: Check that the order book data matches the expected format
3. **Empty data**: Verify that the fake service is generating data for the selected symbol

### Performance Issues

1. **Too many WebSocket connections**: Each chart component creates a separate connection
2. **Memory leaks**: Components properly clean up WebSocket connections on unmount
3. **Chart updates**: The chart updates automatically when new data is received

## Customization

### Styling

The component uses Tailwind CSS classes. You can customize the appearance by modifying the className props.

### Chart Configuration

The chart uses Recharts AreaChart. You can modify the chart configuration in the OrderBookChart component:

- Change colors by modifying the `stroke` and `fill` props
- Adjust chart dimensions by modifying the container height
- Add more chart types by importing additional Recharts components

### Data Processing

The component includes data transformation logic in the `useMemo` hooks. You can modify:

- Price calculations (mid price, spread)
- Chart data formatting
- Order book level processing

## Integration with Real Data

To integrate with real order book data:

1. Replace the fake service with your real data source
2. Ensure the data format matches the expected interface
3. Update the WebSocket endpoint to point to your real WebSocket server
4. Modify the symbol mapping if needed

## Security Considerations

- The current setup allows all origins (`*`) for CORS - restrict this in production
- WebSocket connections should be authenticated in production
- Validate all incoming data on the server side
- Use HTTPS/WSS in production environments
