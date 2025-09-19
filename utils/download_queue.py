#!/usr/bin/env python3
"""
Download Queue Management
Queue system for managing multiple download tasks with priority and concurrency control.
"""

import threading
import time
from typing import List, Optional, Callable
from collections import deque
from .download_task import DownloadTask, TaskStatus

class DownloadQueue:
    """Queue management system for download tasks."""
    
    def __init__(self, max_concurrent: int = 3):
        self.tasks: List[DownloadTask] = []
        self.max_concurrent = max_concurrent
        self.active_downloads = 0
        self._lock = threading.Lock()
        
        # Callbacks
        self.on_task_added: Optional[Callable] = None
        self.on_task_removed: Optional[Callable] = None
        self.on_queue_changed: Optional[Callable] = None
        
    def add_task(self, task: DownloadTask) -> bool:
        """Add a task to the queue."""
        with self._lock:
            self.tasks.append(task)
            task.on_status_change = self._on_task_status_change
            self._sort_by_priority()
            
            if self.on_task_added:
                self.on_task_added(task)
            if self.on_queue_changed:
                self.on_queue_changed()
            
            # Start download if we have capacity
            self._start_next_download()
            return True
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the queue."""
        with self._lock:
            for i, task in enumerate(self.tasks):
                if task.id == task_id:
                    task.cancel()
                    self.tasks.pop(i)
                    
                    if self.on_task_removed:
                        self.on_task_removed(task)
                    if self.on_queue_changed:
                        self.on_queue_changed()
                    
                    return True
            return False
    
    def pause_task(self, task_id: str) -> bool:
        """Pause a specific task."""
        with self._lock:
            task = self._find_task(task_id)
            if task:
                task.pause()
                return True
            return False
    
    def resume_task(self, task_id: str) -> bool:
        """Resume a specific task."""
        with self._lock:
            task = self._find_task(task_id)
            if task:
                task.resume()
                self._start_next_download()
                return True
            return False
    
    def set_task_priority(self, task_id: str, priority: int) -> bool:
        """Set priority for a specific task."""
        with self._lock:
            task = self._find_task(task_id)
            if task:
                task.set_priority(priority)
                self._sort_by_priority()
                
                if self.on_queue_changed:
                    self.on_queue_changed()
                return True
            return False
    
    def move_task_up(self, task_id: str) -> bool:
        """Move task up in priority (higher priority number)."""
        with self._lock:
            task = self._find_task(task_id)
            if task and not task.is_active:
                task.set_priority(task.priority + 1)
                self._sort_by_priority()
                
                if self.on_queue_changed:
                    self.on_queue_changed()
                return True
            return False
    
    def move_task_down(self, task_id: str) -> bool:
        """Move task down in priority (lower priority number)."""
        with self._lock:
            task = self._find_task(task_id)
            if task and not task.is_active:
                task.set_priority(max(0, task.priority - 1))
                self._sort_by_priority()
                
                if self.on_queue_changed:
                    self.on_queue_changed()
                return True
            return False
    
    def pause_all(self):
        """Pause all active downloads."""
        with self._lock:
            for task in self.tasks:
                if task.is_active:
                    task.pause()
    
    def resume_all(self):
        """Resume all paused downloads."""
        with self._lock:
            for task in self.tasks:
                if task.is_paused:
                    task.resume()
            self._start_next_download()
    
    def clear_completed(self):
        """Remove all completed tasks from the queue."""
        with self._lock:
            self.tasks = [task for task in self.tasks if not task.is_completed]
            
            if self.on_queue_changed:
                self.on_queue_changed()
    
    def clear_all(self):
        """Clear all tasks from the queue."""
        with self._lock:
            for task in self.tasks:
                task.cancel()
            self.tasks.clear()
            self.active_downloads = 0
            
            if self.on_queue_changed:
                self.on_queue_changed()
    
    def get_tasks(self) -> List[DownloadTask]:
        """Get all tasks in the queue."""
        with self._lock:
            return self.tasks.copy()
    
    def get_active_tasks(self) -> List[DownloadTask]:
        """Get all currently active (downloading) tasks."""
        with self._lock:
            return [task for task in self.tasks if task.is_active]
    
    def get_queued_tasks(self) -> List[DownloadTask]:
        """Get all queued tasks."""
        with self._lock:
            return [task for task in self.tasks if task.status == TaskStatus.QUEUED]
    
    def get_paused_tasks(self) -> List[DownloadTask]:
        """Get all paused tasks."""
        with self._lock:
            return [task for task in self.tasks if task.is_paused]
    
    def _find_task(self, task_id: str) -> Optional[DownloadTask]:
        """Find a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def _sort_by_priority(self):
        """Sort tasks by priority (highest first)."""
        # Keep active downloads at the top, then sort by priority
        self.tasks.sort(key=lambda t: (not t.is_active, -t.priority))
    
    def _start_next_download(self):
        """Start the next queued download if we have capacity."""
        if self.active_downloads >= self.max_concurrent:
            return
        
        # Find next queued task
        next_task = None
        for task in self.tasks:
            if task.status == TaskStatus.QUEUED:
                next_task = task
                break
        
        if next_task:
            self._start_download(next_task)
    
    def _start_download(self, task: DownloadTask):
        """Start downloading a specific task."""
        if task.status != TaskStatus.QUEUED:
            return
        
        task.status = TaskStatus.DOWNLOADING
        self.active_downloads += 1
        
        # Start download in a separate thread
        thread = threading.Thread(target=self._download_worker, args=(task,))
        thread.daemon = True
        thread.start()
        task._thread = thread
        
        if self.on_queue_changed:
            self.on_queue_changed()
    
    def _download_worker(self, task: DownloadTask):
        """Worker thread for downloading a task."""
        try:
            # Import here to avoid circular imports
            import yt_dlp
            
            # Configure yt-dlp options
            ydl_opts = self._get_ydl_options(task)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                task._ydl_instance = ydl
                ydl.download([task.url])
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.status = TaskStatus.ERROR
            task.error_message = str(e)
            
        finally:
            with self._lock:
                self.active_downloads -= 1
                task._ydl_instance = None
                
                # Start next download
                self._start_next_download()
                
                if self.on_queue_changed:
                    self.on_queue_changed()
    
    def _get_ydl_options(self, task: DownloadTask) -> dict:
        """Get yt-dlp options for a task."""
        options = {
            'outtmpl': str(task.output_path / '%(title)s.%(ext)s'),
            'progress_hooks': [task._progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        # Set format based on options
        if task.audio_only:
            options['format'] = 'bestaudio/best'
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            if task.quality == 'best':
                options['format'] = 'best[height<=1080]/best'
            elif task.quality == 'worst':
                options['format'] = 'worst'
            else:
                options['format'] = f'best[height<={task.quality.replace("p", "")}]/best'
        
        # Handle playlists
        if task.playlist:
            options['outtmpl'] = str(task.output_path / '%(playlist_title)s' / '%(title)s.%(ext)s')
        else:
            options['noplaylist'] = True
        
        return options
    
    def _on_task_status_change(self, task: DownloadTask):
        """Handle task status changes."""
        with self._lock:
            if self.on_queue_changed:
                self.on_queue_changed()
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        with self._lock:
            stats = {
                'total': len(self.tasks),
                'active': self.active_downloads,
                'queued': len([t for t in self.tasks if t.status == TaskStatus.QUEUED]),
                'paused': len([t for t in self.tasks if t.is_paused]),
                'completed': len([t for t in self.tasks if t.is_completed]),
                'error': len([t for t in self.tasks if t.status == TaskStatus.ERROR]),
                'max_concurrent': self.max_concurrent
            }
            return stats
