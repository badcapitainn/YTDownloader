#!/usr/bin/env python3
"""
YouTube Video Downloader
A command-line tool to download YouTube videos and playlists using yt-dlp.
"""

import argparse
import os
import sys
from pathlib import Path
from colorama import init, Fore, Style

import yt_dlp

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class YouTubeDownloader:
    def __init__(self):
        self.download_path = Path.cwd() / "downloads"
        self.download_path.mkdir(exist_ok=True)
    
    def progress_hook(self, d):
        """Progress hook for download status updates."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\r{Fore.CYAN}Downloading: {percent} at {speed} ETA: {eta}", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\n{Fore.GREEN}✓ Download completed: {d['filename']}")
    
    def get_video_info(self, url):
        """Get video information without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info
            except Exception as e:
                print(f"{Fore.RED}Error getting video info: {e}")
                return None
    
    def download_video(self, url, quality='best', audio_only=False, playlist=False):
        """Download a single video or playlist."""
        # Configure download options
        ydl_opts = {
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }
        
        # Set format based on options
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if quality == 'best':
                ydl_opts['format'] = 'best[height<=1080]/best'
            elif quality == 'worst':
                ydl_opts['format'] = 'worst'
            else:
                # Custom quality (e.g., '720p', '480p')
                ydl_opts['format'] = f'best[height<={quality.replace("p", "")}]/best'
        
        # Handle playlists
        if playlist:
            ydl_opts['outtmpl'] = str(self.download_path / '%(playlist_title)s' / '%(title)s.%(ext)s')
        else:
            # Don't download playlists if not requested
            ydl_opts['noplaylist'] = True
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = self.get_video_info(url)
                if not info:
                    return False
                
                # Display video information
                self.display_video_info(info)
                
                # Download the video
                print(f"\n{Fore.YELLOW}Starting download...")
                ydl.download([url])
                print(f"\n{Fore.GREEN}✓ Download completed successfully!")
                print(f"{Fore.CYAN}Files saved to: {self.download_path}")
                return True
                
        except Exception as e:
            print(f"\n{Fore.RED}Error downloading video: {e}")
            return False
    
    def display_video_info(self, info):
        """Display video information."""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}Video Information")
        print(f"{Fore.MAGENTA}{'='*60}")
        
        if 'title' in info:
            print(f"{Fore.WHITE}Title: {info['title']}")
        
        if 'uploader' in info:
            print(f"{Fore.WHITE}Channel: {info['uploader']}")
        
        if 'duration' in info:
            duration = info['duration']
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                print(f"{Fore.WHITE}Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                print(f"{Fore.WHITE}Duration: {minutes:02d}:{seconds:02d}")
        
        if 'view_count' in info:
            views = info['view_count']
            if views >= 1000000:
                print(f"{Fore.WHITE}Views: {views/1000000:.1f}M")
            elif views >= 1000:
                print(f"{Fore.WHITE}Views: {views/1000:.1f}K")
            else:
                print(f"{Fore.WHITE}Views: {views}")
        
        if 'upload_date' in info:
            upload_date = info['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            print(f"{Fore.WHITE}Upload Date: {formatted_date}")
        
        print(f"{Fore.MAGENTA}{'='*60}")

def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos and playlists",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
  python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --quality 720p
  python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
  python yt_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" --playlist
  python yt_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" --output "C:/Downloads"
        """
    )
    
    parser.add_argument('url', help='YouTube video or playlist URL')
    parser.add_argument(
        '--quality', '-q',
        choices=['best', 'worst', '720p', '480p', '360p', '240p'],
        default='best',
        help='Video quality (default: best)'
    )
    parser.add_argument(
        '--audio-only', '-a',
        action='store_true',
        help='Download audio only (MP3 format)'
    )
    parser.add_argument(
        '--playlist', '-p',
        action='store_true',
        help='Download entire playlist'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory (default: ./downloads)'
    )
    parser.add_argument(
        '--info', '-i',
        action='store_true',
        help='Show video information only (no download)'
    )
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = YouTubeDownloader()
    
    # Set custom output directory if specified
    if args.output:
        downloader.download_path = Path(args.output)
        downloader.download_path.mkdir(parents=True, exist_ok=True)
    
    # Show info only
    if args.info:
        print(f"{Fore.CYAN}Getting video information...")
        info = downloader.get_video_info(args.url)
        if info:
            downloader.display_video_info(info)
        return
    
    # Validate URL
    if not ('youtube.com' in args.url or 'youtu.be' in args.url):
        print(f"{Fore.RED}Error: Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Download video
    success = downloader.download_video(
        url=args.url,
        quality=args.quality,
        audio_only=args.audio_only,
        playlist=args.playlist
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
