# NoMoreStealer Analysis - What We Learned and Copied

## Overview

NoMoreStealer is a Windows kernel minifilter driver designed to protect against information-stealing malware. We analyzed its source code to extract kernel-level file protection patterns for our anti-ransomware project.

**Repository**: `/repo/NoMoreStealers`  
**Language**: C++ (Kernel), Go (User-mode)  
**Status**: Demo/Proof-of-Concept  
**License**: MIT

---

## Architecture

### Two-Component System

```
┌─────────────────────────────────────┐
│   User-Mode (Go + Wails)            │
│   - Desktop UI                      │
│   - Event display                   │
│   - Digital signature verification  │
└──────────────┬──────────────────────┘
               │
        Shared Memory (4KB)
               │
┌──────────────▼──────────────────────┐
│   Kernel Driver (C++)               │
│   - Minifilter (IRP_MJ_CREATE)      │
│   - Path protection                 │
│   - Process allowlist               │
└─────────────────────────────────────┘
```

---

## What NoMoreStealer Does

### 1. File System Interception
**File**: `NoMoreStealer/internal/Callbacks/callbacks.cpp`

- Hooks `IRP_MJ_CREATE` operations only
- Gets file path using `FltGetFileNameInformation()`
- Checks if path matches protected directories
- Blocks untrusted processes from accessing protected files

**Protected Paths** (Hardcoded):
- Browser data: `\Google\Chrome\User Data`, `\Mozilla\Firefox\Profiles`
- Crypto wallets: `\AppData\Local\Exodus`, `\AppData\Roaming\Electrum\wallets`
- Communication: `\AppData\Roaming\Discord`, `\AppData\Roaming\Telegram Desktop`

### 2. Process Trust Evaluation
**File**: `NoMoreStealer/internal/Process/process.cpp`

Three trust checks:
1. **System processes**: PID 4, `csrss.exe`, `lsass.exe`, etc.
2. **Known trusted**: `chrome.exe`, `firefox.exe`, `discord.exe` (hardcoded allowlist)
3. **Protected processes**: Uses `PsIsProtectedProcessLight()` to check Microsoft signature

**Trust Logic**:
```cpp
BOOLEAN IsAllowed(PEPROCESS process) {
    if (IsSystemProcess(process)) return TRUE;
    if (IsKnownTrustedProcess(process)) return TRUE;
    if (IsProcessProtected(process)) return TRUE;
    return FALSE;
}
```

### 3. Shared Memory Communication
**File**: `NoMoreStealer/internal/Comm/comm.cpp`

- Creates named section: `\BaseNamedObjects\NoMoreStealersNotify`
- Size: 4096 bytes (PAGE_SIZE)
- Structure: PID + PathLen + ProcName[64] + Ready flag + Path data
- User-mode polls `Ready` flag every 100ms
- Uses work items to avoid blocking kernel operations

**Memory Layout**:
```
Offset 0x00: PID (4 bytes)
Offset 0x04: PathLen (4 bytes)
Offset 0x08: ProcName[64] (64 bytes)
Offset 0x48: Ready (4 bytes)
Offset 0x4C: Path data (variable, UTF-16)
```

### 4. User-Mode Application
**File**: `NoMoreStealers_Usermode/internal/app/app.go`

- Maps shared memory section from kernel
- Polls for events every 100ms
- Verifies digital signatures using WinVerifyTrust
- Displays events in Wails UI (HTML/CSS/JS)
- WebSocket server for real-time updates

---

## What We Copied

### 1. Minifilter Registration Pattern
**Copied to**: `/resources/windows_driver_concepts/minifilter_registration.cpp`

```cpp
FLT_OPERATION_REGISTRATION CallbacksArray[] = {
    { IRP_MJ_CREATE, 0, PreCreateCallback, nullptr },
    { IRP_MJ_WRITE, 0, PreWriteCallback, nullptr },
    { IRP_MJ_SET_INFORMATION, 0, PreSetInfoCallback, nullptr },
    { IRP_MJ_OPERATION_END }
};

const FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),
    FLT_REGISTRATION_VERSION,
    0,
    nullptr,
    CallbacksArray,
    FilterUnload,
    InstanceSetup,
    // ...
};
```

