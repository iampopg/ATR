# Anti-Ransomware Build Order - Component by Component

## Build Order (Like Building a Human)

```
HEAD (Core Detection)
  ↓
UPPER BODY (Token System)
  ↓
HANDS (File Operations)
  ↓
LOWER BODY (Process Tracking)
  ↓
LEGS (Backup & Recovery)
```

---

## 1. HEAD - File Change Detection (Foundation)

**What:** Monitor filesystem for changes in real-time

**Component Name:** `Filesystem Watcher` / `File Monitor`

**GitHub Search Terms:**
- "python file monitoring"
- "inotify python wrapper"
- "filesystem event handler"
- "watchdog python"

**Existing Libraries:**
```python
# Option 1: watchdog (YOU ALREADY HAVE THIS)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Option 2: pyinotify (Linux only)
import pyinotify

# Option 3: fsevents (macOS)
import fsevents
```

**What to Build:**
```python
class FileMonitor:
    def on_file_created(path):
        pass
    
    def on_file_modified(path):
        pass
    
    def on_file_deleted(path):
        pass
```

**GitHub Projects to Copy:**
- `gorakhargosh/watchdog` - File monitoring (YOU HAVE THIS)
- `seb-m/pyinotify` - Linux inotify wrapper
- `fsspec/filesystem_spec` - Abstract filesystem

---

## 2. UPPER BODY - Token Authentication System

**What:** Generate and validate access tokens

**Component Name:** `Token Manager` / `Authentication Service`

**GitHub Search Terms:**
- "python jwt token"
- "argon2 password hashing"
- "HKDF key derivation"
- "token authentication python"

**Existing Libraries:**
```python
# Password hashing (YOU HAVE THIS)
from argon2 import PasswordHasher

# Token generation
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# HMAC validation
import hmac
import hashlib
```

**What to Build:**
```python
class TokenManager:
    def generate_token(user, duration):
        pass
    
    def validate_token(token):
        pass
    
    def is_expired(token):
        pass
```

**GitHub Projects to Copy:**
- `jpadilla/pyjwt` - JWT tokens
- `pyca/cryptography` - Crypto primitives (YOU HAVE THIS)
- `hynek/argon2-cffi` - Password hashing (YOU HAVE THIS)

---

## 3. HANDS (LEFT) - Entropy Calculator

**What:** Calculate Shannon entropy to detect encryption

**Component Name:** `Entropy Analyzer` / `Encryption Detector`

**GitHub Search Terms:**
- "shannon entropy python"
- "file entropy calculator"
- "ransomware entropy detection"
- "byte frequency analysis"

**Existing Libraries:**
```python
# Math for entropy
import math
from collections import Counter

# File reading
import os
```

**What to Build:**
```python
class EntropyAnalyzer:
    def calculate_entropy(filepath):
        # Read file bytes
        # Count byte frequencies
        # Calculate Shannon entropy
        pass
    
    def is_encrypted(entropy):
        return entropy > 7.5
```

**GitHub Projects to Copy:**
- `Maykeye/entropy` - Entropy calculation
- `Neo23x0/munin` - File entropy scanner
- `digitalsleuth/entropy-checker` - Ransomware entropy

---

## 4. HANDS (RIGHT) - Hash Calculator

**What:** Calculate file hashes for integrity checking

**Component Name:** `Hash Calculator` / `Integrity Checker`

**GitHub Search Terms:**
- "python file hash"
- "sha256 calculator"
- "file integrity checker"

**Existing Libraries:**
```python
# Built-in
import hashlib

# Fast hashing
import xxhash  # Optional, faster
```

**What to Build:**
```python
class HashCalculator:
    def calculate_hash(filepath):
        # Read file in chunks
        # Update hash
        return hash_hex
    
    def verify_hash(filepath, expected_hash):
        pass
```

**GitHub Projects to Copy:**
- `python/cpython` - hashlib (built-in)
- `ifduyue/python-xxhash` - Fast hashing
- `tiran/defusedxml` - Secure hash examples

---

## 5. LOWER BODY - Process Tracker

**What:** Track which processes are modifying files

**Component Name:** `Process Monitor` / `PID Tracker`

**GitHub Search Terms:**
- "python process monitoring"
- "psutil process info"
- "get process by pid python"
- "process tree python"

**Existing Libraries:**
```python
# Process info
import psutil
import os

# Process name
from pathlib import Path
```

**What to Build:**
```python
class ProcessTracker:
    def get_process_info(pid):
        # Get process name, path, user
        pass
    
    def track_file_access(pid, filepath):
        # Record which process touched which file
        pass
    
    def get_suspicious_processes():
        # Return processes with high encryption count
        pass
```

**GitHub Projects to Copy:**
- `giampaolo/psutil` - Process utilities
- `nicolargo/glances` - System monitoring
- `iovisor/bcc` - Process tracing (advanced)

