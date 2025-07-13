#!/usr/bin/env python3
"""
Test script for the caching system
Verifies that order book data is properly stored in database and cache
"""

import asyncio
import json
import httpx
import websockets
import time
from datetime import datetime, timedelta
from fake_orderbook_service import FakeOrderBookService

async def test_caching_system():
    """Test the complete caching system"""
    print("🧪 Testing Caching System")
    print("=" * 50)
    
    # Test 1: Check WebSocket middleware health
    print("\n1. Checking WebSocket middleware health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed:")
                print(f"   - Status: {health_data.get('status')}")
                print(f"   - Database: {health_data.get('database')}")
                print(f"   - Cache: {health_data.get('cache')}")
                print(f"   - Connections: {health_data.get('connections')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Send some order book data
    print("\n2. Sending order book data...")
    fake_service = FakeOrderBookService()
    
    # Send data for a few symbols
    symbols = ["US.AAPL", "US.GOOGL", "US.TSLA"]
    for symbol in symbols:
        orderbook_data = fake_service.generate_orderbook_data(symbol)
        await fake_service.send_orderbook_data(symbol, orderbook_data)
        print(f"✅ Sent order book data for {symbol}")
        await asyncio.sleep(0.5)  # Small delay between sends
    
    # Test 3: Check historical data endpoints
    print("\n3. Testing historical data endpoints...")
    try:
        async with httpx.AsyncClient() as client:
            # Test today's data
            response = await client.get(f"http://localhost:8000/orderbook/US.AAPL/today")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Today's data endpoint: {data.get('count', 0)} records")
            else:
                print(f"❌ Today's data endpoint failed: {response.status_code}")
            
            # Test historical data
            response = await client.get(f"http://localhost:8000/orderbook/US.AAPL/history?hours=1")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Historical data endpoint: {data.get('count', 0)} records")
            else:
                print(f"❌ Historical data endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Historical data test error: {e}")
    
    # Test 4: Test WebSocket with historical data
    print("\n4. Testing WebSocket with historical data...")
    try:
        uri = "ws://localhost:8000/ws/test-cache-client"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            # Subscribe to a symbol
            subscribe_message = {
                "action": "subscribe",
                "symbol": "US.AAPL"
            }
            await websocket.send(json.dumps(subscribe_message))
            print("✅ Sent subscription message")
            
            # Wait for historical data
            historical_received = False
            latest_received = False
            timeout = 10
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "historical_data":
                        historical_count = len(data.get("data", []))
                        print(f"✅ Received historical data: {historical_count} points")
                        historical_received = True
                    
                    elif data.get("type") == "orderbook_update":
                        print("✅ Received latest order book update")
                        latest_received = True
                    
                    elif data.get("type") == "subscription_confirmed":
                        print("✅ Subscription confirmed")
                    
                    if historical_received and latest_received:
                        break
                        
                except asyncio.TimeoutError:
                    continue
            
            if historical_received and latest_received:
                print("✅ WebSocket historical data test passed")
            else:
                print("❌ WebSocket historical data test failed")
                
    except Exception as e:
        print(f"❌ WebSocket test error: {e}")
    
    # Test 5: Check cache statistics
    print("\n5. Checking cache statistics...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Cache stats:")
                print(f"   - Active connections: {stats.get('active_connections', 0)}")
                print(f"   - Symbol subscriptions: {stats.get('symbol_subscriptions', 0)}")
                cache_stats = stats.get('cache_stats', {})
                print(f"   - Redis memory: {cache_stats.get('used_memory_human', 'N/A')}")
                print(f"   - Redis commands: {cache_stats.get('total_commands_processed', 0)}")
            else:
                print(f"❌ Stats endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Stats test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Caching system test completed!")
    return True

async def main():
    """Main test function"""
    print("Starting caching system test...")
    print("Make sure the WebSocket middleware is running on localhost:8000")
    print("Make sure Redis and TimescaleDB are running")
    
    try:
        await test_caching_system()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 