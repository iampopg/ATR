#!/usr/bin/env python3
"""Token Generator - Generates access tokens for files"""

import time
import os
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

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

def generate_token_for_file(filepath, password="MySecurePassword123!"):
    """Generate time-based token using HKDF"""
    master_key = derive_master_key(password)
    
    # Token changes every 30 seconds
    time_window = int(time.time() // 30)
    
    # Generate nonces (in real system, these would be exchanged)
    nonce = os.urandom(16)
    
    # Use HKDF for proper key derivation
    info = filepath.encode() + str(time_window).encode()
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=16,
        salt=nonce,
        info=info
    )
    token = hkdf.derive(master_key).hex()
    
    print(f"Token generated for: {filepath}")
    print(f"Token: {token}")
    print(f"Nonce: {nonce.hex()}")
    print(f"Valid for: 30 seconds")
    print(f"One-time use only!")
    print(f"\nUse: python file_protector.py {token} {nonce.hex()}")
    
    return token, nonce.hex()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python token_generator.py <filepath>")
        print("Example: python token_generator.py /home/popg/projects/anti-ransomW/ARCHITECTURE.md")
        sys.exit(1)
    
    filepath = sys.argv[1]
    generate_token_for_file(filepath)
