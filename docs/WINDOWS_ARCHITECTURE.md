# Anti-Ransomware Protection System - Windows Architecture

## Executive Summary

This system protects files using **WPA2-style cryptographic key derivation** where:
- Master key is NEVER transmitted or stored in plaintext
- Dynamic tokens are computed independently by both client and server
- Even administrators cannot access files without deriving the correct token
- File changes are tracked to detect ransomware patterns

**Target Platform: Windows 10/11**

---

## PART 1: MASTER KEY ESTABLISHMENT

### Overview
Like WPA2's 4-way handshake, both endpoints must possess the same master key WITHOUT ever transmitting it.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MASTER KEY ESTABLISHMENT PHASE                        │
│                         (One-Time Setup)                                 │
└─────────────────────────────────────────────────────────────────────────┘

METHOD 1: Password-Based Key Derivation (PBKDF2/Argon2)
═══════════════════════════════════════════════════════

User Input                    System Processing
───────────                   ─────────────────

  User enters:                
  ┌──────────────┐           
  │ Password:    │           
  │ "MySecure123"│           
  └──────┬───────┘           
         │                    
         │                    
         ▼                    
  ┌──────────────────────────────────────────┐
  │  Key Derivation Function (KDF)           │
  │  ────────────────────────────────────    │
  │                                           │
  │  Input:                                   │
  │    • Password: "MySecure123"              │
  │    • Salt: random_32_bytes                │
  │    • Iterations: 100,000                  │
  │    • Output length: 32 bytes              │
  │                                           │
  │  Algorithm: Argon2id                      │
  │  (Memory-hard, resistant to GPU attacks)  │
  │                                           │
  │  MasterKey = Argon2id(                    │
  │    password="MySecure123",                │
  │    salt=0x4f8a...,                        │
  │    time_cost=3,                           │
  │    memory_cost=65536,                     │
  │    parallelism=4                          │
  │  )                                        │
  └──────────────┬───────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────────┐
  │  Master Key Generated                     │
  │  ═══════════════════════                 │
  │  MK = 0x3a7f9b2c...  (32 bytes)          │
  │                                           │
  │  Stored in:                               │
  │  • Windows: DPAPI (Data Protection API)   │
  │  • Hardware: TPM 2.0 chip                 │
  │                                           │
  │  NEVER stored in plaintext on disk!       │
  └──────────────────────────────────────────┘
```

---

## PART 2: WINDOWS FILESYSTEM MONITORING

### Overview
Windows-specific file monitoring using ReadDirectoryChangesW API and minifilter drivers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WINDOWS FILE MONITORING SYSTEM                        │
│                  (Ransomware Detection & Prevention)                     │
└─────────────────────────────────────────────────────────────────────────┘

LAYER 1: WINDOWS FILESYSTEM MONITORING
═══════════════════════════════════════

Protected Folder: C:\Users\%USERNAME%\Documents\
────────────────────────────────────────────────

┌─────────────────────────────────────────────────────────────┐
│  Baseline File State Database                                │
│  ═══════════════════════════                                │
│                                                              │
│  File Path              | SHA256 Hash    | Size  | Modified │
│  ──────────────────────────────────────────────────────────│
│  report.docx            | a3f7b2...      | 45KB  | 10:00:00 │
│  photo.jpg              | 8c4e9d...      | 2.1MB | 09:30:15 │
│  database.db            | f1a8c3...      | 128KB | 10:15:22 │
│  budget.xlsx            | 2d9f7b...      | 67KB  | 08:45:10 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Windows File System Hook                                    │
│  ═══════════════════════════                                │
│                                                              │
│  Technology Options:                                         │
│  • ReadDirectoryChangesW API (userspace)                     │
│  • Minifilter Driver (kernel-level)                          │
│  • SetWindowsHookEx (process-level)                          │
│                                                              │
│  Monitored Events:                                           │
│  ┌────────────┬────────────┬────────────┬────────────┐     │
│  │FILE_ACTION │FILE_ACTION │FILE_ACTION │FILE_ACTION │     │
│  │   _ADDED   │ _MODIFIED  │ _REMOVED   │ _RENAMED   │     │
│  └────────────┴────────────┴────────────┴────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Event Captured                                              │
│  ═══════════════                                            │
│                                                              │
│  Event Type: FILE_ACTION_MODIFIED                            │
│  File: C:\Users\John\Documents\report.docx                   │
│  Process: WINWORD.EXE (PID: 4521)                            │
│  User: DOMAIN\john_doe                                       │
│  Timestamp: 2024-01-01 10:30:45                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 3: WINDOWS-SPECIFIC IMPLEMENTATION

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WINDOWS TECHNOLOGY STACK                              │
└─────────────────────────────────────────────────────────────────────────┘

Core Components:
═══════════════

• Language: Python 3.8+ (prototype), C++ (production)
• Token Library: PyJWT
• Filesystem: ReadDirectoryChangesW (Windows API)
• Database: SQLite (audit logs)
• Crypto: Windows CryptoAPI + cryptography library
• MFA: Windows Hello, YubiKey support

Windows APIs Used:
═════════════════

• ReadDirectoryChangesW - File change notifications
• CryptProtectData/CryptUnprotectData - DPAPI for key storage
• GetFileAttributes - File permission checking
• SetFileAttributes - Permission enforcement
• OpenProcess - Process identification
• GetModuleFileName - Executable path verification

System Requirements:
═══════════════════

• OS: Windows 10 (1903+) or Windows 11
• .NET Framework: 4.8+ (for advanced features)
• Python: 3.8+ (development)
• Privileges: Administrator (for file hooks)
• Hardware: TPM 2.0 chip (recommended)
• Storage: 100MB for application + logs
```

