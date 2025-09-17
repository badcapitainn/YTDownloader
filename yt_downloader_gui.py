#!/usr/bin/env python3
"""
YouTube Video Downloader GUI
A graphical user interface for downloading YouTube videos and playlists.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import yt_dlp

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set default download path
        self.download_path = Path.cwd() / "downloads"
        self.download_path.mkdir(exist_ok=True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.output_var = tk.StringVar(value=str(self.download_path))
        self.audio_only_var = tk.BooleanVar()
        self.playlist_var = tk.BooleanVar()
        
        # Download status
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="YouTube Video Downloader", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="YouTube URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Quality selection
        ttk.Label(main_frame, text="Quality:").grid(row=2, column=0, sticky=tk.W, pady=5)
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, 
                                   values=["best", "worst", "720p", "480p", "360p", "240p"],
                                   state="readonly", width=15)
        quality_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Audio only checkbox
        audio_check = ttk.Checkbutton(options_frame, text="Audio Only (MP3)", 
                                    variable=self.audio_only_var)
        audio_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Playlist checkbox
        playlist_check = ttk.Checkbutton(options_frame, text="Download Playlist", 
                                       variable=self.playlist_var)
        playlist_check.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(20, 0))
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=50)
        output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        browse_btn = ttk.Button(main_frame, text="Browse", command=self.browse_directory)
        browse_btn.grid(row=4, column=2, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Info button
        info_btn = ttk.Button(buttons_frame, text="Get Video Info", 
                             command=self.get_video_info_threaded)
        info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Download button
        self.download_btn = ttk.Button(buttons_frame, text="Download", 
                                      command=self.download_threaded)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Video info display
        info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="10")
        info_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=70, 
                                                  state=tk.DISABLED)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(8, weight=1)
        
    def browse_directory(self):
        """Open directory browser for output path."""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
            self.download_path = Path(directory)
    
    def clear_all(self):
        """Clear all input fields."""
        self.url_var.set("")
        self.output_var.set(str(Path.cwd() / "downloads"))
        self.download_path = Path.cwd() / "downloads"
        self.audio_only_var.set(False)
        self.playlist_var.set(False)
        self.quality_var.set("best")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
        self.status_var.set("Ready")
        self.progress_var.set(0)
    
    def validate_url(self):
        """Validate YouTube URL."""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return False
        
        if not ('youtube.com' in url or 'youtu.be' in url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return False
        
        return True
    
    def get_video_info_threaded(self):
        """Get video info in a separate thread."""
        if not self.validate_url():
            return
        
        if self.is_downloading:
            messagebox.showwarning("Warning", "Please wait for current operation to complete")
            return
        
        thread = threading.Thread(target=self.get_video_info)
        thread.daemon = True
        thread.start()
    
    def get_video_info(self):
        """Get and display video information."""
        try:
            self.status_var.set("Getting video information...")
            self.root.update()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url_var.get(), download=False)
                
                if info:
                    self.display_video_info(info)
                    self.status_var.set("Video information retrieved successfully")
                else:
                    self.status_var.set("Failed to get video information")
                    
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to get video information:\n{str(e)}")
    
    def display_video_info(self, info):
        """Display video information in the text area."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info_text = "=" * 60 + "\n"
        info_text += "VIDEO INFORMATION\n"
        info_text += "=" * 60 + "\n\n"
        
        if 'title' in info:
            info_text += f"Title: {info['title']}\n\n"
        
        if 'uploader' in info:
            info_text += f"Channel: {info['uploader']}\n\n"
        
        if 'duration' in info:
            duration = info['duration']
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                info_text += f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}\n\n"
            else:
                info_text += f"Duration: {minutes:02d}:{seconds:02d}\n\n"
        
        if 'view_count' in info:
            views = info['view_count']
            if views >= 1000000:
                info_text += f"Views: {views/1000000:.1f}M\n\n"
            elif views >= 1000:
                info_text += f"Views: {views/1000:.1f}K\n\n"
            else:
                info_text += f"Views: {views}\n\n"
        
        if 'upload_date' in info:
            upload_date = info['upload_date']
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
            info_text += f"Upload Date: {formatted_date}\n\n"
        
        if 'description' in info:
            description = info['description'][:200] + "..." if len(info['description']) > 200 else info['description']
            info_text += f"Description: {description}\n\n"
        
        info_text += "=" * 60
        
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def download_threaded(self):
        """Start download in a separate thread."""
        if not self.validate_url():
            return
        
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        # Update output path
        self.download_path = Path(self.output_var.get())
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        thread.start()
    
    def download_video(self):
        """Download the video."""
        try:
            self.is_downloading = True
            self.download_btn.config(state=tk.DISABLED)
            self.status_var.set("Starting download...")
            self.progress_var.set(0)
            self.root.update()
            
            # Configure download options
            ydl_opts = {
                'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            # Set format based on options
            if self.audio_only_var.get():
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                quality = self.quality_var.get()
                if quality == 'best':
                    ydl_opts['format'] = 'best[height<=1080]/best'
                elif quality == 'worst':
                    ydl_opts['format'] = 'worst'
                else:
                    ydl_opts['format'] = f'best[height<={quality.replace("p", "")}]/best'
            
            # Handle playlists
            if self.playlist_var.get():
                ydl_opts['outtmpl'] = str(self.download_path / '%(playlist_title)s' / '%(title)s.%(ext)s')
            else:
                ydl_opts['noplaylist'] = True
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url_var.get()])
                
            self.status_var.set("Download completed successfully!")
            self.progress_var.set(100)
            messagebox.showinfo("Success", f"Download completed!\nFiles saved to: {self.download_path}")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Download failed:\n{str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.config(state=tk.NORMAL)
    
    def progress_hook(self, d):
        """Progress hook for download status updates."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            # Extract percentage number
            try:
                percent_num = float(percent.replace('%', ''))
                self.progress_var.set(percent_num)
            except:
                pass
            
            self.status_var.set(f"Downloading: {percent} at {speed} ETA: {eta}")
            
        elif d['status'] == 'finished':
            self.status_var.set(f"Processing: {d['filename']}")
        
        self.root.update()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
