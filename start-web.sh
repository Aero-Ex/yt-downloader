#!/bin/bash

# YouTube Downloader - Web Interface Launcher

echo "========================================"
echo "  YouTube Downloader - Web Interface   "
echo "========================================"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask is not installed!"
    echo "Please run: pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Check if flask_socketio is installed
if ! python3 -c "import flask_socketio" 2>/dev/null; then
    echo "⚠️  Flask-SocketIO is not installed!"
    echo "Please run: pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo "✓ All dependencies installed"
echo ""
echo "Starting web server..."
echo ""
echo "🌐 Open your browser and navigate to:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Run the Flask app
python3 app.py
