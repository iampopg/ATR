#!/usr/bin/env python3
"""
Week 4 - Test Suite
Tests token-protected filesystem
"""

import os
import time
import tempfile
import shutil
from datetime import datetime, timedelta
from colorama import Fore, init

from week2_task1_master_key import MasterKeyDerivation
from week2_task2_token_generation import TokenGenerator
from week3_database import FileDatabase
from week4_protected_monitor import TokenSession

init(autoreset=True)

def test_token_session():
    """Test 1: Token session management"""
    print(f"{Fore.YELLOW}Test 1: Token Session Management")
    
    mkd = MasterKeyDerivation()
    master_key, _ = mkd.derive_master_key("TestPassword")
    
    session = TokenSession(master_key, validity_minutes=1)
    
    # No token initially
    if session.is_valid():
        print(f"{Fore.RED}❌ FAIL - Token should be invalid initially\n")
        return False
    
    # Generate token
    token = session.generate_token("/test/file.txt")
    
    # Should be valid now
    if not session.is_valid():
        print(f"{Fore.RED}❌ FAIL - Token should be valid after generation\n")
        return False
    
    print(f"{Fore.GREEN}✅ PASS\n")
    return True

def test_token_expiry():
    """Test 2: Token expiration"""
    print(f"{Fore.YELLOW}Test 2: Token Expiration")
    
    mkd = MasterKeyDerivation()
    master_key, _ = mkd.derive_master_key("TestPassword")
    
    session = TokenSession(master_key, validity_minutes=0)  # Expires immediately
    session.generate_token("/test/file.txt")
    
    # Manually expire
    session.token_expiry = datetime.now() - timedelta(seconds=1)
    
    if session.is_valid():
        print(f"{Fore.RED}❌ FAIL - Token should be expired\n")
        return False
    
    print(f"{Fore.GREEN}✅ PASS\n")
    return True

def test_write_without_token():
    """Test 3: Write blocked without token"""
    print(f"{Fore.YELLOW}Test 3: Write Blocked Without Token")
    
    mkd = MasterKeyDerivation()
    master_key, _ = mkd.derive_master_key("TestPassword")
    
    session = TokenSession(master_key)
    # Don't generate token
    
    if session.is_valid():
        print(f"{Fore.RED}❌ FAIL - Should not have valid token\n")
        return False
    
    print(f"{Fore.GREEN}✅ PASS - Write would be blocked\n")
    return True

def test_write_with_token():
    """Test 4: Write allowed with token"""
    print(f"{Fore.YELLOW}Test 4: Write Allowed With Token")
    
    mkd = MasterKeyDerivation()
    master_key, _ = mkd.derive_master_key("TestPassword")
    
    session = TokenSession(master_key)
    session.generate_token("/test/file.txt")
    
    if not session.is_valid():
        print(f"{Fore.RED}❌ FAIL - Should have valid token\n")
        return False
    
    print(f"{Fore.GREEN}✅ PASS - Write would be allowed\n")
    return True

def test_token_renewal():
    """Test 5: Token renewal"""
    print(f"{Fore.YELLOW}Test 5: Token Renewal")
    
    mkd = MasterKeyDerivation()
    master_key, _ = mkd.derive_master_key("TestPassword")
    
    session = TokenSession(master_key, validity_minutes=1)
    session.generate_token("/test/file.txt")
    
    original_expiry = session.token_expiry
    time.sleep(1)
    
    session.renew()
    
    if session.token_expiry <= original_expiry:
        print(f"{Fore.RED}❌ FAIL - Token not renewed\n")
        return False
    
    print(f"{Fore.GREEN}✅ PASS\n")
    return True

def test_database_logging():
    """Test 6: Database logs blocked attempts"""
    print(f"{Fore.YELLOW}Test 6: Database Logging")
    
    db = FileDatabase(':memory:')
    
    # Log blocked attempt
    db.log_event('/test/file.txt', 'BLOCKED_MODIFY')
    
    # Check if logged
    events = db.get_events()
    
    db.close()
    
    if len(events) > 0 and 'BLOCKED' in events[0][2]:
        print(f"{Fore.GREEN}✅ PASS\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL\n")
        return False

def test_integration():
    """Test 7: Full integration test"""
    print(f"{Fore.YELLOW}Test 7: Full Integration")
    
    # Create test directory
    test_dir = tempfile.mkdtemp()
    
    try:
        # Initialize components
        mkd = MasterKeyDerivation()
        master_key, _ = mkd.derive_master_key("TestPassword")
        session = TokenSession(master_key)
        db = FileDatabase(':memory:')
        
        # Test 1: Write without token (should fail)
        filepath = os.path.join(test_dir, 'test1.txt')
        write_allowed = session.is_valid()
        
        if write_allowed:
            print(f"{Fore.RED}❌ FAIL - Write should be blocked\n")
            return False
        
        # Test 2: Generate token
        session.generate_token(filepath)
        
        # Test 3: Write with token (should succeed)
        write_allowed = session.is_valid()
        
        if not write_allowed:
            print(f"{Fore.RED}❌ FAIL - Write should be allowed\n")
            return False
        
        # Actually write file
        with open(filepath, 'w') as f:
            f.write("Test content")
        
        # Log to database
        db.log_event(filepath, 'CREATE')
        
        # Verify
        events = db.get_events()
        
        db.close()
        
        if len(events) > 0:
            print(f"{Fore.GREEN}✅ PASS\n")
            return True
        else:
            print(f"{Fore.RED}❌ FAIL\n")
            return False
    
    finally:
        shutil.rmtree(test_dir)

def run_all_tests():
    """Run all Week 4 tests"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Week 4 - Test Suite")
    print(f"{Fore.CYAN}Token-Protected Filesystem")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    tests = [
        test_token_session,
        test_token_expiry,
        test_write_without_token,
        test_write_with_token,
        test_token_renewal,
        test_database_logging,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Test Results")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}Passed: {passed}/7")
    print(f"{Fore.RED}Failed: {failed}/7")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED!")
        print(f"{Fore.GREEN}Week 4 Complete!")
    else:
        print(f"\n{Fore.RED}⚠️  Some tests failed")
    
    print(f"{Fore.CYAN}{'='*60}\n")

if __name__ == "__main__":
    run_all_tests()
