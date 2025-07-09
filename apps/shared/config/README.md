# Configuration Management

This module provides centralized configuration management for the stock monitor application using Pydantic Settings.

## Features

- **Environment Variable Loading**: Automatically loads settings from environment variables
- **Type Safety**: Full type hints and validation using Pydantic
- **Flexible Database Configuration**: Support for both connection URL and individual parameters
- **Validation**: Built-in validation for critical settings
- **Documentation**: Each setting includes descriptions and default values

## Usage

### Basic Usage

```python
from apps.stock_monitor.config import settings

# Access Futu API settings
futu_host = settings.futu_host
futu_port = settings.futu_port

# Access database settings
db_url = settings.database_connection_string
db_host = settings.database_host

# Access application settings
app_name = settings.app_name
log_level = settings.log_level
```

### Environment Variables

Create a `.env` file in the `apps/stock_monitor/` directory with the following variables:

```bash
# Futu API Configuration
FUTU_HOST=127.0.0.1
FUTU_PORT=11111
FUTU_QUOTE_CTX_TIMEOUT=15

# Database Configuration (TimescaleDB/PostgreSQL)
# Option 1: Individual settings
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=futu_helper
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_password_here
DATABASE_POOL_MIN_SIZE=5
DATABASE_POOL_MAX_SIZE=20

# Option 2: Connection URL (overrides individual settings)
# DATABASE_URL=postgresql://username:password@host:port/database_name

# Application Configuration
APP_NAME=futu_helper
APP_ENVIRONMENT=development
LOG_LEVEL=INFO

# External API Configuration
EXTERNAL_API_TIMEOUT=30
EXTERNAL_API_RETRY_ATTEMPTS=3

# Monitoring Configuration
MONITORING_INTERVAL=60
ALERT_CHECK_INTERVAL=30
```

### Database Configuration

The configuration supports two ways to specify database connection:

1. **Individual Parameters**: Set `DATABASE_HOST`, `DATABASE_PORT`, etc.
2. **Connection URL**: Set `DATABASE_URL` (overrides individual parameters)

```python
# Get the database connection string
db_url = settings.database_connection_string

# Use with DatabaseManager
from apps.shared.utils.database import DatabaseManager

db_manager = DatabaseManager(database_url=settings.database_connection_string)
```

### Futu API Configuration

```python
# Get Futu connection info
futu_config = settings.futu_connection_info

# Use with OpenQuoteContext
from futu import OpenQuoteContext

quote_ctx = OpenQuoteContext(
    host=settings.futu_host,
    port=settings.futu_port
)
```

## Available Settings

### Futu API Configuration
- `futu_host`: Futu OpenD host address (default: "127.0.0.1")
- `futu_port`: Futu OpenD port number (default: 11111)
- `futu_quote_ctx_timeout`: Quote context timeout in seconds (default: 15)

### Database Configuration
- `database_url`: Database connection URL (optional, overrides individual settings)
- `database_host`: Database host address (default: "localhost")
- `database_port`: Database port number (default: 5432)
- `database_name`: Database name (default: "futu_helper")
- `database_username`: Database username (default: "postgres")
- `database_password`: Database password (default: "")
- `database_pool_min_size`: Connection pool minimum size (default: 5)
- `database_pool_max_size`: Connection pool maximum size (default: 20)

### Application Configuration
- `app_name`: Application name (default: "futu_helper")
- `app_environment`: Application environment (default: "development")
- `log_level`: Logging level (default: "INFO")

### External API Configuration
- `external_api_timeout`: External API timeout in seconds (default: 30)
- `external_api_retry_attempts`: Number of retry attempts (default: 3)

### Monitoring Configuration
- `monitoring_interval`: Stock monitoring interval in seconds (default: 60)
- `alert_check_interval`: Alert check interval in seconds (default: 30)

## Validation

The configuration automatically validates critical settings on import:

- Database configuration completeness
- Database pool size constraints
- Futu port number validity

If validation fails, the application will raise a `ValueError` with details about the issue.

## Dependencies

Make sure to install the required dependencies:

```bash
uv pip install pydantic-settings
```

## Example Integration

Here's how to integrate the configuration with your existing code:

```python
# In futu_client.py
from apps.stock_monitor.config import settings
from futu import OpenQuoteContext

# Use configuration instead of hardcoded values
quote_ctx = OpenQuoteContext(
    host=settings.futu_host,
    port=settings.futu_port
)

# In database operations
from apps.shared.utils.database import DatabaseManager
from apps.stock_monitor.config import settings

db_manager = DatabaseManager(database_url=settings.database_connection_string)
``` 