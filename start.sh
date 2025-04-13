#!/bin/bash

# Load environment variables
set -a
source .env
set +a

echo "Starting Buzz2Remote development environment..."

# Function to send notification to Telegram if configured
send_telegram_notification() {
    message=$1
    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "parse_mode=HTML" \
            -d "text=$message"
    fi
}

# Create Python virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Setting up Python virtual environment..."
    cd backend
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "Virtual environment already exists."
fi

# Start backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host $API_HOST --port $API_PORT &
BACKEND_PID=$!
cd ..
send_telegram_notification "🚀 <b>Buzz2Remote</b>%0A%0ABackend server started on port $API_PORT"

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..
send_telegram_notification "🚀 <b>Buzz2Remote</b>%0A%0AFrontend server started on port 3000"

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    send_telegram_notification "🛑 <b>Buzz2Remote</b>%0A%0AServers have been stopped"
    exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Development environment is running. Press Ctrl+C to stop."
wait 