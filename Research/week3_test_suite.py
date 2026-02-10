#!/usr/bin/env python3
"""
Week 3 - Test Suite
Tests all Week 3 components
"""

import os
import time
import tempfile
from colorama import Fore, init

from week3_database import FileDatabase
from week3_hash_calculator import calculate_hash, get_file_size
from week3_entropy_analyzer import calculate_entropy, is_encrypted

init(autoreset=True)

def test_hash_calculation():
    """Test 1: Hash calculation"""
    print(f"{Fore.YELLOW}Test 1: Hash Calculation")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Hello World")
        filepath = f.name
    
    hash_val = calculate_hash(filepath)
    expected = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    
    os.unlink(filepath)
    
    if hash_val == expected:
        print(f"{Fore.GREEN}✅ PASS\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL - Hash mismatch\n")
        return False

def test_entropy_normal():
    """Test 2: Entropy on normal file"""
    print(f"{Fore.YELLOW}Test 2: Entropy - Normal File")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("The quick brown fox jumps over the lazy dog. " * 10)
        filepath = f.name
    
    entropy = calculate_entropy(filepath)
    os.unlink(filepath)
    
    if 4.0 < entropy < 6.0:
        print(f"{Fore.GREEN}✅ PASS - Entropy: {entropy:.2f}\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL - Entropy: {entropy:.2f}\n")
        return False

def test_entropy_encrypted():
    """Test 3: Entropy on encrypted-like file"""
    print(f"{Fore.YELLOW}Test 3: Entropy - Encrypted File")
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
        # Random bytes (simulates encryption)
        import random
        f.write(bytes([random.randint(0, 255) for _ in range(1000)]))
        filepath = f.name
    
    entropy = calculate_entropy(filepath)
    encrypted = is_encrypted(entropy)
    os.unlink(filepath)
    
    if encrypted and entropy > 7.5:
        print(f"{Fore.GREEN}✅ PASS - Entropy: {entropy:.2f}, Detected: YES\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL - Entropy: {entropy:.2f}, Detected: {encrypted}\n")
        return False

def test_database():
    """Test 4: Database operations"""
    print(f"{Fore.YELLOW}Test 4: Database Operations")
    
    db = FileDatabase(':memory:')
    
    # Add file
    db.add_file('/test/file.txt', 'abc123', 1024, 5.2)
    
    # Log event
    db.log_event('/test/file.txt', 'CREATE', hash_after='abc123', entropy_after=5.2)
    
    # Query
    file_record = db.get_file('/test/file.txt')
    events = db.get_events()
    
    db.close()
    
    if file_record and events:
        print(f"{Fore.GREEN}✅ PASS\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL\n")
        return False

def test_file_monitoring():
    """Test 5: File monitoring (create 20 files)"""
    print(f"{Fore.YELLOW}Test 5: File Monitoring (20 files)")
    
    test_dir = tempfile.mkdtemp()
    db = FileDatabase(':memory:')
    
    # Create 20 test files
    for i in range(20):
        filepath = os.path.join(test_dir, f'test_{i}.txt')
        with open(filepath, 'w') as f:
            f.write(f"Test file {i}")
        
        # Process file
        hash_val = calculate_hash(filepath)
        size = get_file_size(filepath)
        entropy = calculate_entropy(filepath)
        
        db.add_file(filepath, hash_val, size, entropy)
        db.log_event(filepath, 'CREATE', hash_after=hash_val, entropy_after=entropy)
    
    # Check database
    events = db.get_events(limit=20)
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    db.close()
    
    if len(events) == 20:
        print(f"{Fore.GREEN}✅ PASS - 20 files processed\n")
        return True
    else:
        print(f"{Fore.RED}❌ FAIL - Only {len(events)} files processed\n")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Week 3 - Test Suite")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    tests = [
        test_hash_calculation,
        test_entropy_normal,
        test_entropy_encrypted,
        test_database,
        test_file_monitoring
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
    print(f"{Fore.GREEN}Passed: {passed}/5")
    print(f"{Fore.RED}Failed: {failed}/5")
    
    if failed == 0:
        print(f"\n{Fore.GREEN}🎉 ALL TESTS PASSED!")
        print(f"{Fore.GREEN}Week 3 Complete!")
    else:
        print(f"\n{Fore.RED}⚠️  Some tests failed")
    
    print(f"{Fore.CYAN}{'='*60}\n")

if __name__ == "__main__":
    run_all_tests()