**Key Concepts**:
- Altitude selection: `371000` (FSFilter Activity Monitor)
- Operation callbacks for CREATE, WRITE, SET_INFORMATION
- Instance setup to filter by filesystem type (NTFS only)

### 2. File Name Information Extraction
**Copied to**: `/resources/windows_driver_concepts/file_name_information.cpp`

```cpp
PFLT_FILE_NAME_INFORMATION nameInfo = nullptr;
NTSTATUS status = FltGetFileNameInformation(
    Data,
    FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
    &nameInfo
);

status = FltParseFileNameInformation(nameInfo);

// Access: nameInfo->Name, nameInfo->FinalComponent
```

**Key Concepts**:
- Normalized vs opened name formats
- Path prefix matching with `RtlPrefixUnicodeString()`
- Substring search in paths
- Always release with `FltReleaseFileNameInformation()`

### 3. Process Verification
**Copied to**: `/resources/windows_driver_concepts/process_verification.cpp`

```cpp
BOOLEAN IsProcessProtected(PEPROCESS process) {
    HANDLE hProcess;
    ObOpenObjectByPointer(process, ...);
    
    PROCESS_SIGNATURE_INFORMATION sigInfo;
    ZwQueryInformationProcess(
        hProcess,
        ProcessSignatureInformation,
        &sigInfo,
        sizeof(sigInfo),
        &returnLength
    );
    
    return (sigInfo.SignatureLevel >= SIG_LEVEL_MICROSOFT);
}
```

**Key Concepts**:
- `PsGetProcessImageFileName()` for process name
- `ZwQueryInformationProcess()` for signature info
- Signature levels: UNSIGNED < AUTHENTICODE < MICROSOFT < WINDOWS
- System process identification

### 4. Shared Memory Communication (Complete)
**Copied to**: `/resources/windows_driver_concepts/shared_memory_complete.cpp`

Full production implementation including:
- Security descriptor creation (SYSTEM + Administrators)
- Section creation with proper permissions
- Work item queue for async notifications
- Spinlock synchronization
- Graceful shutdown with work item cleanup

**Key Concepts**:
- `ZwCreateSection()` with security descriptor
- `ZwMapViewOfSection()` for kernel mapping
- `IoAllocateWorkItem()` + `IoQueueWorkItem()` for async work
- Memory barriers before setting ready flag
- Proper cleanup on driver unload

### 5. Complete Driver Entry Point
**Copied to**: `/resources/windows_driver_concepts/driver_entry_complete.cpp`

Integrated driver with:
- Shared memory initialization
- Minifilter registration
- All three callbacks (CREATE, WRITE, SET_INFORMATION)
- Process verification integration
- User-mode notification on block

---

## What We Improved

### NoMoreStealer Limitations → Our Solutions

| NoMoreStealer | Our Anti-Ransomware |
|---------------|---------------------|
| Only monitors `IRP_MJ_CREATE` | Monitors CREATE + WRITE + SET_INFORMATION |
| Process name allowlist (easily spoofed) | Token-based authentication (cryptographic) |
| Hardcoded protected paths | Configurable paths via UI |
| No entropy detection | Shannon entropy analysis (>7.5 threshold) |
| Blocks info stealers | Blocks ransomware encryption |
| No read protection | Protects reads to prevent exfiltration |

---

## Key Differences

### NoMoreStealer: Info Stealer Protection
- **Target**: Malware stealing browser data, crypto wallets
- **Method**: Block untrusted processes from specific paths
- **Trust**: Simple filename matching
- **Scope**: Specific directories only

### Our Project: Ransomware Protection
- **Target**: Ransomware encrypting files
- **Method**: Token-based access control + entropy detection
- **Trust**: Cryptographic token validation (Argon2id + HKDF)
- **Scope**: Entire directories with configurable rules

---

## Code Quality Assessment

### Strengths
✅ Clean separation of concerns (Callbacks, Process, Paths, Comm)  
✅ Proper error handling and cleanup  
✅ Security descriptor implementation  
✅ Work item pattern for async operations  
✅ Comprehensive process verification  

### Weaknesses
⚠️ Only monitors CREATE operations  
⚠️ Hardcoded paths (no runtime configuration)  
⚠️ Process name spoofing vulnerability  
⚠️ No parent process verification  
⚠️ Demo status (not production-ready)  

---

## Integration Plan for Our Project

### Month 4 (Weeks 13-16): Windows Driver Development

