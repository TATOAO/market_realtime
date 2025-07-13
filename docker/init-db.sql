-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create tables for stock data
CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255),
    exchange VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create hypertable for stock prices (time-series data)
CREATE TABLE IF NOT EXISTS stock_prices (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_time ON stock_prices (time DESC);

-- Create table for order book data (time-series)
CREATE TABLE IF NOT EXISTS order_book_data (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    best_bid DECIMAL(10, 4),
    best_ask DECIMAL(10, 4),
    mid_price DECIMAL(10, 4),
    bid_volume DECIMAL(20, 2),
    ask_volume DECIMAL(20, 2),
    total_volume DECIMAL(20, 2),
    spread DECIMAL(10, 4),
    spread_percentage DECIMAL(10, 4),
    bid_levels JSONB,
    ask_levels JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('order_book_data', 'time', if_not_exists => TRUE);

-- Create indexes for order book data
CREATE INDEX IF NOT EXISTS idx_order_book_symbol ON order_book_data (symbol, time DESC);
CREATE INDEX IF NOT EXISTS idx_order_book_time ON order_book_data (time DESC);
CREATE INDEX IF NOT EXISTS idx_order_book_mid_price ON order_book_data (symbol, mid_price, time DESC);

-- Create table for monitoring subscriptions
CREATE TABLE IF NOT EXISTS stock_subscriptions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    user_id VARCHAR(100),
    alert_price DECIMAL(10, 4),
    alert_type VARCHAR(20) CHECK (alert_type IN ('above', 'below')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create table for monitoring logs
CREATE TABLE IF NOT EXISTS monitoring_logs (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    event_type VARCHAR(50),
    message TEXT,
    data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for monitoring tables
CREATE INDEX IF NOT EXISTS idx_stock_subscriptions_symbol ON stock_subscriptions (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_subscriptions_user ON stock_subscriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_logs_symbol ON monitoring_logs (symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_monitoring_logs_event_type ON monitoring_logs (event_type, created_at DESC);

-- Create table for AShare stocks
CREATE TABLE IF NOT EXISTS ashare_stocks (
    id SERIAL PRIMARY KEY,
    sequence INTEGER NOT NULL,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    latest_price DECIMAL(10,2) NOT NULL,
    change_percent DECIMAL(10,2) NOT NULL,
    change_amount DECIMAL(10,2) NOT NULL,
    volume DECIMAL(20,2) NOT NULL,
    turnover DECIMAL(20,2) NOT NULL,
    amplitude DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    previous_close DECIMAL(10,2) NOT NULL,
    volume_ratio DECIMAL(10,2) NOT NULL,
    turnover_rate DECIMAL(10,2) NOT NULL,
    pe_ratio DECIMAL(10,2) NOT NULL,
    pb_ratio DECIMAL(10,2) NOT NULL,
    total_market_cap DECIMAL(20,2) NOT NULL,
    circulating_market_cap DECIMAL(20,2) NOT NULL,
    price_speed DECIMAL(10,2) NOT NULL,
    five_min_change DECIMAL(10,2) NOT NULL,
    sixty_day_change DECIMAL(10,2) NOT NULL,
    ytd_change DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT 'akshare',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for AShare stocks
CREATE INDEX IF NOT EXISTS idx_ashare_stocks_code ON ashare_stocks(code);
CREATE INDEX IF NOT EXISTS idx_ashare_stocks_timestamp ON ashare_stocks(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ashare_stocks_change_percent ON ashare_stocks(change_percent DESC);
CREATE INDEX IF NOT EXISTS idx_ashare_stocks_volume ON ashare_stocks(volume DESC);

-- Insert some sample data
INSERT INTO stocks (symbol, name, exchange) VALUES 
    ('AAPL', 'Apple Inc.', 'NASDAQ'),
    ('GOOGL', 'Alphabet Inc.', 'NASDAQ'),
    ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
    ('TSLA', 'Tesla Inc.', 'NASDAQ')
ON CONFLICT (symbol) DO NOTHING; 