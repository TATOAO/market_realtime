from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class OrderBookEntry(BaseModel):
    """Schema for individual bid/ask entries in the order book"""
    price: float = Field(description="Price level")
    volume: int = Field(description="Volume at this price level")
    order_count: int = Field(description="Number of orders at this price level")
    extra_data: Dict[str, Any] = Field(default_factory=dict, description="Additional data")


class StockQuote(SQLModel, table=True):
    """SQLModel schema for realtime stock quote data"""
    __tablename__ = "stock_quotes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(description="Stock code (e.g., 'US.AAPL')")
    name: str = Field(description="Stock name (e.g., '苹果')")
    svr_recv_time_bid: datetime = Field(description="Server receive time for bid data")
    svr_recv_time_ask: datetime = Field(description="Server receive time for ask data")
    bid_entries: List[OrderBookEntry] = Field(description="Bid order book entries")
    ask_entries: List[OrderBookEntry] = Field(description="Ask order book entries")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    class Config:
        arbitrary_types_allowed = True


class StockQuoteResponse(BaseModel):
    """Pydantic model for API response structure"""
    code: str = Field(description="Stock code (e.g., 'US.AAPL')")
    name: str = Field(description="Stock name (e.g., '苹果')")
    svr_recv_time_bid: str = Field(description="Server receive time for bid data as string")
    svr_recv_time_ask: str = Field(description="Server receive time for ask data as string")
    Bid: List[tuple] = Field(description="Raw bid data as tuples (price, volume, order_count, extra_data)")
    Ask: List[tuple] = Field(description="Raw ask data as tuples (price, volume, order_count, extra_data)")


class StockOrderBook(SQLModel, table=True):
    """
    Schema for creating new stock order book records

    code: str = Field(description="Stock code")
    name: str = Field(description="Stock name")
    svr_recv_time_bid: datetime = Field(description="Server receive time for bid data")
    svr_recv_time_ask: datetime = Field(description="Server receive time for ask data")
    bid_entries: List[OrderBookEntry] = Field(description="Bid order book entries")
    ask_entries: List[OrderBookEntry] = Field(description="Ask order book entries")

    """
    code: str = Field(description="Stock code")
    name: str = Field(description="Stock name")
    svr_recv_time_bid: datetime = Field(description="Server receive time for bid data")
    svr_recv_time_ask: datetime = Field(description="Server receive time for ask data")
    bid_entries: List[OrderBookEntry] = Field(description="Bid order book entries")
    ask_entries: List[OrderBookEntry] = Field(description="Ask order book entries")


class StockQuoteRead(SQLModel):
    """Schema for reading stock quote data"""
    id: int = Field(description="Record ID")
    code: str = Field(description="Stock code")
    name: str = Field(description="Stock name")
    svr_recv_time_bid: datetime = Field(description="Server receive time for bid data")
    svr_recv_time_ask: datetime = Field(description="Server receive time for ask data")
    bid_entries: List[OrderBookEntry] = Field(description="Bid order book entries")
    ask_entries: List[OrderBookEntry] = Field(description="Ask order book entries")
    created_at: datetime = Field(description="Record creation timestamp")


# Utility functions for data conversion
def convert_raw_order_book(raw_data: List[tuple]) -> List[OrderBookEntry]:
    """Convert raw order book data to OrderBookEntry objects"""
    entries = []
    for price, volume, order_count, extra_data in raw_data:
        entry = OrderBookEntry(
            price=price,
            volume=volume,
            order_count=order_count,
            extra_data=extra_data
        )
        entries.append(entry)
    return entries


def parse_datetime_string(datetime_str: str) -> datetime:
    """Parse datetime string from API response"""
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")


def convert_api_response_to_model(response_data: dict) -> StockQuoteCreate:
    """Convert API response data to StockQuoteCreate model"""
    return StockQuoteCreate(
        code=response_data["code"],
        name=response_data["name"],
        svr_recv_time_bid=parse_datetime_string(response_data["svr_recv_time_bid"]),
        svr_recv_time_ask=parse_datetime_string(response_data["svr_recv_time_ask"]),
        bid_entries=convert_raw_order_book(response_data["Bid"]),
        ask_entries=convert_raw_order_book(response_data["Ask"])
    ) 