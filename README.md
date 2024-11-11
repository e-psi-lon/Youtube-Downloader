Here's the revised README section:

# YouTube Downloader

A simple desktop application to download YouTube videos in various formats using PyQt5.

## TL;DR
Download YouTube videos with a GUI interface, support for multiple formats (MP4, AVI, MOV, MP3, OGG, OPUS), and video preview functionality.

## Prerequisites

- Python 3.7+
- FFmpeg installed on your system

## Installation

1. Clone the repository
2. Install required dependencies:
```sh
pip install -r requirements.txt
```

## Features

- Download YouTube videos in multiple formats:
  - Video: MP4, AVI, MOV
  - Audio: MP3, OGG, OPUS
- Preview video details before downloading:
  - Thumbnail
  - Title
  - Duration
  - Description
- Progress bar for download tracking
- Custom save location selection
- Clean and intuitive interface

## Usage

1. Run the application:
```sh
python main.pyw
```

2. Enter a YouTube URL in the input field
3. Click "Preview" to see video details
4. Select desired format from the dropdown menu
5. Choose download directory (optional)
6. Click "Download" to start downloading

## Default Settings

- Download location: Application's current directory
- Default video format: MP4

## Dependencies
- pytubefix: YouTube video downloading
- PyQt5: GUI framework
- python-ffmpeg: Video/audio conversion
- requests: HTTP requests for thumbnails