### Windows File Permissions Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WINDOWS PERMISSION SYSTEM                             │
└─────────────────────────────────────────────────────────────────────────┘

Default Protection Mode:
═══════════════════════

Protected File: C:\Users\John\Documents\secret.docx

Before Protection:
┌────────────────────────────────────┐
│ NTFS Permissions:                  │
│ • SYSTEM: Full Control             │
│ • Administrators: Full Control     │
│ • John: Full Control               │
│ • Users: Read & Execute            │
└────────────────────────────────────┘

After Protection Applied:
┌────────────────────────────────────┐
│ NTFS Permissions (Modified):       │
│ • SYSTEM: Read Only                │
│ • Administrators: Read Only        │
│ • John: Read Only                  │
│ • Users: No Access                 │
│ • AntiRansomware Service: Full     │
└────────────────────────────────────┘

Access Control Process:
══════════════════════

1. User/App attempts write → Denied by NTFS
2. App requests token via our service
3. Service validates token
4. If valid: Temporarily grant write permission
5. After operation: Restore read-only state
```

### Windows Process Whitelisting

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WINDOWS PROCESS VERIFICATION                          │
└─────────────────────────────────────────────────────────────────────────┘

Trusted Process Database:
════════════════════════

┌──────────────────────────────────────────────────────────────────┐
│ Process Name     | Full Path                    | Digital Signature│
├──────────────────────────────────────────────────────────────────┤
│ WINWORD.EXE      | C:\Program Files\Microsoft   | Microsoft Corp   │
│                  | Office\root\Office16\        |                  │
│ notepad.exe      | C:\Windows\System32\         | Microsoft Corp   │
│ chrome.exe       | C:\Program Files\Google\     | Google LLC       │
│ code.exe         | C:\Users\John\AppData\Local\ | Microsoft Corp   │
└──────────────────────────────────────────────────────────────────┘

Verification Process:
════════════════════

When process attempts file access:

1. Get Process Information (Windows API)
   ┌────────────────────────────────┐
   │ PID: 4521                      │
   │ Name: WINWORD.EXE              │
   │ Path: C:\Program Files\...     │
   │ User: DOMAIN\john_doe          │
   │ Parent: explorer.exe           │
   └────────────────────────────────┘

2. Verify Digital Signature
   ┌────────────────────────────────┐
   │ WinVerifyTrust() API call      │
   │ Certificate: Microsoft Corp    │
   │ Valid: Yes                     │
   │ Revoked: No                    │
   └────────────────────────────────┘

3. Check Against Whitelist
   ┌────────────────────────────────┐
   │ Query database:                │
   │ SELECT * FROM whitelist        │
   │ WHERE path = 'C:\Program...'   │
   │ AND signature = 'Microsoft'    │
   └────────────────────────────────┘

4. Decision
   ┌────────────────────────────────┐
   │ If all checks pass:            │
   │   → WHITELISTED                │
   │   → Allow READ without token   │
   │ Else:                          │
   │   → NOT WHITELISTED            │
   │   → Require token for all ops  │
   └────────────────────────────────┘
```

