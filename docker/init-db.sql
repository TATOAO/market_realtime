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

-- Insert some sample data
INSERT INTO stocks (symbol, name, exchange) VALUES 
    ('AAPL', 'Apple Inc.', 'NASDAQ'),
    ('GOOGL', 'Alphabet Inc.', 'NASDAQ'),
    ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
    ('TSLA', 'Tesla Inc.', 'NASDAQ')
ON CONFLICT (symbol) DO NOTHING; 