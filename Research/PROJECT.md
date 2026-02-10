# Anti-Ransomware Protection System

## Overview

A proactive file protection system that enforces zero-trust access control using dynamic token authentication. Protects critical folders from unauthorized access, including ransomware attacks, by requiring ephemeral tokens for sensitive operations.

## Core Concept

- **Default State**: Protected files are read-only or no-permission by default
- **Token-Based Access**: Write operations and sensitive reads require dynamic, time-bound tokens
- **Dynamic Security**: Tokens are ephemeral (10-60 min), signed, and include nonces to prevent replay attacks
- **Kernel-Level Enforcement**: Filesystem hooks intercept operations before OS processes them

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User/Application Layer                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLI/GUI Interface                          │
│  • Token Request UI                                          │
│  • Folder Protection Manager                                 │
│  • Audit Log Viewer                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Token Management Service                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Generator  │  │  Validator   │  │  MFA Engine  │      │
│  │  (JWT+Nonce) │  │ (Signature)  │  │  (PIN/Bio)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Filesystem Access Controller                    │
│  • Permission Enforcer (ACL/chmod)                           │
│  • Whitelist Manager (Trusted Apps)                          │
│  • Operation Interceptor (inotify/eBPF)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Audit & Security Layer                      │
│  • Access Logs (SQLite)                                      │
│  • Alert System (Failed Attempts)                            │
│  • Backup Trigger (Auto-snapshot)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Protected Filesystem                       │
│  /protected/documents/  /protected/data/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Workflow: File Access Process

```
                    START
                      │
                      ▼
        ┌─────────────────────────────┐
        │ User/App Attempts File      │
        │ Access (Read/Write)         │
        └─────────────┬───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Is Folder     │───── NO ────▶ Allow Default OS
              │ Protected?    │               Permissions → END
              └───────┬───────┘
                      │ YES
                      ▼
        ┌─────────────────────────────┐
        │ Intercept via Filesystem    │
        │ Hook (inotify/eBPF)         │
        └─────────────┬───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Operation     │
              │ Type?         │
              └───────┬───────┘
                      │
         ┌────────────┼────────────┐
         │ READ       │            │ WRITE
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Trusted │  │ Require │  │ Require │
    │ App?    │  │ Token?  │  │ Token   │
    └────┬────┘  └────┬────┘  └────┬────┘
         │ YES        │ NO         │
         ▼            ▼            │
    Grant Read   Grant Read       │
         │            │            │
         └────────────┴────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │ Prompt for Token Request    │
        │ (MFA/PIN Required)          │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │ User Provides MFA/PIN       │
        └─────────────┬───────────────┘
                      │
              ┌───────┴───────┐
              │ Valid?        │
              └───────┬───────┘
                      │
         ┌────────────┼────────────┐
         │ NO         │            │ YES
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────────────┐
    │ Deny    │  │ Log     │  │ Generate Token  │
    │ Access  │  │ Failed  │  │ • JWT Signature │
    └────┬────┘  │ Attempt │  │ • Nonce         │
         │       └────┬────┘  │ • Expiry (10m)  │
         │            │       │ • Op-Type       │
         │            │       └────────┬────────┘
         │            │                │
         └────────────┴────────────────┤
                      │                ▼
                      │    ┌─────────────────────┐
                      │    │ Validate Token      │
                      │    │ • Check Signature   │
                      │    │ • Verify Freshness  │
                      │    │ • Match Context     │
                      │    └──────────┬──────────┘
                      │               │
                      │       ┌───────┴───────┐
                      │       │ Valid?        │
                      │       └───────┬───────┘
                      │               │
                      │    ┌──────────┼──────────┐
                      │    │ NO       │          │ YES
                      │    ▼          ▼          ▼
                      │ ┌────────┐ ┌──────┐ ┌──────────────┐
                      │ │ Deny + │ │ Alert│ │ Grant Temp   │
                      │ │ Lock   │ │ Sys  │ │ Access       │
                      │ └────────┘ └──────┘ │ (10-min)     │
                      │                     └──────┬───────┘
                      │                            │
                      │                            ▼
                      │              ┌──────────────────────┐
                      │              │ Perform Operation    │
                      │              │ + Audit Log Entry    │
                      │              └──────────┬───────────┘
                      │                         │
                      │                         ▼
                      │              ┌──────────────────────┐
                      │              │ Token Expires/       │
                      │              │ Auto-Destruct        │
                      │              └──────────┬───────────┘
                      │                         │
                      └─────────────────────────┘
                                                │
                                                ▼
                                              END
```

---

## Token Structure

```
┌─────────────────────────────────────────────────────────────┐
│                      JWT Token Format                        │
├─────────────────────────────────────────────────────────────┤
│ Header:                                                      │
│   {                                                          │
│     "alg": "HS256",                                          │
│     "typ": "JWT"                                             │
│   }                                                          │
├─────────────────────────────────────────────────────────────┤
│ Payload:                                                     │
│   {                                                          │
│     "user_id": "user123",                                    │
│     "session_id": "sess_abc123",                             │
│     "operation": "write",                                    │
│     "path": "/protected/documents/file.txt",                 │
│     "nonce": "random_8f7d9a2b",                              │
│     "iat": 1704067200,        # Issued at                    │
│     "exp": 1704067800         # Expires (10 min)             │
│   }                                                          │
├─────────────────────────────────────────────────────────────┤
│ Signature:                                                   │
│   HMACSHA256(                                                │
│     base64UrlEncode(header) + "." +                          │
│     base64UrlEncode(payload),                                │
│     secret_key_from_TPM                                      │
│   )                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Features

### 1. Token Security

- **Ephemeral**: 10-60 minute lifespan
- **One-Time Nonce**: Prevents replay attacks
- **Context-Bound**: Tied to specific user, session, operation, and file path
- **Hardware-Signed**: Uses TPM/secure enclave for key storage
- **No Persistence**: Never stored on disk

### 2. Access Control Layers

```
Layer 1: OS Permissions (chmod 000 or 400)
         ↓
