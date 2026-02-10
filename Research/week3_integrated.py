#!/usr/bin/env python3
"""
Week 3 - Integrated System
Combines monitoring, database, hash, and entropy
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, init

from week3_database import FileDatabase
from week3_hash_calculator import calculate_hash, get_file_size
from week3_entropy_analyzer import calculate_entropy, is_encrypted

init(autoreset=True)

class IntegratedMonitor(FileSystemEventHandler):
    def __init__(self, db):
        self.db = db
    
    def process_file(self, filepath, event_type):
        """Process file event"""
        if not os.path.exists(filepath):
            # File deleted
            self.db.log_event(filepath, event_type)
            print(f"{Fore.RED}[{event_type}] {filepath}")
            return
        
        # Get file info
        file_hash = calculate_hash(filepath)
        file_size = get_file_size(filepath)
        entropy = calculate_entropy(filepath)
        
        # Check if encrypted
        encrypted = is_encrypted(entropy)
        
        # Get previous state
        prev_state = self.db.get_file(filepath)
        hash_before = prev_state[2] if prev_state else None
        entropy_before = prev_state[4] if prev_state else None
        
        # Update database
        self.db.add_file(filepath, file_hash, file_size, entropy)
        self.db.log_event(filepath, event_type, hash_before, file_hash, 
                         entropy_before, entropy)
        
        # Display
        color = Fore.RED if encrypted else Fore.GREEN
        print(f"{color}[{event_type}] {filepath}")
        print(f"  Hash: {file_hash[:16]}...")
        print(f"  Size: {file_size} bytes")
        print(f"  Entropy: {entropy:.2f}")
        
        if encrypted:
            print(f"{Fore.RED}  ⚠️  POSSIBLE ENCRYPTION DETECTED!")
    
    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, 'CREATE')
    
    def on_modified(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, 'MODIFY')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, 'DELETE')

def monitor_with_protection(folder_path, db_path='file_tracking.db'):
    """Monitor folder with full protection"""
    db = FileDatabase(db_path)
    
    event_handler = IntegratedMonitor(db)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Anti-Ransomware Protection Active")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Monitoring: {folder_path}")
    print(f"{Fore.CYAN}Database: {db_path}")
    print(f"{Fore.CYAN}Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n{Fore.YELLOW}Stopping monitor...")
    
    observer.join()
    db.close()
    print(f"{Fore.GREEN}Monitor stopped.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week3_integrated.py <folder_path>")
        sys.exit(1)
    
    folder = sys.argv[1]
    monitor_with_protection(folder)
