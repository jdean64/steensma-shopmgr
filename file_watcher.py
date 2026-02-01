#!/usr/bin/env python3
"""
File Watcher for Steensma Shop Manager
Watches the datasheets directory for new Excel files and processes them
"""
import os
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = '/home/ubuntu/shopmgr/datasheets'
ARCHIVE_DIR = '/home/ubuntu/shopmgr/archive'
HISTORY_FILE = '/home/ubuntu/shopmgr/daily_history.json'

class DataFileHandler(FileSystemEventHandler):
    """Handle file system events for Excel files"""
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        
        # Check if it's one of our target files
        if any(pattern in filename for pattern in ['Shop Schedule', 'Open Back Orders', 'Gross Profit']):
            print(f"[{datetime.now()}] New file detected: {filename}")
            self.process_file(event.src_path, filename)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        
        if any(pattern in filename for pattern in ['Shop Schedule', 'Open Back Orders', 'Gross Profit']):
            print(f"[{datetime.now()}] File modified: {filename}")
    
    def process_file(self, filepath, filename):
        """Process newly detected file"""
        try:
            # Wait a moment for file to finish writing
            time.sleep(2)
            
            # Create archive directory with date
            today = datetime.now().strftime('%Y-%m-%d')
            archive_subdir = os.path.join(ARCHIVE_DIR, today)
            os.makedirs(archive_subdir, exist_ok=True)
            
            # Copy to archive
            archive_path = os.path.join(archive_subdir, filename)
            shutil.copy2(filepath, archive_path)
            print(f"  → Archived to: {archive_path}")
            
            # TODO: Compare with previous day's data
            # TODO: Send notifications if significant changes
            
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")

def main():
    """Main file watcher loop"""
    print("=" * 60)
    print("Steensma Shop Manager - File Watcher")
    print("=" * 60)
    print(f"Watching directory: {WATCH_DIR}")
    print(f"Archive directory: {ARCHIVE_DIR}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Create directories if they don't exist
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Set up file system observer
    event_handler = DataFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file watcher...")
        observer.stop()
    
    observer.join()
    print("File watcher stopped.")

if __name__ == '__main__':
    main()
