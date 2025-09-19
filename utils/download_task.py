#!/usr/bin/env python3
"""
Download Task Management
Individual download task with state management and control.
"""

import uuid
import threading
import time
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable

class TaskStatus(Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class DownloadProgress:
    """Download progress information."""
    percentage: float = 0.0
    speed: str = "N/A"
    eta: str = "N/A"
    downloaded_bytes: int = 0
    total_bytes: int = 0

class DownloadTask:
    """Individual download task with full state management."""
    
    def __init__(self, url: str, quality: str = "best", audio_only: bool = False, 
                 output_path: Path = None, playlist: bool = False):
        self.id = str(uuid.uuid4())[:8]  # Short ID for display
        self.url = url
        self.quality = quality
        self.audio_only = audio_only
        self.output_path = output_path or Path.cwd() / "downloads"
        self.playlist = playlist
        
        # State management
        self.status = TaskStatus.QUEUED
        self.progress = DownloadProgress()
        self.priority = 0  # Higher number = higher priority
        self.error_message = None
        
        # Control mechanisms
        self._paused = threading.Event()
        self._cancelled = threading.Event()
        self._thread = None
        self._ydl_instance = None
        
        # Callbacks
        self.on_progress: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Metadata
        self.title = "Unknown"
        self.duration = 0
        self.file_size = 0
        self.created_at = time.time()
        
    @property
    def is_active(self) -> bool:
        """Check if task is currently active (downloading)."""
        return self.status == TaskStatus.DOWNLOADING
    
    @property
    def is_paused(self) -> bool:
        """Check if task is paused."""
        return self.status == TaskStatus.PAUSED
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_finished(self) -> bool:
        """Check if task is finished (completed, error, or cancelled)."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED]
    
    def pause(self):
        """Pause the download."""
        if self.status == TaskStatus.DOWNLOADING:
            self.status = TaskStatus.PAUSED
            self._paused.set()
            self._notify_status_change()
    
    def resume(self):
        """Resume the download."""
        if self.status == TaskStatus.PAUSED:
            self.status = TaskStatus.QUEUED
            self._paused.clear()
            self._notify_status_change()
    
    def cancel(self):
        """Cancel the download."""
        self.status = TaskStatus.CANCELLED
        self._cancelled.set()
        self._paused.set()
        if self._ydl_instance:
            # Note: yt-dlp doesn't have direct cancel method
            # We'll rely on the cancelled event
            pass
        self._notify_status_change()
    
    def set_priority(self, priority: int):
        """Set task priority (higher number = higher priority)."""
        self.priority = priority
    
    def _notify_status_change(self):
        """Notify callback of status change."""
        if self.on_status_change:
            self.on_status_change(self)
    
    def _notify_progress(self, progress_data: dict):
        """Update progress and notify callback."""
        if progress_data.get('status') == 'downloading':
            percent_str = progress_data.get('_percent_str', '0%')
            try:
                self.progress.percentage = float(percent_str.replace('%', ''))
            except:
                pass
            
            self.progress.speed = progress_data.get('_speed_str', 'N/A')
            self.progress.eta = progress_data.get('_eta_str', 'N/A')
            
            if self.on_progress:
                self.on_progress(self)
        
        elif progress_data.get('status') == 'finished':
            self.progress.percentage = 100.0
            if self.on_progress:
                self.on_progress(self)
    
    def _progress_hook(self, d):
        """Progress hook for yt-dlp."""
        # Check if cancelled
        if self._cancelled.is_set():
            return
        
        # Handle pause
        if self._paused.is_set() and self.status == TaskStatus.DOWNLOADING:
            # Wait for resume
            while self._paused.is_set() and not self._cancelled.is_set():
                time.sleep(0.1)
            
            if self._cancelled.is_set():
                return
        
        self._notify_progress(d)
    
    def get_display_info(self) -> dict:
        """Get information for display in UI."""
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status.value,
            'progress': self.progress.percentage,
            'speed': self.progress.speed,
            'eta': self.progress.eta,
            'priority': self.priority,
            'quality': self.quality,
            'audio_only': self.audio_only,
            'error': self.error_message
        }