---

## PART 4: WINDOWS DEPLOYMENT

### Installation Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WINDOWS INSTALLATION WORKFLOW                         │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: Administrator Check
═══════════════════════════

┌────────────────────────────────────┐
│ Check if running as Administrator  │
│ If not: Request UAC elevation      │
│ ╔════════════════════════════════╗ │
│ ║ User Account Control           ║ │
│ ║ Do you want to allow this app  ║ │
│ ║ to make changes to your device?║ │
│ ║                                ║ │
│ ║ [Yes]  [No]                    ║ │
│ ╚════════════════════════════════╝ │
└────────────────────────────────────┘

Step 2: Service Installation
════════════════════════════

┌────────────────────────────────────┐
│ Install Windows Service:           │
│ • Name: AntiRansomwareProtection   │
│ • Startup: Automatic               │
│ • Account: LocalSystem             │
│ • Dependencies: None               │
│                                    │
│ sc create AntiRansomwareProtection │
│ binPath= "C:\Program Files\..."    │
│ start= auto                        │
└────────────────────────────────────┘

Step 3: Registry Configuration
══════════════════════════════

┌────────────────────────────────────┐
│ Registry Keys Created:             │
│                                    │
│ HKLM\SOFTWARE\AntiRansomware\      │
│ ├── ProtectedFolders (REG_MULTI_SZ)│
│ ├── TokenTimeout (REG_DWORD)       │
│ ├── LogLevel (REG_DWORD)           │
│ └── WhitelistEnabled (REG_DWORD)   │
│                                    │
│ HKLM\SYSTEM\CurrentControlSet\     │
│ Services\AntiRansomwareProtection\ │
│ └── Parameters\                    │
└────────────────────────────────────┘

Step 4: File System Setup
═════════════════════════

┌────────────────────────────────────┐
│ Create Application Folders:        │
│ • C:\Program Files\AntiRansomware\ │
│ • C:\ProgramData\AntiRansomware\   │
│   ├── Logs\                       │
│   ├── Database\                   │
│   └── Config\                     │
│                                    │
│ Set Permissions:                   │
│ • Program Files: Read-only         │
│ • ProgramData: Service Full Access │
└────────────────────────────────────┘
```

### Usage Example (Windows)

```
# 1. Protect a folder (PowerShell as Admin)
PS> AntiRansomware.exe protect "C:\Users\John\Documents"

# 2. Attempt to write (blocked)
PS> echo "test" > "C:\Users\John\Documents\file.txt"
Access is denied.

# 3. Request token (GUI popup)
PS> AntiRansomware.exe request-token --path "C:\Users\John\Documents\file.txt" --operation write

[Windows Security Dialog appears]
┌─────────────────────────────────────┐
│ Windows Security                    │
│ ─────────────────────────────────   │
│ AntiRansomware Protection           │
│                                     │
│ Microsoft Word wants to save:       │
│ C:\Users\John\Documents\file.txt    │
│                                     │
│ Please verify your identity:        │
│                                     │
│ [Use Windows Hello] [Use PIN]       │
│                                     │
│ [Allow] [Deny]                      │
└─────────────────────────────────────┘

# 4. After authentication - write succeeds
PS> echo "test" > "C:\Users\John\Documents\file.txt"
Success! Access logged.

# 5. View audit log
PS> AntiRansomware.exe logs
[2024-01-01 10:30:15] WRITE C:\Users\John\Documents\file.txt - GRANTED (DOMAIN\john)
[2024-01-01 10:25:03] WRITE C:\Users\John\Documents\data.db - DENIED (unknown_process.exe)
```

---

## CONCLUSION

### Windows-Specific Advantages

**Native Integration:**
- DPAPI for secure key storage
- Windows Hello for biometric authentication
- Digital signature verification for process trust
- NTFS permissions for access control
- Windows Event Log integration

**Security Features:**
- TPM 2.0 integration for hardware-backed keys
- Code signing verification
- UAC integration for privilege escalation
- Windows Defender integration potential

### Recommended Windows Implementation

**Phase 1:** Python prototype using ReadDirectoryChangesW  
**Phase 2:** C++ Windows service with minifilter driver  
**Phase 3:** GUI application with Windows Hello integration  
**Phase 4:** Enterprise features with Group Policy support  

This Windows-focused architecture leverages native Windows security features while maintaining the core WPA2-style token approach.