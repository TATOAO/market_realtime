"""
WebSocket Middleware for Real-time Stock Data
Handles WebSocket connections and broadcasts order book updates to frontend clients
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from pydantic import BaseModel
from datetime import datetime, timedelta

# Import shared utilities
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from utils.database import DatabaseManager
from utils.cache import RedisCacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="WebSocket Middleware", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
db_manager: Optional[DatabaseManager] = None
cache_manager: Optional[RedisCacheManager] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and cache connections on startup."""
    global db_manager, cache_manager
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        await db_manager.initialize()
        await db_manager.create_order_book_table()
        logger.info("Database manager initialized")
        
        # Initialize cache manager
        cache_manager = RedisCacheManager()
        await cache_manager.initialize()
        logger.info("Cache manager initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown."""
    global db_manager, cache_manager
    
    if db_manager:
        await db_manager.close()
    if cache_manager:
        await cache_manager.close()
    logger.info("Services shut down")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.symbol_subscriptions: Dict[str, Set[str]] = {}  # symbol -> set of client_ids
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of symbols

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove client from all symbol subscriptions
        if client_id in self.client_subscriptions:
            for symbol in self.client_subscriptions[client_id]:
                if symbol in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol].discard(client_id)
                    if not self.symbol_subscriptions[symbol]:
                        del self.symbol_subscriptions[symbol]
            del self.client_subscriptions[client_id]
        
        logger.info(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")

    async def subscribe_to_symbol(self, client_id: str, symbol: str):
        """Subscribe a client to a specific stock symbol"""
        if client_id not in self.active_connections:
            raise HTTPException(status_code=400, detail="Client not connected")
        
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        
        self.symbol_subscriptions[symbol].add(client_id)
        self.client_subscriptions[client_id].add(symbol)
        
        logger.info(f"Client {client_id} subscribed to {symbol}")
        
        # Send confirmation
        await self.send_personal_message(
            {"type": "subscription_confirmed", "symbol": symbol}, 
            client_id
        )
        
        # Send cached historical data if available
        await self.send_cached_data(client_id, symbol)

    async def send_cached_data(self, client_id: str, symbol: str):
        """Send cached historical data to a newly subscribed client"""
        try:
            if cache_manager:
                # Get today's cached data
                cached_data = await cache_manager.get_cached_order_book_data_today(symbol)
                
                if cached_data:
                    # Send historical data
                    await self.send_personal_message({
                        "type": "historical_data",
                        "symbol": symbol,
                        "data": cached_data
                    }, client_id)
                    logger.info(f"Sent {len(cached_data)} cached data points to client {client_id} for {symbol}")
                
                # Also send latest data if available
                latest_data = await cache_manager.get_cached_order_book_data(symbol)
                if latest_data:
                    await self.send_personal_message({
                        "type": "orderbook_update",
                        "symbol": symbol,
                        "data": latest_data,
                        "timestamp": latest_data.get("timestamp")
                    }, client_id)
                    
        except Exception as e:
            logger.error(f"Error sending cached data to client {client_id}: {e}")

    async def unsubscribe_from_symbol(self, client_id: str, symbol: str):
        """Unsubscribe a client from a specific stock symbol"""
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(client_id)
            if not self.symbol_subscriptions[symbol]:
                del self.symbol_subscriptions[symbol]
        
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(symbol)
        
        logger.info(f"Client {client_id} unsubscribed from {symbol}")
        
        # Send confirmation
        await self.send_personal_message(
            {"type": "unsubscription_confirmed", "symbol": symbol}, 
            client_id
        )

    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """Broadcast message to all clients subscribed to a specific symbol"""
        if symbol not in self.symbol_subscriptions:
            return
        
        disconnected_clients = set()
        
        for client_id in self.symbol_subscriptions[symbol]:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                disconnected_clients.add(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending personal message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast_orderbook(self, symbol: str, orderbook_data: dict):
        """Broadcast order book data to subscribed clients and store in database/cache"""
        message = {
            "type": "orderbook_update",
            "symbol": symbol,
            "data": orderbook_data,
            "timestamp": orderbook_data.get("timestamp")
        }
        
        # Store in database
        await self.store_orderbook_data(symbol, orderbook_data)
        
        # Cache the data
        await self.cache_orderbook_data(symbol, orderbook_data)
        
        # Broadcast to clients
        await self.broadcast_to_symbol(symbol, message)

    async def store_orderbook_data(self, symbol: str, orderbook_data: dict):
        """Store order book data in the database"""
        try:
            if not db_manager:
                return
            
            # Extract key metrics from order book data
            bid_levels = orderbook_data.get("Bid", [])
            ask_levels = orderbook_data.get("Ask", [])
            
            if not bid_levels or not ask_levels:
                return
            
            # Calculate metrics
            valid_bids = [level for level in bid_levels if isinstance(level, list) and len(level) >= 2]
            valid_asks = [level for level in ask_levels if isinstance(level, list) and len(level) >= 2]
            
            if not valid_bids or not valid_asks:
                return
            
            best_bid = max(level[0] for level in valid_bids)
            best_ask = min(level[0] for level in valid_asks)
            mid_price = (best_bid + best_ask) / 2
            spread = best_ask - best_bid
            spread_percentage = (spread / mid_price) * 100 if mid_price > 0 else 0
            
            bid_volume = sum(level[1] for level in valid_bids)
            ask_volume = sum(level[1] for level in valid_asks)
            total_volume = bid_volume + ask_volume
            
            # Parse timestamp
            timestamp_str = orderbook_data.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.utcnow()
            else:
                timestamp = datetime.utcnow()
            
            # Store in database
            await db_manager.save_order_book_data(
                symbol=symbol,
                time=timestamp,
                best_bid=best_bid,
                best_ask=best_ask,
                mid_price=mid_price,
                bid_volume=bid_volume,
                ask_volume=ask_volume,
                total_volume=total_volume,
                spread=spread,
                spread_percentage=spread_percentage,
                bid_levels=bid_levels,
                ask_levels=ask_levels
            )
            
        except Exception as e:
            logger.error(f"Error storing order book data for {symbol}: {e}")

    async def cache_orderbook_data(self, symbol: str, orderbook_data: dict):
        """Cache order book data in Redis"""
        try:
            if not cache_manager:
                return
            
            # Prepare data for caching
            cache_data = {
                "symbol": symbol,
                "timestamp": orderbook_data.get("timestamp"),
                "data": orderbook_data,
                "cached_at": datetime.utcnow().isoformat()
            }
            
            await cache_manager.cache_order_book_data(symbol, cache_data, ttl_seconds=3600)
            
        except Exception as e:
            logger.error(f"Error caching order book data for {symbol}: {e}")

# Create connection manager instance
manager = ConnectionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = await db_manager.health_check() if db_manager else False
    cache_healthy = await cache_manager.health_check() if cache_manager else False
    
    return {
        "status": "healthy" if db_healthy and cache_healthy else "unhealthy",
        "database": "healthy" if db_healthy else "unhealthy",
        "cache": "healthy" if cache_healthy else "unhealthy",
        "connections": len(manager.active_connections),
        "subscriptions": len(manager.symbol_subscriptions)
    }

@app.get("/stats")
async def get_stats():
    """Get detailed statistics"""
    cache_stats = await cache_manager.get_cache_stats() if cache_manager else {}
    
    return {
        "active_connections": len(manager.active_connections),
        "symbol_subscriptions": len(manager.symbol_subscriptions),
        "subscription_details": {
            symbol: len(clients) for symbol, clients in manager.symbol_subscriptions.items()
        },
        "cache_stats": cache_stats
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for client connections"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("action") == "subscribe":
                await manager.subscribe_to_symbol(client_id, message["symbol"])
            
            elif message.get("action") == "unsubscribe":
                await manager.unsubscribe_from_symbol(client_id, message["symbol"])
            
            elif message.get("action") == "ping":
                await manager.send_personal_message({"type": "pong"}, client_id)
            
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Unknown action"}, 
                    client_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

@app.websocket("/ws")
async def websocket_endpoint_simple(websocket: WebSocket):
    """Simple WebSocket endpoint that auto-generates client ID"""
    import uuid
    client_id = f"frontend-{uuid.uuid4().hex[:8]}"
    await manager.connect(websocket, client_id)
    
    try:
        # Send connection confirmation
        await manager.send_personal_message({"type": "connected", "client_id": client_id}, client_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("action") == "subscribe":
                await manager.subscribe_to_symbol(client_id, message["symbol"])
            
            elif message.get("action") == "unsubscribe":
                await manager.unsubscribe_from_symbol(client_id, message["symbol"])
            
            elif message.get("action") == "ping":
                await manager.send_personal_message({"type": "pong"}, client_id)
            
            else:
                await manager.send_personal_message(
                    {"type": "error", "message": "Unknown action"}, 
                    client_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

@app.post("/broadcast/orderbook")
async def broadcast_orderbook_endpoint(symbol: str, orderbook_data: dict):
    """HTTP endpoint for broadcasting order book data (called by stock monitor)"""
    await manager.broadcast_orderbook(symbol, orderbook_data)
    return {"status": "broadcasted", "symbol": symbol, "subscribers": len(manager.symbol_subscriptions.get(symbol, set()))}

@app.get("/orderbook/{symbol}/history")
async def get_orderbook_history(symbol: str, hours: int = 24):
    """Get historical order book data for a symbol"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        data = await db_manager.get_order_book_data(symbol, start_time, end_time, limit=1000)
        return {"symbol": symbol, "data": data, "count": len(data)}
        
    except Exception as e:
        logger.error(f"Error fetching order book history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch order book history")

@app.get("/orderbook/{symbol}/today")
async def get_orderbook_today(symbol: str):
    """Get all order book data for a symbol from today"""
    try:
        if not db_manager:
            raise HTTPException(status_code=503, detail="Database not available")
        
        data = await db_manager.get_order_book_data_today(symbol)
        return {"symbol": symbol, "data": data, "count": len(data)}
        
    except Exception as e:
        logger.error(f"Error fetching today's order book data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch today's order book data") 