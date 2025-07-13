import time
import pickle
from datetime import datetime
from futu import OrderBookHandlerBase, RET_OK, RET_ERROR, OpenQuoteContext, SubType, StockQuoteHandlerBase
from shared.config import settings


class CombinedDataHandler(StockQuoteHandlerBase, OrderBookHandlerBase):
    def __init__(self):
        super().__init__()
        self.quote_records = []
        self.orderbook_records = []
        self.start_time = time.time()
        self.duration = 100  # 100 seconds
        
    def on_recv_rsp(self, rsp_pb):
        # Handle stock quote data
        if hasattr(rsp_pb, 'quote_list'):
            ret_code, data = super(StockQuoteHandlerBase, self).on_recv_rsp(rsp_pb)
            if ret_code != RET_OK:
                print("CombinedDataHandler StockQuote: error, msg: %s" % data)
                return RET_ERROR, data
            
            # Record the quote data with timestamp
            current_time = time.time()
            timestamp = datetime.fromtimestamp(current_time)
            
            record = {
                'timestamp': timestamp,
                'type': 'quote',
                'data': data
            }
            self.quote_records.append(record)
            
            print(f"CombinedDataHandler Quote {timestamp}: {data}")
            
        # Handle order book data
        elif hasattr(rsp_pb, 'order_book_list'):
            ret_code, data = super(OrderBookHandlerBase, self).on_recv_rsp(rsp_pb)
            if ret_code != RET_OK:
                print("CombinedDataHandler OrderBook: error, msg: %s" % data)
                return RET_ERROR, data
            
            # Record the order book data with timestamp
            current_time = time.time()
            timestamp = datetime.fromtimestamp(current_time)
            
            record = {
                'timestamp': timestamp,
                'type': 'orderbook',
                'data': data
            }
            self.orderbook_records.append(record)
            
            print(f"CombinedDataHandler OrderBook {timestamp}: {data}")
        
        # Check if we've reached the duration limit
        current_time = time.time()
        if current_time - self.start_time >= self.duration:
            self.save_to_pickle()
            return RET_ERROR, "Data collection completed"
            
        return RET_OK, data
    
    def save_to_pickle(self):
        """Save collected records to pickle file"""
        all_data = {
            'quotes': self.quote_records,
            'orderbook': self.orderbook_records,
            'collection_start': datetime.fromtimestamp(self.start_time),
            'collection_end': datetime.now()
        }
        
        filename = f"combined_market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(all_data, f)
        print(f"Saved {len(self.quote_records)} quote records and {len(self.orderbook_records)} orderbook records to {filename}")


# Legacy handlers for reference (can be removed if not needed)
class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("StockQuoteTest ", data) # StockQuoteTest 自己的处理逻辑
        return RET_OK, data

class OrderBookTest(OrderBookHandlerBase):
    def __init__(self):
        super().__init__()
        self.records = []
        self.start_time = time.time()
        self.duration = 100  # 100 seconds
        
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        
        # Record the data with timestamp
        current_time = time.time()
        timestamp = datetime.fromtimestamp(current_time)
        
        record = {
            'timestamp': timestamp,
            'data': data
        }
        self.records.append(record)
        
        print(f"OrderBookTest {timestamp}: {data}") # OrderBookTest 自己的处理逻辑
        
        # Check if we've reached 100 seconds
        if current_time - self.start_time >= self.duration:
            self.save_to_pickle()
            return RET_ERROR, "Data collection completed"
            
        return RET_OK, data
    
    def save_to_pickle(self):
        """Save collected records to pickle file"""
        filename = f"orderbook_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(self.records, f)
        print(f"Saved {len(self.records)} records to {filename}")

# Use configuration instead of hardcoded values
def main():
    quote_ctx = OpenQuoteContext(
        host=settings.futu_host, 
        port=settings.futu_port
    )
    handler = CombinedDataHandler()
    quote_ctx.set_handler(handler)  # 设置实时摆盘回调
    
    # Subscribe to both quote and order book data for the same stock
    stock_code = 'HK.00700'  # You can change this to any stock you want to monitor
    ret, data = quote_ctx.subscribe([stock_code], [SubType.QUOTE, SubType.ORDER_BOOK, SubType.RT_DATA, SubType.TICKER])
    
    if ret == RET_OK:
        print(f"Successfully subscribed to {stock_code} for quotes and order book data")
        print(data)
    else:
        print('Subscription error:', data)
        return
    
    time.sleep(110)  #  设置脚本接收 OpenD 的推送持续时间为110秒 (100 + buffer)
    quote_ctx.close()  # 关闭当条连接，OpenD 会在1分钟后自动取消相应股票相应类型的订阅

# python -m app.core.api_client.futu.futu_client
if __name__ == "__main__":
    main()