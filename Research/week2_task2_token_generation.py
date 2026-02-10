#!/usr/bin/env python3
"""
Week 2 - Task 2: HKDF Token Generation
Dynamic token generation using HKDF (like WPA2)
"""

import hashlib
import hmac
import os
import time
from colorama import Fore, init

init(autoreset=True)

class TokenGenerator:
    def __init__(self, master_key):
        self.master_key = master_key
        
    def hkdf_extract(self, salt, input_key_material):
        """HKDF Extract step"""
        if salt is None or len(salt) == 0:
            salt = bytes([0] * 32)
        return hmac.new(salt, input_key_material, hashlib.sha256).digest()
    
    def hkdf_expand(self, pseudo_random_key, info, length):
        """HKDF Expand step"""
        output = b""
        counter = 1
        
        while len(output) < length:
            output += hmac.new(
                pseudo_random_key,
                output[-32:] + info + bytes([counter]),
                hashlib.sha256
            ).digest()
            counter += 1
        
        return output[:length]
    
    def hkdf(self, salt, info, length=32):
        """Full HKDF implementation"""
        prk = self.hkdf_extract(salt, self.master_key)
        return self.hkdf_expand(prk, info, length)
    
    def generate_token(self, nonce_client, nonce_server, timestamp, filepath, operation="write"):
        """
        Generate dynamic token (WPA2-style)
        Both client and server can compute this independently
        """
        # Combine all inputs
        info = f"{nonce_client}:{nonce_server}:{timestamp}:{filepath}:{operation}".encode()
        
        # Use timestamp as salt for time-based uniqueness
        salt = str(timestamp).encode()
        
        # Generate token using HKDF
        token = self.hkdf(salt, info, length=16)
        
        return token.hex()
    
    def generate_nonce(self):
        """Generate random nonce"""
        return os.urandom(16).hex()

def test_token_generation():
    """Test HKDF token generation"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}WEEK 2 - TASK 2: HKDF Token Generation")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    # Create master key
    master_key = hashlib.sha256(b"MySecurePassword123!").digest()
    tg = TokenGenerator(master_key)
    
    # Test 1: Generate token
    print(f"{Fore.YELLOW}Test 1: Generate Token")
    nonce_client = tg.generate_nonce()
    nonce_server = tg.generate_nonce()
    timestamp = int(time.time())
    filepath = "/home/user/documents/report.docx"
    
    token = tg.generate_token(nonce_client, nonce_server, timestamp, filepath)
    
    print(f"{Fore.WHITE}Nonce Client: {nonce_client[:16]}...")
    print(f"{Fore.WHITE}Nonce Server: {nonce_server[:16]}...")
    print(f"{Fore.WHITE}Timestamp: {timestamp}")
    print(f"{Fore.WHITE}File: {filepath}")
    print(f"{Fore.WHITE}Token: {token}")
    print(f"{Fore.GREEN}✅ Token generated!\n")
    
    # Test 2: Same inputs = same token (deterministic)
    print(f"{Fore.YELLOW}Test 2: Deterministic Token Generation")
    token2 = tg.generate_token(nonce_client, nonce_server, timestamp, filepath)
    if token == token2:
        print(f"{Fore.GREEN}✅ Same inputs produce same token!\n")
    else:
        print(f"{Fore.RED}❌ Tokens don't match (BUG!)\n")
    
    # Test 3: Different nonce = different token
    print(f"{Fore.YELLOW}Test 3: Different Nonce = Different Token")
    nonce_client2 = tg.generate_nonce()
    token3 = tg.generate_token(nonce_client2, nonce_server, timestamp, filepath)
    if token != token3:
        print(f"{Fore.GREEN}✅ Different nonce produces different token!\n")
    else:
        print(f"{Fore.RED}❌ Same token produced (BUG!)\n")
    
    # Test 4: Different file = different token
    print(f"{Fore.YELLOW}Test 4: Different File = Different Token")
    filepath2 = "/home/user/documents/secret.txt"
    token4 = tg.generate_token(nonce_client, nonce_server, timestamp, filepath2)
    if token != token4:
        print(f"{Fore.GREEN}✅ Different file produces different token!\n")
    else:
        print(f"{Fore.RED}❌ Same token produced (BUG!)\n")
    
    # Test 5: Different timestamp = different token
    print(f"{Fore.YELLOW}Test 5: Different Timestamp = Different Token")
    timestamp2 = timestamp + 300  # 5 minutes later
    token5 = tg.generate_token(nonce_client, nonce_server, timestamp2, filepath)
    if token != token5:
        print(f"{Fore.GREEN}✅ Different timestamp produces different token!\n")
    else:
        print(f"{Fore.RED}❌ Same token produced (BUG!)\n")
    
    # Test 6: Both sides can compute same token
    print(f"{Fore.YELLOW}Test 6: Client and Server Compute Same Token")
    # Simulate client side
    client_tg = TokenGenerator(master_key)
    client_token = client_tg.generate_token(nonce_client, nonce_server, timestamp, filepath)
    
    # Simulate server side
    server_tg = TokenGenerator(master_key)
    server_token = server_tg.generate_token(nonce_client, nonce_server, timestamp, filepath)
    
    if client_token == server_token:
        print(f"{Fore.GREEN}✅ Client and server compute same token!\n")
    else:
        print(f"{Fore.RED}❌ Tokens don't match (BUG!)\n")
    
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}TASK 2 COMPLETE: HKDF Token Generation Working!")
    print(f"{Fore.GREEN}{'='*60}")

if __name__ == "__main__":
    test_token_generation()