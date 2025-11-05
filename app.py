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
import yt_dlp

from downloader import YouTubeDownloader, format_duration, format_size

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

# Store active downloads
active_downloads = {}


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


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information"""
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

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

        return jsonify(response)

    except Exception as e:
        error_msg = str(e)

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
    """Start a download"""
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

        # Generate unique download ID
        download_id = str(uuid.uuid4())

        # Create download directory
        download_dir = app.config['DOWNLOAD_FOLDER']
        download_dir.mkdir(exist_ok=True)

        # Start download in background thread
        def download_task():
            try:
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

                active_downloads[download_id] = {
                    'status': 'completed',
                    'filename': os.path.basename(filename),
                    'filepath': filename
                }

                if socket_id:
                    socketio.emit('download_complete', {
                        'download_id': download_id,
                        'filename': os.path.basename(filename)
                    }, room=socket_id)

            except Exception as e:
                active_downloads[download_id] = {
                    'status': 'error',
                    'error': str(e)
                }

                if socket_id:
                    socketio.emit('download_error', {
                        'error': str(e)
                    }, room=socket_id)

        # Store download info
        active_downloads[download_id] = {
            'status': 'downloading',
            'url': url
        }

        # Start thread
        thread = Thread(target=download_task)
        thread.daemon = True
        thread.start()

        return jsonify({
            'download_id': download_id,
            'status': 'started'
        })

    except Exception as e:
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
    print(f'Client connected and joined room: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('join')
def handle_join(data):
    """Handle room joining for progress updates"""
    room = request.sid
    join_room(room)
    print(f'Client explicitly joined room: {room}')


@socketio.on_error_default
def default_error_handler(e):
    """Handle SocketIO errors gracefully"""
    print(f'SocketIO error: {e}')
    # Don't propagate errors to client, just log them
    return False


@socketio.on('connect_error')
def handle_connect_error():
    """Handle connection errors"""
    print('Client connection error')
    return False


if __name__ == '__main__':
    # Create downloads directory
    app.config['DOWNLOAD_FOLDER'].mkdir(exist_ok=True)

    # Run the app
    print("Starting YouTube Downloader Web Interface...")
    print("Open your browser and navigate to: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
