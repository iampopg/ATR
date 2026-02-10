# Watchdog Research - Cross-Platform File Monitoring

## Overview
Watchdog is a Python library that provides cross-platform file system event monitoring. It's perfect for our anti-ransomware project as it works on both Windows and Linux with the same API.

## Installation
```bash
pip install watchdog colorama
```

## Key Features
- **Cross-platform**: Works on Windows, Linux, macOS
- **Real-time monitoring**: Detects file changes instantly
- **Event types**: CREATE, MODIFY, DELETE, MOVE
- **Recursive monitoring**: Can monitor subdirectories
- **Pattern matching**: Filter specific file types

## Implementation

### Basic File Monitor
```python
import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class AntiRansomwareHandler(FileSystemEventHandler):
    def __init__(self):
        self.event_count = 0
        self.start_time = time.time()
        
    def on_any_event(self, event):
        if event.is_directory:
            return
            
        self.event_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Color coding based on event type
        if event.event_type == 'created':
            color = Fore.GREEN
            icon = "✓"
        elif event.event_type == 'modified':
            color = Fore.YELLOW
            icon = "⚠"
        elif event.event_type == 'deleted':
            color = Fore.RED
            icon = "✗"
        elif event.event_type == 'moved':
            color = Fore.BLUE
            icon = "→"
        else:
            color = Fore.WHITE
            icon = "?"
            
        print(f"{color}{icon} [{timestamp}] {event.event_type.upper()}: {event.src_path}")
        
        # Ransomware detection logic
        self.detect_suspicious_activity()
        
    def detect_suspicious_activity(self):
        """Basic ransomware detection based on event frequency"""
        current_time = time.time()
        time_window = current_time - self.start_time
        
        if time_window > 0:
            events_per_second = self.event_count / time_window
            
            if events_per_second > 5:  # More than 5 events per second
                print(f"{Back.RED}{Fore.WHITE}🚨 SUSPICIOUS ACTIVITY DETECTED!")
                print(f"   Events per second: {events_per_second:.2f}")
                print(f"   Total events: {self.event_count}")
                print(f"   Time window: {time_window:.2f}s{Style.RESET_ALL}")

def monitor_directory(path):
    """Monitor a directory for file changes"""
    if not os.path.exists(path):
        print(f"{Fore.RED}Error: Directory '{path}' does not exist!")
        return
        
    print(f"{Fore.CYAN}🔍 Starting Anti-Ransomware Monitor")
    print(f"{Fore.CYAN}📁 Monitoring: {path}")
    print(f"{Fore.CYAN}🖥️  Platform: {os.name}")
    print(f"{Fore.CYAN}{'='*50}")
    
    event_handler = AntiRansomwareHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    try:
        observer.start()
        print(f"{Fore.GREEN}✓ Monitor started successfully!")
        print(f"{Fore.WHITE}Press Ctrl+C to stop monitoring...")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Stopping monitor...")
        observer.stop()
        
    observer.join()
    print(f"{Fore.GREEN}✓ Monitor stopped successfully!")

if __name__ == "__main__":
    # Monitor the research directory
    monitor_path = "/home/popg/projects/anti-ransomW/Research"
    
    # Create directory if it doesn't exist
    os.makedirs(monitor_path, exist_ok=True)
    
    monitor_directory(monitor_path)
```

### Advanced Monitor with File Analysis
```python
import os
import hashlib
import math
from collections import Counter
from pathlib import Path

class AdvancedAntiRansomwareHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.file_hashes = {}
        self.event_history = []
        self.suspicious_extensions = {'.encrypted', '.locked', '.crypto', '.crypt'}
        
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
        except:
            return 0
    
    def get_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None
    
    def on_created(self, event):
        if event.is_directory:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = event.src_path
        file_ext = Path(file_path).suffix.lower()
        
        print(f"{Fore.GREEN}✓ [{timestamp}] CREATED: {file_path}")
        
        # Check for suspicious extensions
        if file_ext in self.suspicious_extensions:
            print(f"{Back.RED}{Fore.WHITE}🚨 RANSOMWARE EXTENSION DETECTED: {file_ext}")
        
        # Calculate entropy for new files
        entropy = self.calculate_entropy(file_path)
        if entropy > 7.5:  # High entropy indicates encryption
            print(f"{Back.YELLOW}{Fore.BLACK}⚠️  HIGH ENTROPY DETECTED: {entropy:.2f}")
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_path = event.src_path
        
        print(f"{Fore.YELLOW}⚠ [{timestamp}] MODIFIED: {file_path}")
        
        # Check if file hash changed significantly
        new_hash = self.get_file_hash(file_path)
        old_hash = self.file_hashes.get(file_path)
        
        if old_hash and new_hash and old_hash != new_hash:
            entropy = self.calculate_entropy(file_path)
            print(f"   Hash changed: {old_hash[:8]}... → {new_hash[:8]}...")
            print(f"   Entropy: {entropy:.2f}")
            
            if entropy > 7.5:
                print(f"{Back.RED}{Fore.WHITE}🚨 POSSIBLE ENCRYPTION DETECTED!")
        
        if new_hash:
            self.file_hashes[file_path] = new_hash
    
    def on_deleted(self, event):
        if event.is_directory:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.RED}✗ [{timestamp}] DELETED: {event.src_path}")
        
        # Remove from hash tracking
        if event.src_path in self.file_hashes:
            del self.file_hashes[event.src_path]
    
    def on_moved(self, event):
        if event.is_directory:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.BLUE}→ [{timestamp}] MOVED: {event.src_path} → {event.dest_path}")
        
        # Update hash tracking
        if event.src_path in self.file_hashes:
            self.file_hashes[event.dest_path] = self.file_hashes.pop(event.src_path)

def advanced_monitor(path):
    """Advanced monitoring with entropy analysis"""
    print(f"{Fore.MAGENTA}🔬 Starting Advanced Anti-Ransomware Monitor")
    print(f"{Fore.MAGENTA}📁 Monitoring: {path}")
    print(f"{Fore.MAGENTA}🧮 Features: Entropy Analysis, Hash Tracking, Extension Detection")
    print(f"{Fore.MAGENTA}{'='*60}")
    
    event_handler = AdvancedAntiRansomwareHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    try:
        observer.start()
        print(f"{Fore.GREEN}✓ Advanced monitor started!")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🛑 Stopping advanced monitor...")
        observer.stop()
        
    observer.join()
```

