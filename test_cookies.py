#!/usr/bin/env python3
"""
Test if YouTube cookies are working
"""
from downloader import YouTubeDownloader
from pathlib import Path

def test_cookies():
    print("=" * 60)
    print("YouTube Cookies Test")
    print("=" * 60)
    print()

    # Check if cookies file exists
    cookies_file = Path(__file__).parent / 'cookies' / 'youtube.txt'

    if cookies_file.exists():
        print(f"✓ Cookies file found: {cookies_file}")
        size = cookies_file.stat().st_size
        print(f"  File size: {size} bytes")
        print()
    else:
        print(f"✗ Cookies file NOT found: {cookies_file}")
        print()
        print("To fix:")
        print("1. Install browser extension to export cookies")
        print("2. Export YouTube cookies as 'youtube.txt'")
        print("3. Place in: cookies/youtube.txt")
        print("4. Run this test again")
        print()
        print("See: YOUTUBE-BOT-FIX.md for detailed instructions")
        return False

    # Test with a YouTube video
    print("Testing with YouTube video...")
    test_url = "https://youtu.be/gwEBjgCe5aY?si=lpWYOxW3K8tXS36q"

    dl = YouTubeDownloader()

    try:
        print(f"Fetching: {test_url}")
        info = dl.get_video_info(test_url)

        print()
        print("✓ SUCCESS! YouTube access working!")
        print()
        print(f"Video Info:")
        print(f"  Title: {info['title']}")
        print(f"  Duration: {info['duration']} seconds")
        print(f"  Uploader: {info['uploader']}")
        print()
        print("Your cookies are valid and working! 🎉")
        return True

    except Exception as e:
        error_msg = str(e)
        print()
        print("✗ FAILED!")
        print()
        print(f"Error: {error_msg}")
        print()

        if "Sign in to confirm" in error_msg or "bot" in error_msg.lower():
            print("This is the bot detection error.")
            print()
            if cookies_file.exists():
                print("Your cookies might be:")
                print("  - Expired (export fresh ones)")
                print("  - Invalid (check file format)")
                print("  - From wrong browser (export from browser you use)")
                print()
                print("Try:")
                print("1. Clear YouTube cookies in your browser")
                print("2. Visit YouTube and browse a bit")
                print("3. Re-export cookies")
                print("4. Replace cookies/youtube.txt")
                print("5. Run this test again")
        else:
            print("Different error - this might not be bot detection.")
            print("Check the error message above.")

        return False


if __name__ == "__main__":
    success = test_cookies()

    print()
    print("=" * 60)

    if success:
        print("✓ All good! You can now use the downloader.")
    else:
        print("✗ Please fix the issues above and try again.")

    print("=" * 60)
