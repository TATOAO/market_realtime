from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField


class AShareStockRecord(SQLModel, table=True):
    """SQLModel for A-share stock real-time data records that can be saved to database"""
    
    __tablename__ = "ashare_stocks"
    
    # Primary key
    id: Optional[int] = SQLField(default=None, primary_key=True)
    
    # Basic identification
    sequence: int = SQLField(description="序号 - Sequence number")
    code: str = SQLField(description="代码 - Stock code", index=True)
    name: str = SQLField(description="名称 - Stock name")
    
    # Price information
    latest_price: float = SQLField(description="最新价 - Latest price")
    change_percent: float = SQLField(description="涨跌幅 - Price change percentage")
    change_amount: float = SQLField(description="涨跌额 - Price change amount")
    
    # Volume and turnover
    volume: float = SQLField(description="成交量 - Trading volume")
    turnover: float = SQLField(description="成交额 - Trading turnover")
    
    # Price range
    amplitude: float = SQLField(description="振幅 - Price amplitude")
    high: float = SQLField(description="最高 - Highest price")
    low: float = SQLField(description="最低 - Lowest price")
    open: float = SQLField(description="今开 - Today's opening price")
    previous_close: float = SQLField(description="昨收 - Previous closing price")
    
    # Technical indicators
    volume_ratio: float = SQLField(description="量比 - Volume ratio")
    turnover_rate: float = SQLField(description="换手率 - Turnover rate")
    
    # Valuation metrics
    pe_ratio: float = SQLField(description="市盈率-动态 - P/E ratio (dynamic)")
    pb_ratio: float = SQLField(description="市净率 - P/B ratio")
    
    # Market capitalization
    total_market_cap: float = SQLField(description="总市值 - Total market capitalization")
    circulating_market_cap: float = SQLField(description="流通市值 - Circulating market capitalization")
    
    # Additional metrics
    price_speed: float = SQLField(description="涨速 - Price change speed")
    five_min_change: float = SQLField(description="5分钟涨跌 - 5-minute price change")
    sixty_day_change: float = SQLField(description="60日涨跌幅 - 60-day price change percentage")
    ytd_change: float = SQLField(description="年初至今涨跌幅 - Year-to-date price change percentage")
    
    # Metadata
    timestamp: datetime = SQLField(default_factory=datetime.now, description="Data timestamp", index=True)
    source: str = SQLField(default="akshare", description="Data source")
    
    # Database timestamps
    created_at: datetime = SQLField(default_factory=datetime.now, description="Record creation timestamp")
    updated_at: datetime = SQLField(default_factory=datetime.now, description="Record update timestamp")


class AShareStockResponse(BaseModel):
    """Response model for A-share stock data API"""
    data: list[AShareStockRecord] = Field(description="List of stock records")
    total_count: int = Field(description="Total number of records")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")



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