### Cross-Platform Test Script
```python
import platform
import tempfile
import random
import string

def create_test_files(directory, count=10):
    """Create test files to trigger monitoring events"""
    print(f"{Fore.CYAN}📝 Creating {count} test files...")
    
    for i in range(count):
        # Create random filename
        filename = ''.join(random.choices(string.ascii_letters, k=8)) + '.txt'
        filepath = os.path.join(directory, filename)
        
        # Write random content
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        time.sleep(0.1)  # Small delay to see events
    
    print(f"{Fore.GREEN}✓ Test files created!")

def simulate_ransomware_attack(directory):
    """Simulate ransomware-like behavior"""
    print(f"{Back.RED}{Fore.WHITE}🦠 SIMULATING RANSOMWARE ATTACK")
    print(f"   This will rapidly modify files to test detection")
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    
    for filename in txt_files[:5]:  # Modify first 5 files
        filepath = os.path.join(directory, filename)
        
        # Simulate encryption by writing random bytes
        encrypted_content = bytes([random.randint(0, 255) for _ in range(200)])
        
        with open(filepath, 'wb') as f:
            f.write(encrypted_content)
        
        # Rename to .encrypted extension
        encrypted_path = filepath + '.encrypted'
        os.rename(filepath, encrypted_path)
        
        time.sleep(0.05)  # Very fast to trigger detection

def platform_info():
    """Display platform information"""
    print(f"{Fore.CYAN}🖥️  Platform Information:")
    print(f"   System: {platform.system()}")
    print(f"   Release: {platform.release()}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print(f"   Python: {platform.python_version()}")
    
    if platform.system() == 'Windows':
        print(f"   File System: NTFS (likely)")
        print(f"   Monitoring: Uses ReadDirectoryChangesW")
    else:
        print(f"   File System: ext4/btrfs (likely)")
        print(f"   Monitoring: Uses inotify")

def main():
    """Main function with menu system"""
    monitor_path = "/home/popg/projects/anti-ransomW/Research"
    os.makedirs(monitor_path, exist_ok=True)
    
    platform_info()
    print(f"\n{Fore.YELLOW}Choose monitoring mode:")
    print(f"1. Basic Monitor")
    print(f"2. Advanced Monitor (with entropy analysis)")
    print(f"3. Create Test Files")
    print(f"4. Simulate Ransomware Attack")
    print(f"5. Exit")
    
    choice = input(f"\n{Fore.WHITE}Enter choice (1-5): ")
    
    if choice == '1':
        monitor_directory(monitor_path)
    elif choice == '2':
        advanced_monitor(monitor_path)
    elif choice == '3':
        create_test_files(monitor_path)
        print(f"{Fore.GREEN}Now run monitor in another terminal to see events!")
    elif choice == '4':
        print(f"{Fore.RED}⚠️  This will modify files in {monitor_path}")
        confirm = input("Continue? (y/N): ")
        if confirm.lower() == 'y':
            simulate_ransomware_attack(monitor_path)
    elif choice == '5':
        print(f"{Fore.GREEN}Goodbye!")
    else:
        print(f"{Fore.RED}Invalid choice!")

if __name__ == "__main__":
    main()
```

## Key Findings

### Advantages of Watchdog:
1. **Cross-platform compatibility** - Same code works on Windows/Linux
2. **Real-time monitoring** - Events triggered immediately
3. **Recursive monitoring** - Can monitor subdirectories
4. **Low overhead** - Efficient native implementations
5. **Pattern filtering** - Can ignore specific files/extensions

### Platform Differences:
- **Windows**: Uses `ReadDirectoryChangesW` API internally
- **Linux**: Uses `inotify` API internally
- **Performance**: Both platforms handle 1000+ events/second easily

### Ransomware Detection Capabilities:
1. **Rapid file changes** - Detect mass modifications
2. **Extension changes** - Spot .encrypted, .locked files
3. **Entropy analysis** - Identify encrypted content
4. **Hash tracking** - Monitor file integrity

### Limitations:
1. **Userspace only** - Can't intercept kernel-level operations
2. **No blocking** - Can only detect, not prevent
3. **Performance impact** - Entropy calculation is CPU intensive
4. **False positives** - Legitimate apps can trigger alerts

## Conclusion
Watchdog is excellent for **detection and monitoring** but needs to be combined with **permission controls** and **token validation** for actual protection. Perfect for the monitoring component of our anti-ransomware system.