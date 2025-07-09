"""
Database Manager for TimescaleDB

This module provides a shared database manager utility that can be used by both
the backend and stock_monitor applications. It handles connection management,
data fetching, and saving operations using async PostgreSQL client.
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Pool, Connection
from asyncpg.exceptions import PostgresError, UniqueViolationError

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Async database manager for TimescaleDB operations.
    
    This class provides methods for:
    - Connection management with connection pooling
    - Stock data operations (CRUD)
    - Stock price time-series data operations
    - Monitoring subscription operations
    - Error handling and logging
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            database_url: PostgreSQL connection string. If not provided,
                         will use DATABASE_URL environment variable.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("Database URL must be provided or set in DATABASE_URL environment variable")
        
        self.pool: Optional[Pool] = None
        self._connection_lock = asyncio.Lock()
    
    async def initialize(self, min_size: int = 5, max_size: int = 20) -> None:
        """
        Initialize the connection pool.
        
        Args:
            min_size: Minimum number of connections in the pool
            max_size: Maximum number of connections in the pool
        """
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60,
                server_settings={
                    'application_name': 'futu_helper_db_manager'
                }
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """
        Get a database connection from the pool.
        
        Yields:
            Connection: AsyncPG connection object
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def health_check(self) -> bool:
        """
        Check if the database is healthy and accessible.
        
        Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # Stock operations
    async def get_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get stock information by symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Dict containing stock information or None if not found
        """
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT id, symbol, name, exchange, created_at, updated_at "
                    "FROM stocks WHERE symbol = $1",
                    symbol
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching stock {symbol}: {e}")
            return None
    
    async def create_stock(self, symbol: str, name: str, exchange: str) -> Optional[int]:
        """
        Create a new stock record.
        
        Args:
            symbol: Stock symbol
            name: Stock name
            exchange: Stock exchange
            
        Returns:
            Stock ID if created successfully, None otherwise
        """
        try:
            async with self.get_connection() as conn:
                stock_id = await conn.fetchval(
                    "INSERT INTO stocks (symbol, name, exchange) VALUES ($1, $2, $3) "
                    "RETURNING id",
                    symbol, name, exchange
                )
                logger.info(f"Created stock: {symbol} (ID: {stock_id})")
                return stock_id
        except UniqueViolationError:
            logger.warning(f"Stock {symbol} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating stock {symbol}: {e}")
            return None
    
    async def update_stock(self, symbol: str, name: str = None, exchange: str = None) -> bool:
        """
        Update stock information.
        
        Args:
            symbol: Stock symbol
            name: New stock name (optional)
            exchange: New exchange (optional)
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                # Build dynamic update query
                update_parts = []
                params = [symbol]
                param_count = 1
                
                if name is not None:
                    update_parts.append(f"name = ${param_count + 1}")
                    params.append(name)
                    param_count += 1
                
                if exchange is not None:
                    update_parts.append(f"exchange = ${param_count + 1}")
                    params.append(exchange)
                    param_count += 1
                
                if not update_parts:
                    return False
                
                update_parts.append("updated_at = NOW()")
                
                query = f"UPDATE stocks SET {', '.join(update_parts)} WHERE symbol = $1"
                result = await conn.execute(query, *params)
                
                success = result.split()[-1] == '1'
                if success:
                    logger.info(f"Updated stock: {symbol}")
                return success
        except Exception as e:
            logger.error(f"Error updating stock {symbol}: {e}")
            return False
    
    async def list_stocks(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List stocks with pagination.
        
        Args:
            limit: Maximum number of stocks to return
            offset: Number of stocks to skip
            
        Returns:
            List of stock dictionaries
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    "SELECT id, symbol, name, exchange, created_at, updated_at "
                    "FROM stocks ORDER BY symbol LIMIT $1 OFFSET $2",
                    limit, offset
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing stocks: {e}")
            return []
    
    # Stock price operations (time-series data)
    async def save_stock_price(self, symbol: str, time: datetime, open_price: float = None,
                              high_price: float = None, low_price: float = None,
                              close_price: float = None, volume: int = None) -> bool:
        """
        Save stock price data to the time-series table.
        
        Args:
            symbol: Stock symbol
            time: Timestamp for the price data
            open_price: Opening price
            high_price: Highest price
            low_price: Lowest price
            close_price: Closing price
            volume: Trading volume
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    "INSERT INTO stock_prices (time, symbol, open, high, low, close, volume) "
                    "VALUES ($1, $2, $3, $4, $5, $6, $7)",
                    time, symbol, open_price, high_price, low_price, close_price, volume
                )
                return True
        except Exception as e:
            logger.error(f"Error saving stock price for {symbol}: {e}")
            return False
    
    async def get_stock_prices(self, symbol: str, start_time: datetime = None,
                              end_time: datetime = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get stock price data for a given symbol and time range.
        
        Args:
            symbol: Stock symbol
            start_time: Start of time range (default: 24 hours ago)
            end_time: End of time range (default: now)
            limit: Maximum number of records to return
            
        Returns:
            List of price data dictionaries
        """
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if end_time is None:
            end_time = datetime.utcnow()
        
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    "SELECT time, symbol, open, high, low, close, volume, created_at "
                    "FROM stock_prices "
                    "WHERE symbol = $1 AND time BETWEEN $2 AND $3 "
                    "ORDER BY time DESC LIMIT $4",
                    symbol, start_time, end_time, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching stock prices for {symbol}: {e}")
            return []
    
    async def get_latest_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest stock price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest price data dictionary or None if not found
        """
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT time, symbol, open, high, low, close, volume, created_at "
                    "FROM stock_prices "
                    "WHERE symbol = $1 "
                    "ORDER BY time DESC LIMIT 1",
                    symbol
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            return None
    
    # Stock subscription operations
    async def create_subscription(self, symbol: str, user_id: str, alert_price: float,
                                 alert_type: str) -> Optional[int]:
        """
        Create a stock price alert subscription.
        
        Args:
            symbol: Stock symbol
            user_id: User identifier
            alert_price: Price threshold for alert
            alert_type: 'above' or 'below'
            
        Returns:
            Subscription ID if created successfully, None otherwise
        """
        try:
            async with self.get_connection() as conn:
                subscription_id = await conn.fetchval(
                    "INSERT INTO stock_subscriptions (symbol, user_id, alert_price, alert_type) "
                    "VALUES ($1, $2, $3, $4) RETURNING id",
                    symbol, user_id, alert_price, alert_type
                )
                logger.info(f"Created subscription: {symbol} for user {user_id}")
                return subscription_id
        except Exception as e:
            logger.error(f"Error creating subscription for {symbol}: {e}")
            return None
    
    async def get_subscriptions(self, symbol: str = None, user_id: str = None,
                               active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get stock subscriptions with optional filtering.
        
        Args:
            symbol: Filter by symbol (optional)
            user_id: Filter by user ID (optional)
            active_only: Only return active subscriptions
            
        Returns:
            List of subscription dictionaries
        """
        try:
            async with self.get_connection() as conn:
                query = "SELECT id, symbol, user_id, alert_price, alert_type, is_active, created_at, updated_at FROM stock_subscriptions WHERE 1=1"
                params = []
                param_count = 0
                
                if symbol:
                    param_count += 1
                    query += f" AND symbol = ${param_count}"
                    params.append(symbol)
                
                if user_id:
                    param_count += 1
                    query += f" AND user_id = ${param_count}"
                    params.append(user_id)
                
                if active_only:
                    query += " AND is_active = TRUE"
                
                query += " ORDER BY created_at DESC"
                
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching subscriptions: {e}")
            return []
    
    async def update_subscription(self, subscription_id: int, alert_price: float = None,
                                 alert_type: str = None, is_active: bool = None) -> bool:
        """
        Update a subscription.
        
        Args:
            subscription_id: Subscription ID to update
            alert_price: New alert price (optional)
            alert_type: New alert type (optional)
            is_active: New active status (optional)
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                update_parts = []
                params = [subscription_id]
                param_count = 1
                
                if alert_price is not None:
                    param_count += 1
                    update_parts.append(f"alert_price = ${param_count}")
                    params.append(alert_price)
                
                if alert_type is not None:
                    param_count += 1
                    update_parts.append(f"alert_type = ${param_count}")
                    params.append(alert_type)
                
                if is_active is not None:
                    param_count += 1
                    update_parts.append(f"is_active = ${param_count}")
                    params.append(is_active)
                
                if not update_parts:
                    return False
                
                update_parts.append("updated_at = NOW()")
                
                query = f"UPDATE stock_subscriptions SET {', '.join(update_parts)} WHERE id = $1"
                result = await conn.execute(query, *params)
                
                success = result.split()[-1] == '1'
                if success:
                    logger.info(f"Updated subscription: {subscription_id}")
                return success
        except Exception as e:
            logger.error(f"Error updating subscription {subscription_id}: {e}")
            return False
    
    async def delete_subscription(self, subscription_id: int) -> bool:
        """
        Delete a subscription.
        
        Args:
            subscription_id: Subscription ID to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "DELETE FROM stock_subscriptions WHERE id = $1",
                    subscription_id
                )
                success = result.split()[-1] == '1'
                if success:
                    logger.info(f"Deleted subscription: {subscription_id}")
                return success
        except Exception as e:
            logger.error(f"Error deleting subscription {subscription_id}: {e}")
            return False
    
    # Monitoring log operations
    async def log_monitoring_event(self, symbol: str, event_type: str, message: str,
                                  data: Dict[str, Any] = None) -> Optional[int]:
        """
        Log a monitoring event.
        
        Args:
            symbol: Stock symbol
            event_type: Type of event (e.g., 'price_alert', 'subscription_created')
            message: Event message
            data: Additional event data (optional)
            
        Returns:
            Log ID if created successfully, None otherwise
        """
        try:
            async with self.get_connection() as conn:
                log_id = await conn.fetchval(
                    "INSERT INTO monitoring_logs (symbol, event_type, message, data) "
                    "VALUES ($1, $2, $3, $4) RETURNING id",
                    symbol, event_type, message, data
                )
                logger.info(f"Logged monitoring event: {event_type} for {symbol}")
                return log_id
        except Exception as e:
            logger.error(f"Error logging monitoring event for {symbol}: {e}")
            return None
    
    async def get_monitoring_logs(self, symbol: str = None, event_type: str = None,
                                 limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get monitoring logs with optional filtering.
        
        Args:
            symbol: Filter by symbol (optional)
            event_type: Filter by event type (optional)
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of log dictionaries
        """
        try:
            async with self.get_connection() as conn:
                query = "SELECT id, symbol, event_type, message, data, created_at FROM monitoring_logs WHERE 1=1"
                params = []
                param_count = 0
                
                if symbol:
                    param_count += 1
                    query += f" AND symbol = ${param_count}"
                    params.append(symbol)
                
                if event_type:
                    param_count += 1
                    query += f" AND event_type = ${param_count}"
                    params.append(event_type)
                
                query += " ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params.extend([limit, offset])
                
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching monitoring logs: {e}")
            return []
    
    # Utility methods
    async def execute_query(self, query: str, *args) -> Any:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Query result
        """
        try:
            async with self.get_connection() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def execute_transaction(self, queries: List[tuple]) -> bool:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            bool: True if all queries executed successfully, False otherwise
        """
        try:
            async with self.get_connection() as conn:
                async with conn.transaction():
                    for query, params in queries:
                        await conn.execute(query, *params)
                return True
        except Exception as e:
            logger.error(f"Error executing transaction: {e}")
            return False


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


async def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager: Initialized database manager
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        await _db_manager.initialize()
    return _db_manager


async def close_database_manager() -> None:
    """Close the global database manager."""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None 