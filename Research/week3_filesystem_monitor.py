#!/usr/bin/env python3
"""
Week 3 - Task 1: Filesystem Monitoring
Monitors folder for file changes (create, modify, delete)
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, init

init(autoreset=True)

class FileMonitor(FileSystemEventHandler):
    def __init__(self, callback=None):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            print(f"{Fore.GREEN}[CREATE] {event.src_path}")
            if self.callback:
                self.callback('CREATE', event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"{Fore.YELLOW}[MODIFY] {event.src_path}")
            if self.callback:
                self.callback('MODIFY', event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f"{Fore.RED}[DELETE] {event.src_path}")
            if self.callback:
                self.callback('DELETE', event.src_path)

def monitor_folder(path, callback=None):
    """Monitor folder for changes"""
    event_handler = FileMonitor(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print(f"{Fore.CYAN}Monitoring: {path}")
    print(f"{Fore.CYAN}Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week3_filesystem_monitor.py <folder_path>")
        sys.exit(1)
    
    folder = sys.argv[1]
    monitor_folder(folder)
