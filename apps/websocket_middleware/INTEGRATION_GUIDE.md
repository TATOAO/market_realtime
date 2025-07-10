# WebSocket Middleware Integration Guide

## Overview

This guide explains how to integrate the WebSocket middleware with your existing stock monitor backend to enable real-time order book updates.

## Architecture Flow

```
Futu API → Stock Monitor Backend → WebSocket Middleware → Frontend Clients
                ↓                           ↓
            TimescaleDB                 Redis (Sessions)
```

## Step 1: Update Stock Monitor Backend

### 1.1 Add WebSocket Broadcasting Function

Add this function to your stock monitor backend:

```python
# In your stock monitor backend (e.g., app/api.py or app/core/center/potential_candidates_monitor.py)

import httpx
import asyncio
from typing import Dict, Any

async def broadcast_orderbook_to_websocket(symbol: str, orderbook_data: Dict[str, Any]):
    """
    Broadcast order book data to WebSocket clients
    """
    try:
        websocket_url = os.getenv("WEBSOCKET_URL", "http://websocket_middleware:8002")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{websocket_url}/broadcast/orderbook",
                params={"symbol": symbol},
                json=orderbook_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Broadcasted orderbook for {symbol} to {result.get('subscribers', 0)} clients")
            else:
                logger.error(f"Failed to broadcast orderbook for {symbol}: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error broadcasting orderbook for {symbol}: {e}")
```

### 1.2 Update Your Futu Callback

Modify your existing Futu order book callback to include broadcasting:

```python
# In your Futu client callback handler

async def on_orderbook_update(symbol: str, orderbook_data: dict):
    """
    Handle order book updates from Futu API
    """
    try:
        # 1. Store in database (your existing logic)
        await store_orderbook_data(symbol, orderbook_data)
        
        # 2. Broadcast to WebSocket clients (NEW)
        await broadcast_orderbook_to_websocket(symbol, orderbook_data)
        
        # 3. Any other processing you need
        await process_orderbook_data(symbol, orderbook_data)
        
    except Exception as e:
        logger.error(f"Error processing orderbook update for {symbol}: {e}")
```

### 1.3 Add Environment Variables

Add these to your stock monitor backend's environment:

```bash
# In your .env file or docker-compose environment
WEBSOCKET_URL=http://websocket_middleware:8002
REDIS_URL=redis://redis:6379
```

## Step 2: Update Frontend

### 2.1 Create WebSocket Client

Create a WebSocket client in your frontend:

```typescript
// In your frontend (e.g., src/utils/websocket.ts)

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private clientId: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private subscriptions = new Set<string>();

  constructor(clientId: string) {
    this.clientId = clientId;
  }

  connect() {
    const wsUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8002';
    this.ws = new WebSocket(`${wsUrl}/ws/${this.clientId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Resubscribe to previously subscribed symbols
      this.subscriptions.forEach(symbol => {
        this.subscribe(symbol);
      });
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  subscribe(symbol: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        symbol: symbol
      }));
      this.subscriptions.add(symbol);
    }
  }

  unsubscribe(symbol: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'unsubscribe',
        symbol: symbol
      }));
      this.subscriptions.delete(symbol);
    }
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'orderbook_update':
        // Emit event or call callback
        this.onOrderBookUpdate?.(message.symbol, message.data);
        break;
      case 'subscription_confirmed':
        console.log(`Subscribed to ${message.symbol}`);
        break;
      case 'error':
        console.error('WebSocket error:', message.message);
        break;
    }
  }

  private reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }

  // Callback for order book updates
  onOrderBookUpdate?: (symbol: string, data: any) => void;
}
```

### 2.2 Integrate with React Components

```typescript
// In your React component (e.g., src/components/StockChart.tsx)

import { useEffect, useRef } from 'react';
import { WebSocketClient } from '../utils/websocket';

export const StockChart = ({ symbol }: { symbol: string }) => {
  const wsClientRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    // Initialize WebSocket client
    wsClientRef.current = new WebSocketClient(`chart-${symbol}`);
    
    // Set up order book update handler
    wsClientRef.current.onOrderBookUpdate = (symbol, data) => {
      // Update your chart with real-time data
      updateChart(data);
    };

    // Connect and subscribe
    wsClientRef.current.connect();
    wsClientRef.current.subscribe(symbol);

    // Cleanup on unmount
    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.unsubscribe(symbol);
        wsClientRef.current.disconnect();
      }
    };
  }, [symbol]);

  const updateChart = (orderbookData: any) => {
    // Your chart update logic here
    console.log('Real-time order book update:', orderbookData);
  };

  return (
    <div>
      <h3>Real-time Order Book: {symbol}</h3>
      {/* Your chart component */}
    </div>
  );
};
```

## Step 3: Testing the Integration

### 3.1 Start All Services

```bash
# From the docker directory
docker-compose up -d
```

### 3.2 Test WebSocket Connection

```bash
# Run the test script
cd apps/websocket_middleware
python test_websocket.py
```

### 3.3 Monitor Logs

```bash
# Check WebSocket middleware logs
docker-compose logs -f websocket_middleware

# Check stock monitor logs
docker-compose logs -f stock_monitor
```

## Step 4: Performance Optimization

### 4.1 Message Batching

For high-frequency updates, consider batching:

```python
# In your stock monitor backend

class OrderBookBatcher:
    def __init__(self, batch_interval_ms=100):
        self.batch_interval_ms = batch_interval_ms
        self.pending_updates = {}
        self.batch_task = None

    async def add_update(self, symbol: str, orderbook_data: dict):
        self.pending_updates[symbol] = orderbook_data
        
        if not self.batch_task:
            self.batch_task = asyncio.create_task(self.flush_batch())

    async def flush_batch(self):
        await asyncio.sleep(self.batch_interval_ms / 1000)
        
        for symbol, data in self.pending_updates.items():
            await broadcast_orderbook_to_websocket(symbol, data)
        
        self.pending_updates.clear()
        self.batch_task = None
```

### 4.2 Connection Limits

Add connection limits to prevent abuse:

```python
# In WebSocket middleware (app/main.py)

MAX_CONNECTIONS_PER_CLIENT = 10
MAX_SUBSCRIPTIONS_PER_CLIENT = 50

class ConnectionManager:
    async def connect(self, websocket: WebSocket, client_id: str):
        # Check connection limits
        if len(self.active_connections) >= MAX_CONNECTIONS_PER_CLIENT:
            await websocket.close(code=1008, reason="Connection limit exceeded")
            return
        
        # ... rest of connect logic
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure WebSocket middleware is running on port 8002
   - Check Docker network configuration
   - Verify service dependencies in docker-compose.yml

2. **Messages Not Received**
   - Check subscription to correct symbol
   - Verify client ID uniqueness
   - Monitor WebSocket connection status

3. **High Latency**
   - Check network connectivity between services
   - Monitor Redis performance
   - Review message processing pipeline

### Debug Commands

```bash
# Check service health
curl http://localhost:8002/health

# Get WebSocket statistics
curl http://localhost:8002/stats

# Test broadcast endpoint
curl -X POST "http://localhost:8002/broadcast/orderbook?symbol=AAPL" \
  -H "Content-Type: application/json" \
  -d '{"bids":[],"asks":[],"timestamp":"2024-01-01T12:00:00Z"}'
```

## Next Steps

1. **Implement authentication** for WebSocket connections
2. **Add message compression** for large order books
3. **Set up monitoring** and alerting
4. **Implement horizontal scaling** with Redis session management
5. **Add rate limiting** to prevent abuse

This integration provides a solid foundation for real-time order book updates with sub-100ms latency while maintaining scalability and reliability. 