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

    def get_video_info(self, url: str) -> Dict:
        """
        Get information about the video without downloading

        Args:
            url: YouTube video URL

        Returns:
            Dictionary with video information
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

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
            format_type: Type to download ('video', 'audio', or 'both')
            start_time: Start time in format HH:MM:SS or seconds
            end_time: End time in format HH:MM:SS or seconds
            output_filename: Custom filename (without extension)

        Returns:
            Path to downloaded file
        """
        # Build format string based on type
        if format_type == "audio":
            format_string = "bestaudio/best"
        elif format_type == "video":
            if quality == "best":
                format_string = "bestvideo+bestaudio/best"
            elif quality == "worst":
                format_string = "worstvideo+worstaudio/worst"
            else:
                # Custom quality (e.g., "720p", "1080p")
                format_string = f"bestvideo[height<={quality.replace('p', '')}]+bestaudio/best"
        else:
            format_string = "bestvideo+bestaudio/best"

        # Base options
        ydl_opts = {
            'format': format_string,
            'outtmpl': str(self.output_dir / (output_filename or '%(title)s.%(ext)s')),
            'progress_hooks': [self._progress_hook],
            'quiet': False,
            'no_warnings': False,
        }

        # Add audio extraction for audio-only
        if format_type == "audio":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
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
                # Replace the audio extractor with one that includes trimming
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                # For video with trimming
                postprocessors = ydl_opts.get('postprocessors', [])
                postprocessors.append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                })
                ydl_opts['postprocessors'] = postprocessors

        # Merge output for video+audio (only if no trimming was applied)
        elif format_type == "video":
            postprocessors = ydl_opts.get('postprocessors', [])
            postprocessors.append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
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
                    final_filename = base_filename + '.mp3'
                elif format_type == "video" or (start_time or end_time):
                    final_filename = base_filename + '.mp4'
                else:
                    # Use original extension
                    final_filename = ydl.prepare_filename(info)

                return final_filename
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
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
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
