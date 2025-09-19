# YouTube Video Downloader

A powerful tool to download YouTube videos and playlists with advanced queue management, priority control, and concurrent downloads. Available in both command-line and advanced GUI versions.

## 🚀 Features

### Core Features
- 🎥 Download individual YouTube videos or entire playlists
- 🎵 Audio-only downloads (MP3 format)
- 📊 Multiple video quality options (best, 720p, 480p, 360p, 240p)
- 📂 Custom output directory support
- 📋 Video information display before downloading

### Advanced Queue Management
- 📋 **Multiple Concurrent Downloads** - Download up to 10 videos simultaneously
- 🎯 **Priority Control** - Set priority levels (0-10) for download order
- ⏸️ **Pause/Resume** - Individual task control with pause/resume functionality
- 📊 **Real-time Progress** - Live progress tracking for each download
- 🔄 **Queue Persistence** - Saves and restores queue state between sessions
- 🎛️ **Queue Management** - Visual queue with drag-and-drop reordering

### User Interfaces
- 🖥️ **Advanced GUI** - Professional tabbed interface with queue management
- 💻 **Command Line** - Full-featured CLI with colored output
- 📱 **Responsive Design** - Clean, modern interface

## 📦 Installation

1. **Clone or download this repository**
2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Usage

### Advanced GUI Version (Recommended)

Run the advanced graphical interface:
```bash
python yt_downloader_advanced_gui.py
```

#### GUI Features:
- **Download Tab** - Add new downloads with all configuration options
- **Queue Tab** - Manage active downloads, reorder by priority, pause/resume
- **Settings Tab** - Configure concurrent downloads and other preferences

#### How to Use:
1. **Paste YouTube URL** in the Download tab
2. **Configure options** (quality, priority, audio-only, playlist)
3. **Click "Add to Queue"** - download starts automatically
4. **Switch to Queue tab** to manage downloads
5. **Use controls** to pause, resume, remove, or change priority

### Command Line Version

#### Basic Usage:
```bash
# Download a video with best quality
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Download with specific quality
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --quality 720p

# Download audio only (MP3)
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only

# Download entire playlist
python yt_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist

# Show video information only
python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --info
```

#### Command Line Options:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--quality` | `-q` | Video quality: `best`, `worst`, `720p`, `480p`, `360p`, `240p` | `best` |
| `--audio-only` | `-a` | Download audio only (MP3 format) | `False` |
| `--playlist` | `-p` | Download entire playlist | `False` |
| `--output` | `-o` | Output directory | `./downloads` |
| `--info` | `-i` | Show video information only | `False` |

## 📁 Project Structure

```
YTDownloader/
├── yt_downloader_advanced_gui.py  # Advanced GUI with queue management
├── yt_downloader.py               # Command-line version
├── utils/                         # Core functionality modules
│   ├── download_task.py          # Individual download task management
│   ├── download_queue.py         # Queue management with threading
│   └── queue_persistence.py      # Save/load queue state
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## ⚙️ Advanced Features

### Priority System
- **Higher numbers = Higher priority** (0-10)
- Downloads with higher priority start first
- Change priority even while in queue
- Automatic queue reordering

### Concurrent Downloads
- **Configurable limits** (1-10 concurrent downloads)
- **Automatic queue processing** - starts next download when one completes
- **Thread-safe operations** for reliable concurrent downloads

### Queue Management
- **Visual queue display** with real-time updates
- **Individual task controls** - pause, resume, remove, change priority
- **Global controls** - pause all, resume all, clear completed
- **Queue statistics** - see active, queued, paused, completed, and error counts

### Queue Persistence
- **Automatic saving** - queue state saved between sessions
- **Graceful restoration** - resumes interrupted downloads
- **Error handling** - handles corrupted queue files

## 🔧 Requirements

- **Python 3.7+**
- **yt-dlp** - YouTube downloading library
- **colorama** - Colored terminal output (CLI only)

## 🐛 Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   # Make sure you're in the project directory
   cd YTDownloader
   python yt_downloader_advanced_gui.py
   ```

2. **yt-dlp not found:**
   ```bash
   pip install yt-dlp
   ```

3. **Permission errors:**
   - Ensure write permissions to output directory
   - Run as administrator if needed (Windows)

4. **Video unavailable:**
   - Check if URL is correct and accessible
   - Some videos may be region-restricted or private

5. **Slow downloads:**
   - Try different quality settings
   - Check internet connection
   - Reduce concurrent download limit

### Getting Help

Run the CLI version with `--help`:
```bash
python yt_downloader.py --help
```

## 📊 Performance

- **Concurrent Downloads**: Up to 10 simultaneous downloads
- **Queue Processing**: Automatic with priority-based ordering
- **Memory Usage**: Minimal - downloads stream directly to disk
- **Thread Safety**: Full thread-safe operations for concurrent downloads

## 📄 License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws when downloading content.

---

## 🆕 What's New

- **Advanced Queue Management** - Professional download queue with priority control
- **Concurrent Downloads** - Download multiple videos simultaneously
- **Pause/Resume** - Full control over individual downloads
- **Queue Persistence** - Saves your download queue between sessions
- **Enhanced GUI** - Modern tabbed interface with real-time progress tracking