# RansomGuard Features to Steal for Anti-RansomW

## Critical Features to Implement

### 1. Memory-Mapped I/O Protection ⭐⭐⭐
**Why:** Your current watchdog monitoring misses memory-mapped writes

**What to steal:**
```python
# From: RansomGuard/sections.cpp
class SectionTracker:
    """Track processes creating R/W memory mappings"""
    
    def __init__(self):
        self.sections = {}  # {pid: [file_paths]}
    
    def track_mmap(self, pid, filepath):
        """Track when process memory-maps a file"""
        if pid not in self.sections:
            self.sections[pid] = []
        self.sections[pid].append(filepath)
    
    def is_section_owner(self, pid, filepath):
        """Check if process has R/W mapping to file"""
        return pid in self.sections and filepath in self.sections[pid]
    
    def block_mapped_write(self, pid, filepath):
        """Prevent writes via memory mapping"""
        if self.is_section_owner(pid, filepath):
            # Restore original content to mapped buffer
            return True
        return False
```

**Implementation:**
- Monitor `/proc/[pid]/maps` on Linux
- Track `mmap()` syscalls with eBPF
- Block writes from malicious processes with mappings

---

### 2. Delete-Then-Recreate Detection ⭐⭐⭐
**Why:** Ransomware deletes original, creates encrypted copy with new extension

**What to steal:**
```python
# From: RansomGuard/files.cpp
class DeletedFileTracker:
    """Track deleted files to detect recreate pattern"""
    
    def __init__(self, max_tracked=25):
        self.deleted_files = {}  # {pid: [(filepath, content, entropy)]}
        self.max_tracked = max_tracked
    
    def add_deleted(self, pid, filepath, content, entropy):
        """Store deleted file data"""
        if pid not in self.deleted_files:
            self.deleted_files[pid] = []
        
        if len(self.deleted_files[pid]) >= self.max_tracked:
            self.deleted_files[pid].pop(0)  # Remove oldest
        
        self.deleted_files[pid].append({
            'path': filepath,
            'content': content,
            'entropy': entropy,
            'name_no_ext': self.remove_extension(filepath)
        })
    
    def check_recreate_pattern(self, pid, new_filepath):
        """Check if new file matches deleted file (ignoring extension)"""
        if pid not in self.deleted_files:
            return None
        
        new_name = self.remove_extension(new_filepath)
        
        for deleted in self.deleted_files[pid]:
            if deleted['name_no_ext'] == new_name:
                return deleted  # Return original content for comparison
        
        return None
    
    @staticmethod
    def remove_extension(filepath):
        """Remove file extension for comparison"""
        return filepath.rsplit('.', 1)[0]
```

**Integration:**
```python
# In your week4_protected_monitor.py
def on_deleted(self, event):
    # Store deleted file content
    content = read_file(event.src_path)
    entropy = calculate_entropy(event.src_path)
    self.deleted_tracker.add_deleted(pid, event.src_path, content, entropy)

def on_created(self, event):
    # Check if recreate pattern
    deleted_data = self.deleted_tracker.check_recreate_pattern(pid, event.src_path)
    if deleted_data:
        # Compare entropy: deleted vs new
        new_entropy = calculate_entropy(event.src_path)
        if new_entropy > deleted_data['entropy'] + 2.0:
            # RANSOMWARE DETECTED!
            self.block_and_alert()
```

---

### 3. Paging I/O Simulation ⭐⭐
**Why:** Detect encryption before it hits disk

**What to steal:**
```python
# From: RansomGuard/filters.cpp PreWrite
class WriteSimulator:
    """Simulate write operation to predict entropy"""
    
    def simulate_write(self, filepath, offset, new_data):
        """Simulate write and calculate resulting entropy"""
        # Read current file content
        with open(filepath, 'rb') as f:
            original = f.read()
        
        # Simulate write
        simulated = bytearray(original)
        simulated[offset:offset+len(new_data)] = new_data
        
        # Calculate entropies
        pre_entropy = calculate_entropy_bytes(original)
        post_entropy = calculate_entropy_bytes(simulated)
        
        return pre_entropy, post_entropy
    
    def should_block_write(self, filepath, offset, new_data):
        """Predict if write will encrypt file"""
        pre, post = self.simulate_write(filepath, offset, new_data)
        
        # RansomGuard's detection logic
        entropy_diff = post - pre
        suspicious_diff = (8.0 - pre) * 0.83
        
        if post >= 5.5 and entropy_diff >= suspicious_diff:
            return True  # Block - likely encryption
        
        return False
```

