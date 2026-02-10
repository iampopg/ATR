#!/usr/bin/env python3
"""
Anti-Ransomware File Monitor
Cross-platform file monitoring using Watchdog library
Monitors /home/popg/projects/anti-ransomW/Research directory
"""

import os
import time
import hashlib
import math
import platform
import random
import string
from datetime import datetime
from collections import Counter
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class AntiRansomwareHandler(FileSystemEventHandler):
    def __init__(self):
        self.event_count = 0
        self.start_time = time.time()
        self.file_hashes = {}
        self.suspicious_extensions = {'.encrypted', '.locked', '.crypto', '.crypt', '.enc'}
        
    def calculate_entropy(self, file_path):
        """Calculate Shannon entropy of a file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1024)  # Read first 1KB
                
            if not data:
                return 0
                
            # Count byte frequencies
            byte_counts = Counter(data)
            entropy = 0
            
            for count in byte_counts.values():
                probability = count / len(data)
                entropy -= probability * math.log2(probability)
                
            return entropy
        except Exception as e:
            return 0
    
    def get_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]  # First 16 chars
        except:
            return None
    
    def detect_suspicious_activity(self):
        """Basic ransomware detection based on event frequency"""
        current_time = time.time()
        time_window = current_time - self.start_time
        
        if time_window > 0:
            events_per_second = self.event_count / time_window
            
            if events_per_second > 5:  # More than 5 events per second
                print(f"\n{Back.RED}{Fore.WHITE}🚨 SUSPICIOUS ACTIVITY DETECTED!")
                print(f"   Events per second: {events_per_second:.2f}")
                print(f"   Total events: {self.event_count}")
                print(f"   Time window: {time_window:.2f}s{Style.RESET_ALL}\n")
    
    def on_created(self, event):
        if event.is_directory:
            return
            
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        print(f"{Fore.GREEN}✓ [{timestamp}] CREATED: {file_name}")
        
        # Check for suspicious extensions
        if file_ext in self.suspicious_extensions:
            print(f"  {Back.RED}{Fore.WHITE}🚨 RANSOMWARE EXTENSION: {file_ext}{Style.RESET_ALL}")
        
        # Calculate entropy for new files
        entropy = self.calculate_entropy(file_path)
        if entropy > 7.5:  # High entropy indicates encryption
            print(f"  {Back.YELLOW}{Fore.BLACK}⚠️  HIGH ENTROPY: {entropy:.2f} (possible encryption){Style.RESET_ALL}")
        elif entropy > 0:
            print(f"  📊 Entropy: {entropy:.2f}")
        
        # Store hash
        file_hash = self.get_file_hash(file_path)
        if file_hash:
            self.file_hashes[file_path] = file_hash
            print(f"  🔐 Hash: {file_hash}")
        
        self.detect_suspicious_activity()
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        print(f"{Fore.YELLOW}⚠ [{timestamp}] MODIFIED: {file_name}")
        
        # Check if file hash changed
        new_hash = self.get_file_hash(file_path)
        old_hash = self.file_hashes.get(file_path)
        
        if old_hash and new_hash and old_hash != new_hash:
            entropy = self.calculate_entropy(file_path)
            print(f"  🔄 Hash: {old_hash} → {new_hash}")
            print(f"  📊 Entropy: {entropy:.2f}")
            
            if entropy > 7.5:
                print(f"  {Back.RED}{Fore.WHITE}🚨 POSSIBLE ENCRYPTION DETECTED!{Style.RESET_ALL}")
        
        if new_hash:
            self.file_hashes[file_path] = new_hash
        
        self.detect_suspicious_activity()
    
    def on_deleted(self, event):
        if event.is_directory:
            return
            
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        file_name = os.path.basename(event.src_path)
        
        print(f"{Fore.RED}✗ [{timestamp}] DELETED: {file_name}")
        
        # Remove from hash tracking
        if event.src_path in self.file_hashes:
            del self.file_hashes[event.src_path]
        
        self.detect_suspicious_activity()
    
    def on_moved(self, event):
        if event.is_directory:
            return
            
        self.event_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        src_name = os.path.basename(event.src_path)
        dest_name = os.path.basename(event.dest_path)
        
        print(f"{Fore.BLUE}→ [{timestamp}] MOVED: {src_name} → {dest_name}")
        
        # Check if moved to suspicious extension
        dest_ext = Path(event.dest_path).suffix.lower()
        if dest_ext in self.suspicious_extensions:
            print(f"  {Back.RED}{Fore.WHITE}🚨 MOVED TO RANSOMWARE EXTENSION: {dest_ext}{Style.RESET_ALL}")
        
        # Update hash tracking
        if event.src_path in self.file_hashes:
            self.file_hashes[event.dest_path] = self.file_hashes.pop(event.src_path)
        
        self.detect_suspicious_activity()

def print_header():
    """Print colorful header"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🛡️  ANTI-RANSOMWARE FILE MONITOR")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE}📁 Target: /home/popg/projects/anti-ransomW/Research")
    print(f"{Fore.WHITE}🖥️  Platform: {platform.system()} {platform.release()}")
    print(f"{Fore.WHITE}🐍 Python: {platform.python_version()}")
    
    if platform.system() == 'Windows':
        print(f"{Fore.WHITE}⚙️  Backend: ReadDirectoryChangesW")
    else:
        print(f"{Fore.WHITE}⚙️  Backend: inotify")
    
    print(f"{Fore.CYAN}{'='*60}")