---

## 6. LEGS (LEFT) - Database Logger

**What:** Store all events in database

**Component Name:** `Event Logger` / `Audit Database`

**GitHub Search Terms:**
- "python sqlite logging"
- "database event logger"
- "audit trail python"

**Existing Libraries:**
```python
# Built-in
import sqlite3

# ORM (optional)
from sqlalchemy import create_engine
```

**What to Build:**
```python
class EventLogger:
    def log_event(filepath, event_type, hash, entropy):
        # Insert into database
        pass
    
    def get_events(limit=100):
        # Query recent events
        pass
    
    def get_file_history(filepath):
        # Get all events for a file
        pass
```

**GitHub Projects to Copy:**
- `python/cpython` - sqlite3 (built-in)
- `sqlalchemy/sqlalchemy` - Database ORM
- `encode/databases` - Async database

---

## 7. LEGS (RIGHT) - Backup System

**What:** Automatically backup files before changes

**Component Name:** `Backup Manager` / `File Snapshotter`

**GitHub Search Terms:**
- "python file backup"
- "snapshot system python"
- "file versioning python"
- "backup restore utility"

**Existing Libraries:**
```python
# File operations
import shutil
import os
from datetime import datetime

# Compression (optional)
import zipfile
import tarfile
```

**What to Build:**
```python
class BackupManager:
    def backup_file(filepath):
        # Copy file to backup location
        # Name: original_path_timestamp
        pass
    
    def restore_file(filepath):
        # Restore from latest backup
        pass
    
    def list_backups(filepath):
        # Show all backups for a file
        pass
```

**GitHub Projects to Copy:**
- `borgbackup/borg` - Deduplicating backups
- `restic/restic` - Backup program
- `duplicity/duplicity` - Encrypted backups

---

## 8. BRAIN - Delete-Recreate Detector (RansomGuard Feature)

**What:** Detect when file is deleted and recreated with different extension

**Component Name:** `Pattern Detector` / `Behavior Analyzer`

**GitHub Search Terms:**
- "file pattern detection python"
- "ransomware behavior detection"
- "file rename tracker"

**No Library Needed - Build Custom:**
```python
class PatternDetector:
    def __init__(self):
        self.deleted_files = {}  # {pid: [(path, content, entropy)]}
    
    def track_deletion(pid, filepath, content, entropy):
        # Store deleted file info
        pass
    
    def check_recreate(pid, new_filepath):
        # Check if new file matches deleted (ignoring extension)
        # Compare entropy
        pass
```

**GitHub Projects to Copy:**
- `Neo23x0/Loki` - IOC scanner (pattern matching)
- `JPCERTCC/MalConfScan` - Malware detection
- Custom implementation (no direct library)

---

## 9. NERVOUS SYSTEM - Integration Layer

**What:** Connect all components together

**Component Name:** `Protection Engine` / `Main Controller`

**What to Build:**
```python
class ProtectionEngine:
    def __init__(self):
        self.file_monitor = FileMonitor()
        self.token_manager = TokenManager()
        self.entropy_analyzer = EntropyAnalyzer()
        self.hash_calculator = HashCalculator()
        self.process_tracker = ProcessTracker()
        self.event_logger = EventLogger()
        self.backup_manager = BackupManager()
        self.pattern_detector = PatternDetector()
    
    def on_file_change(event):
        # 1. Check token
        # 2. Backup file
        # 3. Calculate hash
        # 4. Calculate entropy
        # 5. Track process
        # 6. Check patterns
        # 7. Log event
        # 8. Block if suspicious
        pass
```

---

## Complete Build Order with GitHub Projects

### Phase 1: Foundation (Week 1)
```bash
# 1. File Monitor
pip install watchdog  # ✓ YOU HAVE THIS

# 2. Database
# sqlite3 built-in  # ✓ YOU HAVE THIS
```

### Phase 2: Security (Week 2)
```bash
# 3. Token System
pip install pyjwt argon2-cffi cryptography  # ✓ YOU HAVE THIS

# 4. Hash Calculator
# hashlib built-in  # ✓ YOU HAVE THIS
```

### Phase 3: Detection (Week 3)
```bash
# 5. Entropy Analyzer
# math built-in  # ✓ YOU HAVE THIS

# 6. Process Tracker
pip install psutil
```

### Phase 4: Protection (Week 4)
```bash
# 7. Backup System
# shutil built-in

# 8. Pattern Detector
# Custom code (no library)
```

---

## GitHub Projects to Clone and Study

### 1. File Monitoring
```bash
git clone https://github.com/gorakhargosh/watchdog.git
# Study: watchdog/src/watchdog/observers/
```

### 2. Token Authentication
```bash
git clone https://github.com/jpadilla/pyjwt.git
# Study: jwt/api_jwt.py

git clone https://github.com/hynek/argon2-cffi.git
# Study: src/argon2/
```

