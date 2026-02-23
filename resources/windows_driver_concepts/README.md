# Windows Driver Concepts from NoMoreStealer

Reference implementations for Month 4 (Weeks 13-16): Windows Driver Development

## Files

### 1. minifilter_registration.cpp
- Driver entry point and registration
- Altitude selection (371000 - FSFilter Activity Monitor)
- Operation callbacks setup
- Instance attachment logic

**Key Concepts:**
- `FltRegisterFilter()` - Register minifilter with Filter Manager
- `FltStartFiltering()` - Begin intercepting operations
- Altitude determines filter position in stack
- Instance setup controls which volumes to monitor

### 2. file_name_information.cpp
- Getting file paths in kernel callbacks
- Path matching and substring search
- Normalized vs opened name formats

**Key Concepts:**
- `FltGetFileNameInformation()` - Get file path from IRP
- `FltParseFileNameInformation()` - Parse into components
- `RtlPrefixUnicodeString()` - Check path prefixes
- Always call `FltReleaseFileNameInformation()` when done

### 3. process_verification.cpp
- Process trust evaluation
- Digital signature checking
- System process identification

**Key Concepts:**
- `PsIsProtectedProcessLight()` - Check if Microsoft signed
- `ZwQueryInformationProcess()` - Get process information
- `PsGetProcessImageFileName()` - Get process name
- Signature levels: UNSIGNED < AUTHENTICODE < MICROSOFT < WINDOWS

### 4. shared_memory_communication.cpp
- Kernel-to-user-mode event notifications
- Shared memory section creation
- Spinlock synchronization

**Key Concepts:**
- `ZwCreateSection()` - Create named shared memory
- `ZwMapViewOfSection()` - Map into address space
- User-mode polls `Ready` flag for new events
- Use spinlocks for thread-safe access

## Integration with Your Project

### Current (Month 1-3): Python Prototype
- Week 2: Token system (Argon2id + HKDF)
- Week 3: Filesystem monitoring (watchdog)
- Week 4: Token-protected filesystem

### Future (Month 4): Windows Driver
1. Replace Python watchdog with minifilter driver
2. Intercept IRP_MJ_CREATE, IRP_MJ_WRITE, IRP_MJ_SET_INFORMATION
3. Validate tokens in kernel space
4. Use shared memory to communicate with user-mode UI
5. Integrate entropy analysis in post-operation callback

## Build Requirements (Month 4)
- Visual Studio 2019/2022
- Windows Driver Kit (WDK)
- Windows 10/11 SDK
- Test signing enabled for development

## Testing Approach
- Always test in virtual machines
- Use DebugView for kernel debug output
- Create system restore points
- Start with read-only monitoring before blocking

## Security Notes
- Never trust process names alone (easily spoofed)
- Always verify digital signatures
- Use token-based authentication (your unique approach)
- Monitor all destructive operations (WRITE, DELETE, RENAME)
- Implement entropy analysis to detect encryption

## References
- NoMoreStealer: https://github.com/yourusername/NoMoreStealers
- Microsoft Filter Manager: https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/filter-manager-concepts
- Minifilter Best Practices: https://docs.microsoft.com/en-us/windows-hardware/drivers/ifs/minifilter-altitude-request
