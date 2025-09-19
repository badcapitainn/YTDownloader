#!/usr/bin/env python3
"""
Queue Persistence
Save and load download queue state to/from file.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
from .download_task import DownloadTask, TaskStatus
from .download_queue import DownloadQueue

class QueuePersistence:
    """Handle saving and loading of download queue state."""
    
    def __init__(self, save_file: str = "download_queue.json"):
        self.save_file = Path(save_file)
    
    def save_queue(self, queue: DownloadQueue) -> bool:
        """Save queue state to file."""
        try:
            queue_data = {
                'max_concurrent': queue.max_concurrent,
                'tasks': []
            }
            
            for task in queue.get_tasks():
                task_data = {
                    'id': task.id,
                    'url': task.url,
                    'quality': task.quality,
                    'audio_only': task.audio_only,
                    'output_path': str(task.output_path),
                    'playlist': task.playlist,
                    'priority': task.priority,
                    'status': task.status.value,
                    'title': task.title,
                    'duration': task.duration,
                    'created_at': task.created_at
                }
                queue_data['tasks'].append(task_data)
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving queue: {e}")
            return False
    
    def load_queue(self) -> Dict[str, Any]:
        """Load queue state from file."""
        try:
            if not self.save_file.exists():
                return {'max_concurrent': 3, 'tasks': []}
            
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"Error loading queue: {e}")
            return {'max_concurrent': 3, 'tasks': []}
    
    def restore_queue(self) -> DownloadQueue:
        """Restore queue from saved state."""
        data = self.load_queue()
        queue = DownloadQueue(max_concurrent=data.get('max_concurrent', 3))
        
        for task_data in data.get('tasks', []):
            # Only restore queued, paused, or error tasks
            status = task_data.get('status', 'queued')
            if status in ['queued', 'paused', 'error']:
                task = DownloadTask(
                    url=task_data['url'],
                    quality=task_data.get('quality', 'best'),
                    audio_only=task_data.get('audio_only', False),
                    output_path=Path(task_data.get('output_path', 'downloads')),
                    playlist=task_data.get('playlist', False)
                )
                
                task.id = task_data['id']
                task.set_priority(task_data.get('priority', 0))
                task.title = task_data.get('title', 'Unknown')
                task.duration = task_data.get('duration', 0)
                task.created_at = task_data.get('created_at', 0)
                
                # Set status appropriately
                if status == 'paused':
                    task.status = TaskStatus.PAUSED
                elif status == 'error':
                    task.status = TaskStatus.ERROR
                    task.error_message = "Restored from previous session"
                else:
                    task.status = TaskStatus.QUEUED
                
                queue.add_task(task)
        
        return queue
    
    def clear_saved_queue(self):
        """Clear saved queue file."""
        try:
            if self.save_file.exists():
                self.save_file.unlink()
        except Exception as e:
            print(f"Error clearing saved queue: {e}")
