# YouTube Video Downloader

A powerful tool to download YouTube videos and playlists using Python and yt-dlp. Available in both command-line and GUI versions.

## Features

- 🎥 Download individual YouTube videos
- 📁 Download entire playlists
- 🎵 Audio-only downloads (MP3 format)
- 📊 Multiple video quality options
- 📋 Video information display
- 🎨 Colored terminal output (CLI version)
- 🖥️ User-friendly GUI interface
- 📂 Custom output directory support
- 📦 Standalone executable creation

## Installation

1. **Clone or download this repository**
2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Version (Recommended)

Run the graphical interface:
```bash
python yt_downloader_gui.py
```

The GUI provides:
- Easy URL input
- Quality selection dropdown
- Audio-only and playlist options
- Output directory browser
- Real-time progress bar
- Video information display
- One-click download

### Command Line Version

### Basic Usage

```bash
# Download a video with best quality
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Download with specific quality
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --quality 720p

# Download audio only (MP3)
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only

# Download entire playlist
python yt_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist

# Show video information only (no download)
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --info
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--quality` | `-q` | Video quality: `best`, `worst`, `720p`, `480p`, `360p`, `240p` | `best` |
| `--audio-only` | `-a` | Download audio only (MP3 format) | `False` |
| `--playlist` | `-p` | Download entire playlist | `False` |
| `--output` | `-o` | Output directory | `./downloads` |
| `--info` | `-i` | Show video information only | `False` |

### Examples

#### Download a single video:
```bash
python yt_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### Download with 720p quality:
```bash
python yt_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --quality 720p
```

#### Download audio only:
```bash
python yt_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio-only
```

#### Download entire playlist:
```bash
python yt_downloader.py "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMOVaJ7QyWg8c2ZvA8" --playlist
```

#### Custom output directory:
```bash
python yt_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output "C:/MyVideos"
```

#### Show video information:
```bash
python yt_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

## Output

- Videos are saved to the `downloads` folder by default
- Playlists are saved in subfolders named after the playlist
- Audio files are converted to MP3 format
- Progress is shown with colored output

## Requirements

- Python 3.7+
- yt-dlp
- colorama (for colored output)

## Troubleshooting

### Common Issues

1. **"yt-dlp not found" error:**
   ```bash
   pip install yt-dlp
   ```

2. **Permission errors:**
   - Make sure you have write permissions to the output directory
   - Try running as administrator (Windows) or with sudo (Linux/Mac)

3. **Video unavailable:**
   - Some videos may be region-restricted or private
   - Check if the URL is correct and accessible

4. **Slow downloads:**
   - Try different quality settings
   - Check your internet connection

### Getting Help

Run the script with `--help` to see all available options:
```bash
python yt_downloader.py --help
```

## Creating Executable

To create a standalone executable that doesn't require Python installation:

### Windows
```bash
# Run the build script
python build_executable.py

# Or use the batch file
build.bat
```

### Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name=YouTube_Downloader yt_downloader_gui.py
```

The executable will be created in the `dist` folder and can be distributed without requiring Python installation.

## Files

- `yt_downloader.py` - Command-line version
- `yt_downloader_gui.py` - GUI version
- `build_executable.py` - Build script for creating executable
- `build.bat` - Windows batch file for building
- `requirements.txt` - Python dependencies

## License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws when downloading content.
