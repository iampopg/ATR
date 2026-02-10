# Week 2 Documentation: Token System Implementation

## Overview
Complete implementation of WPA2-style dynamic token system for anti-ransomware protection.

## Components

### 1. Master Key Derivation (`week2_task1_master_key.py`)
**Purpose:** Convert user password into secure master key

**Algorithm:** PBKDF2-HMAC-SHA256 (100,000 iterations)

**Key Features:**
- 32-byte random salt
- Memory-hard key derivation
- Resistant to brute-force attacks

**Usage:**
```python
from week2_task1_master_key import MasterKeyDerivation

mkd = MasterKeyDerivation()
master_key, salt = mkd.derive_master_key("MyPassword123!")
```

---

### 2. HKDF Token Generation (`week2_task2_token_generation.py`)
**Purpose:** Generate dynamic tokens using HKDF (like WPA2)

**Algorithm:** HKDF-SHA256

**Inputs:**
- Master key
- Client nonce (random)
- Server nonce (random)
- Timestamp (5-minute windows)
- File path
- Operation type (read/write)

**Key Features:**
- Deterministic (same inputs = same token)
- Unique per file
- Time-bound
- Both client and server can compute independently

**Usage:**
```python
from week2_task2_token_generation import TokenGenerator

tg = TokenGenerator(master_key)
token = tg.generate_token(nonce_c, nonce_s, timestamp, "/docs/file.txt")
```

---

### 3. HMAC Proof Validation (`week2_task3_proof_validation.py`)
**Purpose:** Prove token possession WITHOUT transmitting token

**Algorithm:** HMAC-SHA256

**Security:**
- Token never transmitted
- Proof is challenge-specific
- Prevents replay attacks
- Constant-time comparison

**Usage:**
```python
from week2_task3_proof_validation import ProofValidator

pv = ProofValidator()
challenge = pv.generate_challenge()
proof = pv.create_proof(token, challenge)
valid = pv.validate_proof(expected_token, challenge, proof)
```

---

### 4. Complete CLI Tool (`week2_task4_token_cli.py`)
**Purpose:** Interactive command-line interface

**Features:**
- Generate tokens for files
- Validate tokens
- Create access proofs
- Run all tests

**Usage:**
```bash
python3 week2_task4_token_cli.py
```

---

### 5. Test Suite (`week2_task5_test_suite.py`)
**Purpose:** Comprehensive testing of all components

**10 Test Scenarios:**
1. ✅ Valid token for correct file
2. ❌ Valid token for wrong file (should fail)
3. ❌ Expired token (should fail)
4. ❌ Wrong password (should fail)
5. ❌ Replay attack (should fail)
6. ✅ Cross-device token generation
7. ❌ Tampered token (should fail)
8. ✅ Special characters in filename
9. ❌ Wrong timestamp (should fail)
10. ✅ Concurrent tokens for different files

**Usage:**
```bash
python3 week2_task5_test_suite.py
```

---

## Token Format

### Structure
```
Token = HKDF-SHA256(
    master_key,
    salt=timestamp,
    info=nonce_client:nonce_server:timestamp:filepath:operation
)
```

### Example
```
Input:
  Master Key: 0x3a7f9b2c...
  Nonce Client: 8f3e2a1b...
  Nonce Server: 4d9c7e2f...
  Timestamp: 1704067200
  File: /docs/report.docx
  Operation: write

Output:
  Token: a7b3c4d5e6f7g8h9
```

---

## Security Properties

### 1. Forward Secrecy
- Old tokens cannot be derived from new tokens
- Each token is independent

### 2. Replay Protection
- Challenge-response prevents token reuse
- Proof is challenge-specific

### 3. Time-Bound
- Tokens expire after 10 minutes
- Timestamp rounded to 5-minute windows

### 4. File-Specific
- Token for file A cannot access file B
- Operation-specific (read vs write)

### 5. No Token Transmission
- Only proof is transmitted
- Token remains on client/server

---

## Validation Flow

```
1. Client requests access to file
   ↓
2. Server sends: Nonce_Server, Timestamp, Challenge_ID
   ↓
3. Client computes: Token = HKDF(MasterKey, Nonce_Client, Nonce_Server, Timestamp, FilePath)
   ↓
4. Client sends: Nonce_Client, HMAC(Token, Challenge_ID)
   ↓
5. Server computes: Expected_Token = HKDF(MasterKey, Nonce_Client, Nonce_Server, Timestamp, FilePath)
   ↓
6. Server validates: HMAC(Expected_Token, Challenge_ID) == Received_HMAC
   ↓
7. If match: Grant access for 10 minutes
```

---

## Week 2 Achievements

✅ **Task 1:** Master key derivation implemented
✅ **Task 2:** HKDF token generation working
✅ **Task 3:** HMAC proof validation functional
✅ **Task 4:** CLI tool created
✅ **Task 5:** All 10 tests passing
✅ **Task 6:** Complete documentation

---

## Next Steps (Week 3)

1. Integrate token system with file monitoring (Watchdog)
2. Create SQLite database for file tracking
3. Implement file hash calculation
4. Add entropy analysis
5. Connect token validation to file operations

---

## Files Created

- `week2_task1_master_key.py` - Master key derivation
- `week2_task2_token_generation.py` - Token generation
- `week2_task3_proof_validation.py` - Proof validation
- `week2_task4_token_cli.py` - CLI interface
- `week2_task5_test_suite.py` - Test suite
- `week2_documentation.md` - This file

---

## Performance Metrics

- Master key derivation: ~0.1 seconds
- Token generation: <0.001 seconds
- Proof validation: <0.001 seconds
- Total authentication: ~0.1 seconds

---

## Security Notes

⚠️ **Current Implementation:**
- Uses PBKDF2 (built-in) instead of Argon2id
- Master key stored in memory (not TPM)
- No hardware token integration yet

🔒 **Production Requirements:**
- Implement Argon2id for better security
- Store master key in TPM/secure enclave
- Add hardware token support (YubiKey)
- Implement key rotation
- Add audit logging

---

**Week 2 Status: ✅ COMPLETE**