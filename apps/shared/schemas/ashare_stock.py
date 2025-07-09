from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AShareStockRecord(BaseModel):
    """Pydantic model for A-share stock real-time data records"""
    
    # Basic identification
    sequence: int = Field(description="序号 - Sequence number")
    code: str = Field(description="代码 - Stock code")
    name: str = Field(description="名称 - Stock name")
    
    # Price information
    latest_price: float = Field(description="最新价 - Latest price")
    change_percent: float = Field(description="涨跌幅 - Price change percentage")
    change_amount: float = Field(description="涨跌额 - Price change amount")
    
    # Volume and turnover
    volume: float = Field(description="成交量 - Trading volume")
    turnover: float = Field(description="成交额 - Trading turnover")
    
    # Price range
    amplitude: float = Field(description="振幅 - Price amplitude")
    high: float = Field(description="最高 - Highest price")
    low: float = Field(description="最低 - Lowest price")
    open: float = Field(description="今开 - Today's opening price")
    previous_close: float = Field(description="昨收 - Previous closing price")
    
    # Technical indicators
    volume_ratio: float = Field(description="量比 - Volume ratio")
    turnover_rate: float = Field(description="换手率 - Turnover rate")
    
    # Valuation metrics
    pe_ratio: float = Field(description="市盈率-动态 - P/E ratio (dynamic)")
    pb_ratio: float = Field(description="市净率 - P/B ratio")
    
    # Market capitalization
    total_market_cap: float = Field(description="总市值 - Total market capitalization")
    circulating_market_cap: float = Field(description="流通市值 - Circulating market capitalization")
    
    # Additional metrics
    price_speed: float = Field(description="涨速 - Price change speed")
    five_min_change: float = Field(description="5分钟涨跌 - 5-minute price change")
    sixty_day_change: float = Field(description="60日涨跌幅 - 60-day price change percentage")
    ytd_change: float = Field(description="年初至今涨跌幅 - Year-to-date price change percentage")
    
    # Metadata
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Data timestamp")
    source: str = Field(default="akshare", description="Data source")


class AShareStockResponse(BaseModel):
    """Response model for A-share stock data API"""
    data: list[AShareStockRecord] = Field(description="List of stock records")
    total_count: int = Field(description="Total number of records")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class AShareStockFilter(BaseModel):
    """Filter model for querying A-share stock data"""
    codes: Optional[list[str]] = Field(default=None, description="Filter by stock codes")
    min_change_percent: Optional[float] = Field(default=None, description="Minimum change percentage")
    max_change_percent: Optional[float] = Field(default=None, description="Maximum change percentage")
    min_volume: Optional[float] = Field(default=None, description="Minimum volume")
    min_turnover: Optional[float] = Field(default=None, description="Minimum turnover")
    min_pe_ratio: Optional[float] = Field(default=None, description="Minimum P/E ratio")
    max_pe_ratio: Optional[float] = Field(default=None, description="Maximum P/E ratio")
    min_pb_ratio: Optional[float] = Field(default=None, description="Minimum P/B ratio")
    max_pb_ratio: Optional[float] = Field(default=None, description="Maximum P/B ratio")
    limit: Optional[int] = Field(default=100, description="Maximum number of records to return")


# Utility functions for data conversion
def convert_dataframe_to_records(df) -> list[AShareStockRecord]:
    """Convert pandas DataFrame to list of AShareStockRecord objects"""
    records = []
    
    # Column mapping from Chinese to English
    column_mapping = {
        '序号': 'sequence',
        '代码': 'code', 
        '名称': 'name',
        '最新价': 'latest_price',
        '涨跌幅': 'change_percent',
        '涨跌额': 'change_amount',
        '成交量': 'volume',
        '成交额': 'turnover',
        '振幅': 'amplitude',
        '最高': 'high',
        '最低': 'low',
        '今开': 'open',
        '昨收': 'previous_close',
        '量比': 'volume_ratio',
        '换手率': 'turnover_rate',
        '市盈率-动态': 'pe_ratio',
        '市净率': 'pb_ratio',
        '总市值': 'total_market_cap',
        '流通市值': 'circulating_market_cap',
        '涨速': 'price_speed',
        '5分钟涨跌': 'five_min_change',
        '60日涨跌幅': 'sixty_day_change',
        '年初至今涨跌幅': 'ytd_change'
    }
    
    for _, row in df.iterrows():
        record_data = {}
        for chinese_col, english_col in column_mapping.items():
            if chinese_col in row:
                record_data[english_col] = row[chinese_col]
        
        records.append(AShareStockRecord(**record_data))
    
    return records

