from typing import List
from datetime import datetime
from shared.schemas.stock_quote import StockOrderBook, OrderBookEntry
from pydantic import BaseModel
from random import randint


class ContinueOrderBook(BaseModel):
    last_order_book: StockOrderBook
    current_order_book: StockOrderBook


def random_order_book_initializer(code="HK.00700", name="腾讯控股") -> StockOrderBook:
    bid_entries: List[OrderBookEntry] = []
    ask_entries: List[OrderBookEntry] = []

    return StockOrderBook(
        code=code,
        name=name,
        svr_recv_time_bid=datetime.now(),
        bid_entries=bid_entries,
        ask_entries=ask_entries,
    )



class MockFutuClient:
    def __init__(self):
        self.order_book = StockOrderBook(
            code='HK.00700',
            name='腾讯控股',
            svr_recv_time_bid=datetime.now(),
        )
    
    async def on_recv_rsp(self, rsp_pb):
        """
        rsp_pb is the response from the futu client
        data is the data to be processed
        return the data to be processed
        """
        pass
