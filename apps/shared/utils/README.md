# Database Manager Utility

This module provides a shared database manager utility for TimescaleDB operations that can be used by both the backend and stock_monitor applications.

## Features

- **Async PostgreSQL Client**: Uses `asyncpg` for high-performance async database operations
- **Connection Pooling**: Efficient connection management with configurable pool sizes
- **TimescaleDB Support**: Optimized for time-series data operations
- **Comprehensive CRUD Operations**: Full support for stocks, prices, subscriptions, and monitoring logs
- **Error Handling**: Robust error handling with detailed logging
- **Transaction Support**: Support for multi-query transactions
- **Health Checks**: Database connectivity monitoring

## Installation

The database manager requires the following dependencies:

```bash
# Install dependencies
uv pip install asyncpg pydantic sqlmodel python-dotenv
```

## Quick Start

### Basic Usage

```python
import asyncio
from apps.shared.utils.database import get_database_manager

async def main():
    # Get the database manager instance
    db = await get_database_manager()
  
    # Check database health
    is_healthy = await db.health_check()
    print(f"Database is healthy: {is_healthy}")
  
    # Create a stock
    stock_id = await db.create_stock("AAPL", "Apple Inc.", "NASDAQ")
    print(f"Created stock with ID: {stock_id}")
  
    # Get stock information
    stock = await db.get_stock("AAPL")
    print(f"Stock: {stock}")

# Run the example
asyncio.run(main())
```

### Environment Setup

Make sure the `DATABASE_URL` environment variable is set:

```bash
export DATABASE_URL="postgresql://futu_user:futu_password@localhost:5432/futu_db"
```

Or in your application:

```python
import os
os.environ['DATABASE_URL'] = 'postgresql://futu_user:futu_password@localhost:5432/futu_db'
```

## API Reference

### DatabaseManager Class

#### Initialization

```python
from apps.shared.utils.database import DatabaseManager

# Create with custom database URL
db = DatabaseManager("postgresql://user:pass@host:port/db")

# Or use environment variable
db = DatabaseManager()  # Uses DATABASE_URL env var

# Initialize connection pool
await db.initialize(min_size=5, max_size=20)

# Clean up
await db.close()
```

#### Stock Operations

```python
# Create a stock
stock_id = await db.create_stock("TSLA", "Tesla Inc.", "NASDAQ")

# Get stock by symbol
stock = await db.get_stock("TSLA")

# Update stock
success = await db.update_stock("TSLA", name="Tesla, Inc.")

# List stocks
stocks = await db.list_stocks(limit=100, offset=0)
```

#### Price Operations (Time-Series)

```python
from datetime import datetime

# Save price data
success = await db.save_stock_price(
    symbol="TSLA",
    time=datetime.utcnow(),
    open_price=150.0,
    high_price=155.0,
    low_price=148.0,
    close_price=152.5,
    volume=1000000
)

# Get latest price
latest = await db.get_latest_stock_price("TSLA")

# Get price history
prices = await db.get_stock_prices(
    symbol="TSLA",
    start_time=datetime.utcnow() - timedelta(hours=24),
    end_time=datetime.utcnow(),
    limit=1000
)
```

#### Subscription Operations

```python
# Create subscription
sub_id = await db.create_subscription(
    symbol="TSLA",
    user_id="user123",
    alert_price=160.0,
    alert_type="above"  # or "below"
)

# Get user subscriptions
subscriptions = await db.get_subscriptions(user_id="user123")

# Update subscription
success = await db.update_subscription(
    sub_id,
    alert_price=165.0,
    is_active=True
)

# Delete subscription
success = await db.delete_subscription(sub_id)
```

#### Monitoring Logs

```python
# Log an event
log_id = await db.log_monitoring_event(
    symbol="TSLA",
    event_type="price_alert",
    message="Price exceeded threshold",
    data={"current_price": 165.5, "threshold": 160.0}
)

# Get logs
logs = await db.get_monitoring_logs(
    symbol="TSLA",
    event_type="price_alert",
    limit=100
)
```

#### Utility Methods

```python
# Health check
is_healthy = await db.health_check()

# Custom query
result = await db.execute_query("SELECT COUNT(*) FROM stocks")

# Transaction
queries = [
    ("INSERT INTO stocks (symbol, name) VALUES ($1, $2)", ["AMD", "AMD Inc."]),
    ("INSERT INTO stocks (symbol, name) VALUES ($1, $2)", ["NVDA", "NVIDIA Corp."])
]
success = await db.execute_transaction(queries)
```

### Global Instance Management

For convenience, the module provides global instance management:

```python
from apps.shared.utils.database import get_database_manager, close_database_manager

# Get global instance (creates if not exists)
db = await get_database_manager()

# Close global instance
await close_database_manager()
```

## Integration Examples

### Backend Application

```python
# server/main.py or similar
from fastapi import FastAPI, Depends
from apps.shared.utils.database import get_database_manager

app = FastAPI()

async def get_db():
    return await get_database_manager()

@app.get("/stocks/{symbol}")
async def get_stock(symbol: str, db = Depends(get_db)):
    stock = await db.get_stock(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

@app.post("/stocks")
async def create_stock(stock_data: dict, db = Depends(get_db)):
    stock_id = await db.create_stock(
        stock_data["symbol"],
        stock_data["name"],
        stock_data["exchange"]
    )
    return {"id": stock_id}
```

### Stock Monitor Application

```python
# server/monitoring.py or similar
from apps.shared.utils.database import get_database_manager

async def monitor_stock_prices():
    db = await get_database_manager()
  
    # Get active subscriptions
    subscriptions = await db.get_subscriptions(active_only=True)
  
    for sub in subscriptions:
        # Get latest price
        latest_price = await db.get_latest_stock_price(sub["symbol"])
      
        if latest_price:
            current_price = latest_price["close"]
          
            # Check alert conditions
            if sub["alert_type"] == "above" and current_price > sub["alert_price"]:
                await db.log_monitoring_event(
                    symbol=sub["symbol"],
                    event_type="price_alert",
                    message=f"Price {current_price} exceeded threshold {sub['alert_price']}",
                    data={"current_price": current_price, "threshold": sub["alert_price"]}
                )
```

## Error Handling

The database manager includes comprehensive error handling:

```python
try:
    stock = await db.get_stock("INVALID")
    if stock is None:
        print("Stock not found")
except Exception as e:
    print(f"Database error: {e}")
```

## Performance Considerations

- **Connection Pooling**: The manager uses connection pooling for efficient resource usage
- **Batch Operations**: Use transactions for multiple related operations
- **Indexing**: The database schema includes appropriate indexes for common queries
- **Time-Series Optimization**: TimescaleDB hypertables are used for price data

## Testing

Run the example usage to test the database manager:

```bash
cd apps/shared/utils
python example_usage.py
```

Make sure your TimescaleDB instance is running and accessible before running the examples.

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check your `DATABASE_URL` and ensure TimescaleDB is running
2. **Pool Exhaustion**: Increase `max_size` in the pool configuration
3. **Timeout Errors**: Increase `command_timeout` in the pool configuration

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new features to the database manager:

1. Follow the existing async pattern
2. Add comprehensive error handling
3. Include logging for important operations
4. Update this documentation
5. Add example usage in `example_usage.py`
