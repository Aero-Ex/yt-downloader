#!/usr/bin/env python3
"""
Flask web application for YouTube Downloader
"""
# IMPORTANT: eventlet monkey patching MUST be the first thing that happens
# This is required for gunicorn with eventlet worker
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room
import os
import sys
import uuid
import json
from pathlib import Path
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import time
import logging
import yt_dlp

from downloader import YouTubeDownloader, format_duration, format_size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['DOWNLOAD_FOLDER'] = Path('downloads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Configure SocketIO with longer timeouts and ping settings
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    ping_timeout=120,  # 2 minutes before considering connection dead
    ping_interval=25,  # Send ping every 25 seconds to keep connection alive
    async_mode='eventlet',  # Use eventlet for production with gunicorn
    engineio_logger=False,
    logger=False,
    # Allow both websocket and polling, with polling as fallback
    transports=['polling', 'websocket'],
    # Session management settings
    manage_session=False,  # Don't manage sessions server-side (stateless)
    # Allow reconnection with new session if old one is invalid
    always_connect=True,
)

# Store active downloads with TTL
active_downloads = {}

# Video info cache (URL -> {info, timestamp})
video_info_cache = {}
VIDEO_INFO_CACHE_TTL = 600  # 10 minutes

# Thread pool for downloads (max 5 concurrent downloads)
download_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="download")

# Cleanup configuration
DOWNLOAD_TTL = 3600  # 1 hour - downloads older than this are removed
CLEANUP_INTERVAL = 300  # Run cleanup every 5 minutes


class WebDownloader(YouTubeDownloader):
    """Extended downloader with websocket progress support"""

    def __init__(self, output_dir: str = "downloads", socket_id: str = None):
        super().__init__(output_dir)
        self.socket_id = socket_id

    def _progress_hook(self, d):
        """Enhanced progress hook with websocket support"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta = d.get('_eta_str', 'N/A').strip()
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)

            progress_data = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta,
                'downloaded': format_size(downloaded),
                'total': format_size(total) if total else 'Unknown'
            }

            if self.socket_id:
                socketio.emit('download_progress', progress_data, room=self.socket_id)

        elif d['status'] == 'finished':
            if self.socket_id:
                socketio.emit('download_progress', {
                    'status': 'processing',
                    'message': 'Processing file...'
                }, room=self.socket_id)


def cleanup_old_downloads():
    """Remove old downloads and their files from memory and disk"""
    try:
        now = datetime.now()
        to_remove = []

        for download_id, info in list(active_downloads.items()):
            # Check if download has timestamp
            if 'timestamp' in info:
                age = (now - info['timestamp']).total_seconds()

                # Remove if older than TTL
                if age > DOWNLOAD_TTL:
                    to_remove.append(download_id)

                    # Delete file if it exists and download is completed
                    if info.get('status') == 'completed' and 'filepath' in info:
                        try:
                            filepath = Path(info['filepath'])
                            if filepath.exists():
                                filepath.unlink()
                                logger.info(f"Cleaned up old download file: {filepath}")
                        except Exception as e:
                            logger.error(f"Error deleting file {info['filepath']}: {e}")

        # Remove from active downloads
        for download_id in to_remove:
            del active_downloads[download_id]
            logger.info(f"Removed old download from memory: {download_id}")

        if to_remove:
            logger.info(f"Cleanup: Removed {len(to_remove)} old downloads")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def cleanup_video_info_cache():
    """Remove old entries from video info cache"""
    try:
        now = time.time()
        to_remove = []

        for url, cache_entry in list(video_info_cache.items()):
            if now - cache_entry['timestamp'] > VIDEO_INFO_CACHE_TTL:
                to_remove.append(url)

        for url in to_remove:
            del video_info_cache[url]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} cached video info entries")

    except Exception as e:
        logger.error(f"Error cleaning video info cache: {e}")


def start_cleanup_thread():
    """Start background thread for periodic cleanup"""
    def cleanup_loop():
        while True:
            time.sleep(CLEANUP_INTERVAL)
            cleanup_old_downloads()
            cleanup_video_info_cache()

    cleanup_thread = Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    logger.info("Started cleanup background thread")


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'active_downloads': len(active_downloads),
        'cached_videos': len(video_info_cache)
    })


@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information with caching"""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Check cache first
        now = time.time()
        if url in video_info_cache:
            cache_entry = video_info_cache[url]
            if now - cache_entry['timestamp'] < VIDEO_INFO_CACHE_TTL:
                logger.info(f"Cache hit for video info: {url}")
                return jsonify(cache_entry['data'])

        # Not in cache or expired, fetch new
        logger.info(f"Cache miss for video info: {url}")
        downloader = YouTubeDownloader()
        info = downloader.get_video_info(url)

        # Format response
        response = {
            'title': info['title'],
            'duration': format_duration(info['duration']),
            'duration_seconds': info['duration'],
            'uploader': info['uploader'],
            'id': info['id'],
            'thumbnail': f"https://img.youtube.com/vi/{info['id']}/maxresdefault.jpg"
        }

        # Cache the result
        video_info_cache[url] = {
            'data': response,
            'timestamp': now
        }

        return jsonify(response)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting video info: {error_msg}")

        # Check for bot detection error
        if 'Sign in to confirm' in error_msg or 'bot' in error_msg.lower():
            return jsonify({
                'error': 'YouTube bot detection triggered. Server needs cookies configured.',
                'details': 'The server administrator needs to add YouTube cookies. See DEPLOY-WITH-COOKIES.md for setup instructions.',
                'technical': error_msg
            }), 503

        return jsonify({'error': error_msg}), 400


