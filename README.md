# Anti-Ransomware Protection System (UNDER DEVELOPMENT)

Hardware token-based file protection system that prevents ransomware attacks through cryptographic access control.

## Overview

This project implements WPA2-style dynamic token generation for file system protection. Files are locked by default and require a physical hardware token for access, preventing both local and remote ransomware encryption attacks.

## Key Features

- **Token-Based Access Control**: Files require valid tokens for read/write operations
- **Entropy-Based Detection**: Identifies encryption attempts through Shannon entropy analysis (>7.5 threshold)
- **Event Logging**: SQLite database tracks all file operations with hash and entropy data
- **Session Management**: 10-minute token sessions with automatic expiration
- **Cross-Platform**: Built with Python watchdog library for Linux/Windows compatibility

## Project Status

**Month 1 Complete** (Weeks 1-4)
- ✅ Week 1: File monitoring research and implementation
- ✅ Week 2: WPA2-style token system (Argon2id + HKDF)
- ✅ Week 3: Filesystem monitoring with entropy analysis
- ✅ Week 4: Token-protected filesystem integration

**All test suites passing**: 5/5 (Week 3), 7/7 (Week 4), 10/10 (Week 2)

## Architecture

### Core Components

1. **Master Key Derivation** (Argon2id)
   - Time cost: 2, Memory: 64MB, Parallelism: 1
   - 1000x more secure than SHA256 for password hashing

2. **Token Generation** (HKDF)
   - Deterministic 16-byte hex tokens
   - Includes nonce, timestamp, filepath, operation type

3. **Proof Validation** (HMAC-SHA256)
   - Challenge-response authentication
   - Prevents token replay attacks

4. **Filesystem Monitor** (Watchdog)
   - Real-time file event detection
   - SHA256 hash calculation
   - Shannon entropy analysis

5. **Protected Monitor**
   - Blocks writes without valid token
   - 10-minute session management
   - Comprehensive event logging

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/anti-ransomW.git
cd anti-ransomW

# Create virtual environment
python3 -m venv atrenv
source atrenv/bin/activate  # Linux/Mac
# or: atrenv\Scripts\activate  # Windows

# Install dependencies
pip install -r Research/requirements.txt
```

## Quick Start

### Run Week 4 Protected Monitor

```bash
cd Research
python week4_protected_monitor.py /path/to/protected/directory
```

Commands:
- `token` - Generate new 10-minute session token
- `status` - Check current token status
- `stats` - View blocked vs allowed operations
- `quit` - Exit monitor

### Run Test Suites

```bash
# Week 2: Token system tests
python week2_task5_test_suite.py

# Week 3: Monitoring tests
python week3_test_suite.py

# Week 4: Integration tests
python week4_test_suite.py
```

### Simulate Ransomware Attack

```bash
python week4_ransomware_simulator.py /path/to/test/directory
```

## How It Works

1. **Default State**: All files are locked (no read/write access)
2. **Authentication**: User provides hardware token (currently password-based prototype)
3. **Token Generation**: System generates time-limited session token using Argon2id + HKDF
4. **File Access**: Token validates each read/write operation
5. **Ransomware Protection**: 
   - Blocks unauthorized writes (prevents paste-back attacks)
   - Blocks unauthorized reads (prevents data exfiltration)
   - Detects encryption via entropy analysis (>7.5 bits/byte)

## Development Timeline

- **Month 1** (Weeks 1-4): Core token system and monitoring ✅
- **Month 2** (Weeks 5-8): Enhanced detection and UI
- **Month 3** (Weeks 9-12): Hardware token integration
- **Month 4** (Weeks 13-16): Windows driver development
- **Month 5** (Weeks 17-20): Performance optimization
- **Month 6** (Weeks 21-26): Testing and documentation

## Technical Specifications

- **Language**: Python 3.13
- **Key Libraries**: argon2-cffi, watchdog, cryptography
- **Database**: SQLite3
- **Target OS**: Windows (developing on Linux)
- **Security**: Argon2id (password hashing), HKDF (key derivation), HMAC-SHA256 (validation)

## Differentiation from Windows Defender Protected Folders

- Hardware token requirement (physical device authentication)
- Read operation protection (prevents data exfiltration)
- MFA for permission changes (prevents bypass)
- Entropy-based encryption detection
- Comprehensive event logging with hash tracking

## Project Goals

**Personal Project** (First 6 months)
- Zero spending budget
- Proof of concept validation
- Hardware token integration
- Real-world testing

**Future Considerations** (After 6 months)
- Broader application potential
- Business viability assessment
- Community feedback integration

## Documentation

See `/Research` directory for detailed documentation:
- `DETAILED_PLAN.md` - 26-week development roadmap
- `REDDIT_LESSONS_LEARNED.md` - Community validation insights
- `UPDATED_ARCHITECTURE_TOKEN_READS_MFA.md` - System architecture
- `REMOTE_RANSOMWARE_EXPLAINED.md` - Modern ransomware techniques

## License

Personal project - License TBD

## Location

Developed in Abuja, Nigeria 🇳🇬

## Contact

Project started: January 27, 2026
