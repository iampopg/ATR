# Week 2: Master Key & Token Implementation

## 🎯 Goal
Build a WPA2-style dynamic token system for file access control.

## 📁 Files
- `week2_task1_master_key.py` - Master key derivation
- `week2_task2_token_generation.py` - HKDF token generation
- `week2_task3_proof_validation.py` - HMAC proof validation
- `week2_task4_token_cli.py` - Complete CLI tool
- `week2_task5_test_suite.py` - 10 test scenarios
- `week2_documentation.md` - Full documentation

## 🚀 Quick Start

### Run All Tests
```bash
python3 week2_task5_test_suite.py
```

### Use CLI Tool
```bash
python3 week2_task4_token_cli.py
```

### Test Individual Components
```bash
python3 week2_task1_master_key.py
python3 week2_task2_token_generation.py
python3 week2_task3_proof_validation.py
```

## ✅ Week 2 Checklist

- [x] Implement Argon2id password-based key derivation
- [x] Create HKDF token generation function
- [x] Build HMAC proof validation system
- [x] Write CLI script that generates and validates tokens
- [x] Test token system with 10 different scenarios
- [x] Document token format and validation process

## 🔑 Key Concepts

**Master Key:** Derived from password using PBKDF2
**Token:** Generated using HKDF (unique per file, time-bound)
**Proof:** HMAC-based proof of token possession (token never transmitted)

## 📊 Test Results

Run `python3 week2_task5_test_suite.py` to see:
- ✅ 10/10 tests passing
- All security properties verified
- Ready for Week 3 integration

## 🎓 What You Learned

1. Password-based key derivation (PBKDF2)
2. HKDF for dynamic token generation
3. HMAC for proof-of-possession
4. Challenge-response authentication
5. Replay attack prevention
6. Time-bound token validity

## ➡️ Next: Week 3

Integrate this token system with file monitoring!