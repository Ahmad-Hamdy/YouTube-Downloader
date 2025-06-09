# YouTube-Downloader

A modern desktop application for downloading YouTube videos with a user-friendly interface.

## Features

- Download YouTube videos in various resolutions and formats
- Simple, clean, and responsive UI built with PyQt5
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust and up-to-date YouTube support
- Multi-threaded downloads for a smooth user experience
- Customizable dark theme via external `style.qss` file

## Requirements

- Python 3.7+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [yt-dlp](https://pypi.org/project/yt-dlp/)
- [requests](https://pypi.org/project/requests/)
- [ffmpeg](https://ffmpeg.org/) (for best video/audio merging, see below)

## Setup

1. Install dependencies:
    ```
    pip install pyqt5 yt-dlp requests
    ```
2. [Download and install ffmpeg](https://ffmpeg.org/download.html) and add it to your system PATH for best results.
3. Ensure `youtube.ui`, `style.qss`, and all `.py` files are in the same directory.

## Customizing the Style

The application's appearance is controlled by the `style.qss` file (Qt Style Sheet).
You can edit `style.qss` to change colors, fonts, and other UI properties without modifying the Python code.

**Example:**
```css
QMainWindow {
    background-color: #232629;
}
```

If you want to reset to the default style, simply remove or rename the `style.qss` file.

## Usage

1. Run the application:
    ```
    python main.py
    ```
2. Paste a YouTube video URL.
3. Select the desired type and resolution.
4. Choose a download location.
5. Click "Download" to start.

## Notes

- The application uses `yt-dlp` for all YouTube interactions, ensuring high reliability.
- If you encounter issues with video merging or quality, make sure `ffmpeg` is installed and available in your system PATH.

---