**Phase 1: Basic Driver**
- Use minifilter registration pattern
- Implement CREATE + WRITE + SET_INFORMATION callbacks
- Add file name information extraction

**Phase 2: Token Validation**
- Port Week 2 token system to kernel space
- Implement token validation in callbacks
- Replace process allowlist with token checks

**Phase 3: Communication**
- Implement shared memory communication
- Notify user-mode UI of blocked operations
- Add entropy analysis results to notifications

**Phase 4: Integration**
- Connect kernel driver to existing Python UI
- Test with Week 4 ransomware simulator
- Performance optimization

---

## Files Extracted

### From NoMoreStealer
```
repo/NoMoreStealers/
├── NoMoreStealer/internal/
│   ├── Callbacks/callbacks.cpp       → File interception logic
│   ├── Process/process.cpp           → Trust verification
│   ├── Paths/paths.cpp               → Path matching
│   └── Comm/comm.cpp                 → Shared memory
└── NoMoreStealers_Usermode/
    └── internal/app/app.go           → User-mode polling
```

### To Our Resources
```
resources/windows_driver_concepts/
├── minifilter_registration.cpp       → Driver setup
├── file_name_information.cpp         → Path extraction
├── process_verification.cpp          → Trust checking
├── shared_memory_communication.cpp   → Basic pattern
├── shared_memory_complete.cpp        → Full implementation
└── driver_entry_complete.cpp         → Integrated driver
```

---

## Testing Approach

### NoMoreStealer Testing
- Virtual machine with test signing enabled
- DebugView for kernel debug output
- Process Monitor for validation
- Manual testing with info stealer samples

### Our Testing Plan
- Same VM setup with test signing
- Week 4 ransomware simulator for validation
- Entropy analysis verification
- Token system integration tests
- Performance benchmarking

---

## Build Requirements

### NoMoreStealer
- Visual Studio 2019/2022
- Windows Driver Kit (WDK)
- Go 1.19+ (for user-mode)
- Wails framework

### Our Project (Month 4)
- Visual Studio 2019/2022
- Windows Driver Kit (WDK)
- Python 3.13 (existing UI)
- Flask + Socket.IO (existing)

---

## Security Considerations

### NoMoreStealer Vulnerabilities
1. **Process name spoofing**: Malware can name itself `chrome.exe`
2. **No parent verification**: Doesn't check process genealogy
3. **Limited IRP coverage**: Only CREATE operations
4. **Hardcoded trust**: Can't adapt to new threats

### Our Mitigations
1. **Token-based auth**: Cryptographic validation, not names
2. **Entropy detection**: Catches encryption regardless of process
3. **Full IRP coverage**: CREATE + WRITE + SET_INFORMATION
4. **Configurable rules**: Runtime updates via UI

---

## Performance Impact

### NoMoreStealer
- Minimal CPU impact (only CREATE operations)
- ~10MB memory for path storage
- No significant I/O degradation

### Expected for Our Project
- Moderate CPU impact (more operations monitored)
- ~20MB memory (token cache + entropy buffers)
- Entropy calculation overhead on writes
- Acceptable for security-critical systems

---

## Lessons Learned

### What Worked Well
1. **Shared memory pattern**: Efficient kernel-to-user communication
2. **Work item queue**: Prevents blocking kernel operations
3. **Modular design**: Easy to understand and modify
4. **Security descriptor**: Proper access control

### What to Avoid
1. **Hardcoded values**: Use configuration files or registry
2. **Simple allowlists**: Use cryptographic authentication
3. **Limited monitoring**: Cover all destructive operations
4. **Process name trust**: Verify signatures or use tokens

---

## References

- **NoMoreStealer GitHub**: Original source code
- **Microsoft Filter Manager**: https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts
- **Minifilter Best Practices**: https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/minifilter-altitude-request
- **IRP Major Functions**: https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-major-function-codes

---

## Conclusion

NoMoreStealer provided excellent reference implementations for:
- Minifilter driver structure
- File system interception patterns
- Shared memory communication
- Process verification techniques

We extracted the core patterns and improved upon them with:
- Token-based authentication (not process names)
- Entropy detection for encryption
- Comprehensive IRP coverage
- Configurable protection rules

The extracted code in `/resources/windows_driver_concepts/` is ready for Month 4 implementation.
