#!/usr/bin/env python3
"""
Example usage of the YouTube Downloader module
"""
from downloader import YouTubeDownloader, format_duration


def example_basic_download():
    """Example: Basic video download"""
    print("\n=== Example 1: Basic Video Download ===")

    dl = YouTubeDownloader(output_dir="downloads")

    # Replace with actual video URL
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        output = dl.download(url, quality="best", format_type="video")
        print(f"Video downloaded to: {output}")
    except Exception as e:
        print(f"Error: {e}")


def example_audio_download():
    """Example: Audio-only download"""
    print("\n=== Example 2: Audio-Only Download ===")

    dl = YouTubeDownloader(output_dir="downloads")

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        output = dl.download(url, format_type="audio")
        print(f"Audio downloaded to: {output}")
    except Exception as e:
        print(f"Error: {e}")


def example_custom_duration():
    """Example: Download with custom duration trimming"""
    print("\n=== Example 3: Custom Duration Download ===")

    dl = YouTubeDownloader(output_dir="downloads")

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        # Download from 30 seconds to 1 minute 30 seconds
        output = dl.download(
            url,
            format_type="video",
            start_time="00:00:30",
            end_time="00:01:30",
            output_filename="trimmed_video"
        )
        print(f"Trimmed video downloaded to: {output}")
    except Exception as e:
        print(f"Error: {e}")


def example_video_info():
    """Example: Get video information"""
    print("\n=== Example 4: Get Video Information ===")

    dl = YouTubeDownloader()

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        info = dl.get_video_info(url)
        print(f"Title: {info['title']}")
        print(f"Duration: {format_duration(info['duration'])}")
        print(f"Uploader: {info['uploader']}")
        print(f"Video ID: {info['id']}")
    except Exception as e:
        print(f"Error: {e}")


def example_list_formats():
    """Example: List available formats"""
    print("\n=== Example 5: List Available Formats ===")

    dl = YouTubeDownloader()

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        formats = dl.list_formats(url)

        print("\nVideo Formats:")
        video_formats = [f for f in formats if f['vcodec'] != 'none'][:5]
        for fmt in video_formats:
            print(f"  {fmt['format_id']}: {fmt['resolution']} - {fmt['quality']}")

        print("\nAudio Formats:")
        audio_formats = [f for f in formats if f['vcodec'] == 'none'][:5]
        for fmt in audio_formats:
            print(f"  {fmt['format_id']}: {fmt['quality']}")

    except Exception as e:
        print(f"Error: {e}")


def example_quality_download():
    """Example: Download with specific quality"""
    print("\n=== Example 6: Download Specific Quality ===")

    dl = YouTubeDownloader(output_dir="downloads")

    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        # Download in 720p
        output = dl.download(url, quality="720p", format_type="video")
        print(f"720p video downloaded to: {output}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("YouTube Downloader - Example Usage")
    print("=" * 50)

    # Uncomment the examples you want to run:

    # example_video_info()
    # example_list_formats()

    # WARNING: These will actually download files
    # example_basic_download()
    # example_audio_download()
    # example_custom_duration()
    # example_quality_download()

    print("\nNote: Uncomment examples in the code to run them.")
    print("Warning: Download examples will actually download files.")


if __name__ == "__main__":
    main()
