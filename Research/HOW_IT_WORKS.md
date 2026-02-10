# How Token System Works

## Simple Explanation

**Token Generator** and **File Protector** share the same SECRET PASSWORD.

### Token Generation (token_generator.py)
```
Token = SHA256(PASSWORD + FILEPATH + TIME_WINDOW)
```

Example:
- Password: "MySecurePassword123!"
- Filepath: "/home/popg/projects/anti-ransomW/ARCHITECTURE.md"
- Time Window: 59876543 (changes every 30 seconds)
- Token: cbd91d3d39bca9bc4d17ffcb1617a9a2

### Token Validation (file_protector.py)
When you give it a token, it:

1. **Calculates expected token** using same formula:
   ```
   Expected = SHA256(PASSWORD + FILEPATH + CURRENT_TIME_WINDOW)
   ```

2. **Compares**: Does your token match expected token?
   - ✅ YES → Access granted (mark token as used)
   - ❌ NO → Access denied

3. **Checks if already used**: Is token in used_tokens.json?
   - ✅ YES → Deny (replay attack)
   - ❌ NO → Continue to step 1

## Why It Works

### Valid Token Recognition
Both scripts use **SAME PASSWORD** + **SAME FILEPATH** + **SAME TIME WINDOW** = **SAME TOKEN**

### Invalid Token Detection
- **Wrong file**: Different filepath → Different token
- **Expired**: Different time window → Different token  
- **Wrong password**: Different password → Different token
- **Already used**: Token in used_tokens.json → Denied

## Current Implementation vs Week 2 System

### Current (Simplified)
```python
# Simple SHA256 hash
token = SHA256(password + filepath + time_window)
```
- ❌ No Argon2id
- ❌ No master key derivation
- ❌ No HKDF
- ✅ Simple demonstration

### Week 2 (Full System)
```python
# Step 1: Derive master key from password (PBKDF2)
master_key = PBKDF2(password, salt, 100000 iterations)

# Step 2: Generate token (HKDF)
token = HKDF(master_key, nonce_c, nonce_s, timestamp, filepath)
```
- ✅ Uses master key derivation
- ✅ Uses HKDF for token generation
- ✅ More secure (but more complex)

## Should You Use Argon2id?

**YES** - Argon2id is better than PBKDF2 for password hashing.

### Upgrade Path:
```python
# Replace PBKDF2 with Argon2id in week2_task1_master_key.py
from argon2 import PasswordHasher

ph = PasswordHasher()
master_key = ph.hash(password)
```

**Benefits:**
- Stronger against GPU/ASIC attacks
- Memory-hard (harder to crack)
- Modern standard (won PBKDF competition)

## Next Steps

1. **Keep current simple scripts** for testing/demo
2. **Use Week 2 full system** for real protection:
   - Master key derivation (PBKDF2 or Argon2id)
   - HKDF token generation
   - HMAC proof validation
3. **Month 6**: Replace password with hardware token

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│  Token Generator    │         │  File Protector     │
│                     │         │                     │
│  Password ──────────┼────────▶│  Password           │
│  Filepath           │  SAME   │  Filepath           │
│  Time Window        │  SECRET │  Time Window        │
│         │           │         │         │           │
│         ▼           │         │         ▼           │
│    SHA256 Hash      │         │    SHA256 Hash      │
│         │           │         │         │           │
│         ▼           │         │         ▼           │
│  Token: abc123      │────────▶│  Expected: abc123   │
└─────────────────────┘         │         │           │
                                │         ▼           │
                                │    Compare Tokens   │
                                │         │           │
                                │         ▼           │
                                │  ✅ Match → Grant   │
                                │  ❌ No Match → Deny │
                                └─────────────────────┘
```

## Security Properties

1. **File-specific**: Token for file1.txt won't work on file2.txt
2. **Time-limited**: Token expires after 30 seconds
3. **One-time use**: Each token can only be used once
4. **Password-protected**: Need correct password to generate valid token
5. **Tamper-proof**: Changing 1 character makes token invalid
