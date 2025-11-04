#!/usr/bin/env python3
"""
Command-line interface for YouTube Downloader
"""
import argparse
import sys
from pathlib import Path
from colorama import Fore, Style, init

from downloader import YouTubeDownloader, format_size, format_duration

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║     YouTube Video Downloader with Advanced Features   ║
║                   Powered by yt-dlp                   ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_video_info(info: dict):
    """Print formatted video information"""
    print(f"\n{Fore.GREEN}Video Information:{Style.RESET_ALL}")
    print(f"  Title: {Fore.YELLOW}{info['title']}{Style.RESET_ALL}")
    print(f"  Duration: {format_duration(info['duration'])}")
    print(f"  Uploader: {info['uploader']}")
    print(f"  Video ID: {info['id']}\n")


def print_formats(formats: list):
    """Print available formats in a table"""
    print(f"\n{Fore.GREEN}Available Formats:{Style.RESET_ALL}")
    print(f"{'ID':<8} {'Extension':<12} {'Resolution':<15} {'Quality':<15} {'Size':<12}")
    print("-" * 75)

    # Filter and sort formats
    video_formats = [f for f in formats if f['vcodec'] != 'none']
    audio_formats = [f for f in formats if f['vcodec'] == 'none' and f['acodec'] != 'none']

    if video_formats:
        print(f"\n{Fore.CYAN}Video Formats:{Style.RESET_ALL}")
        for fmt in video_formats[:15]:  # Show top 15
            print(
                f"{fmt['format_id']:<8} "
                f"{fmt['ext']:<12} "
                f"{fmt['resolution']:<15} "
                f"{fmt['quality']:<15} "
                f"{format_size(fmt['filesize']):<12}"
            )

    if audio_formats:
        print(f"\n{Fore.CYAN}Audio Formats:{Style.RESET_ALL}")
        for fmt in audio_formats[:10]:  # Show top 10
            print(
                f"{fmt['format_id']:<8} "
                f"{fmt['ext']:<12} "
                f"{fmt['resolution']:<15} "
                f"{fmt['quality']:<15} "
                f"{format_size(fmt['filesize']):<12}"
            )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Download YouTube videos with advanced options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download best quality video
  python cli.py https://youtube.com/watch?v=VIDEO_ID

  # Download audio only as MP3
  python cli.py https://youtube.com/watch?v=VIDEO_ID -t audio

  # Download specific quality
  python cli.py https://youtube.com/watch?v=VIDEO_ID -q 720p

  # Download with custom duration (trim from 1:30 to 3:45)
  python cli.py https://youtube.com/watch?v=VIDEO_ID -s 00:01:30 -e 00:03:45

  # List available formats
  python cli.py https://youtube.com/watch?v=VIDEO_ID --list-formats

  # Download playlist
  python cli.py https://youtube.com/playlist?list=PLAYLIST_ID --playlist

  # Download specific videos from playlist (1-5)
  python cli.py https://youtube.com/playlist?list=PLAYLIST_ID --playlist --start 1 --end 5
        """
    )

    parser.add_argument(
        'url',
        help='YouTube video or playlist URL'
    )

    parser.add_argument(
        '-o', '--output',
        default='downloads',
        help='Output directory (default: downloads)'
    )

    parser.add_argument(
        '-q', '--quality',
        default='best',
        help='Video quality: best, worst, 360p, 480p, 720p, 1080p, etc. (default: best)'
    )

    parser.add_argument(
        '-t', '--type',
        choices=['video', 'audio', 'both'],
        default='video',
        help='Download type: video, audio, or both (default: video)'
    )

    parser.add_argument(
        '-s', '--start',
        help='Start time for trimming (format: HH:MM:SS or seconds)'
    )

    parser.add_argument(
        '-e', '--end',
        help='End time for trimming (format: HH:MM:SS or seconds)'
    )

    parser.add_argument(
        '-f', '--filename',
        help='Custom output filename (without extension)'
    )

    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='List all available formats without downloading'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='Show video information without downloading'
    )

    parser.add_argument(
        '--playlist',
        action='store_true',
        help='Download entire playlist'
    )

    parser.add_argument(
        '--playlist-start',
        type=int,
        default=1,
        help='Playlist start index (default: 1)'
    )

    parser.add_argument(
        '--playlist-end',
        type=int,
        help='Playlist end index'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Initialize downloader
    downloader = YouTubeDownloader(output_dir=args.output)

    try:
        # Handle list formats
        if args.list_formats:
            print(f"{Fore.CYAN}Fetching available formats...{Style.RESET_ALL}")
            info = downloader.get_video_info(args.url)
            print_video_info(info)
            formats = downloader.list_formats(args.url)
            print_formats(formats)
            return

        # Handle info only
        if args.info:
            print(f"{Fore.CYAN}Fetching video information...{Style.RESET_ALL}")
            info = downloader.get_video_info(args.url)
            print_video_info(info)
            return

        # Handle playlist download
        if args.playlist:
            print(f"{Fore.CYAN}Downloading playlist...{Style.RESET_ALL}")
            files = downloader.download_playlist(
                url=args.url,
                quality=args.quality,
                format_type=args.type,
                start_index=args.playlist_start,
                end_index=args.playlist_end,
            )
            print(f"\n{Fore.GREEN}Successfully downloaded {len(files)} video(s)!{Style.RESET_ALL}")
            print(f"Location: {Path(args.output).absolute()}")
            return

        # Handle single video download
        print(f"{Fore.CYAN}Starting download...{Style.RESET_ALL}")

        # Show video info first
        info = downloader.get_video_info(args.url)
        print_video_info(info)

        # Download
        output_file = downloader.download(
            url=args.url,
            quality=args.quality,
            format_type=args.type,
            start_time=args.start,
            end_time=args.end,
            output_filename=args.filename,
        )

        print(f"\n{Fore.GREEN}✓ Download completed successfully!{Style.RESET_ALL}")
        print(f"Saved to: {Fore.YELLOW}{output_file}{Style.RESET_ALL}\n")

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Download cancelled by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
