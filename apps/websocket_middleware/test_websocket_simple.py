#!/usr/bin/env python3
"""
Simple WebSocket test client
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("Connected successfully!")
            
            # Send subscription message
            subscribe_msg = {
                "action": "subscribe",
                "symbol": "US.GOOGL"
            }
            print(f"Sending: {subscribe_msg}")
            await websocket.send(json.dumps(subscribe_msg))
            
            # Wait for response
            print("Waiting for response...")
            response = await websocket.recv()
            print(f"Received: {response}")
            
            # Keep connection alive for a few seconds
            print("Keeping connection alive for 5 seconds...")
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1) 