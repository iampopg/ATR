#!/usr/bin/env python3
"""File Protector - Protects ARCHITECTURE.md, validates tokens"""

import os
import json
import time
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Protected file
PROTECTED_FILE = "/home/popg/projects/anti-ransomW/ARCHITECTURE.md"
PASSWORD = "MySecurePassword123!"
USED_TOKENS_FILE = "/tmp/used_tokens.json"
SALT = b"anti_ransomware_2026"

def derive_master_key(password):
    """Derive master key using Argon2id"""
    master_key = hash_secret_raw(
        secret=password.encode(),
        salt=SALT,
        time_cost=2,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )
    return master_key

def load_used_tokens():
    """Load list of used tokens"""
    if os.path.exists(USED_TOKENS_FILE):
        with open(USED_TOKENS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_used_token(token):
    """Mark token as used"""
    used = load_used_tokens()
    used.append(token)
    with open(USED_TOKENS_FILE, 'w') as f:
        json.dump(used, f)

def generate_current_token(filepath, password, nonce_hex):
    """Generate current valid token using HKDF"""
    master_key = derive_master_key(password)
    time_window = int(time.time() // 30)
    
    nonce = bytes.fromhex(nonce_hex)
    info = filepath.encode() + str(time_window).encode()
    
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=16,
        salt=nonce,
        info=info
    )
    return hkdf.derive(master_key).hex()

def validate_token(token, nonce_hex, requested_file):
    """Validate if token is valid for requested file"""
    
    # Check if token already used
    used_tokens = load_used_tokens()
    if token in used_tokens:
        print(f"❌ DENIED: Token already used")
        return False
    
    # Check if token matches current time window
    expected_token = generate_current_token(requested_file, PASSWORD, nonce_hex)
    
    if token == expected_token:
        # Mark token as used
        save_used_token(token)
        print(f"✅ ACCESS GRANTED to {requested_file}")
        print(f"⚠️  Token now expired (one-time use)")
        return True
    else:
        print(f"❌ DENIED: Invalid or expired token")
        return False

if __name__ == "__main__":
    import sys
    
    print(f"File Protector - Protecting: {PROTECTED_FILE}\n")
    
    if len(sys.argv) < 3:
        print("Usage: python file_protector.py <token> <nonce>")
        print("\nGenerate token first using token_generator.py")
        sys.exit(1)
    
    token = sys.argv[1]
    nonce_hex = sys.argv[2]
    
    # Always check against protected file
    validate_token(token, nonce_hex, PROTECTED_FILE)
