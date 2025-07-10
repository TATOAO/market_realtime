# WebSocket Middleware

## Overview

The WebSocket Middleware is a real-time communication layer that bridges your Futu API data sources with frontend clients. It provides low-latency, bidirectional communication for order book updates and other real-time stock data.

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│  Futu API   │───▶│ WebSocket Server │───▶│  Frontend   │
│ (Data Source)│    │   (Middleware)   │    │  (Client)   │
└─────────────┘    └──────────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    Redis    │
                   │ (Sessions)  │
                   └─────────────┘
```

## Key Features

### 1. **Connection Management**
- Automatic WebSocket connection handling
- Client authentication and session management
- Graceful disconnection and cleanup
- Connection health monitoring

### 2. **Subscription System**
- Symbol-based subscriptions (e.g., "AAPL", "TSLA")
- Dynamic subscribe/unsubscribe
- Efficient broadcasting to relevant clients only
- Subscription confirmation messages

### 3. **Real-time Broadcasting**
- Sub-100ms latency for order book updates
- Automatic reconnection with exponential backoff
- Message queuing during disconnections
- Error handling and recovery

### 4. **Scalability**
- Redis integration for session management
- Horizontal scaling support
- Connection pooling
- Load balancing ready

## API Endpoints

### WebSocket Endpoint
```
ws://localhost:8002/ws/{client_id}
```

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8002/ws/client123');
```

### HTTP Endpoints

#### Health Check
```
GET /health
```
Returns connection statistics and health status.

#### Broadcast Order Book
```
POST /broadcast/orderbook?symbol=AAPL
Content-Type: application/json

{
  "bids": [...],
  "asks": [...],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Statistics
```
GET /stats
```
Returns detailed WebSocket statistics.

## Message Protocol

### Client to Server Messages

#### Subscribe to Symbol
```json
{
  "action": "subscribe",
  "symbol": "AAPL"
}
```

#### Unsubscribe from Symbol
```json
{
  "action": "unsubscribe",
  "symbol": "AAPL"
}
```

#### Ping (Keep-alive)
```json
{
  "action": "ping"
}
```

### Server to Client Messages

#### Order Book Update
```json
{
  "type": "orderbook_update",
  "symbol": "AAPL",
  "data": {
    "bids": [...],
    "asks": [...],
    "timestamp": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Subscription Confirmation
```json
{
  "type": "subscription_confirmed",
  "symbol": "AAPL"
}
```

#### Unsubscription Confirmation
```json
{
  "type": "unsubscription_confirmed",
  "symbol": "AAPL"
}
```

#### Pong Response
```json
{
  "type": "pong"
}
```

#### Error Message
```json
{
  "type": "error",
  "message": "Unknown action"
}
```

## Frontend Integration

### Basic WebSocket Client
```javascript
class WebSocketClient {
  constructor(clientId) {
    this.clientId = clientId;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8002/ws/${this.clientId}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
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

  subscribe(symbol) {
    this.sendMessage({
      action: 'subscribe',
      symbol: symbol
    });
  }

  unsubscribe(symbol) {
    this.sendMessage({
      action: 'unsubscribe',
      symbol: symbol
    });
  }

  sendMessage(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  handleMessage(message) {
    switch (message.type) {
      case 'orderbook_update':
        this.onOrderBookUpdate(message.symbol, message.data);
        break;
      case 'subscription_confirmed':
        console.log(`Subscribed to ${message.symbol}`);
        break;
      case 'unsubscription_confirmed':
        console.log(`Unsubscribed from ${message.symbol}`);
        break;
      case 'pong':
        // Handle pong response
        break;
      case 'error':
        console.error('WebSocket error:', message.message);
        break;
    }
  }

  onOrderBookUpdate(symbol, data) {
    // Handle order book updates
    console.log(`Order book update for ${symbol}:`, data);
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const wsClient = new WebSocketClient('frontend-client-1');
wsClient.connect();

// Subscribe to symbols
wsClient.subscribe('AAPL');
wsClient.subscribe('TSLA');
```

## Backend Integration

### Broadcasting from Stock Monitor
```python
import httpx
import asyncio

async def broadcast_orderbook(symbol: str, orderbook_data: dict):
    """Broadcast order book data to WebSocket clients"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://websocket_middleware:8002/broadcast/orderbook",
            params={"symbol": symbol},
            json=orderbook_data
        )
        return response.json()

# Usage in your Futu callback
async def on_orderbook_update(symbol: str, orderbook_data: dict):
    # Store in database
    await store_orderbook_data(symbol, orderbook_data)
    
    # Broadcast to WebSocket clients
    await broadcast_orderbook(symbol, orderbook_data)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBSOCKET_PORT` | WebSocket server port | `8002` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379` |
| `ENVIRONMENT` | Application environment | `development` |

## Monitoring

### Health Check
```bash
curl http://localhost:8002/health
```

### Statistics
```bash
curl http://localhost:8002/stats
```

## Performance Considerations

### Latency Optimization
- Use async/await throughout the pipeline
- Minimize data transformation overhead
- Consider message compression for large order books
- Use `uvloop` for better performance

### Scalability
- Redis for session management across multiple instances
- Horizontal scaling with sticky sessions
- Connection limits per client
- Message batching for high-frequency updates

### Reliability
- Heartbeat mechanism (ping/pong)
- Automatic reconnection with exponential backoff
- Circuit breakers for external dependencies
- Graceful error handling

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if WebSocket middleware is running
   - Verify port 8002 is accessible
   - Check Docker network configuration

2. **Messages Not Received**
   - Verify subscription to correct symbol
   - Check client ID uniqueness
   - Monitor WebSocket connection status

3. **High Latency**
   - Check network connectivity
   - Monitor Redis performance
   - Review message processing pipeline

### Debug Mode
Set logging level to DEBUG for detailed connection and message logs:
```python
logging.basicConfig(level=logging.DEBUG)
``` 