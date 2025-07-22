import time
import math
import asyncio
from typing import List, Tuple
from datetime import datetime
from shared.schemas.stock_quote import StockOrderBook, OrderBookEntry
from pydantic import BaseModel
from random import randint, gauss

class ContinueOrderBook(BaseModel):
    last_order_book: StockOrderBook
    current_order_book: StockOrderBook

class StandardError(BaseModel):
    mean: float = 0.0
    variance: float = 1.0

class RandomWalk(BaseModel):
    step: int = 1

async def random_order_book_entry(count: int = 10, 
                            middle_quote: float = 30.0,
                            volumn_max: int = 1000,
                            price_unit: float = 0.01, 
                            decay_rate: float = 0.9, 
                            decay_rate_noise: StandardError = StandardError(mean=0.0, variance=0.1)) -> Tuple[List[OrderBookEntry], List[OrderBookEntry]]:

    bid_counts = count + randint(-5, 5)
    ask_counts = count + randint(-5, 5)

    decay_rate_noise.mean = decay_rate_noise.mean * decay_rate

    bid_entries: List[OrderBookEntry] = [ OrderBookEntry(price=middle_quote + price_unit * (i+1), volume=volumn_max * (decay_rate + gauss(decay_rate_noise.mean, decay_rate_noise.variance))  ** (i+1)) for i,_ in enumerate(range(bid_counts)) ]
    ask_entries: List[OrderBookEntry] = [ OrderBookEntry(price=middle_quote - price_unit * (i+1), volume=volumn_max * (decay_rate + gauss(decay_rate_noise.mean, decay_rate_noise.variance))  ** (i+1)) for i,_ in enumerate(range(ask_counts)) ]

    return bid_entries, ask_entries

async def random_order_book_initializer(code="HK.00700", name="腾讯控股", **args) -> StockOrderBook:
    bid_entries: List[OrderBookEntry] = []
    ask_entries: List[OrderBookEntry] = []

    bid_entries, ask_entries = random_order_book_entry(**args)
    return StockOrderBook(
        code=code,
        name=name,
        svr_recv_time_bid=datetime.now(),
        svr_recv_time_ask=datetime.now(),
        bid_entries=bid_entries,
        ask_entries=ask_entries,
    )


async def direction_generator(volumn_delta: int, volumn_max: int, noise: StandardError) -> int:
    """
    volumn_delta: the delta of the volumn
    noise: the noise of the volumn
    return the direction of the volumn, which is 1 or -1 or 0


    """

    mean = volumn_delta / volumn_max + noise.mean
    variance = noise.variance
    
    z = gauss(mean, variance)

    if z > mean + math.sqrt(variance) * 1:
        return 1
    elif z < mean - math.sqrt(variance) * 1:
        return -1
    else:
        return 0

async def random_next_order_book(order_book: StockOrderBook, price_unit: float = 0.01, **args) -> StockOrderBook:

    bid_volumn = sum([entry.volume * entry.price for entry in order_book.bid_entries])
    ask_volumn = sum([entry.volume * entry.price for entry in order_book.ask_entries])

    middle_quote = (order_book.bid_entries[0].price + order_book.ask_entries[0].price) / 2

    count = max(len(order_book.bid_entries), len(order_book.ask_entries))

    direction = direction_generator(ask_volumn - bid_volumn, max(ask_volumn, bid_volumn), StandardError(mean=0.0, variance=0.1))

    new_bid_entries, new_ask_entries = random_order_book_entry(
        count=count, 
        middle_quote=middle_quote + direction * price_unit, 
        **args)

    time.sleep(0.01)

    return StockOrderBook(
        code=order_book.code,
        name=order_book.name,
        svr_recv_time_bid=datetime.now(),
        svr_recv_time_ask=datetime.now(),
        bid_entries=new_bid_entries,
        ask_entries=new_ask_entries,
    )



"""
class MockFutuClient:
    def __init__(self):
        self.order_book = random_order_book_initializer(
            code='HK.00700',
            name='腾讯控股',
            **kwargs
        )


    def on_recv_rsp(self, rsp_pb):
        pass

"""



# python -m app.core.api_client.futu.mock_client
if __name__ == "__main__":
    async def main():
        bid_entries, ask_entries = await random_order_book_entry()
        print(bid_entries)
        print(ask_entries)

    asyncio.run(main())