# YouTube Video Downloader

A powerful YouTube downloader with both **Web Interface** and **Command-Line** options. Download videos with advanced features including quality selection, audio extraction, custom duration trimming, and playlist support.

## Two Ways to Use

### 🌐 Web Interface (Recommended)
Modern, user-friendly web interface with real-time progress tracking.

### 💻 Command-Line Interface
Full-featured CLI for power users and automation.

## 🚀 Host FREE on the Web

### 🆓 Free Hosting (Recommended)

Deploy your app online for **completely FREE**:

- **[Railway Quick Start](RAILWAY-QUICKSTART.md)** ⚡ - Deploy in 2 minutes (NO CREDIT CARD)
- **[Free Hosting Guide](FREE-HOSTING.md)** 📋 - 3 free hosting options compared

**Popular choices:**
- 🚂 **Railway** - Easiest, 500 hrs/month free, no credit card
- 🎨 **Render** - 750 hrs/month free, auto HTTPS
- 🐳 **Fly.io** - Always on, 3 apps free

### 💰 Paid Hosting (Optional)

For production or heavy usage:
- **[Quick Start Deploy](QUICKSTART-DEPLOY.md)** - Multiple paid options
- **[Full Deployment Guide](DEPLOYMENT.md)** - Complete guide for VPS, Docker, and more

## Features

- **Download videos in multiple qualities**: Choose from best, 720p, 1080p, 4K, etc.
- **Audio extraction**: Download audio-only as MP3
- **Custom duration trimming**: Extract specific portions of videos
- **Playlist support**: Download entire playlists or specific ranges
- **Format listing**: View all available formats before downloading
- **Real-time progress tracking**: Live download progress with speed and ETA
- **Beautiful web interface**: Modern, responsive design
- **Colored CLI output**: Beautiful and informative terminal interface

## Prerequisites

- Python 3.7 or higher
- FFmpeg installed on your system

### Installing FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## Installation

1. Clone or download this project:
```bash
cd yt-downloader
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Make the CLI executable (Linux/macOS):
```bash
chmod +x cli.py
```

## Usage

## 🌐 Web Interface

The web interface provides a modern, user-friendly way to download videos with real-time progress tracking.

### Starting the Web Server

Run the Flask application:
```bash
python app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

### Using the Web Interface

1. **Paste YouTube URL** - Enter the video URL in the input field
2. **Fetch Video Info** - Click "Fetch Info" to load video details
3. **Choose Options**:
   - Select format type (Video or Audio Only)
   - Choose quality (Best, 720p, 1080p, etc.)
   - Optionally set custom start/end times for trimming
4. **Download** - Click "Start Download" to begin
5. **Watch Progress** - Real-time progress bar with speed and ETA
6. **Download File** - Once complete, click to download your file

### Web Interface Features

- **Real-time Progress**: WebSocket-based live progress updates
- **Video Preview**: Thumbnail and video information before downloading
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Error Handling**: Clear error messages and retry options
- **Custom Trimming**: Visual input for start/end times

---

## 💻 Command-Line Interface

### Basic Download

Download a video in best quality:
```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID"
```

### Download Audio Only

Extract audio as MP3:
```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -t audio
```

### Download Specific Quality

Download in 720p:
```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -q 720p
```

Available quality options:
- `best` - Best available quality (default)
- `worst` - Lowest quality
- `360p`, `480p`, `720p`, `1080p`, `1440p`, `2160p` (4K)

### Custom Duration Trimming

Download only a specific portion of the video:

```bash
# From 1 minute 30 seconds to 3 minutes 45 seconds
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -s 00:01:30 -e 00:03:45

# Using seconds
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -s 90 -e 225

# From start to 2 minutes
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -e 00:02:00

# From 1 minute to end
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -s 00:01:00
```

### Custom Output Directory and Filename

```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID" -o "my_videos" -f "my_custom_name"
```

### List Available Formats

See all available formats before downloading:
```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID" --list-formats
```

### Video Information

Get video information without downloading:
```bash
python cli.py "https://youtube.com/watch?v=VIDEO_ID" --info
```

### Download Playlists

Download entire playlist:
```bash
python cli.py "https://youtube.com/playlist?list=PLAYLIST_ID" --playlist
```

Download specific videos from playlist (videos 1-5):
```bash
python cli.py "https://youtube.com/playlist?list=PLAYLIST_ID" --playlist --playlist-start 1 --playlist-end 5
```

Download playlist audio only:
```bash
python cli.py "https://youtube.com/playlist?list=PLAYLIST_ID" --playlist -t audio
```

## Command-Line Options

```
positional arguments:
  url                   YouTube video or playlist URL

optional arguments:
  -h, --help            Show help message
  -o, --output DIR      Output directory (default: downloads)
  -q, --quality QUALITY Video quality: best, worst, 360p, 480p, 720p, 1080p, etc.
  -t, --type TYPE       Download type: video, audio, or both
  -s, --start TIME      Start time for trimming (HH:MM:SS or seconds)
  -e, --end TIME        End time for trimming (HH:MM:SS or seconds)
  -f, --filename NAME   Custom output filename (without extension)
  --list-formats        List all available formats
  --info                Show video information only
  --playlist            Download entire playlist
  --playlist-start N    Playlist start index (default: 1)
  --playlist-end N      Playlist end index
```

## Examples

### Download video in 1080p with custom name:
```bash
python cli.py "https://youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p -f "my_video"
```

### Extract 30-second audio clip:
```bash
python cli.py "https://youtube.com/watch?v=dQw4w9WgXcQ" -t audio -s 00:00:30 -e 00:01:00
```

### Download first 10 videos from playlist in 720p:
```bash
python cli.py "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" --playlist -q 720p --playlist-end 10
```

### Check available formats before downloading:
```bash
python cli.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --list-formats
```

## Programmatic Usage

You can also use the downloader as a Python module:

```python
from downloader import YouTubeDownloader

# Initialize downloader
dl = YouTubeDownloader(output_dir="my_downloads")

# Get video information
info = dl.get_video_info("https://youtube.com/watch?v=VIDEO_ID")
print(f"Title: {info['title']}")

# Download video
output_file = dl.download(
    url="https://youtube.com/watch?v=VIDEO_ID",
    quality="720p",
    format_type="video",
    start_time="00:01:00",
    end_time="00:02:00"
)
print(f"Downloaded to: {output_file}")

# Download audio only
audio_file = dl.download(
    url="https://youtube.com/watch?v=VIDEO_ID",
    format_type="audio"
)

# List available formats
formats = dl.list_formats("https://youtube.com/watch?v=VIDEO_ID")
for fmt in formats:
    print(f"{fmt['format_id']}: {fmt['resolution']} - {fmt['quality']}")
```

## Troubleshooting

### FFmpeg not found
Make sure FFmpeg is installed and available in your system PATH.

### Download fails
- Check your internet connection
- Verify the URL is correct and accessible
- Some videos may have restrictions (age-restricted, private, etc.)
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### Slow download speeds
This depends on your internet connection and YouTube's servers. The tool shows real-time speed information.

## Notes

- Downloaded files are saved in the `downloads` directory by default
- Audio files are converted to MP3 format at 192kbps
- Video files are saved as MP4 when merging video+audio
- Trimming uses FFmpeg for accurate frame-level cuts

## License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws when downloading content.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The best YouTube downloader
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing
- [colorama](https://github.com/tartley/colorama) - Colored terminal output
