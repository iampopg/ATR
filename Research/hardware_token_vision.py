#!/usr/bin/env python3
"""
Hardware Token Simulation (Your Vision!)
Simulates YubiKey-style hardware token for file protection
"""

import os
import time
import hashlib
import hmac
from colorama import Fore, init

init(autoreset=True)

class HardwareTokenSimulator:
    """Simulates a physical hardware token (like YubiKey)"""
    
    def __init__(self, token_id="TOKEN_001"):
        self.token_id = token_id
        # Master key stored INSIDE hardware (never extracted)
        self._master_key = self._generate_hardware_key()
        self.is_plugged_in = False
        self.button_pressed = False
        
    def _generate_hardware_key(self):
        """Generate unique key for this hardware token"""
        # In real hardware, this is burned into chip at factory
        return hashlib.sha256(f"HARDWARE_TOKEN_{self.token_id}".encode()).digest()
    
    def plug_in(self):
        """Simulate plugging in USB token"""
        self.is_plugged_in = True
        print(f"{Fore.GREEN}🔌 Hardware token plugged in!")
        print(f"{Fore.WHITE}   Token ID: {self.token_id}")
    
    def unplug(self):
        """Simulate unplugging USB token"""
        self.is_plugged_in = False
        self.button_pressed = False
        print(f"{Fore.YELLOW}🔌 Hardware token unplugged!")
    
    def press_button(self):
        """Simulate pressing physical button on token"""
        if not self.is_plugged_in:
            print(f"{Fore.RED}❌ Token not plugged in!")
            return False
        
        print(f"{Fore.GREEN}👆 Button pressed on hardware token!")
        self.button_pressed = True
        
        # Button press is valid for 10 seconds
        import threading
        def reset_button():
            time.sleep(10)
            self.button_pressed = False
        
        threading.Thread(target=reset_button, daemon=True).start()
        return True
    
    def generate_challenge_response(self, challenge):
        """
        Hardware token generates response to challenge
        Master key NEVER leaves the device!
        """
        if not self.is_plugged_in:
            return None
        
        if not self.button_pressed:
            return None
        
        # Compute response using internal master key
        response = hmac.new(
            self._master_key,
            challenge.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return response
    
    def get_token_id(self):
        """Get token ID (public information)"""
        return self.token_id if self.is_plugged_in else None


class FileProtectionSystem:
    """File protection system using hardware token"""
    
    def __init__(self):
        self.registered_tokens = {}  # token_id -> expected_responses
        self.protected_files = set()
    
    def register_token(self, hardware_token):
        """Register a hardware token with the system"""
        if not hardware_token.is_plugged_in:
            print(f"{Fore.RED}❌ Token must be plugged in to register!")
            return False
        
        print(f"{Fore.CYAN}📝 Registering hardware token...")
        
        # Challenge-response to verify token
        challenge = os.urandom(16).hex()
        print(f"{Fore.WHITE}   Challenge: {challenge[:16]}...")
        
        print(f"{Fore.YELLOW}   Press button on token to confirm...")
        input(f"{Fore.CYAN}   [Press Enter after pressing button]")
        
        response = hardware_token.generate_challenge_response(challenge)
        
        if response:
            self.registered_tokens[hardware_token.token_id] = {
                'challenge': challenge,
                'response': response
            }
            print(f"{Fore.GREEN}✅ Token registered successfully!")
            return True
        else:
            print(f"{Fore.RED}❌ Registration failed!")
            return False
    
    def protect_file(self, filepath):
        """Protect a file with hardware token"""
        self.protected_files.add(filepath)
        print(f"{Fore.GREEN}🔒 File protected: {filepath}")
    
    def request_file_access(self, filepath, hardware_token):
        """Request access to protected file"""
        if filepath not in self.protected_files:
            print(f"{Fore.GREEN}✅ File not protected - access granted")
            return True
        
        print(f"{Fore.YELLOW}🔒 Protected file access requested: {filepath}")
        
        # Check if token is plugged in
        if not hardware_token.is_plugged_in:
            print(f"{Fore.RED}❌ Hardware token not detected!")
            print(f"{Fore.RED}   Please plug in your token")
            return False
        
        # Check if token is registered
        token_id = hardware_token.get_token_id()
        if token_id not in self.registered_tokens:
            print(f"{Fore.RED}❌ Token not registered!")
            return False
        
        # Request button press
        print(f"{Fore.CYAN}👆 Press button on hardware token to access file...")
        input(f"{Fore.CYAN}   [Press Enter after pressing button]")
        
        # Generate new challenge
        challenge = os.urandom(16).hex()
        response = hardware_token.generate_challenge_response(challenge)
        
        if response:
            print(f"{Fore.GREEN}✅ Hardware token authenticated!")
            print(f"{Fore.GREEN}✅ Access granted to: {filepath}")
            return True
        else:
            print(f"{Fore.RED}❌ Authentication failed!")
            print(f"{Fore.RED}   Did you press the button?")
            return False


def demo_hardware_token_system():
    """Demonstrate hardware token protection"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}HARDWARE TOKEN FILE PROTECTION DEMO")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    # Create hardware token (simulates physical device)
    token = HardwareTokenSimulator("YUBIKEY_12345")
    
    # Create protection system
    protection = FileProtectionSystem()
    
    print(f"{Fore.YELLOW}Scenario 1: Setup and Registration")
    print(f"{Fore.YELLOW}{'='*40}\n")
    
    # Plug in token
    token.plug_in()
    
    # Register token
    token.press_button()
    protection.register_token(token)
    
    # Protect files
    print(f"\n{Fore.YELLOW}Protecting files...")
    protection.protect_file("/home/user/documents/report.docx")
    protection.protect_file("/home/user/documents/secret.txt")
    
    print(f"\n{Fore.YELLOW}Scenario 2: Legitimate User Access")
    print(f"{Fore.YELLOW}{'='*40}\n")
    
    # User wants to access file
    print(f"{Fore.WHITE}User wants to edit report.docx...")
    token.press_button()
    protection.request_file_access("/home/user/documents/report.docx", token)
    
    print(f"\n{Fore.YELLOW}Scenario 3: Ransomware Attack (Token Unplugged)")
    print(f"{Fore.YELLOW}{'='*40}\n")
    
    # User unplugs token and leaves
    token.unplug()
    print(f"{Fore.WHITE}User left office (token unplugged)...\n")
    
    # Ransomware tries to access
    print(f"{Fore.RED}🦠 Ransomware tries to encrypt files...")
    protection.request_file_access("/home/user/documents/report.docx", token)
    
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}RESULT: Files protected by physical token!")
    print(f"{Fore.GREEN}Ransomware cannot access without hardware!")
    print(f"{Fore.GREEN}{'='*60}\n")


def show_real_world_usage():
    """Show real-world usage scenarios"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}REAL-WORLD USAGE SCENARIOS")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    scenarios = [
        {
            "title": "Office Worker",
            "description": "You arrive at office, plug in token, work all day. When you leave, unplug token. Files are locked until you return.",
            "security": "Even if ransomware infects computer overnight, files stay protected!"
        },
        {
            "title": "Remote Worker",
            "description": "Token stays in your pocket. Only plug in when accessing sensitive files. Unplug when done.",
            "security": "Ransomware running in background cannot access files without token!"
        },
        {
            "title": "Shared Computer",
            "description": "Multiple users, each with their own token. Only your token can access your files.",
            "security": "Other users cannot access your files, even with admin rights!"
        },
        {
            "title": "Laptop Theft",
            "description": "Laptop stolen, but token is with you. Thief cannot access protected files.",
            "security": "Physical separation = ultimate security!"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{Fore.YELLOW}{i}. {scenario['title']}")
        print(f"{Fore.WHITE}   {scenario['description']}")
        print(f"{Fore.GREEN}   🛡️  {scenario['security']}\n")


if __name__ == "__main__":
    print(f"{Fore.CYAN}HARDWARE TOKEN VISION - YOUR IDEA!")
    print(f"{Fore.CYAN}This is what you'll build in Month 6\n")
    
    choice = input(f"{Fore.YELLOW}1. Run Demo\n2. Show Real-World Scenarios\n3. Both\n\nChoice: ")
    
    if choice in ['1', '3']:
        demo_hardware_token_system()
    
    if choice in ['2', '3']:
        show_real_world_usage()
    
    print(f"\n{Fore.GREEN}✅ This is your vision - hardware-based protection!")
    print(f"{Fore.YELLOW}📅 Week 2: Build token system (software)")
    print(f"{Fore.YELLOW}📅 Month 6: Add hardware token support")