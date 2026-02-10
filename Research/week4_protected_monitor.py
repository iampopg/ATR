#!/usr/bin/env python3
"""
Week 4 - Token-Protected Filesystem
Integrates Week 2 tokens with Week 3 monitoring
Blocks file writes without valid token
"""

import os
import time
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore, init

from week2_task1_master_key import MasterKeyDerivation
from week2_task2_token_generation import TokenGenerator
from week3_database import FileDatabase
from week3_hash_calculator import calculate_hash, get_file_size
from week3_entropy_analyzer import calculate_entropy, is_encrypted

init(autoreset=True)

class TokenSession:
    """Manages token sessions"""
    def __init__(self, master_key, validity_minutes=10):
        self.master_key = master_key
        self.token_generator = TokenGenerator(master_key)
        self.validity_minutes = validity_minutes
        self.current_token = None
        self.token_expiry = None
    
    def generate_token(self, filepath):
        """Generate token for file access"""
        nonce_c = self.token_generator.generate_nonce()
        nonce_s = self.token_generator.generate_nonce()
        timestamp = int(time.time())
        
        token = self.token_generator.generate_token(nonce_c, nonce_s, timestamp, filepath)
        self.current_token = token
        self.token_expiry = datetime.now() + timedelta(minutes=self.validity_minutes)
        
        return token
    
    def is_valid(self):
        """Check if current token is valid"""
        if not self.current_token or not self.token_expiry:
            return False
        return datetime.now() < self.token_expiry
    
    def renew(self):
        """Renew token session"""
        self.token_expiry = datetime.now() + timedelta(minutes=self.validity_minutes)

class ProtectedMonitor(FileSystemEventHandler):
    """Monitor with token protection"""
    def __init__(self, db, token_session, protected_folder):
        self.db = db
        self.token_session = token_session
        self.protected_folder = protected_folder
        self.blocked_count = 0
        self.allowed_count = 0
    
    def is_write_allowed(self, filepath):
        """Check if write is allowed (has valid token)"""
        if not self.token_session.is_valid():
            return False
        return True
    
    def process_write(self, filepath, event_type):
        """Process write operation with token check"""
        # Check token
        if not self.is_write_allowed(filepath):
            self.blocked_count += 1
            print(f"{Fore.RED}[BLOCKED] {event_type} - No valid token")
            print(f"{Fore.RED}  File: {filepath}")
            print(f"{Fore.YELLOW}  Reason: Token required for write operations")
            
            # Log blocked attempt
            self.db.log_event(filepath, f'BLOCKED_{event_type}')
            return False
        
        # Token valid - allow operation
        self.allowed_count += 1
        
        if not os.path.exists(filepath):
            self.db.log_event(filepath, event_type)
            print(f"{Fore.GREEN}[ALLOWED] {event_type} - {filepath}")
            return True
        
        # Get file info
        file_hash = calculate_hash(filepath)
        file_size = get_file_size(filepath)
        entropy = calculate_entropy(filepath)
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
        print(f"{color}[ALLOWED] {event_type} - {filepath}")
        print(f"  Hash: {file_hash[:16]}...")
        print(f"  Entropy: {entropy:.2f}")
        
        if encrypted:
            print(f"{Fore.RED}  ⚠️  HIGH ENTROPY - POSSIBLE ENCRYPTION!")
        
        return True
    
    def on_created(self, event):
        if not event.is_directory:
            self.process_write(event.src_path, 'CREATE')
    
    def on_modified(self, event):
        if not event.is_directory:
            self.process_write(event.src_path, 'MODIFY')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.process_write(event.src_path, 'DELETE')

def run_protected_monitor(folder_path, password, db_path='protected_files.db'):
    """Run filesystem monitor with token protection"""
    
    # Initialize
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Anti-Ransomware Protection System")
    print(f"{Fore.CYAN}Week 4 - Token-Protected Filesystem")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    # Derive master key
    print(f"{Fore.YELLOW}Initializing...")
    mkd = MasterKeyDerivation()
    master_key, salt = mkd.derive_master_key(password)
    print(f"{Fore.GREEN}✓ Master key derived")
    
    # Create token session
    token_session = TokenSession(master_key, validity_minutes=10)
    print(f"{Fore.GREEN}✓ Token session created")
    
    # Initialize database
    db = FileDatabase(db_path)
    print(f"{Fore.GREEN}✓ Database initialized")
    
    # Create monitor
    event_handler = ProtectedMonitor(db, token_session, folder_path)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"{Fore.GREEN}✓ Monitor started\n")
    
    print(f"{Fore.CYAN}Protected Folder: {folder_path}")
    print(f"{Fore.CYAN}Token Validity: 10 minutes")
    print(f"{Fore.CYAN}Database: {db_path}\n")
    
    print(f"{Fore.YELLOW}Commands:")
    print(f"  'token' - Generate new token (enable writes)")
    print(f"  'status' - Show protection status")
    print(f"  'stats' - Show statistics")
    print(f"  'quit' - Stop protection\n")
    
    try:
        while True:
            cmd = input(f"{Fore.CYAN}> ").strip().lower()
            
            if cmd == 'token':
                token = token_session.generate_token(folder_path)
                print(f"{Fore.GREEN}✓ Token generated")
                print(f"{Fore.GREEN}  Valid for: 10 minutes")
                print(f"{Fore.GREEN}  Token: {token[:16]}...")
                print(f"{Fore.YELLOW}  File writes now ALLOWED\n")
            
            elif cmd == 'status':
                if token_session.is_valid():
                    remaining = (token_session.token_expiry - datetime.now()).seconds // 60
                    print(f"{Fore.GREEN}✓ Token ACTIVE")
                    print(f"{Fore.GREEN}  Time remaining: {remaining} minutes\n")
                else:
                    print(f"{Fore.RED}✗ Token EXPIRED")
                    print(f"{Fore.YELLOW}  Type 'token' to generate new token\n")
            
            elif cmd == 'stats':
                print(f"{Fore.CYAN}Protection Statistics:")
                print(f"{Fore.GREEN}  Allowed: {event_handler.allowed_count}")
                print(f"{Fore.RED}  Blocked: {event_handler.blocked_count}")
                
                events = db.get_events(limit=10)
                print(f"{Fore.CYAN}  Recent events: {len(events)}\n")
            
            elif cmd == 'quit':
                break
            
            else:
                print(f"{Fore.RED}Unknown command\n")
    
    except KeyboardInterrupt:
        pass
    
    print(f"\n{Fore.YELLOW}Stopping protection...")
    observer.stop()
    observer.join()
    db.close()
    
    print(f"{Fore.GREEN}Protection stopped")
    print(f"{Fore.CYAN}Final Statistics:")
    print(f"{Fore.GREEN}  Allowed: {event_handler.allowed_count}")
    print(f"{Fore.RED}  Blocked: {event_handler.blocked_count}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week4_protected_monitor.py <folder_path> [password]")
        sys.exit(1)
    
    folder = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else "MySecurePassword123!"
    
    run_protected_monitor(folder, password)
