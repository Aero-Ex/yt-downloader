"""
YouTube Video Downloader with Advanced Features
"""
import yt_dlp
import os
import sys
from typing import Optional, Dict, List
from pathlib import Path


class YouTubeDownloader:
    """Main class for downloading YouTube videos with various options"""

    def __init__(self, output_dir: str = "downloads"):
        """
        Initialize the downloader

        Args:
            output_dir: Directory to save downloaded files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Setup cookies - check environment variable first, then file
        self._setup_cookies()

    def _setup_cookies(self):
        """Setup cookies from environment variable or file"""
        import base64

        # Method 1: Check for base64-encoded cookies in environment
        cookies_env = os.environ.get('YOUTUBE_COOKIES_BASE64') or os.environ.get('YT_COOKIES_B64')
        if cookies_env:
            try:
                self.cookies_file = Path(__file__).parent / 'youtube.txt'

                # Decode and write cookies
                cookies_content = base64.b64decode(cookies_env).decode('utf-8')
                self.cookies_file.write_text(cookies_content)
                print(f"✓ Cookies loaded from environment variable")
                return
            except Exception as e:
                print(f"Warning: Failed to load cookies from environment: {e}")

        # Method 2: Check for direct cookies content in environment
        cookies_content = os.environ.get('YOUTUBE_COOKIES')
        if cookies_content:
            try:
                self.cookies_file = Path(__file__).parent / 'youtube.txt'
                self.cookies_file.write_text(cookies_content)
                print(f"✓ Cookies loaded from YOUTUBE_COOKIES environment variable")
                return
            except Exception as e:
                print(f"Warning: Failed to load cookies from environment: {e}")

        # Method 3: Use existing file
        self.cookies_file = Path(__file__).parent / 'youtube.txt'
        if self.cookies_file.exists():
            print(f"✓ Cookies file found: {self.cookies_file}")
        else:
            print(f"⚠ WARNING: Cookies file not found: {self.cookies_file}")

    def _get_base_opts(self) -> Dict:
        """Get base yt-dlp options with cookies and anti-bot measures"""
        opts = {
            # Anti-bot measures
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

            # Additional anti-bot headers
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },

            # Network options - OPTIMIZED FOR SPEED
            # Only use minimal delays when cookies are present
            'sleep_interval': 0,  # No delay when we have cookies
            'max_sleep_interval': 0,
            'sleep_interval_requests': 0,  # No delay between fragments

            # Use IPv4 to avoid some detection
            'source_address': '0.0.0.0',

            # Extract formats without downloading (helps with rate limiting)
            'extract_flat': False,

            # Performance optimizations
            'concurrent_fragment_downloads': 8,  # Download up to 8 fragments at once
            'http_chunk_size': 10485760,  # 10MB chunks (YouTube's limit)
            'noprogress': False,  # We want progress updates

            # YouTube-specific optimizations
            # Note: Removed restrictive player_client settings to ensure compatibility
            # with all video types (some videos only work with certain clients)
            'extractor_args': {
                'youtube': {
                    'skip': ['hls'],  # Only skip HLS, allow all clients
                }
            },
        }

        # Add proxy if configured (helps bypass datacenter IP detection)
        proxy = os.environ.get('PROXY_URL')
        if proxy:
            opts['proxy'] = proxy
            print(f"✓ Using proxy for requests")

        # Geo-bypass options
        geo_bypass_country = os.environ.get('GEO_BYPASS_COUNTRY')
        if geo_bypass_country:
            opts['geo_bypass_country'] = geo_bypass_country

        # Add cookies if file exists
        if self.cookies_file.exists():
            opts['cookiefile'] = str(self.cookies_file)
            print(f"✓ Using cookies file: {self.cookies_file}")
        else:
            print(f"⚠ WARNING: Cookies file does not exist, requests may fail: {self.cookies_file}")

        return opts

    def get_video_info(self, url: str) -> Dict:
        """
        Get information about the video without downloading

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video information
        """
        ydl_opts = self._get_base_opts()
        ydl_opts.update({
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,  # Explicitly skip download for speed
            'format': 'best',  # Don't be picky about format when just getting info
        })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'formats': info.get('formats'),
                    'id': info.get('id'),
                }
        except Exception as e:
            raise Exception(f"Error getting video info: {str(e)}")

    def list_formats(self, url: str) -> List[Dict]:
        """
        List available formats for the video

        Args:
            url: YouTube video URL

        Returns:
            List of available formats with quality info
        """
        info = self.get_video_info(url)
        formats = []

        for fmt in info['formats']:
            format_info = {
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext'),
                'resolution': fmt.get('resolution', 'audio only'),
                'filesize': fmt.get('filesize'),
                'vcodec': fmt.get('vcodec', 'none'),
                'acodec': fmt.get('acodec', 'none'),
                'fps': fmt.get('fps'),
                'quality': fmt.get('format_note', 'unknown'),
            }
            formats.append(format_info)

        return formats

    def download(
        self,
        url: str,
        quality: str = "best",
        format: str = "mp4",
        format_type: str = "video",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> str:
        """
        Download video with specified options

        Args:
            url: YouTube video URL
            quality: Quality setting (best, worst, or specific format code)
            format: Container format (mp4, webm, mkv for video; mp3, m4a, opus, flac for audio)
            format_type: Type to download ('video', 'audio', or 'both')
            start_time: Start time in format HH:MM:SS or seconds
            end_time: End time in format HH:MM:SS or seconds
            output_filename: Custom filename (without extension)

        Returns:
            Path to downloaded file
        """
        # Build format string based on type with better fallbacks
        if format_type == "audio":
            format_string = "bestaudio/best"
        elif format_type == "video":
            # Map common formats to their extensions
            ext = format if format in ['mp4', 'webm', 'mkv'] else 'mp4'

            if quality == "best":
                # Try best video+audio with preferred format, fallback to best single file
                if ext == 'mp4':
                    format_string = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                elif ext == 'webm':
                    format_string = "bestvideo[ext=webm]+bestaudio[ext=webm]/bestvideo+bestaudio/best"
                else:  # mkv or fallback
                    format_string = "bestvideo+bestaudio/best"
            elif quality == "worst":
                format_string = "worstvideo+worstaudio/worst"
            else:
                # Custom quality (e.g., "720p", "1080p") with multiple fallbacks
                height = quality.replace('p', '')
                # IMPORTANT: Try single-file formats FIRST (for videos without separate streams)
                if ext == 'mp4':
                    format_string = (
                        f"best[height<={height}][ext=mp4]/"  # Try single mp4 file first
                        f"best[height<={height}]/"
                        f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
                        f"bestvideo[height<={height}][ext=mp4]+bestaudio/"
                        f"bestvideo[height<={height}]+bestaudio[ext=m4a]/"
                        f"bestvideo[height<={height}]+bestaudio/"
                        "best[ext=mp4]/"
                        "best"
                    )
                elif ext == 'webm':
                    format_string = (
                        f"best[height<={height}][ext=webm]/"  # Try single webm file first
                        f"best[height<={height}]/"
                        f"bestvideo[height<={height}][ext=webm]+bestaudio[ext=webm]/"
                        f"bestvideo[height<={height}][ext=webm]+bestaudio/"
                        f"bestvideo[height<={height}]+bestaudio/"
                        "best[ext=webm]/"
                        "best"
                    )
                else:  # mkv or fallback
                    format_string = (
                        f"best[height<={height}]/"  # Try single file first
                        f"bestvideo[height<={height}]+bestaudio/"
                        "best"
                    )
        else:
            ext = format if format in ['mp4', 'webm', 'mkv'] else 'mp4'
            # Use more permissive format strings with better fallbacks
            # IMPORTANT: Try single-file formats FIRST (for videos without separate streams)
            if ext == 'mp4':
                format_string = (
                    "best[ext=mp4]/"  # Try single mp4 file first
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "bestvideo[ext=mp4]+bestaudio/"
                    "bestvideo+bestaudio[ext=m4a]/"
                    "bestvideo+bestaudio/"
                    "best"
                )
            elif ext == 'webm':
                format_string = (
                    "best[ext=webm]/"  # Try single webm file first
                    "bestvideo[ext=webm]+bestaudio[ext=webm]/"
                    "bestvideo[ext=webm]+bestaudio/"
                    "bestvideo+bestaudio/"
                    "best"
                )
            else:
                format_string = "best/bestvideo+bestaudio"

        # Base options with anti-bot measures
        ydl_opts = self._get_base_opts()
        ydl_opts.update({
            'format': format_string,
            'outtmpl': str(self.output_dir / (output_filename or '%(title)s.%(ext)s')),
            'progress_hooks': [self._progress_hook],
            'quiet': False,
            'no_warnings': False,
            # Additional options to handle YouTube's format restrictions
            'allow_unplayable_formats': False,  # Skip unplayable formats
            'check_formats': 'selected',  # Only check selected format
            'ignoreerrors': False,  # Don't ignore errors, but fallback will handle them
        })

        # Add audio extraction for audio-only
        if format_type == "audio":
            # Determine audio quality - use numeric bitrate if provided, else default to 320 for "best"
            audio_quality = '320' if quality == 'best' else quality
            # Ensure it's a valid bitrate value
            if not audio_quality.isdigit():
                audio_quality = '192'  # Fallback to 192 if invalid

            # Determine codec based on format
            codec = format if format in ['mp3', 'm4a', 'opus', 'flac'] else 'mp3'

            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': audio_quality if codec != 'flac' else '0',  # FLAC is lossless, no quality setting
            }]

        # Add custom duration trimming if specified
        if start_time or end_time:
            # FFmpeg arguments for trimming
            ffmpeg_args = []
            if start_time:
                ffmpeg_args.extend(['-ss', start_time])
            if end_time:
                ffmpeg_args.extend(['-to', end_time])

            ydl_opts['postprocessor_args'] = {
                'ffmpeg': ffmpeg_args
            }

            # For audio with trimming, we need to re-encode
            if format_type == "audio":
                # Determine audio quality - use numeric bitrate if provided, else default to 320 for "best"
                audio_quality = '320' if quality == 'best' else quality
                # Ensure it's a valid bitrate value
                if not audio_quality.isdigit():
                    audio_quality = '192'  # Fallback to 192 if invalid

                # Determine codec based on format
                codec = format if format in ['mp3', 'm4a', 'opus', 'flac'] else 'mp3'

                # Replace the audio extractor with one that includes trimming
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': codec,
                    'preferredquality': audio_quality if codec != 'flac' else '0',  # FLAC is lossless, no quality setting
                }]
            else:
                # For video with trimming
                video_format = format if format in ['mp4', 'webm', 'mkv'] else 'mp4'
                postprocessors = ydl_opts.get('postprocessors', [])
                postprocessors.append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': video_format,
                })
                ydl_opts['postprocessors'] = postprocessors

        # Merge output for video+audio (only if no trimming was applied)
        elif format_type == "video":
            video_format = format if format in ['mp4', 'webm', 'mkv'] else 'mp4'
            postprocessors = ydl_opts.get('postprocessors', [])
            postprocessors.append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': video_format,
            })
            ydl_opts['postprocessors'] = postprocessors

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Get the base filename (before extension)
                base_filename = ydl.prepare_filename(info)
                base_filename = base_filename.rsplit('.', 1)[0]

                # Determine final extension based on format type and postprocessors
                if format_type == "audio":
                    audio_ext = format if format in ['mp3', 'm4a', 'opus', 'flac'] else 'mp3'
                    final_filename = base_filename + f'.{audio_ext}'
                elif format_type == "video" or (start_time or end_time):
                    video_ext = format if format in ['mp4', 'webm', 'mkv'] else 'mp4'
                    final_filename = base_filename + f'.{video_ext}'
                else:
                    # Use original extension
                    final_filename = ydl.prepare_filename(info)

                return final_filename
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # If format not available, try with simple "best" format as last resort
            if "Requested format is not available" in error_msg or "No video formats found" in error_msg:
                print(f"⚠ Requested format not available, retrying with best available format...")
                ydl_opts['format'] = 'best'  # Simplest fallback
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        base_filename = ydl.prepare_filename(info)
                        base_filename = base_filename.rsplit('.', 1)[0]
                        if format_type == "audio":
                            audio_ext = format if format in ['mp3', 'm4a', 'opus', 'flac'] else 'mp3'
                            final_filename = base_filename + f'.{audio_ext}'
                        else:
                            final_filename = ydl.prepare_filename(info)
                        return final_filename
                except Exception as retry_error:
                    raise Exception(f"Download failed even with best format fallback: {str(retry_error)}")
            else:
                raise Exception(f"Download failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

    def _progress_hook(self, d: Dict):
        """Hook for download progress"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')

            sys.stdout.write(f"\rDownloading: {percent} | Speed: {speed} | ETA: {eta}")
            sys.stdout.flush()
        elif d['status'] == 'finished':
            print("\nDownload completed! Processing...")

    def download_playlist(
        self,
        url: str,
        quality: str = "best",
        format_type: str = "video",
        start_index: int = 1,
        end_index: Optional[int] = None,
    ) -> List[str]:
        """
        Download entire playlist or specific range

        Args:
            url: YouTube playlist URL
            quality: Quality setting
            format_type: Type to download
            start_index: Start from this video (1-indexed)
            end_index: End at this video (inclusive)

        Returns:
            List of downloaded file paths
        """
        if format_type == "audio":
            format_string = "bestaudio/best"
        else:
            format_string = "bestvideo+bestaudio/best"

        ydl_opts = {
            'format': format_string,
            'outtmpl': str(self.output_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
            'progress_hooks': [self._progress_hook],
            'playliststart': start_index,
        }

        if end_index:
            ydl_opts['playlistend'] = end_index

        if format_type == "audio":
            # Determine audio quality - use numeric bitrate if provided, else default to 320 for "best"
            audio_quality = '320' if quality == 'best' else quality
            # Ensure it's a valid bitrate value
            if not audio_quality.isdigit():
                audio_quality = '192'  # Fallback to 192 if invalid

            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }]

        downloaded_files = []

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            filename = ydl.prepare_filename(entry)
                            if format_type == "audio":
                                filename = filename.rsplit('.', 1)[0] + '.mp3'
                            downloaded_files.append(filename)

                return downloaded_files
        except Exception as e:
            raise Exception(f"Playlist download failed: {str(e)}")


def format_size(bytes_size: Optional[int]) -> str:
    """Format file size in human-readable format"""
    if bytes_size is None:
        return "Unknown"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in human-readable format"""
    if seconds is None:
        return "Unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