**Integration:**
```python
# Hook into file writes BEFORE they happen
def intercept_write(self, filepath, offset, data):
    if not self.token_session.is_valid():
        return False  # Already blocked by token
    
    # Additional check: simulate write
    if self.write_simulator.should_block_write(filepath, offset, data):
        print(f"[BLOCKED] Write would encrypt file: {filepath}")
        return False
    
    return True  # Allow
```

---

### 4. Process Encryption Counter ⭐⭐⭐
**Why:** Track suspicious behavior per process

**What to steal:**
```python
# From: RansomGuard/processes.cpp
class ProcessTracker:
    """Track encryption activity per process"""
    
    def __init__(self, threshold=6):
        self.processes = {}  # {pid: {'encrypted': 0, 'malicious': False}}
        self.threshold = threshold
    
    def update_encrypted_count(self, pid):
        """Increment encryption counter"""
        if pid not in self.processes:
            self.processes[pid] = {'encrypted': 0, 'malicious': False}
        
        self.processes[pid]['encrypted'] += 1
        
        if self.processes[pid]['encrypted'] >= self.threshold:
            self.processes[pid]['malicious'] = True
            self.kill_process(pid)
            return True  # Process killed
        
        return False
    
    def is_malicious(self, pid):
        """Check if process is marked malicious"""
        return self.processes.get(pid, {}).get('malicious', False)
    
    def block_filesystem_access(self, pid):
        """Block all filesystem access from malicious process"""
        if self.is_malicious(pid):
            return True
        return False
```

**Integration:**
```python
# In your monitor
def on_modified(self, event):
    pid = get_process_id(event)
    
    # Check if process is already malicious
    if self.process_tracker.is_malicious(pid):
        print(f"[BLOCKED] Malicious process {pid} denied access")
        return
    
    # Check entropy
    if is_encrypted(event.src_path):
        killed = self.process_tracker.update_encrypted_count(pid)
        if killed:
            print(f"[KILLED] Process {pid} encrypted {self.threshold} files")
```

---

### 5. Automatic Backup System ⭐⭐⭐
**Why:** Last line of defense when detection fails

**What to steal:**
```python
# From: RansomGuard/restore.cpp
class AutoBackup:
    """Automatic file backup before modifications"""
    
    def __init__(self, backup_dir='/var/antiransomw/backups'):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def backup_file(self, filepath, content):
        """Backup file with path-based naming"""
        # Convert path to backup name: /home/user/doc.txt -> _home_user_doc.txt
        backup_name = filepath.replace('/', '_')
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        with open(backup_path, 'wb') as f:
            f.write(content)
        
        return backup_path
    
    def backup_before_write(self, filepath):
        """Backup file before allowing write"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
            
            backup_path = self.backup_file(filepath, content)
            print(f"[BACKUP] {filepath} -> {backup_path}")
            return backup_path
        
        return None
    
    def restore_file(self, filepath):
        """Restore file from backup"""
        backup_name = filepath.replace('/', '_')
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if os.path.exists(backup_path):
            with open(backup_path, 'rb') as f:
                content = f.read()
            
            with open(filepath, 'wb') as f:
                f.write(content)
            
            print(f"[RESTORED] {filepath}")
            return True
        
        return False
```

**Integration:**
```python
# In your monitor
def on_modified(self, event):
    # Backup BEFORE allowing write
    self.auto_backup.backup_before_write(event.src_path)
    
    # Then check token/entropy
    if self.is_write_allowed(event.src_path):
        # Write happens
        pass
    else:
        # Write blocked, backup preserved
        pass
```

---

### 6. Deferred Process Cleanup ⭐
**Why:** Handle async writes after process termination

