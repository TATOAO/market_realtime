"""
Example usage of the Database Manager

This file demonstrates how to use the DatabaseManager class in both
backend and stock_monitor applications.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .database import DatabaseManager, get_database_manager, close_database_manager


async def example_stock_operations():
    """Example of basic stock operations."""
    print("=== Stock Operations Example ===")
    
    # Get database manager
    db = await get_database_manager()
    
    # Create a new stock
    stock_id = await db.create_stock("TSLA", "Tesla Inc.", "NASDAQ")
    print(f"Created stock with ID: {stock_id}")
    
    # Get stock information
    stock = await db.get_stock("TSLA")
    print(f"Stock info: {stock}")
    
    # Update stock information
    success = await db.update_stock("TSLA", name="Tesla, Inc.")
    print(f"Update successful: {success}")
    
    # List all stocks
    stocks = await db.list_stocks(limit=10)
    print(f"Found {len(stocks)} stocks")


async def example_price_operations():
    """Example of stock price time-series operations."""
    print("\n=== Stock Price Operations Example ===")
    
    db = await get_database_manager()
    
    # Save some price data
    now = datetime.utcnow()
    success = await db.save_stock_price(
        symbol="TSLA",
        time=now,
        open_price=150.0,
        high_price=155.0,
        low_price=148.0,
        close_price=152.5,
        volume=1000000
    )
    print(f"Saved price data: {success}")
    
    # Save more historical data
    for i in range(5):
        time = now - timedelta(hours=i+1)
        await db.save_stock_price(
            symbol="TSLA",
            time=time,
            open_price=150.0 + i,
            high_price=155.0 + i,
            low_price=148.0 + i,
            close_price=152.5 + i,
            volume=1000000 + i * 10000
        )
    
    # Get latest price
    latest_price = await db.get_latest_stock_price("TSLA")
    print(f"Latest price: {latest_price}")
    
    # Get price history
    start_time = now - timedelta(hours=6)
    prices = await db.get_stock_prices("TSLA", start_time, now, limit=10)
    print(f"Found {len(prices)} price records")


async def example_subscription_operations():
    """Example of subscription operations."""
    print("\n=== Subscription Operations Example ===")
    
    db = await get_database_manager()
    
    # Create a subscription
    subscription_id = await db.create_subscription(
        symbol="TSLA",
        user_id="user123",
        alert_price=160.0,
        alert_type="above"
    )
    print(f"Created subscription with ID: {subscription_id}")
    
    # Get user subscriptions
    subscriptions = await db.get_subscriptions(user_id="user123")
    print(f"User has {len(subscriptions)} subscriptions")
    
    # Update subscription
    success = await db.update_subscription(
        subscription_id,
        alert_price=165.0,
        is_active=True
    )
    print(f"Updated subscription: {success}")
    
    # Get all active subscriptions for a symbol
    symbol_subscriptions = await db.get_subscriptions(symbol="TSLA", active_only=True)
    print(f"Found {len(symbol_subscriptions)} active subscriptions for TSLA")


async def example_monitoring_logs():
    """Example of monitoring log operations."""
    print("\n=== Monitoring Logs Example ===")
    
    db = await get_database_manager()
    
    # Log some events
    await db.log_monitoring_event(
        symbol="TSLA",
        event_type="price_alert",
        message="Price exceeded alert threshold",
        data={"current_price": 165.5, "threshold": 160.0}
    )
    
    await db.log_monitoring_event(
        symbol="TSLA",
        event_type="subscription_created",
        message="New price alert subscription created",
        data={"user_id": "user123", "alert_price": 160.0}
    )
    
    # Get monitoring logs
    logs = await db.get_monitoring_logs(symbol="TSLA", limit=5)
    print(f"Found {len(logs)} monitoring logs for TSLA")
    
    for log in logs:
        print(f"- {log['event_type']}: {log['message']}")


async def example_health_check():
    """Example of database health check."""
    print("\n=== Health Check Example ===")
    
    db = await get_database_manager()
    
    # Check database health
    is_healthy = await db.health_check()
    print(f"Database is healthy: {is_healthy}")


async def example_custom_queries():
    """Example of custom query execution."""
    print("\n=== Custom Queries Example ===")
    
    db = await get_database_manager()
    
    # Execute a custom query
    result = await db.execute_query(
        "SELECT COUNT(*) as total_stocks FROM stocks"
    )
    print(f"Total stocks in database: {result[0]['total_stocks']}")
    
    # Execute a transaction
    queries = [
        ("INSERT INTO stocks (symbol, name, exchange) VALUES ($1, $2, $3)", 
         ["AMD", "Advanced Micro Devices", "NASDAQ"]),
        ("INSERT INTO stocks (symbol, name, exchange) VALUES ($1, $2, $3)", 
         ["NVDA", "NVIDIA Corporation", "NASDAQ"])
    ]
    
    success = await db.execute_transaction(queries)
    print(f"Transaction successful: {success}")


async def main():
    """Run all examples."""
    print("Database Manager Examples")
    print("=" * 50)
    
    try:
        await example_stock_operations()
        await example_price_operations()
        await example_subscription_operations()
        await example_monitoring_logs()
        await example_health_check()
        await example_custom_queries()
        
    except Exception as e:
        print(f"Error running examples: {e}")
    
    finally:
        # Clean up
        await close_database_manager()


if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault('DATABASE_URL', 'postgresql://futu_user:futu_password@localhost:5432/futu_db')
    
    # Run examples
    asyncio.run(main()) 