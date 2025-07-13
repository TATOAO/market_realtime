# Caching System for Real-time Market Data

## Overview

This document explains the caching system implemented for the real-time market data platform. The system provides **historical data persistence** and **fast access to recent data** to ensure users see historical charts immediately when they reload the page.

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
                   │ (Real-time  │
                   │   Cache)    │
                   └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │TimescaleDB  │
                   │(Historical  │
                   │   Storage)  │
                   └─────────────┘
```

## Key Features

### 1. **Historical Data Persistence**

- All order book data is stored in TimescaleDB (time-series database)
- Data is automatically organized by time for efficient querying
- Supports queries for today's data, historical ranges, and summaries

### 2. **Real-time Caching**

- Recent data is cached in Redis for fast access
- Cache includes both latest data and recent history (last 100 points)
- Automatic cache invalidation with TTL (1 hour default)

### 3. **Seamless User Experience**

- When users subscribe to a symbol, they immediately receive:
  1. **Historical data** from the beginning of today
  2. **Latest real-time data**
  3. **Continuous real-time updates**

### 4. **Automatic Data Processing**

- Order book data is automatically processed and stored
- Key metrics are calculated and stored (mid-price, spread, volumes)
- Both raw order book levels and calculated metrics are preserved

## Data Flow

### 1. **Data Ingestion**

```
Futu API → WebSocket Middleware → Database + Cache → Frontend Clients
```

### 2. **Data Storage**

- **TimescaleDB**: Stores all historical data with time-series optimization
- **Redis**: Caches recent data for fast retrieval
- **WebSocket**: Streams real-time updates to connected clients

### 3. **Data Retrieval**

- **New Subscriptions**: Historical data + latest data + real-time stream
- **Page Reloads**: Historical data immediately available
- **Historical Queries**: Direct database access for analysis

## Database Schema

### Order Book Data Table

```sql
CREATE TABLE order_book_data (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    best_bid DECIMAL(10, 4),
    best_ask DECIMAL(10, 4),
    mid_price DECIMAL(10, 4),
    bid_volume DECIMAL(20, 2),
    ask_volume DECIMAL(20, 2),
    total_volume DECIMAL(20, 2),
    spread DECIMAL(10, 4),
    spread_percentage DECIMAL(10, 4),
    bid_levels JSONB,
    ask_levels JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Redis Cache Structure

```
orderbook:{symbol}:latest     → Latest order book data (TTL: 1 hour)
orderbook:{symbol}:history    → Recent history list (TTL: 1 hour, max 100 entries)
```

## API Endpoints

### WebSocket Endpoints

- `ws://localhost:8000/ws/{client_id}` - WebSocket connection with client ID
- `ws://localhost:8000/ws` - Simple WebSocket connection (auto-generates client ID)

### HTTP Endpoints

- `GET /health` - Health check for all services
- `GET /stats` - Detailed statistics and cache info
- `GET /orderbook/{symbol}/today` - Today's data for a symbol
- `GET /orderbook/{symbol}/history?hours=24` - Historical data for a symbol

### WebSocket Messages

#### Client to Server

```json
{
  "action": "subscribe",
  "symbol": "US.AAPL"
}
```

#### Server to Client

```json
// Historical data (sent on subscription)
{
  "type": "historical_data",
  "symbol": "US.AAPL",
  "data": [...]
}

// Real-time updates
{
  "type": "orderbook_update",
  "symbol": "US.AAPL",
  "data": {...},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# WebSocket
WEBSOCKET_PORT=8000
```

### Docker Compose

The system is configured to run with Docker Compose:

```yaml
services:
  websocket_middleware:
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:pass@timescaledb:5432/dbname
    depends_on:
      - redis
      - timescaledb
```

## Usage Examples

### 1. **Start the System**

```bash
# Start all services
cd docker
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### 2. **Test the Caching System**

```bash
cd apps/websocket_middleware
python test_caching_system.py
```

### 3. **Query Historical Data**

```bash
# Get today's data
curl "http://localhost:8000/orderbook/US.AAPL/today"

# Get last 24 hours
curl "http://localhost:8000/orderbook/US.AAPL/history?hours=24"
```

### 4. **Frontend Integration**

```typescript
// The frontend automatically receives historical data
// when subscribing to a symbol
const ws = new WebSocket('ws://localhost:8000/ws');
ws.send(JSON.stringify({
  action: 'subscribe',
  symbol: 'US.AAPL'
}));

// Historical data is received first, then real-time updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'historical_data') {
    // Display historical chart data
    displayHistoricalData(data.data);
  } else if (data.type === 'orderbook_update') {
    // Update real-time chart
    updateRealTimeData(data.data);
  }
};
```

## Performance Considerations

### 1. **Database Performance**

- TimescaleDB hypertables for efficient time-series queries
- Indexes on symbol and time for fast lookups
- Automatic data retention policies (configurable)

### 2. **Cache Performance**

- Redis for sub-millisecond access to recent data
- TTL-based cache invalidation to prevent memory bloat
- Limited history size (100 entries) to control memory usage

### 3. **WebSocket Performance**

- Efficient broadcasting to subscribed clients only
- Automatic cleanup of disconnected clients
- Connection pooling and health monitoring

## Monitoring and Maintenance

### 1. **Health Monitoring**

```bash
# Check system health
curl http://localhost:8000/health

# Get detailed stats
curl http://localhost:8000/stats
```

### 2. **Cache Management**

```python
# Clear all cache (if needed)
from apps.shared.utils.cache import get_cache_manager
cache = await get_cache_manager()
await cache.clear_all_order_book_cache()
```

### 3. **Database Maintenance**

```sql
-- Check data retention
SELECT 
    symbol,
    COUNT(*) as records,
    MIN(time) as earliest,
    MAX(time) as latest
FROM order_book_data 
GROUP BY symbol;

-- Clean old data (if needed)
DELETE FROM order_book_data 
WHERE time < NOW() - INTERVAL '30 days';
```

## Troubleshooting

### Common Issues

1. **No Historical Data on Page Reload**

   - Check if database is connected: `curl http://localhost:8000/health`
   - Verify data is being stored: Check database directly
   - Check cache status in Redis
2. **Slow Data Loading**

   - Check database performance and indexes
   - Monitor Redis memory usage
   - Verify network connectivity
3. **WebSocket Connection Issues**

   - Check WebSocket middleware logs
   - Verify port configuration
   - Check firewall settings

### Debug Commands

```bash
# Check Redis
redis-cli ping
redis-cli keys "orderbook:*"

# Check database
psql -h localhost -U postgres -d futu_helper -c "SELECT COUNT(*) FROM order_book_data;"

# Check logs
docker-compose logs websocket_middleware
```

## Future Enhancements

### 1. **Data Compression**

- Implement data compression for historical data
- Use TimescaleDB compression policies

### 2. **Advanced Caching**

- Implement cache warming strategies
- Add cache hit/miss monitoring
- Implement cache eviction policies

### 3. **Analytics**

- Add data aggregation for different time periods
- Implement trend analysis
- Add alerting based on historical patterns

### 4. **Scalability**

- Implement horizontal scaling for WebSocket servers
- Add load balancing for multiple instances
- Implement data partitioning strategies

## Conclusion

The caching system provides a robust foundation for real-time market data with historical persistence. It ensures users always see meaningful charts with historical context while maintaining high performance for real-time updates.

The hybrid approach of Redis + TimescaleDB gives us the best of both worlds: fast access to recent data and reliable long-term storage for historical analysis.
