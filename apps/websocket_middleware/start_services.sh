#!/bin/bash

# Start Order Book Services Script
# This script starts the WebSocket middleware and fake order book service

echo "🚀 Starting Order Book Services..."
echo "=================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Check if ports are available
echo "Checking ports..."
check_port 8000 || exit 1

# Start WebSocket middleware
echo ""
echo "📡 Starting WebSocket middleware on port 8000..."

# Check if middleware is already running
if check_port 8000; then
    echo "✅ WebSocket middleware is already running on port 8000"
    MIDDLEWARE_PID=""
else
    echo "   Starting new instance..."
    # Start the middleware in the background
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    MIDDLEWARE_PID=$!
    
    # Wait a moment for the middleware to start
    sleep 3
    
    # Check if middleware started successfully
    if ! check_port 8000; then
        echo "❌ Failed to start WebSocket middleware"
        kill $MIDDLEWARE_PID 2>/dev/null
        exit 1
    fi
    
    echo "✅ WebSocket middleware started successfully"
fi

# Start fake order book service
echo ""
echo "📊 Starting fake order book service..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the fake service
python fake_orderbook_service.py &
FAKE_SERVICE_PID=$!

echo "✅ Fake order book service started"
echo ""
echo "🎉 All services are running!"
echo "   - WebSocket middleware: http://localhost:8000"
echo "   - Health check: http://localhost:8000/health"
echo "   - Frontend: http://localhost:3000/orderbook"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ ! -z "$MIDDLEWARE_PID" ]; then
        kill $MIDDLEWARE_PID 2>/dev/null
    fi
    kill $FAKE_SERVICE_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait 