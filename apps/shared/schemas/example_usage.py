"""
Example usage of AShareStockRecord with database operations

This file demonstrates how to use the SQLModel-based AShareStockRecord
for convenient database operations.
"""

import asyncio
from datetime import datetime
from typing import List

from shared.schemas.ashare_stock import AShareStockRecord, convert_dataframe_to_records
from shared.utils.database import get_database_manager


async def example_save_single_stock():
    """Example: Save a single AShare stock record to database"""
    db_manager = await get_database_manager()
    
    # Create a stock record
    stock_record = AShareStockRecord(
        sequence=1,
        code="000001",
        name="平安银行",
        latest_price=12.34,
        change_percent=2.5,
        change_amount=0.30,
        volume=1000000.0,
        turnover=12340000.0,
        amplitude=3.2,
        high=12.50,
        low=12.10,
        open=12.20,
        previous_close=12.04,
        volume_ratio=1.2,
        turnover_rate=0.8,
        pe_ratio=15.6,
        pb_ratio=1.2,
        total_market_cap=123456789.0,
        circulating_market_cap=98765432.0,
        price_speed=0.5,
        five_min_change=0.1,
        sixty_day_change=5.2,
        ytd_change=12.3,
        timestamp=datetime.now(),
        source="akshare"
    )
    
    # Save to database
    record_id = await db_manager.save_ashare_stock(stock_record)
    print(f"Saved stock record with ID: {record_id}")


async def example_save_batch_stocks():
    """Example: Save multiple AShare stock records in batch"""
    db_manager = await get_database_manager()
    
    # Create multiple stock records
    stock_records = [
        AShareStockRecord(
            sequence=1,
            code="000001",
            name="平安银行",
            latest_price=12.34,
            change_percent=2.5,
            change_amount=0.30,
            volume=1000000.0,
            turnover=12340000.0,
            amplitude=3.2,
            high=12.50,
            low=12.10,
            open=12.20,
            previous_close=12.04,
            volume_ratio=1.2,
            turnover_rate=0.8,
            pe_ratio=15.6,
            pb_ratio=1.2,
            total_market_cap=123456789.0,
            circulating_market_cap=98765432.0,
            price_speed=0.5,
            five_min_change=0.1,
            sixty_day_change=5.2,
            ytd_change=12.3,
            timestamp=datetime.now(),
            source="akshare"
        ),
        AShareStockRecord(
            sequence=2,
            code="000002",
            name="万科A",
            latest_price=18.56,
            change_percent=-1.2,
            change_amount=-0.22,
            volume=800000.0,
            turnover=14848000.0,
            amplitude=2.8,
            high=18.80,
            low=18.30,
            open=18.78,
            previous_close=18.78,
            volume_ratio=0.9,
            turnover_rate=0.6,
            pe_ratio=12.3,
            pb_ratio=0.8,
            total_market_cap=987654321.0,
            circulating_market_cap=876543210.0,
            price_speed=-0.3,
            five_min_change=-0.05,
            sixty_day_change=-3.1,
            ytd_change=8.7,
            timestamp=datetime.now(),
            source="akshare"
        )
    ]
    
    # Save batch to database
    saved_count = await db_manager.save_ashare_stocks_batch(stock_records)
    print(f"Saved {saved_count} stock records in batch")


async def example_query_stocks():
    """Example: Query AShare stocks from database"""
    db_manager = await get_database_manager()
    
    # Get latest stocks
    latest_stocks = await db_manager.get_latest_ashare_stocks(limit=10)
    print(f"Found {len(latest_stocks)} latest stocks")
    
    # Get specific stock
    stock_records = await db_manager.get_ashare_stock("000001", limit=5)
    print(f"Found {len(stock_records)} records for stock 000001")
    
    # Get stocks with filter
    filter_params = {
        'min_change_percent': 2.0,  # Stocks with >2% gain
        'min_volume': 500000.0,     # Minimum volume
        'max_pe_ratio': 20.0        # Maximum P/E ratio
    }
    filtered_stocks = await db_manager.get_ashare_stocks_by_filter(filter_params, limit=20)
    print(f"Found {len(filtered_stocks)} stocks matching filter criteria")


async def example_convert_dataframe():
    """Example: Convert DataFrame to AShareStockRecord objects and save"""
    import pandas as pd
    
    db_manager = await get_database_manager()
    
    # Simulate DataFrame from akshare
    df_data = {
        '序号': [1, 2, 3],
        '代码': ['000001', '000002', '000858'],
        '名称': ['平安银行', '万科A', '五粮液'],
        '最新价': [12.34, 18.56, 156.78],
        '涨跌幅': [2.5, -1.2, 3.8],
        '涨跌额': [0.30, -0.22, 5.78],
        '成交量': [1000000.0, 800000.0, 500000.0],
        '成交额': [12340000.0, 14848000.0, 78390000.0],
        '振幅': [3.2, 2.8, 4.1],
        '最高': [12.50, 18.80, 158.90],
        '最低': [12.10, 18.30, 154.20],
        '今开': [12.20, 18.78, 155.00],
        '昨收': [12.04, 18.78, 151.00],
        '量比': [1.2, 0.9, 1.5],
        '换手率': [0.8, 0.6, 1.2],
        '市盈率-动态': [15.6, 12.3, 25.8],
        '市净率': [1.2, 0.8, 8.5],
        '总市值': [123456789.0, 987654321.0, 456789123.0],
        '流通市值': [98765432.0, 876543210.0, 345678901.0],
        '涨速': [0.5, -0.3, 0.8],
        '5分钟涨跌': [0.1, -0.05, 0.3],
        '60日涨跌幅': [5.2, -3.1, 12.5],
        '年初至今涨跌幅': [12.3, 8.7, 25.6]
    }
    
    df = pd.DataFrame(df_data)
    
    # Convert DataFrame to AShareStockRecord objects
    stock_records = convert_dataframe_to_records(df)
    print(f"Converted {len(stock_records)} records from DataFrame")
    
    # Save to database
    saved_count = await db_manager.save_ashare_stocks_batch(stock_records)
    print(f"Saved {saved_count} records to database")


async def example_create_table():
    """Example: Create the ashare_stocks table"""
    db_manager = await get_database_manager()
    
    success = await db_manager.create_ashare_stocks_table()
    if success:
        print("Successfully created ashare_stocks table")
    else:
        print("Failed to create ashare_stocks table")


async def main():
    """Run all examples"""
    print("=== AShare Stock Database Operations Examples ===\n")
    
    # Create table first
    print("1. Creating table...")
    await example_create_table()
    print()
    
    # Save single record
    print("2. Saving single stock record...")
    await example_save_single_stock()
    print()
    
    # Save batch records
    print("3. Saving batch stock records...")
    await example_save_batch_stocks()
    print()
    
    # Query records
    print("4. Querying stocks...")
    await example_query_stocks()
    print()
    
    # Convert DataFrame
    print("5. Converting DataFrame to records...")
    await example_convert_dataframe()
    print()
    
    print("=== Examples completed ===")


# python -m shared.schemas.example_usage
if __name__ == "__main__":
    asyncio.run(main()) 