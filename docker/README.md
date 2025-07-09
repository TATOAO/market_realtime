# Docker Setup for Futu Helper

This directory contains the Docker configuration for the Futu Helper application with 4 services:

## Services

1. **Frontend** (Port 3000) - React application for the user interface
2. **Backend** (Port 8000) - FastAPI service for main API endpoints
3. **Monitoring** (Port 8001) - FastAPI service for stock subscription and monitoring
4. **TimescaleDB** (Port 5432) - Time-series database for stock data

## Prerequisites

- Docker and Docker Compose installed
- Futu OpenD running on localhost:11111 (for stock data)

## Quick Start

1. **Start all services:**
   ```bash
   cd docker
   docker-compose up -d
   ```

   **Note:** Dockerfiles are located in their respective app folders:
   - Frontend: `apps/frontend/Dockerfile`
   - Backend: `apps/backend/Dockerfile`
   - Monitoring: `apps/stock_monitor/Dockerfile`

2. **View logs:**
   ```bash
   docker-compose logs -f [service_name]
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **Rebuild and restart:**
   ```bash
   docker-compose up -d --build
   ```

## Service Details

### Frontend
- **URL:** http://localhost:3000
- **Build:** Uses Node.js 18 with React
- **Hot reload:** Enabled for development

### Backend API
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Dependencies:** FastAPI, SQLAlchemy, Futu API, yfinance

### Monitoring Service
- **URL:** http://localhost:8001
- **Docs:** http://localhost:8001/docs
- **Features:** Stock subscription, real-time monitoring, alerts

### TimescaleDB
- **Host:** localhost
- **Port:** 5432
- **Database:** futu_db
- **User:** futu_user
- **Password:** futu_password
- **Features:** Time-series data, hypertables for stock prices

## Environment Variables

Key environment variables can be modified in `docker-compose.yml`:

- `DATABASE_URL`: PostgreSQL connection string
- `FUTU_OPENAPI_HOST`: Futu OpenD host (default: 127.0.0.1)
- `FUTU_OPENAPI_PORT`: Futu OpenD port (default: 11111)
- `ENVIRONMENT`: Development/production mode

## Database Schema

The database includes:
- `stocks` - Stock information
- `stock_prices` - Time-series price data (hypertable)
- `stock_subscriptions` - User subscriptions for alerts
- `monitoring_logs` - Monitoring event logs

## Development

For development with hot reload:
- Frontend: Code changes will auto-reload
- Backend: Uses uvicorn with --reload flag
- Monitoring: Uses uvicorn with --reload flag

## Troubleshooting

1. **Database connection issues:**
   ```bash
   docker-compose logs timescaledb
   ```

2. **Service not starting:**
   ```bash
   docker-compose logs [service_name]
   ```

3. **Port conflicts:**
   - Check if ports 3000, 8000, 8001, 5432 are available
   - Modify ports in docker-compose.yml if needed

4. **Futu API connection:**
   - Ensure Futu OpenD is running on localhost:11111
   - Check firewall settings if using remote Futu OpenD 