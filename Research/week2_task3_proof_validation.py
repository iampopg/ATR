#!/usr/bin/env python3
"""
Week 2 - Task 3: HMAC Proof Validation
Prove token possession WITHOUT transmitting the token
"""

import hashlib
import hmac
import os
from colorama import Fore, init

init(autoreset=True)

class ProofValidator:
    def __init__(self):
        pass
    
    def create_proof(self, token, challenge_id):
        """
        Create proof of token possession
        Token is never transmitted - only the proof
        """
        proof = hmac.new(
            token.encode() if isinstance(token, str) else token,
            challenge_id.encode() if isinstance(challenge_id, str) else challenge_id,
            hashlib.sha256
        ).hexdigest()[:16]  # First 16 chars
        
        return proof
    
    def validate_proof(self, expected_token, challenge_id, received_proof):
        """
        Validate proof without seeing the actual token
        Server computes expected proof and compares
        """
        expected_proof = self.create_proof(expected_token, challenge_id)
        
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_proof, received_proof)
    
    def generate_challenge(self):
        """Generate random challenge ID"""
        return os.urandom(16).hex()

def test_proof_validation():
    """Test HMAC proof validation"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}WEEK 2 - TASK 3: HMAC Proof Validation")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    pv = ProofValidator()
    
    # Test 1: Create and validate proof
    print(f"{Fore.YELLOW}Test 1: Create and Validate Proof")
    token = "a7b3c4d5e6f7g8h9"
    challenge_id = pv.generate_challenge()
    
    # Client creates proof
    proof = pv.create_proof(token, challenge_id)
    
    print(f"{Fore.WHITE}Token: {token}")
    print(f"{Fore.WHITE}Challenge ID: {challenge_id}")
    print(f"{Fore.WHITE}Proof: {proof}")
    
    # Server validates proof
    if pv.validate_proof(token, challenge_id, proof):
        print(f"{Fore.GREEN}✅ Proof validated successfully!\n")
    else:
        print(f"{Fore.RED}❌ Proof validation failed!\n")
    
    # Test 2: Wrong token = invalid proof
    print(f"{Fore.YELLOW}Test 2: Wrong Token = Invalid Proof")
    wrong_token = "wrong_token_123"
    if not pv.validate_proof(wrong_token, challenge_id, proof):
        print(f"{Fore.GREEN}✅ Wrong token correctly rejected!\n")
    else:
        print(f"{Fore.RED}❌ Wrong token accepted (BUG!)\n")
    
    # Test 3: Modified proof = invalid
    print(f"{Fore.YELLOW}Test 3: Modified Proof = Invalid")
    modified_proof = proof[:-1] + "x"  # Change last character
    if not pv.validate_proof(token, challenge_id, modified_proof):
        print(f"{Fore.GREEN}✅ Modified proof correctly rejected!\n")
    else:
        print(f"{Fore.RED}❌ Modified proof accepted (BUG!)\n")
    
    # Test 4: Different challenge = different proof
    print(f"{Fore.YELLOW}Test 4: Different Challenge = Different Proof")
    challenge_id2 = pv.generate_challenge()
    proof2 = pv.create_proof(token, challenge_id2)
    if proof != proof2:
        print(f"{Fore.GREEN}✅ Different challenge produces different proof!\n")
    else:
        print(f"{Fore.RED}❌ Same proof produced (BUG!)\n")
    
    # Test 5: Replay attack prevention
    print(f"{Fore.YELLOW}Test 5: Replay Attack Prevention")
    # Attacker intercepts proof and tries to reuse it with different challenge
    new_challenge = pv.generate_challenge()
    if not pv.validate_proof(token, new_challenge, proof):
        print(f"{Fore.GREEN}✅ Replay attack prevented!\n")
    else:
        print(f"{Fore.RED}❌ Replay attack succeeded (BUG!)\n")
    
    # Test 6: Demonstrate security - token never transmitted
    print(f"{Fore.YELLOW}Test 6: Security Demonstration")
    print(f"{Fore.WHITE}Scenario: Client wants to prove they have the token")
    print(f"{Fore.WHITE}1. Server sends challenge: {challenge_id}")
    print(f"{Fore.WHITE}2. Client computes proof: {proof}")
    print(f"{Fore.WHITE}3. Client sends ONLY proof (not token)")
    print(f"{Fore.WHITE}4. Server validates proof")
    print(f"{Fore.GREEN}✅ Token never transmitted - secure!\n")
    
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}TASK 3 COMPLETE: HMAC Proof Validation Working!")
    print(f"{Fore.GREEN}{'='*60}")

if __name__ == "__main__":
    test_proof_validation()