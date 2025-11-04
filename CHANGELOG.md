# Changelog

## Fixed Issues - 2025-11-04

### Bug Fix: Audio Download Format Issue

**Problem:**
- When downloading audio files, the system was incorrectly converting MP3 files to MP4
- This caused "File not found" errors when trying to download completed files
- The issue occurred because the video converter was being applied to audio downloads

**Root Cause:**
- The custom duration trimming logic was adding `FFmpegVideoConvertor` postprocessor to ALL downloads, including audio-only downloads
- The filename tracking didn't account for unexpected format conversions

**Solution:**
1. **Fixed postprocessor logic** (downloader.py:134-171):
   - Audio downloads now stay as MP3, even with trimming enabled
   - Video downloads properly convert to MP4
   - Postprocessors are only applied to the appropriate format type

2. **Improved filename tracking** (downloader.py:173-192):
   - Correctly predicts final file extension based on format type
   - Audio → `.mp3`
   - Video → `.mp4`

3. **Added fallback file detection** (app.py:262-285):
   - If expected file not found, searches for files with common extensions
   - Automatically updates filepath if found with different extension
   - Provides detailed error messages for debugging

4. **Added file existence verification** (app.py:190-192):
   - Verifies file exists before marking download as complete
   - Prevents "file not found" errors on download

### Testing
- Audio-only downloads: ✓ Creates `.mp3` files
- Video downloads: ✓ Creates `.mp4` files
- Custom duration trimming: ✓ Works for both audio and video
- File download: ✓ Successfully locates and serves files

### Files Modified
- `downloader.py` - Fixed postprocessor logic and filename tracking
- `app.py` - Added file verification and fallback detection
