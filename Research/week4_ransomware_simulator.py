#!/usr/bin/env python3
"""
Week 4 - Ransomware Simulator
Simulates ransomware behavior for testing protection
"""

import os
import time
import random
from colorama import Fore, init

init(autoreset=True)

def simulate_ransomware(target_folder, num_files=10, delay=0.5):
    """Simulate ransomware encrypting files"""
    
    print(f"{Fore.RED}{'='*60}")
    print(f"{Fore.RED}RANSOMWARE SIMULATION")
    print(f"{Fore.RED}{'='*60}\n")
    
    print(f"{Fore.YELLOW}Target: {target_folder}")
    print(f"{Fore.YELLOW}Files to encrypt: {num_files}")
    print(f"{Fore.YELLOW}Delay: {delay}s between files\n")
    
    print(f"{Fore.RED}Starting attack in 3 seconds...")
    time.sleep(3)
    
    encrypted_count = 0
    blocked_count = 0
    
    # Try to encrypt files
    for i in range(num_files):
        filepath = os.path.join(target_folder, f'document_{i}.txt')
        
        try:
            # Try to create/modify file (simulating encryption)
            with open(filepath, 'wb') as f:
                # Write random bytes (simulates encrypted data)
                f.write(bytes([random.randint(0, 255) for _ in range(1000)]))
            
            encrypted_count += 1
            print(f"{Fore.RED}[ENCRYPTED] {filepath}")
        
        except PermissionError:
            blocked_count += 1
            print(f"{Fore.GREEN}[BLOCKED] {filepath} - Permission denied")
        
        except Exception as e:
            blocked_count += 1
            print(f"{Fore.YELLOW}[FAILED] {filepath} - {e}")
        
        time.sleep(delay)
    
    # Results
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Attack Results")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.RED}Files encrypted: {encrypted_count}/{num_files}")
    print(f"{Fore.GREEN}Files protected: {blocked_count}/{num_files}")
    
    success_rate = (blocked_count / num_files) * 100
    print(f"\n{Fore.CYAN}Protection Success Rate: {success_rate:.0f}%")
    
    if success_rate >= 80:
        print(f"{Fore.GREEN}✓ Protection EFFECTIVE!")
    elif success_rate >= 50:
        print(f"{Fore.YELLOW}⚠ Protection PARTIAL")
    else:
        print(f"{Fore.RED}✗ Protection FAILED")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python week4_ransomware_simulator.py <target_folder> [num_files]")
        sys.exit(1)
    
    folder = sys.argv[1]
    num_files = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    simulate_ransomware(folder, num_files)
