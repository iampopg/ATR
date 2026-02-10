#!/usr/bin/env python3
"""
Week 3 - Task 3: Hash Calculator
Calculates SHA256 hash of files
"""

import hashlib
import os

def calculate_hash(filepath, chunk_size=8192):
    """Calculate SHA256 hash of file"""
    if not os.path.exists(filepath):
        return None
    
    sha256 = hashlib.sha256()
    
    try:
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256.update(chunk)
        
        return sha256.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week3_hash_calculator.py <file_path>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"File: {filepath}")
    print(f"Size: {get_file_size(filepath)} bytes")
    print(f"Hash: {calculate_hash(filepath)}")
