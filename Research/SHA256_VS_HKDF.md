# SHA256 vs HKDF - What's the Difference?

## Simple Answer

**SHA256** = Hash function (one-way, fixed output)
**HKDF** = Key derivation function (designed for creating multiple keys from one master key)

---

## Current Implementation (SHA256 Concatenation)

```python
master_key = Argon2id(password, salt)
token = SHA256(master_key + filepath + time_window)
```

**What it does:**
- Concatenates (joins) master_key + filepath + time_window
- Hashes the result with SHA256
- Output: 32-byte token

**Example:**
```
master_key = b'\x3a\x7f\x2c...' (32 bytes)
filepath = b'/home/file.txt'
time_window = b'59876543'

Combined = b'\x3a\x7f\x2c.../home/file.txt59876543'
Token = SHA256(Combined) = 'cbd91d3d39bca9bc4d17ffcb1617a9a2'
```

---

## Week 2 Implementation (HKDF)

```python
master_key = Argon2id(password, salt)
token = HKDF(master_key, salt=nonce_c+nonce_s, info=filepath+timestamp)
```

**What it does:**
- Uses HMAC-based Key Derivation Function
- Properly extracts and expands key material
- Output: 16-byte token

**Example:**
```
master_key = b'\x3a\x7f\x2c...' (32 bytes)
nonce_c = b'client_random_123'
nonce_s = b'server_random_456'
filepath = b'/home/file.txt'
timestamp = b'1706400000'

Token = HKDF(
    master_key,
    salt=nonce_c+nonce_s,
    info=filepath+timestamp,
    length=16
) = '48b21e4170bf5500'
```

---

## Key Differences

| Feature | SHA256 Concatenation | HKDF |
|---------|---------------------|------|
| **Purpose** | General hashing | Key derivation |
| **Design** | Not designed for key derivation | Specifically designed for keys |
| **Security** | ⚠️ Adequate but not ideal | ✅ Cryptographically proper |
| **Multiple Keys** | ❌ Hard to derive multiple keys safely | ✅ Can derive many keys from one master |
| **Salt Handling** | Manual concatenation | Built-in salt parameter |
| **Info Context** | Manual concatenation | Built-in info parameter |
| **Standard** | Generic hash | RFC 5869 standard |

---

## Security Comparison

### SHA256 Concatenation Weaknesses

1. **No Proper Key Separation**
   ```python
   # If you need multiple tokens from same master key:
   token1 = SHA256(master_key + data1)
   token2 = SHA256(master_key + data2)
   # Not cryptographically ideal
   ```

2. **Length Extension Attacks (Theoretical)**
   - SHA256 vulnerable to length extension
   - Attacker might manipulate hash if they know length
   - Low risk in practice, but exists

3. **Not Designed for Key Derivation**
   - SHA256 designed for integrity checking
   - Using it for keys works but not optimal

### HKDF Strengths

1. **Proper Key Derivation**
   ```python
   # Can safely derive unlimited keys:
   token1 = HKDF(master_key, salt=salt1, info=info1)
   token2 = HKDF(master_key, salt=salt2, info=info2)
   # Cryptographically sound
   ```

2. **Extract-then-Expand Pattern**
   - Step 1: Extract pseudorandom key from master key
   - Step 2: Expand to desired length
   - Ensures uniform randomness

3. **Context Binding**
   - `salt` parameter: Adds randomness
   - `info` parameter: Binds key to specific context
   - Prevents key reuse across contexts

---

## Real-World Example

### Scenario: Generate 3 tokens for same file

**SHA256 Approach:**
```python
master_key = Argon2id(password)
token1 = SHA256(master_key + filepath + "context1")
token2 = SHA256(master_key + filepath + "context2")
token3 = SHA256(master_key + filepath + "context3")
```
⚠️ Works but not cryptographically ideal

**HKDF Approach:**
```python
master_key = Argon2id(password)
token1 = HKDF(master_key, salt=salt1, info=filepath+"context1")
token2 = HKDF(master_key, salt=salt2, info=filepath+"context2")
token3 = HKDF(master_key, salt=salt3, info=filepath+"context3")
```
✅ Cryptographically proper

---

## Performance Comparison

| Operation | SHA256 | HKDF |
|-----------|--------|------|
| Speed | ⚡ Fast (~0.00001s) | 🐢 Slightly slower (~0.00003s) |
| Complexity | Simple | More complex |
| Memory | Low | Low |

**Verdict:** HKDF is 3x slower but still VERY fast (0.00003s = 30 microseconds)

---

## When to Use Each

### Use SHA256 Concatenation When:
- ✅ Simple demo/prototype
- ✅ Single token per master key
- ✅ Speed is critical (though difference is tiny)
- ✅ You understand the limitations

### Use HKDF When:
- ✅ Production system
- ✅ Multiple tokens from same master key
- ✅ Following cryptographic best practices
- ✅ Need to pass security audits
- ✅ Want RFC-standard implementation

---

## Your Current Situation

**file_protector.py & token_generator.py:**
```python
token = SHA256(master_key + filepath + time_window)
```
- ✅ Works fine for demo
- ⚠️ Not cryptographically ideal
- ⚠️ Won't pass security audit

**week2_task2_token_generation.py:**
```python
token = HKDF(master_key, salt=nonces, info=filepath+timestamp)
```
- ✅ Cryptographically proper
- ✅ Follows RFC 5869 standard
- ✅ Production-ready

---

## Recommendation

**For Week 2 completion:**
Use HKDF (already in week2_task2.py) because:
1. It's the requirement
2. It's cryptographically proper
3. Performance difference is negligible (30 microseconds)
4. It's industry standard

**For simple demos:**
SHA256 concatenation is fine for learning/testing

---

## Code Comparison

### SHA256 Concatenation (Current Simple Scripts)
```python
import hashlib

def generate_token(master_key, filepath, time_window):
    data = master_key + filepath.encode() + str(time_window).encode()
    return hashlib.sha256(data).hexdigest()[:32]
```

### HKDF (Week 2 System)
```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def generate_token(master_key, nonce_c, nonce_s, timestamp, filepath):
    salt = nonce_c + nonce_s
    info = filepath.encode() + str(timestamp).encode()
    
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=16,
        salt=salt,
        info=info
    )
    return hkdf.derive(master_key).hex()
```

---

## Bottom Line

**SHA256 concatenation:**
- Simple, fast, works
- Not ideal for key derivation
- Fine for demos

**HKDF:**
- Proper key derivation function
- Industry standard (RFC 5869)
- Slightly more complex but worth it
- Required for Week 2

**Verdict:** Use HKDF for production, SHA256 for quick demos.
