#!/usr/bin/env python3
"""
Test script to verify the integration between fake order book service and WebSocket middleware
"""

import asyncio
import json
import websockets
import httpx
import time
from fake_orderbook_service import FakeOrderBookService

async def test_websocket_connection():
    """Test WebSocket connection and subscription"""
    uri = "ws://localhost:8000/ws/test-client"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Subscribe to a symbol
            subscribe_message = {
                "action": "subscribe",
                "symbol": "US.AAPL"
            }
            await websocket.send(json.dumps(subscribe_message))
            print("✅ Sent subscription message")
            
            # Wait for confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Received response: {data}")
            
            # Wait for order book data
            print("⏳ Waiting for order book data...")
            timeout = 10  # 10 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    if data.get("type") == "orderbook_update":
                        print("✅ Received order book data!")
                        print(f"   Symbol: {data.get('symbol')}")
                        print(f"   Timestamp: {data.get('timestamp')}")
                        return True
                except asyncio.TimeoutError:
                    continue
            
            print("❌ Timeout waiting for order book data")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_fake_service():
    """Test the fake order book service"""
    try:
        service = FakeOrderBookService("http://localhost:8000")
        
        # Generate test data
        orderbook_data = service.generate_orderbook_data("US.AAPL")
        print("✅ Generated order book data:")
        print(f"   Symbol: {orderbook_data['code']}")
        print(f"   Name: {orderbook_data['name']}")
        print(f"   Bid levels: {len(orderbook_data['Bid'])}")
        print(f"   Ask levels: {len(orderbook_data['Ask'])}")
        
        # Send data to middleware
        await service.send_orderbook_data("US.AAPL", orderbook_data)
        print("✅ Sent order book data to middleware")
        
        return True
        
    except Exception as e:
        print(f"❌ Fake service test failed: {e}")
        return False

async def test_health_endpoint():
    """Test the health endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health endpoint working:")
                print(f"   Status: {data.get('status')}")
                print(f"   Active connections: {data.get('active_connections')}")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Order Book Integration")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    health_ok = await test_health_endpoint()
    
    # Test WebSocket connection
    print("\n2. Testing WebSocket connection...")
    websocket_ok = await test_websocket_connection()
    
    # Test fake service
    print("\n3. Testing fake service...")
    fake_service_ok = await test_fake_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   WebSocket connection: {'✅ PASS' if websocket_ok else '❌ FAIL'}")
    print(f"   Fake service: {'✅ PASS' if fake_service_ok else '❌ FAIL'}")
    
    if all([health_ok, websocket_ok, fake_service_ok]):
        print("\n🎉 All tests passed! The system is ready for frontend integration.")
    else:
        print("\n⚠️  Some tests failed. Please check the WebSocket middleware and fake service.")

if __name__ == "__main__":
    asyncio.run(main()) 