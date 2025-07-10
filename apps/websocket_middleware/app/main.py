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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.symbol_subscriptions: Dict[str, Set[str]] = {}  # symbol -> set of client_ids
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of symbols
        self.redis_client: Optional[redis.Redis] = None

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
        """Broadcast order book data to subscribed clients"""
        message = {
            "type": "orderbook_update",
            "symbol": symbol,
            "data": orderbook_data,
            "timestamp": orderbook_data.get("timestamp")
        }
        await self.broadcast_to_symbol(symbol, message)

manager = ConnectionManager()

# Pydantic models for message validation
class SubscribeMessage(BaseModel):
    action: str
    symbol: str

class UnsubscribeMessage(BaseModel):
    action: str
    symbol: str

@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    try:
        manager.redis_client = redis.from_url("redis://redis:6379", decode_responses=True)
        await manager.redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection on shutdown"""
    if manager.redis_client:
        await manager.redis_client.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "total_subscriptions": sum(len(subs) for subs in manager.symbol_subscriptions.values())
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

@app.post("/broadcast/orderbook")
async def broadcast_orderbook_endpoint(symbol: str, orderbook_data: dict):
    """HTTP endpoint for broadcasting order book data (called by stock monitor)"""
    await manager.broadcast_orderbook(symbol, orderbook_data)
    return {"status": "broadcasted", "symbol": symbol, "subscribers": len(manager.symbol_subscriptions.get(symbol, set()))}

@app.get("/stats")
async def get_stats():
    """Get WebSocket statistics"""
    return {
        "active_connections": len(manager.active_connections),
        "symbol_subscriptions": {
            symbol: len(clients) for symbol, clients in manager.symbol_subscriptions.items()
        },
        "total_subscriptions": sum(len(clients) for clients in manager.symbol_subscriptions.values())
    } 