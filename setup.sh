#!/bin/bash

# YouTube Downloader Setup Script

echo "========================================"
echo "  YouTube Downloader - Setup Script    "
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [ $? -eq 0 ]; then
    echo "✓ Found: $python_version"
else
    echo "✗ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check FFmpeg
echo ""
echo "Checking FFmpeg installation..."
ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1)
if [ $? -eq 0 ]; then
    echo "✓ Found: $ffmpeg_version"
else
    echo "✗ FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org"
    exit 1
fi

# Check if pip is available
echo ""
echo "Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 is available"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    echo "✓ pip is available"
    PIP_CMD="pip"
else
    echo "✗ pip is not installed"
    exit 1
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x cli.py
chmod +x example.py
chmod +x app.py
chmod +x start-web.sh

# Create downloads directory
mkdir -p downloads

echo ""
echo "========================================"
echo "  Setup completed successfully! 🎉     "
echo "========================================"
echo ""
echo "Two ways to use YouTube Downloader:"
echo ""
echo "1. 🌐 Web Interface (Recommended):"
echo "   ./start-web.sh"
echo "   Then open: http://localhost:5000"
echo ""
echo "2. 💻 Command-Line Interface:"
echo "   python cli.py --help"
echo "   python cli.py 'YOUTUBE_URL'"
echo ""
echo "CLI Examples:"
echo "   python cli.py 'URL' -t audio"
echo "   python cli.py 'URL' -q 720p"
echo "   python cli.py 'URL' --list-formats"
echo ""
