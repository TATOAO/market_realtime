"""
Example usage of the stock quote schemas
"""
from .stock_quote import convert_api_response_to_model, StockQuote

# Example API response data
sample_api_response = {
    'code': 'US.AAPL',
    'name': '苹果',
    'svr_recv_time_bid': '2025-04-07 05:00:52.266',
    'svr_recv_time_ask': '2025-04-07 05:00:53.973',
    'Bid': [
        (180.2, 15, 3, {}),
        (180.19, 1, 1, {}),
        (180.18, 11, 2, {}),
        (180.14, 200, 1, {}),
        (180.13, 3, 2, {}),
        (180.1, 99, 3, {}),
        (180.05, 3, 1, {}),
        (180.03, 400, 1, {}),
        (180.02, 10, 1, {}),
        (180.01, 100, 1, {}),
        (180.0, 441, 24, {})
    ],
    'Ask': [
        (180.3, 100, 1, {}),
        (180.38, 4, 2, {}),
        (180.4, 100, 1, {}),
        (180.42, 200, 1, {}),
        (180.46, 29, 1, {}),
        (180.5, 1019, 2, {}),
        (180.6, 1000, 1, {}),
        (180.8, 2001, 3, {}),
        (180.84, 15, 2, {}),
        (181.0, 2036, 4, {}),
        (181.2, 2000, 2, {}),
        (181.3, 3, 1, {}),
        (181.4, 2021, 3, {}),
        (181.5, 59, 2, {}),
        (181.79, 9, 1, {}),
        (181.8, 20, 1, {}),
        (181.9, 94, 4, {}),
        (181.98, 20, 1, {}),
        (182.0, 150, 7, {})
    ]
}


def example_usage():
    """Demonstrate how to use the schemas"""
    
    # Convert API response to SQLModel
    stock_quote_create = convert_api_response_to_model(sample_api_response)
    
    print("Converted API response to StockQuoteCreate model:")
    print(f"Code: {stock_quote_create.code}")
    print(f"Name: {stock_quote_create.name}")
    print(f"Bid entries count: {len(stock_quote_create.bid_entries)}")
    print(f"Ask entries count: {len(stock_quote_create.ask_entries)}")
    
    # Access individual bid/ask entries
    print("\nFirst bid entry:")
    first_bid = stock_quote_create.bid_entries[0]
    print(f"Price: {first_bid.price}, Volume: {first_bid.volume}, Orders: {first_bid.order_count}")
    
    print("\nFirst ask entry:")
    first_ask = stock_quote_create.ask_entries[0]
    print(f"Price: {first_ask.price}, Volume: {first_ask.volume}, Orders: {first_ask.order_count}")
    
    # Create a database record (example)
    # stock_quote = StockQuote(**stock_quote_create.dict())
    # db.add(stock_quote)
    # db.commit()
    
    return stock_quote_create


if __name__ == "__main__":
    example_usage() 