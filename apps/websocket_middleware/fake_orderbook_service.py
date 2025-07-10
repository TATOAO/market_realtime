"""
Fake Order Book Service
Generates random order book data similar to OrderBookTest and sends it to the websocket middleware
"""

import asyncio
import json
import random
import time
from datetime import datetime, timedelta
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FakeOrderBookService:
    def __init__(self, websocket_url: str = "http://localhost:8000"):
        self.websocket_url = websocket_url
        self.symbols = [
            "US.AAPL", "US.GOOGL", "US.MSFT", "US.TSLA", "US.AMZN",
            "US.NVDA", "US.META", "US.NFLX", "US.AMD", "US.INTC"
        ]
        self.base_prices = {
            "US.AAPL": 180.0,
            "US.GOOGL": 140.0,
            "US.MSFT": 380.0,
            "US.TSLA": 240.0,
            "US.AMZN": 150.0,
            "US.NVDA": 850.0,
            "US.META": 480.0,
            "US.NFLX": 580.0,
            "US.AMD": 120.0,
            "US.INTC": 45.0
        }
        
    def generate_random_price(self, base_price: float, volatility: float = 0.02) -> float:
        """Generate a random price around the base price"""
        change = random.uniform(-volatility, volatility)
        return round(base_price * (1 + change), 2)
    
    def generate_order_book_levels(self, base_price: float, side: str) -> list:
        """Generate random order book levels for bid or ask side"""
        levels = []
        num_levels = random.randint(8, 15)
        
        if side == "Bid":
            # Bid prices are below base price
            for i in range(num_levels):
                price_offset = random.uniform(0.01, 0.50) * (i + 1)
                price = round(base_price - price_offset, 2)
                quantity = random.randint(1, 1000)
                num_orders = random.randint(1, 10)
                level = (price, quantity, num_orders, {})
                levels.append(level)
        else:
            # Ask prices are above base price
            for i in range(num_levels):
                price_offset = random.uniform(0.01, 0.50) * (i + 1)
                price = round(base_price + price_offset, 2)
                quantity = random.randint(1, 1000)
                num_orders = random.randint(1, 10)
                level = (price, quantity, num_orders, {})
                levels.append(level)
        
        # Sort bid levels in descending order, ask levels in ascending order
        if side == "Bid":
            levels.sort(key=lambda x: x[0], reverse=True)
        else:
            levels.sort(key=lambda x: x[0])
        
        return levels
    
    def generate_orderbook_data(self, symbol: str) -> dict:
        """Generate complete order book data for a symbol"""
        base_price = self.base_prices.get(symbol, 100.0)
        
        # Update base price with some random movement
        self.base_prices[symbol] = self.generate_random_price(base_price, 0.005)
        current_price = self.base_prices[symbol]
        
        # Generate current time
        now = datetime.now()
        svr_recv_time_bid = (now - timedelta(milliseconds=random.randint(100, 500))).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        svr_recv_time_ask = (now - timedelta(milliseconds=random.randint(100, 500))).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Generate Chinese name mapping
        chinese_names = {
            "US.AAPL": "苹果",
            "US.GOOGL": "谷歌",
            "US.MSFT": "微软",
            "US.TSLA": "特斯拉",
            "US.AMZN": "亚马逊",
            "US.NVDA": "英伟达",
            "US.META": "元",
            "US.NFLX": "奈飞",
            "US.AMD": "超微",
            "US.INTC": "英特尔"
        }
        
        orderbook_data = {
            'code': symbol,
            'name': chinese_names.get(symbol, symbol),
            'svr_recv_time_bid': svr_recv_time_bid,
            'svr_recv_time_ask': svr_recv_time_ask,
            'Bid': self.generate_order_book_levels(current_price, "Bid"),
            'Ask': self.generate_order_book_levels(current_price, "Ask"),
            'timestamp': now.isoformat()
        }
        
        return orderbook_data
    
    async def send_orderbook_data(self, symbol: str, orderbook_data: dict):
        """Send order book data to the websocket middleware"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.websocket_url}/broadcast/orderbook",
                    params={"symbol": symbol},
                    json=orderbook_data,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Sent orderbook data for {symbol} to {result.get('subscribers', 0)} subscribers")
                else:
                    logger.error(f"Failed to send orderbook data for {symbol}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending orderbook data for {symbol}: {e}")
    
    async def run_fake_service(self, interval: float = 1.0):
        """Run the fake service, generating and sending order book data"""
        logger.info(f"Starting fake order book service. Generating data every {interval} seconds.")
        logger.info(f"Available symbols: {', '.join(self.symbols)}")
        
        while True:
            try:
                # Generate data for a random symbol
                symbol = random.choice(self.symbols)
                orderbook_data = self.generate_orderbook_data(symbol)
                
                # Send the data
                await self.send_orderbook_data(symbol, orderbook_data)
                
                # Log the generated data (similar to OrderBookTest output)
                logger.info(f"OrderBookTest {orderbook_data}")
                
                # Wait for next iteration
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Fake service stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in fake service: {e}")
                await asyncio.sleep(interval)

async def main():
    """Main function to run the fake service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fake Order Book Service")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="WebSocket middleware URL")
    parser.add_argument("--interval", type=float, default=1.0,
                       help="Interval between data generation (seconds)")
    
    args = parser.parse_args()
    
    service = FakeOrderBookService(args.url)
    await service.run_fake_service(args.interval)

if __name__ == "__main__":
    asyncio.run(main()) 