**What to steal:**
```python
# From: RansomGuard/kernelcallbacks.cpp
class DeferredCleanup:
    """Defer process cleanup for async operations"""
    
    def __init__(self, delay_seconds=120):
        self.delay = delay_seconds
        self.pending = {}  # {pid: cleanup_time}
    
    def defer_removal(self, pid, section_count):
        """Defer process removal if many sections exist"""
        if section_count >= 12:  # RansomGuard threshold
            cleanup_time = time.time() + self.delay
            self.pending[pid] = cleanup_time
            
            # Schedule cleanup
            threading.Timer(self.delay, self.cleanup_process, args=[pid]).start()
            return True
        
        return False
    
    def cleanup_process(self, pid):
        """Remove process entry after delay"""
        if pid in self.pending:
            del self.pending[pid]
            # Remove from process tracker
```

---

## Implementation Priority

### Week 5 (Immediate)
1. **Delete-recreate detection** - Easy, high impact
2. **Process encryption counter** - Simple tracking
3. **Automatic backup** - Critical safety net

### Week 6-7 (Medium)
4. **Memory-mapped I/O tracking** - Requires eBPF/kernel
5. **Write simulation** - Performance testing needed

### Week 8+ (Advanced)
6. **Deferred cleanup** - Edge case handling

---

## Code Integration Example

```python
# Enhanced week4_protected_monitor.py
class EnhancedProtectedMonitor(FileSystemEventHandler):
    def __init__(self, db, token_session, protected_folder):
        self.db = db
        self.token_session = token_session
        self.protected_folder = protected_folder
        
        # NEW: RansomGuard features
        self.deleted_tracker = DeletedFileTracker(max_tracked=25)
        self.process_tracker = ProcessTracker(threshold=6)
        self.auto_backup = AutoBackup()
        self.write_simulator = WriteSimulator()
        self.section_tracker = SectionTracker()
    
    def on_deleted(self, event):
        """Track deleted files"""
        if os.path.exists(event.src_path):
            content = read_file(event.src_path)
            entropy = calculate_entropy(event.src_path)
            pid = get_process_id(event)
            self.deleted_tracker.add_deleted(pid, event.src_path, content, entropy)
    
    def on_created(self, event):
        """Check for delete-recreate pattern"""
        pid = get_process_id(event)
        
        # Check recreate pattern
        deleted_data = self.deleted_tracker.check_recreate_pattern(pid, event.src_path)
        if deleted_data:
            new_entropy = calculate_entropy(event.src_path)
            if new_entropy > deleted_data['entropy'] + 2.0:
                print(f"[RANSOMWARE] Delete-recreate detected: {event.src_path}")
                self.process_tracker.update_encrypted_count(pid)
                return
        
        self.process_write(event.src_path, 'CREATE')
    
    def on_modified(self, event):
        """Enhanced write protection"""
        pid = get_process_id(event)
        
        # Block if process is malicious
        if self.process_tracker.is_malicious(pid):
            print(f"[BLOCKED] Malicious process {pid}")
            return
        
        # Backup before write
        self.auto_backup.backup_before_write(event.src_path)
        
        # Check token
        if not self.token_session.is_valid():
            print(f"[BLOCKED] No valid token")
            return
        
        # Allow write and check entropy
        self.process_write(event.src_path, 'MODIFY')
        
        # Update process counter if encrypted
        if is_encrypted(event.src_path):
            self.process_tracker.update_encrypted_count(pid)
```

---

## Quick Win: Minimal Integration

```python
# Add to existing week4_protected_monitor.py (10 lines)

# At top
deleted_files = {}  # {pid: [(path, entropy)]}

# In on_deleted
deleted_files[pid] = deleted_files.get(pid, []) + [(path, entropy)]

# In on_created
for old_path, old_entropy in deleted_files.get(pid, []):
    if old_path.rsplit('.', 1)[0] == path.rsplit('.', 1)[0]:  # Same name
        if calculate_entropy(path) > old_entropy + 2.0:
            print("[RANSOMWARE] Delete-recreate attack detected!")
            block_process(pid)
```

---

## Summary

**Must Steal:**
1. Delete-recreate detection (easiest, high value)
2. Process encryption counter (simple tracking)
3. Automatic backup (safety net)

**Should Steal:**
4. Memory-mapped I/O tracking (requires kernel work)
5. Write simulation (performance consideration)

**Nice to Have:**
6. Deferred cleanup (edge cases)

**Implementation Time:** 2-3 weeks for items 1-3
