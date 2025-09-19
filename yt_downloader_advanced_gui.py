#!/usr/bin/env python3
"""
Advanced YouTube Video Downloader GUI
Enhanced GUI with download queue management, priority control, and pause/resume functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from utils.download_task import DownloadTask, TaskStatus
from utils.download_queue import DownloadQueue

class AdvancedYouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader - Advanced")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Initialize download queue
        self.download_queue = DownloadQueue(max_concurrent=3)
        self.download_queue.on_task_added = self.on_task_added
        self.download_queue.on_task_removed = self.on_task_removed
        self.download_queue.on_queue_changed = self.on_queue_changed
        
        # Set default download path
        self.download_path = Path.cwd() / "downloads"
        self.download_path.mkdir(exist_ok=True)
        
        # Variables
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="best")
        self.output_var = tk.StringVar(value=str(self.download_path))
        self.audio_only_var = tk.BooleanVar()
        self.playlist_var = tk.BooleanVar()
        self.priority_var = tk.IntVar(value=0)
        
        # Queue display variables
        self.queue_tree = None
        self.queue_stats_var = tk.StringVar(value="Queue: 0 tasks")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the enhanced user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Download tab
        self.setup_download_tab(notebook)
        
        # Queue tab
        self.setup_queue_tab(notebook)
        
        # Settings tab
        self.setup_settings_tab(notebook)
        
    def setup_download_tab(self, notebook):
        """Setup the download configuration tab."""
        download_frame = ttk.Frame(notebook)
        notebook.add(download_frame, text="Download")
        
        # Main frame
        main_frame = ttk.Frame(download_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add New Download", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="YouTube URL:").pack(side=tk.LEFT)
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=80)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Quality selection
        quality_frame = ttk.Frame(options_frame)
        quality_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                   values=["best", "worst", "720p", "480p", "360p", "240p"],
                                   state="readonly", width=15)
        quality_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Priority selection
        ttk.Label(quality_frame, text="Priority:").pack(side=tk.LEFT)
        priority_spin = ttk.Spinbox(quality_frame, from_=0, to=10, 
                                   textvariable=self.priority_var, width=5)
        priority_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Checkboxes
        checkbox_frame = ttk.Frame(options_frame)
        checkbox_frame.pack(fill=tk.X, pady=5)
        
        audio_check = ttk.Checkbutton(checkbox_frame, text="Audio Only (MP3)", 
                                    variable=self.audio_only_var)
        audio_check.pack(side=tk.LEFT)
        
        playlist_check = ttk.Checkbutton(checkbox_frame, text="Download Playlist", 
                                       variable=self.playlist_var)
        playlist_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Output directory
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Add to queue button
        add_btn = ttk.Button(buttons_frame, text="Add to Queue", 
                           command=self.add_to_queue)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Get info button
        info_btn = ttk.Button(buttons_frame, text="Get Video Info", 
                             command=self.get_video_info_threaded)
        info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_btn = ttk.Button(buttons_frame, text="Clear", command=self.clear_all)
        clear_btn.pack(side=tk.LEFT)
        
        # Video info display
        info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=70, 
                                                  state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_queue_tab(self, notebook):
        """Setup the download queue management tab."""
        queue_frame = ttk.Frame(notebook)
        notebook.add(queue_frame, text="Download Queue")
        
        # Queue controls frame
        controls_frame = ttk.Frame(queue_frame, padding="10")
        controls_frame.pack(fill=tk.X)
        
        # Queue stats
        stats_label = ttk.Label(controls_frame, textvariable=self.queue_stats_var, 
                               font=("Arial", 10, "bold"))
        stats_label.pack(side=tk.LEFT)
        
        # Queue control buttons
        queue_buttons = ttk.Frame(controls_frame)
        queue_buttons.pack(side=tk.RIGHT)
        
        pause_all_btn = ttk.Button(queue_buttons, text="Pause All", 
                                  command=self.download_queue.pause_all)
        pause_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        resume_all_btn = ttk.Button(queue_buttons, text="Resume All", 
                                   command=self.download_queue.resume_all)
        resume_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_completed_btn = ttk.Button(queue_buttons, text="Clear Completed", 
                                        command=self.download_queue.clear_completed)
        clear_completed_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_all_btn = ttk.Button(queue_buttons, text="Clear All", 
                                  command=self.clear_queue)
        clear_all_btn.pack(side=tk.LEFT)
        
        # Queue display
        queue_display_frame = ttk.Frame(queue_frame, padding="10")
        queue_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for queue
        columns = ('ID', 'Title', 'Status', 'Progress', 'Speed', 'ETA', 'Priority')
        self.queue_tree = ttk.Treeview(queue_display_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.queue_tree.heading('ID', text='ID')
        self.queue_tree.heading('Title', text='Title')
        self.queue_tree.heading('Status', text='Status')
        self.queue_tree.heading('Progress', text='Progress')
        self.queue_tree.heading('Speed', text='Speed')
        self.queue_tree.heading('ETA', text='ETA')
        self.queue_tree.heading('Priority', text='Priority')
        
        self.queue_tree.column('ID', width=80)
        self.queue_tree.column('Title', width=300)
        self.queue_tree.column('Status', width=100)
        self.queue_tree.column('Progress', width=100)
        self.queue_tree.column('Speed', width=100)
        self.queue_tree.column('ETA', width=100)
        self.queue_tree.column('Priority', width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(queue_display_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        h_scrollbar = ttk.Scrollbar(queue_display_frame, orient=tk.HORIZONTAL, command=self.queue_tree.xview)
        self.queue_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Task control frame
        task_controls_frame = ttk.Frame(queue_frame, padding="10")
        task_controls_frame.pack(fill=tk.X)
        
        ttk.Label(task_controls_frame, text="Selected Task Controls:").pack(side=tk.LEFT)
        
        pause_btn = ttk.Button(task_controls_frame, text="Pause", command=self.pause_selected_task)
        pause_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        resume_btn = ttk.Button(task_controls_frame, text="Resume", command=self.resume_selected_task)
        resume_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(task_controls_frame, text="Remove", command=self.remove_selected_task)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        up_btn = ttk.Button(task_controls_frame, text="↑ Priority", command=self.move_task_up)
        up_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        down_btn = ttk.Button(task_controls_frame, text="↓ Priority", command=self.move_task_down)
        down_btn.pack(side=tk.LEFT)
        
        # Bind selection event
        self.queue_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        
    def setup_settings_tab(self, notebook):
        """Setup the settings tab."""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        main_frame = ttk.Frame(settings_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Concurrent downloads setting
        concurrent_frame = ttk.LabelFrame(main_frame, text="Download Settings", padding="10")
        concurrent_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(concurrent_frame, text="Max Concurrent Downloads:").pack(side=tk.LEFT)
        concurrent_var = tk.IntVar(value=self.download_queue.max_concurrent)
        concurrent_spin = ttk.Spinbox(concurrent_frame, from_=1, to=10, 
                                     textvariable=concurrent_var, width=5,
                                     command=lambda: self.set_max_concurrent(concurrent_var.get()))
        concurrent_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save settings button
        save_btn = ttk.Button(main_frame, text="Save Settings", 
                             command=lambda: self.save_settings(concurrent_var.get()))
        save_btn.pack(pady=20)
        
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
        self.priority_var.set(0)
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
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
        
        thread = threading.Thread(target=self.get_video_info)
        thread.daemon = True
        thread.start()
    
    def get_video_info(self):
        """Get and display video information."""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url_var.get(), download=False)
                
                if info:
                    self.display_video_info(info)
                else:
                    self.info_text.config(state=tk.NORMAL)
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, "Failed to get video information")
                    self.info_text.config(state=tk.DISABLED)
                    
        except Exception as e:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"Error: {str(e)}")
            self.info_text.config(state=tk.DISABLED)
    
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
    
    def add_to_queue(self):
        """Add current download to queue."""
        if not self.validate_url():
            return
        
        # Update output path
        self.download_path = Path(self.output_var.get())
        self.download_path.mkdir(parents=True, exist_ok=True)
        
        # Create download task
        task = DownloadTask(
            url=self.url_var.get(),
            quality=self.quality_var.get(),
            audio_only=self.audio_only_var.get(),
            output_path=self.download_path,
            playlist=self.playlist_var.get()
        )
        task.set_priority(self.priority_var.get())
        
        # Add to queue
        self.download_queue.add_task(task)
        
        messagebox.showinfo("Success", "Download added to queue!")
        
        # Clear URL field for next entry
        self.url_var.set("")
    
    def on_task_added(self, task):
        """Callback when a task is added to queue."""
        pass
    
    def on_task_removed(self, task):
        """Callback when a task is removed from queue."""
        pass
    
    def on_queue_changed(self):
        """Callback when queue changes."""
        self.update_queue_display()
        self.update_queue_stats()
    
    def update_queue_display(self):
        """Update the queue treeview display."""
        # Clear existing items
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        
        # Add all tasks
        for task in self.download_queue.get_tasks():
            info = task.get_display_info()
            status_color = self.get_status_color(task.status)
            
            item = self.queue_tree.insert('', 'end', values=(
                info['id'],
                info['title'],
                info['status'],
                f"{info['progress']:.1f}%",
                info['speed'],
                info['eta'],
                info['priority']
            ))
            
            # Color code based on status
            if status_color:
                self.queue_tree.set(item, 'Status', info['status'])
    
    def update_queue_stats(self):
        """Update queue statistics display."""
        stats = self.download_queue.get_queue_stats()
        self.queue_stats_var.set(
            f"Queue: {stats['total']} total | "
            f"{stats['active']} active | "
            f"{stats['queued']} queued | "
            f"{stats['paused']} paused | "
            f"{stats['completed']} completed | "
            f"{stats['error']} errors"
        )
    
    def get_status_color(self, status):
        """Get color for status display."""
        colors = {
            TaskStatus.QUEUED: 'blue',
            TaskStatus.DOWNLOADING: 'green',
            TaskStatus.PAUSED: 'orange',
            TaskStatus.COMPLETED: 'darkgreen',
            TaskStatus.ERROR: 'red',
            TaskStatus.CANCELLED: 'gray'
        }
        return colors.get(status, 'black')
    
    def on_task_select(self, event):
        """Handle task selection in queue."""
        selection = self.queue_tree.selection()
        if selection:
            item = selection[0]
            values = self.queue_tree.item(item, 'values')
            if values:
                self.selected_task_id = values[0]
    
    def pause_selected_task(self):
        """Pause the selected task."""
        if hasattr(self, 'selected_task_id'):
            self.download_queue.pause_task(self.selected_task_id)
    
    def resume_selected_task(self):
        """Resume the selected task."""
        if hasattr(self, 'selected_task_id'):
            self.download_queue.resume_task(self.selected_task_id)
    
    def remove_selected_task(self):
        """Remove the selected task."""
        if hasattr(self, 'selected_task_id'):
            if messagebox.askyesno("Confirm", "Remove this download from queue?"):
                self.download_queue.remove_task(self.selected_task_id)
    
    def move_task_up(self):
        """Move selected task up in priority."""
        if hasattr(self, 'selected_task_id'):
            self.download_queue.move_task_up(self.selected_task_id)
    
    def move_task_down(self):
        """Move selected task down in priority."""
        if hasattr(self, 'selected_task_id'):
            self.download_queue.move_task_down(self.selected_task_id)
    
    def clear_queue(self):
        """Clear all tasks from queue."""
        if messagebox.askyesno("Confirm", "Clear all downloads from queue?"):
            self.download_queue.clear_all()
    
    def set_max_concurrent(self, value):
        """Set maximum concurrent downloads."""
        self.download_queue.max_concurrent = value
    
    def save_settings(self, max_concurrent):
        """Save application settings."""
        self.download_queue.max_concurrent = max_concurrent
        messagebox.showinfo("Settings", "Settings saved successfully!")

def main():
    root = tk.Tk()
    app = AdvancedYouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
