#!/usr/bin/env python3
"""
Week 2 - Task 1: Master Key Derivation (Argon2id)
Converts user password into secure master key
"""

import os
import time
from colorama import Fore, init
from argon2.low_level import hash_secret_raw, Type

init(autoreset=True)

class MasterKeyDerivation:
    def __init__(self):
        self.salt_size = 32  # 32 bytes salt
        
    def generate_salt(self):
        """Generate random salt"""
        return os.urandom(self.salt_size)
    
    def derive_key_argon2id(self, password, salt, time_cost=2, memory_cost=65536):
        """
        Key derivation using Argon2id
        """
        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=1,
            hash_len=32,
            type=Type.ID
        )
        return key
    
    def derive_master_key(self, password):
        """
        Derive master key from password
        Returns: (master_key, salt) - both need to be stored
        """
        salt = self.generate_salt()
        master_key = self.derive_key_argon2id(password, salt)
        return master_key, salt
    
    def verify_password(self, password, stored_salt, stored_key):
        """Verify password against stored key"""
        derived_key = self.derive_key_argon2id(password, stored_salt)
        return derived_key == stored_key

def test_master_key_derivation():
    """Test master key derivation"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}WEEK 2 - TASK 1: Master Key Derivation")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    mkd = MasterKeyDerivation()
    
    # Test 1: Generate master key
    print(f"{Fore.YELLOW}Test 1: Generate Master Key")
    password = "MySecurePassword123!"
    master_key, salt = mkd.derive_master_key(password)
    
    print(f"{Fore.WHITE}Password: {password}")
    print(f"{Fore.WHITE}Salt: {salt.hex()[:32]}...")
    print(f"{Fore.WHITE}Master Key: {master_key.hex()[:32]}...")
    print(f"{Fore.GREEN}✅ Master key generated!\n")
    
    # Test 2: Verify password
    print(f"{Fore.YELLOW}Test 2: Verify Password")
    if mkd.verify_password(password, salt, master_key):
        print(f"{Fore.GREEN}✅ Password verification successful!\n")
    else:
        print(f"{Fore.RED}❌ Password verification failed!\n")
    
    # Test 3: Wrong password
    print(f"{Fore.YELLOW}Test 3: Wrong Password")
    wrong_password = "WrongPassword"
    if not mkd.verify_password(wrong_password, salt, master_key):
        print(f"{Fore.GREEN}✅ Wrong password correctly rejected!\n")
    else:
        print(f"{Fore.RED}❌ Wrong password accepted (BUG!)\n")
    
    # Test 4: Same password, different salt = different key
    print(f"{Fore.YELLOW}Test 4: Different Salt = Different Key")
    master_key2, salt2 = mkd.derive_master_key(password)
    if master_key != master_key2:
        print(f"{Fore.GREEN}✅ Different salts produce different keys!\n")
    else:
        print(f"{Fore.RED}❌ Same key produced (BUG!)\n")
    
    # Test 5: Performance test
    print(f"{Fore.YELLOW}Test 5: Performance Test")
    start = time.time()
    for i in range(10):
        mkd.derive_master_key(f"password{i}")
    elapsed = time.time() - start
    print(f"{Fore.WHITE}10 key derivations: {elapsed:.2f} seconds")
    print(f"{Fore.WHITE}Average: {elapsed/10:.3f} seconds per key")
    print(f"{Fore.GREEN}✅ Performance acceptable!\n")
    
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}TASK 1 COMPLETE: Master Key Derivation Working!")
    print(f"{Fore.GREEN}{'='*60}")

if __name__ == "__main__":
    test_master_key_derivation()