### 3. Entropy Detection
```bash
git clone https://github.com/Neo23x0/munin.git
# Study: munin.py (entropy calculation)

git clone https://github.com/digitalsleuth/entropy-checker.git
# Study: entropy_checker.py
```

### 4. Process Monitoring
```bash
git clone https://github.com/giampaolo/psutil.git
# Study: psutil/__init__.py
```

### 5. Ransomware Detection (Full Systems)
```bash
git clone https://github.com/0xmilkmix/RansomWatch.git
# Study: detection patterns

git clone https://github.com/Neo23x0/Loki.git
# Study: loki.py (IOC detection)
```

---

## Assembly Instructions

### Step 1: Copy File Monitor (Head)
```python
# From: watchdog examples
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"File changed: {event.src_path}")
```

### Step 2: Add Token System (Upper Body)
```python
# From: pyjwt examples
import jwt

token = jwt.encode({"user": "admin"}, "secret", algorithm="HS256")
decoded = jwt.decode(token, "secret", algorithms=["HS256"])
```

### Step 3: Add Entropy (Left Hand)
```python
# From: munin or custom
def calculate_entropy(data):
    from collections import Counter
    import math
    
    counter = Counter(data)
    length = len(data)
    entropy = -sum((count/length) * math.log2(count/length) 
                   for count in counter.values())
    return entropy
```

### Step 4: Add Hash (Right Hand)
```python
# Built-in
import hashlib

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
```

### Step 5: Add Process Tracker (Lower Body)
```python
# From: psutil examples
import psutil

def get_process_info(pid):
    try:
        proc = psutil.Process(pid)
        return {
            'name': proc.name(),
            'exe': proc.exe(),
            'user': proc.username()
        }
    except:
        return None
```

### Step 6: Add Backup (Left Leg)
```python
# Built-in
import shutil
from datetime import datetime

def backup_file(filepath):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup.{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path
```

### Step 7: Add Logger (Right Leg)
```python
# Built-in
import sqlite3

def log_event(filepath, event_type):
    conn = sqlite3.connect('events.db')
    conn.execute("""
        INSERT INTO events (filepath, event_type, timestamp)
        VALUES (?, ?, datetime('now'))
    """, (filepath, event_type))
    conn.commit()
    conn.close()
```

### Step 8: Add Pattern Detector (Brain)
```python
# Custom (from RansomGuard)
deleted_files = {}

def track_deletion(pid, filepath, entropy):
    if pid not in deleted_files:
        deleted_files[pid] = []
    deleted_files[pid].append((filepath, entropy))

def check_recreate(pid, new_filepath, new_entropy):
    if pid not in deleted_files:
        return False
    
    new_name = new_filepath.rsplit('.', 1)[0]
    
    for old_path, old_entropy in deleted_files[pid]:
        old_name = old_path.rsplit('.', 1)[0]
        if old_name == new_name and new_entropy > old_entropy + 2.0:
            return True  # RANSOMWARE!
    
    return False
```

---

## Final Assembly (Integration)

```python
# Combine everything
class AntiRansomware:
    def __init__(self):
        # Head
        self.observer = Observer()
        
        # Upper body
        self.token_manager = TokenManager()
        
        # Hands
        self.entropy = EntropyAnalyzer()
        self.hasher = HashCalculator()
        
        # Lower body
        self.process_tracker = ProcessTracker()
        
        # Legs
        self.backup = BackupManager()
        self.logger = EventLogger()
        
        # Brain
        self.pattern_detector = PatternDetector()
    
    def on_file_change(self, filepath, event_type):
        # 1. Get process
        pid = get_current_pid()
        
        # 2. Check token
        if not self.token_manager.is_valid():
            print("BLOCKED: No token")
            return
        
        # 3. Backup
        self.backup.backup_file(filepath)
        
        # 4. Calculate metrics
        file_hash = self.hasher.calculate_hash(filepath)
        entropy = self.entropy.calculate_entropy(filepath)
        
        # 5. Check patterns
        if event_type == 'DELETE':
            self.pattern_detector.track_deletion(pid, filepath, entropy)
        elif event_type == 'CREATE':
            if self.pattern_detector.check_recreate(pid, filepath, entropy):
                print("RANSOMWARE DETECTED!")
                return
        
        # 6. Log
        self.logger.log_event(filepath, event_type, file_hash, entropy)
```

---

## Summary: What to Search on GitHub

1. **watchdog** - File monitoring (HAVE)
2. **pyjwt** - Token generation (HAVE)
3. **argon2-cffi** - Password hashing (HAVE)
4. **psutil** - Process tracking (NEED)
5. **munin** - Entropy examples (STUDY)
6. **Loki** - Pattern detection (STUDY)

**You already have 60% of the components!** Just need to add process tracking and pattern detection.