Layer 2: Filesystem Hook (Intercept before kernel)
         ↓
Layer 3: Token Validation (Cryptographic verification)
         ↓
Layer 4: Audit Logging (Forensic trail)
```

### 3. Ransomware Protection Mechanisms

- **Default Deny**: All writes blocked without token
- **Rapid Detection**: Unusual access patterns trigger alerts
- **Auto-Lockdown**: Suspicious activity freezes folder access
- **Immutable Backups**: Automatic snapshots on successful writes
- **Process Whitelisting**: Only trusted apps bypass token for reads

---

## Implementation Phases

### Phase 1: Core Prototype (MVP)

- [X] Token generation/validation (JWT)
- [X] Filesystem monitoring (inotify)
- [X] Basic permission enforcement (chmod/ACL)
- [X] CLI interface for token requests
- [X] Audit logging (SQLite)
- [X] PIN-based MFA simulation

### Phase 2: Enhanced Security

- [ ] Hardware token integration (YubiKey)
- [ ] Biometric authentication
- [ ] eBPF/FUSE kernel hooks
- [ ] Real-time threat detection (ML-based)
- [ ] Encrypted audit logs

### Phase 3: Production Features

- [ ] GUI application (Qt/Electron)
- [ ] Multi-user support
- [ ] Cloud backup integration
- [ ] Windows support (minifilter driver)
- [ ] Network-based token service
- [ ] Admin dashboard

---

## Technology Stack

### Core Components

- **Language**: Python 3.8+ (prototype), C/C++ (production)
- **Token Library**: PyJWT
- **Filesystem**: inotify (Linux), eBPF (advanced), FUSE (overlay)
- **Database**: SQLite (audit logs)
- **Crypto**: cryptography library (Python)
- **MFA**: pyotp (TOTP), python-fido2 (hardware keys)

### System Requirements

- **OS**: Linux (Ubuntu 20.04+, Fedora 35+)
- **Kernel**: 5.4+ (for eBPF support)
- **Python**: 3.8+
- **Privileges**: Root/sudo (for filesystem hooks)
- **Optional**: TPM 2.0 chip, YubiKey

---

## Usage Example

```bash
# 1. Protect a folder
$ sudo antiransomw protect /home/user/documents

# 2. Attempt to write (blocked)
$ echo "test" > /home/user/documents/file.txt
Permission denied

# 3. Request token
$ antiransomw request-token --path /home/user/documents/file.txt --operation write
Enter PIN: ****
Token generated: eyJhbGc...
Valid for: 10 minutes

# 4. Write with token
$ ANTIRANSOMW_TOKEN=eyJhbGc... echo "test" > /home/user/documents/file.txt
Success! Access logged.

# 5. View audit log
$ antiransomw logs
[2024-01-01 10:30:15] WRITE /home/user/documents/file.txt - GRANTED (user123)
[2024-01-01 10:25:03] WRITE /home/user/documents/data.db - DENIED (unknown_process)
```

---

## Performance Considerations

- **Overhead**: Target <5% performance impact
- **Caching**: Token validation results cached for active sessions
- **Selective Hooks**: Only monitor protected paths, not entire filesystem
- **Async Logging**: Non-blocking audit writes
- **Optimized Checks**: Fast-path for whitelisted apps

---

## Threat Model

### Protected Against

✅ Ransomware encryption attempts
✅ Unauthorized file modifications
✅ Privilege escalation attacks
✅ Malicious admin access (without token)
✅ Credential theft (tokens expire)

### Limitations

⚠️ Kernel-level rootkits (requires secure boot)
⚠️ Physical access attacks (needs full-disk encryption)
⚠️ Social engineering (user grants token to malware)
⚠️ Zero-day kernel exploits (defense-in-depth needed)

---

## Future Enhancements

1. **AI-Based Anomaly Detection**: Learn normal access patterns, flag deviations
2. **Distributed Token Service**: Multi-device token synchronization
3. **Blockchain Audit Trail**: Immutable, tamper-proof logs
4. **Hardware Security Module (HSM)**: Enterprise-grade key storage
5. **Cross-Platform Support**: Windows (minifilter), macOS (Endpoint Security)

---

## License

MIT License (or specify your choice)

## Contributing

Contributions welcome! Focus areas:

- Kernel module development (eBPF/FUSE)
- Windows minifilter driver
- GUI development
- Security audits

---

## References

- [JWT Specification (RFC 7519)](https://tools.ietf.org/html/rfc7519)
- [Linux inotify API](https://man7.org/linux/man-pages/man7/inotify.7.html)
- [eBPF Documentation](https://ebpf.io/)
- [NIST Ransomware Risk Management](https://www.nist.gov/publications/ransomware-risk-management)