def monitor_directory(path):
    """Monitor a directory for file changes"""
    if not os.path.exists(path):
        print(f"{Fore.RED}❌ Error: Directory '{path}' does not exist!")
        return
    
    print_header()
    print(f"{Fore.GREEN}🔍 Starting monitor...")
    
    event_handler = AntiRansomwareHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    try:
        observer.start()
        print(f"{Fore.GREEN}✅ Monitor active! Watching for file changes...")
        print(f"{Fore.WHITE}Press Ctrl+C to stop\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Stopping monitor...")
        observer.stop()
        
    observer.join()
    print(f"{Fore.GREEN}✅ Monitor stopped successfully!")

def create_test_files(directory, count=5):
    """Create test files to trigger monitoring events"""
    print(f"{Fore.CYAN}📝 Creating {count} test files...")
    
    for i in range(count):
        # Create random filename
        filename = f"test_{i+1}_{''.join(random.choices(string.ascii_lowercase, k=4))}.txt"
        filepath = os.path.join(directory, filename)
        
        # Write random content
        content = f"Test file {i+1}\n" + ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=200))
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"  ✓ Created: {filename}")
        time.sleep(0.2)  # Small delay to see events clearly
    
    print(f"{Fore.GREEN}✅ Test files created!")

def simulate_ransomware_attack(directory):
    """Simulate ransomware-like behavior"""
    print(f"{Back.RED}{Fore.WHITE}🦠 SIMULATING RANSOMWARE ATTACK{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  This will rapidly modify files to test detection")
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"{Fore.YELLOW}No .txt files found. Create test files first.")
        return
    
    print(f"{Fore.RED}🎯 Targeting {len(txt_files)} files...")
    
    for filename in txt_files[:3]:  # Modify first 3 files
        filepath = os.path.join(directory, filename)
        
        # Simulate encryption by writing random bytes (high entropy)
        encrypted_content = bytes([random.randint(0, 255) for _ in range(500)])
        
        with open(filepath, 'wb') as f:
            f.write(encrypted_content)
        
        # Rename to .encrypted extension
        encrypted_path = filepath + '.encrypted'
        os.rename(filepath, encrypted_path)
        
        print(f"  🔒 Encrypted: {filename} → {os.path.basename(encrypted_path)}")
        time.sleep(0.1)  # Fast to trigger detection
    
    print(f"{Fore.RED}💀 Simulated attack complete!")

def main():
    """Main function with menu system"""
    monitor_path = "/home/popg/.aws/amazonq"
    os.makedirs(monitor_path, exist_ok=True)
    
    while True:
        print(f"\n{Fore.YELLOW}🔧 ANTI-RANSOMWARE MONITOR - RESEARCH MODE")
        print(f"{Fore.WHITE}1. 🔍 Start File Monitor")
        print(f"{Fore.WHITE}2. 📝 Create Test Files")
        print(f"{Fore.WHITE}3. 🦠 Simulate Ransomware Attack")
        print(f"{Fore.WHITE}4. 📊 Show Directory Contents")
        print(f"{Fore.WHITE}5. 🧹 Clean Test Files")
        print(f"{Fore.WHITE}6. ❌ Exit")
        
        choice = input(f"\n{Fore.CYAN}Enter choice (1-6): {Fore.WHITE}")
        
        if choice == '1':
            monitor_directory(monitor_path)
        elif choice == '2':
            create_test_files(monitor_path)
        elif choice == '3':
            confirm = input(f"{Fore.RED}⚠️  This will modify files. Continue? (y/N): {Fore.WHITE}")
            if confirm.lower() == 'y':
                simulate_ransomware_attack(monitor_path)
        elif choice == '4':
            files = os.listdir(monitor_path)
            print(f"\n{Fore.CYAN}📁 Directory contents ({len(files)} files):")
            for f in sorted(files):
                filepath = os.path.join(monitor_path, f)
                size = os.path.getsize(filepath)
                print(f"  📄 {f} ({size} bytes)")
        elif choice == '5':
            files = [f for f in os.listdir(monitor_path) if f.startswith('test_') or f.endswith('.encrypted')]
            for f in files:
                os.remove(os.path.join(monitor_path, f))
            print(f"{Fore.GREEN}✅ Cleaned {len(files)} test files")
        elif choice == '6':
            print(f"{Fore.GREEN}👋 Goodbye!")
            break
        else:
            print(f"{Fore.RED}❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Exiting...")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")