@app.route('/api/list-formats', methods=['POST'])
def list_formats():
    """List available formats"""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        downloader = YouTubeDownloader()
        formats = downloader.list_formats(url)

        # Filter and organize formats
        video_formats = []
        audio_formats = []

        seen_resolutions = set()
        for fmt in formats:
            if fmt['vcodec'] != 'none':
                resolution = fmt['resolution']
                # Only add unique resolutions
                if resolution not in seen_resolutions and resolution != 'audio only':
                    seen_resolutions.add(resolution)
                    video_formats.append({
                        'id': fmt['format_id'],
                        'resolution': resolution,
                        'ext': fmt['ext'],
                        'size': format_size(fmt['filesize']),
                        'quality': fmt['quality']
                    })

            elif fmt['acodec'] != 'none':
                audio_formats.append({
                    'id': fmt['format_id'],
                    'quality': fmt['quality'],
                    'ext': fmt['ext'],
                    'size': format_size(fmt['filesize'])
                })

        # Limit and sort
        video_formats = video_formats[:10]
        audio_formats = audio_formats[:5]

        return jsonify({
            'video_formats': video_formats,
            'audio_formats': audio_formats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/download', methods=['POST'])
def start_download():
    """Start a download using thread pool"""
    try:
        data = request.get_json()
        url = data.get('url')
        quality = data.get('quality', 'best')
        format = data.get('format', 'mp4')
        format_type = data.get('format_type', 'video')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        socket_id = data.get('socket_id')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Validate socket_id is from an active connection
        # Note: We still accept socket_id from client for backwards compatibility,
        # but we could enhance this with server-side tracking

        # Generate unique download ID
        download_id = str(uuid.uuid4())

        # Create download directory
        download_dir = app.config['DOWNLOAD_FOLDER']
        download_dir.mkdir(exist_ok=True)

        # Download task function
        def download_task():
            try:
                logger.info(f"Starting download {download_id} for URL: {url}")
                downloader = WebDownloader(
                    output_dir=str(download_dir),
                    socket_id=socket_id
                )

                filename = downloader.download(
                    url=url,
                    quality=quality,
                    format=format,
                    format_type=format_type,
                    start_time=start_time if start_time else None,
                    end_time=end_time if end_time else None
                )

                # Verify file exists
                if not os.path.exists(filename):
                    raise Exception(f"Download completed but file not found: {filename}")

                active_downloads[download_id].update({
                    'status': 'completed',
                    'filename': os.path.basename(filename),
                    'filepath': filename,
                    'timestamp': datetime.now()
                })

                logger.info(f"Download {download_id} completed: {filename}")

                if socket_id:
                    socketio.emit('download_complete', {
                        'download_id': download_id,
                        'filename': os.path.basename(filename)
                    }, room=socket_id)

            except Exception as e:
                logger.error(f"Download {download_id} failed: {str(e)}")
                active_downloads[download_id].update({
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now()
                })

                if socket_id:
                    socketio.emit('download_error', {
                        'error': str(e)
                    }, room=socket_id)

        # Store download info with timestamp
        active_downloads[download_id] = {
            'status': 'downloading',
            'url': url,
            'timestamp': datetime.now()
        }

        # Submit to thread pool (bounded concurrency)
        download_executor.submit(download_task)
        logger.info(f"Download {download_id} submitted to executor")

        return jsonify({
            'download_id': download_id,
            'status': 'started'
        })

    except Exception as e:
        logger.error(f"Error starting download: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/download-status/<download_id>', methods=['GET'])
def download_status(download_id):
    """Get download status"""
    if download_id not in active_downloads:
        return jsonify({'error': 'Download not found'}), 404

    return jsonify(active_downloads[download_id])


@app.route('/api/download-file/<download_id>', methods=['GET'])
def download_file(download_id):
    """Download the completed file"""
    if download_id not in active_downloads:
        return jsonify({'error': 'Download not found'}), 404

    download_info = active_downloads[download_id]

    if download_info['status'] != 'completed':
        return jsonify({'error': f"Download not completed. Status: {download_info['status']}"}), 400

    filepath = download_info.get('filepath')

    if not filepath:
        return jsonify({'error': 'File path not found in download info'}), 500

    if not os.path.exists(filepath):
        # Check if file exists with different extension
        base = filepath.rsplit('.', 1)[0]
        possible_files = [
            base + '.mp3',
            base + '.m4a',
            base + '.opus',
            base + '.flac',
            base + '.mp4',
            base + '.webm',
            base + '.mkv'
        ]

        for possible_file in possible_files:
            if os.path.exists(possible_file):
                filepath = possible_file
                # Update the stored filepath
                active_downloads[download_id]['filepath'] = filepath
                active_downloads[download_id]['filename'] = os.path.basename(filepath)
                break
        else:
            # Still not found
            return jsonify({
                'error': 'File not found',
                'expected_path': filepath,
                'message': 'The downloaded file could not be located. It may have been moved or deleted.'
            }), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=download_info['filename']
    )


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    # Automatically join the client to a room with their socket ID
    join_room(request.sid)
    logger.info(f'Client connected and joined room: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')


@socketio.on('join')
def handle_join(data):
    """Handle room joining for progress updates"""
    room = request.sid
    join_room(room)
    logger.info(f'Client explicitly joined room: {room}')


@socketio.on_error_default
def default_error_handler(e):
    """Handle SocketIO errors gracefully"""
    logger.error(f'SocketIO error: {e}')
    # Don't propagate errors to client, just log them
    return False


@socketio.on('connect_error')
def handle_connect_error():
    """Handle connection errors"""
    logger.warning('Client connection error')
    return False


# Initialize on module load (for production servers like Gunicorn)
def init_app():
    """Initialize application - called on startup"""
    app.config['DOWNLOAD_FOLDER'].mkdir(exist_ok=True)
    start_cleanup_thread()
    logger.info("Application initialized")

# Auto-initialize for production (Gunicorn, etc.)
# This ensures cleanup thread starts even when not running with __main__
try:
    if not getattr(init_app, '_initialized', False):
        init_app()
        init_app._initialized = True
except Exception as e:
    logger.error(f"Error during app initialization: {e}")


if __name__ == '__main__':
    # Create downloads directory
    app.config['DOWNLOAD_FOLDER'].mkdir(exist_ok=True)

    # Start cleanup background thread
    start_cleanup_thread()

    # Run the app
    logger.info("Starting YouTube Downloader Web Interface...")
    logger.info("Open your browser and navigate to: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
