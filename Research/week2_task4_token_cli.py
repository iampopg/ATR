#!/usr/bin/env python3
"""
Week 2 - Task 4: Complete Token CLI
Command-line interface for token generation and validation
Integrates all Week 2 components
"""

import hashlib
import hmac
import os
import time
import json
from colorama import Fore, Style, init

init(autoreset=True)

# Import our Week 2 components
from week2_task1_master_key import MasterKeyDerivation
from week2_task2_token_generation import TokenGenerator
from week2_task3_proof_validation import ProofValidator

class TokenCLI:
    def __init__(self):
        self.mkd = MasterKeyDerivation()
        self.pv = ProofValidator()
        self.token_validity = 600  # 10 minutes
        
    def setup_master_key(self, password):
        """Setup master key from password"""
        master_key, salt = self.mkd.derive_master_key(password)
        return master_key, salt
    
    def generate_token_for_file(self, password, filepath, operation="write"):
        """Generate token for file access"""
        # Derive master key
        master_key, salt = self.setup_master_key(password)
        
        # Create token generator
        tg = TokenGenerator(master_key)
        
        # Generate nonces
        nonce_client = tg.generate_nonce()
        nonce_server = tg.generate_nonce()
        
        # Get current timestamp (rounded to 5-minute windows)
        timestamp = int(time.time() // 300) * 300
        
        # Generate token
        token = tg.generate_token(nonce_client, nonce_server, timestamp, filepath, operation)
        
        # Calculate expiry
        expiry_time = timestamp + self.token_validity
        
        return {
            'token': token,
            'nonce_client': nonce_client,
            'nonce_server': nonce_server,
            'timestamp': timestamp,
            'filepath': filepath,
            'operation': operation,
            'expiry': expiry_time,
            'salt': salt.hex()
        }
    
    def validate_token_for_file(self, password, token_data, provided_token):
        """Validate token for file access"""
        # Derive master key with stored salt
        salt = bytes.fromhex(token_data['salt'])
        master_key = self.mkd.derive_key_simple(password, salt)
        
        # Create token generator
        tg = TokenGenerator(master_key)
        
        # Regenerate expected token
        expected_token = tg.generate_token(
            token_data['nonce_client'],
            token_data['nonce_server'],
            token_data['timestamp'],
            token_data['filepath'],
            token_data['operation']
        )
        
        # Check if token matches
        if expected_token != provided_token:
            return False, "Invalid token"
        
        # Check if expired
        if time.time() > token_data['expiry']:
            return False, "Token expired"
        
        return True, "Token valid"
    
    def create_access_proof(self, token, challenge_id):
        """Create proof of token possession"""
        return self.pv.create_proof(token, challenge_id)

def main():
    """Main CLI interface"""
    cli = TokenCLI()
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}WEEK 2 - COMPLETE TOKEN SYSTEM CLI")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    while True:
        print(f"{Fore.YELLOW}Options:")
        print(f"{Fore.WHITE}1. 🔑 Generate Token for File")
        print(f"{Fore.WHITE}2. ✅ Validate Token")
        print(f"{Fore.WHITE}3. 🔐 Create Access Proof")
        print(f"{Fore.WHITE}4. 🧪 Run All Tests")
        print(f"{Fore.WHITE}5. ❌ Exit")
        
        choice = input(f"\n{Fore.CYAN}Enter choice (1-5): {Fore.WHITE}")
        
        if choice == '1':
            print(f"\n{Fore.YELLOW}Generate Token")
            password = input(f"{Fore.WHITE}Enter password: ")
            filepath = input(f"{Fore.WHITE}Enter file path: ")
            operation = input(f"{Fore.WHITE}Enter operation (read/write) [write]: ") or "write"
            
            token_data = cli.generate_token_for_file(password, filepath, operation)
            
            print(f"\n{Fore.GREEN}✅ Token Generated!")
            print(f"{Fore.WHITE}Token: {token_data['token']}")
            print(f"{Fore.WHITE}File: {token_data['filepath']}")
            print(f"{Fore.WHITE}Operation: {token_data['operation']}")
            print(f"{Fore.WHITE}Valid until: {time.ctime(token_data['expiry'])}")
            print(f"{Fore.YELLOW}Save this token data for validation!\n")
            
            # Save to file
            with open('token_data.json', 'w') as f:
                json.dump(token_data, f, indent=2)
            print(f"{Fore.GREEN}Token data saved to token_data.json\n")
        
        elif choice == '2':
            print(f"\n{Fore.YELLOW}Validate Token")
            
            # Load token data
            try:
                with open('token_data.json', 'r') as f:
                    token_data = json.load(f)
            except FileNotFoundError:
                print(f"{Fore.RED}❌ No token data found. Generate a token first!\n")
                continue
            
            password = input(f"{Fore.WHITE}Enter password: ")
            provided_token = input(f"{Fore.WHITE}Enter token: ")
            
            valid, message = cli.validate_token_for_file(password, token_data, provided_token)
            
            if valid:
                print(f"{Fore.GREEN}✅ {message}")
                print(f"{Fore.GREEN}Access granted to: {token_data['filepath']}\n")
            else:
                print(f"{Fore.RED}❌ {message}")
                print(f"{Fore.RED}Access denied!\n")
        
        elif choice == '3':
            print(f"\n{Fore.YELLOW}Create Access Proof")
            token = input(f"{Fore.WHITE}Enter token: ")
            challenge_id = input(f"{Fore.WHITE}Enter challenge ID: ")
            
            proof = cli.create_access_proof(token, challenge_id)
            
            print(f"\n{Fore.GREEN}✅ Proof Created!")
            print(f"{Fore.WHITE}Proof: {proof}")
            print(f"{Fore.YELLOW}Send this proof (not the token) to server\n")
        
        elif choice == '4':
            print(f"\n{Fore.YELLOW}Running All Tests...\n")
            
            # Run all test scripts
            import subprocess
            
            scripts = [
                'week2_task1_master_key.py',
                'week2_task2_token_generation.py',
                'week2_task3_proof_validation.py'
            ]
            
            for script in scripts:
                print(f"{Fore.CYAN}Running {script}...")
                subprocess.run(['python3', script])
                print()
        
        elif choice == '5':
            print(f"{Fore.GREEN}👋 Goodbye!")
            break
        
        else:
            print(f"{Fore.RED}❌ Invalid choice!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Exiting...")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}")