#!/usr/bin/env python3
"""
Test script for WebSocket Middleware
Demonstrates how to connect, subscribe, and receive real-time updates
"""

import asyncio
import websockets
import json
import uuid
from datetime import datetime

class WebSocketTester:
    def __init__(self, uri="ws://localhost:8002/ws/test-client"):
        self.uri = uri
        self.websocket = None
        self.client_id = f"test-client-{uuid.uuid4().hex[:8]}"
        self.uri = f"ws://localhost:8002/ws/{self.client_id}"

    async def connect(self):
        """Connect to WebSocket middleware"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"✅ Connected to WebSocket middleware as {self.client_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False

    async def subscribe(self, symbol):
        """Subscribe to a stock symbol"""
        message = {
            "action": "subscribe",
            "symbol": symbol
        }
        await self.websocket.send(json.dumps(message))
        print(f"📡 Subscribed to {symbol}")

    async def unsubscribe(self, symbol):
        """Unsubscribe from a stock symbol"""
        message = {
            "action": "unsubscribe",
            "symbol": symbol
        }
        await self.websocket.send(json.dumps(message))
        print(f"📡 Unsubscribed from {symbol}")

    async def ping(self):
        """Send ping to keep connection alive"""
        message = {"action": "ping"}
        await self.websocket.send(json.dumps(message))

    async def listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket connection closed")
        except Exception as e:
            print(f"❌ Error listening: {e}")

    async def handle_message(self, message):
        """Handle incoming messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if message.get("type") == "orderbook_update":
            symbol = message.get("symbol")
            data = message.get("data", {})
            print(f"[{timestamp}] 📊 Order book update for {symbol}:")
            print(f"   Bids: {len(data.get('bids', []))} levels")
            print(f"   Asks: {len(data.get('asks', []))} levels")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        
        elif message.get("type") == "subscription_confirmed":
            symbol = message.get("symbol")
            print(f"[{timestamp}] ✅ Subscribed to {symbol}")
        
        elif message.get("type") == "unsubscription_confirmed":
            symbol = message.get("symbol")
            print(f"[{timestamp}] ✅ Unsubscribed from {symbol}")
        
        elif message.get("type") == "pong":
            print(f"[{timestamp}] 🏓 Pong received")
        
        elif message.get("type") == "error":
            error_msg = message.get("message", "Unknown error")
            print(f"[{timestamp}] ❌ Error: {error_msg}")
        
        else:
            print(f"[{timestamp}] 📨 Unknown message: {message}")

    async def run_demo(self):
        """Run a complete demo"""
        if not await self.connect():
            return

        # Start listening in background
        listen_task = asyncio.create_task(self.listen())
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(1)
        
        # Subscribe to some symbols
        symbols = ["AAPL", "TSLA", "GOOGL"]
        for symbol in symbols:
            await self.subscribe(symbol)
            await asyncio.sleep(0.5)
        
        # Send some pings
        for i in range(3):
            await self.ping()
            await asyncio.sleep(2)
        
        # Unsubscribe from one symbol
        await asyncio.sleep(2)
        await self.unsubscribe("TSLA")
        
        # Keep listening for a while
        print("🎧 Listening for updates... (Press Ctrl+C to stop)")
        try:
            await asyncio.sleep(30)  # Listen for 30 seconds
        except KeyboardInterrupt:
            print("\n🛑 Stopping demo...")
        
        # Cleanup
        listen_task.cancel()
        await self.websocket.close()
        print("👋 Demo completed")

async def test_broadcast():
    """Test broadcasting order book data"""
    import httpx
    
    print("\n🧪 Testing broadcast endpoint...")
    
    # Sample order book data
    orderbook_data = {
        "bids": [
            {"price": 150.00, "quantity": 100},
            {"price": 149.99, "quantity": 200},
            {"price": 149.98, "quantity": 150}
        ],
        "asks": [
            {"price": 150.01, "quantity": 120},
            {"price": 150.02, "quantity": 180},
            {"price": 150.03, "quantity": 90}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8002/broadcast/orderbook",
                params={"symbol": "AAPL"},
                json=orderbook_data
            )
            result = response.json()
            print(f"📡 Broadcast result: {result}")
    except Exception as e:
        print(f"❌ Broadcast test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 WebSocket Middleware Test")
    print("=" * 50)
    
    # Test WebSocket connection and messaging
    tester = WebSocketTester()
    await tester.run_demo()
    
    # Test broadcast endpoint
    await test_broadcast()

if __name__ == "__main__":
    asyncio.run(main()) 