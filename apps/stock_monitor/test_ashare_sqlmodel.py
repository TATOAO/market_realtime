#!/usr/bin/env python3
"""
Test script for AShareStockRecord SQLModel functionality

This script tests the conversion from Pydantic to SQLModel and basic database operations.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.schemas.ashare_stock import AShareStockRecord, convert_dataframe_to_records
from shared.utils.database import get_database_manager


async def test_ashare_stock_record():
    """Test creating and using AShareStockRecord"""
    print("Testing AShareStockRecord creation...")
    
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
    
    print(f"✓ Created AShareStockRecord: {stock_record.code} - {stock_record.name}")
    print(f"  Latest price: {stock_record.latest_price}")
    print(f"  Change percent: {stock_record.change_percent}%")
    print(f"  Volume: {stock_record.volume}")
    
    return stock_record


async def test_database_operations():
    """Test database operations with AShareStockRecord"""
    print("\nTesting database operations...")
    
    try:
        db_manager = await get_database_manager()
        
        # Create table
        print("Creating ashare_stocks table...")
        success = await db_manager.create_ashare_stocks_table()
        if success:
            print("✓ Table created successfully")
        else:
            print("✗ Failed to create table")
            return
        
        # Create test record
        stock_record = await test_ashare_stock_record()
        
        # Save single record
        print("\nSaving single record to database...")
        record_id = await db_manager.save_ashare_stock(stock_record)
        if record_id:
            print(f"✓ Saved record with ID: {record_id}")
        else:
            print("✗ Failed to save record")
            return
        
        # Query the record
        print("\nQuerying saved record...")
        records = await db_manager.get_ashare_stock("000001", limit=1)
        if records:
            print(f"✓ Found {len(records)} record(s)")
            saved_record = records[0]
            print(f"  Code: {saved_record['code']}")
            print(f"  Name: {saved_record['name']}")
            print(f"  Latest price: {saved_record['latest_price']}")
        else:
            print("✗ No records found")
        
        # Test batch operations
        print("\nTesting batch operations...")
        stock_records = [
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
            ),
            AShareStockRecord(
                sequence=3,
                code="000858",
                name="五粮液",
                latest_price=156.78,
                change_percent=3.8,
                change_amount=5.78,
                volume=500000.0,
                turnover=78390000.0,
                amplitude=4.1,
                high=158.90,
                low=154.20,
                open=155.00,
                previous_close=151.00,
                volume_ratio=1.5,
                turnover_rate=1.2,
                pe_ratio=25.8,
                pb_ratio=8.5,
                total_market_cap=456789123.0,
                circulating_market_cap=345678901.0,
                price_speed=0.8,
                five_min_change=0.3,
                sixty_day_change=12.5,
                ytd_change=25.6,
                timestamp=datetime.now(),
                source="akshare"
            )
        ]
        
        saved_count = await db_manager.save_ashare_stocks_batch(stock_records)
        print(f"✓ Saved {saved_count} records in batch")
        
        # Test filtering
        print("\nTesting filtered queries...")
        filter_params = {
            'min_change_percent': 2.0,  # Stocks with >2% gain
            'max_pe_ratio': 20.0        # Maximum P/E ratio
        }
        filtered_stocks = await db_manager.get_ashare_stocks_by_filter(filter_params, limit=10)
        print(f"✓ Found {len(filtered_stocks)} stocks with >2% gain and P/E < 20")
        
        # Get latest stocks
        latest_stocks = await db_manager.get_latest_ashare_stocks(limit=5)
        print(f"✓ Found {len(latest_stocks)} latest stock records")
        
        print("\n✓ All database operations completed successfully!")
        
    except Exception as e:
        print(f"✗ Database operation failed: {e}")
        import traceback
        traceback.print_exc()


async def test_dataframe_conversion():
    """Test DataFrame to AShareStockRecord conversion"""
    print("\nTesting DataFrame conversion...")
    
    try:
        import pandas as pd
        
        # Create sample DataFrame
        df_data = {
            '序号': [1, 2],
            '代码': ['000001', '000002'],
            '名称': ['平安银行', '万科A'],
            '最新价': [12.34, 18.56],
            '涨跌幅': [2.5, -1.2],
            '涨跌额': [0.30, -0.22],
            '成交量': [1000000.0, 800000.0],
            '成交额': [12340000.0, 14848000.0],
            '振幅': [3.2, 2.8],
            '最高': [12.50, 18.80],
            '最低': [12.10, 18.30],
            '今开': [12.20, 18.78],
            '昨收': [12.04, 18.78],
            '量比': [1.2, 0.9],
            '换手率': [0.8, 0.6],
            '市盈率-动态': [15.6, 12.3],
            '市净率': [1.2, 0.8],
            '总市值': [123456789.0, 987654321.0],
            '流通市值': [98765432.0, 876543210.0],
            '涨速': [0.5, -0.3],
            '5分钟涨跌': [0.1, -0.05],
            '60日涨跌幅': [5.2, -3.1],
            '年初至今涨跌幅': [12.3, 8.7]
        }
        
        df = pd.DataFrame(df_data)
        print(f"✓ Created DataFrame with {len(df)} rows")
        
        # Convert to AShareStockRecord objects
        stock_records = convert_dataframe_to_records(df)
        print(f"✓ Converted to {len(stock_records)} AShareStockRecord objects")
        
        for record in stock_records:
            print(f"  - {record.code}: {record.name} @ {record.latest_price}")
        
        print("✓ DataFrame conversion completed successfully!")
        
    except ImportError:
        print("✗ pandas not available, skipping DataFrame test")
    except Exception as e:
        print(f"✗ DataFrame conversion failed: {e}")


async def main():
    """Run all tests"""
    print("=== AShareStockRecord SQLModel Test ===\n")
    
    # Test basic record creation
    await test_ashare_stock_record()
    
    # Test DataFrame conversion
    await test_dataframe_conversion()
    
    # Test database operations (only if DATABASE_URL is set)
    if os.getenv('DATABASE_URL'):
        await test_database_operations()
    else:
        print("\nSkipping database tests (DATABASE_URL not set)")
        print("Set DATABASE_URL environment variable to test database operations")
    
    print("\n=== Test completed ===")


if __name__ == "__main__":
    asyncio.run(main()) 