// Process Verification Pattern from NoMoreStealer
// Reference for verifying process trust and integrity

#include <fltKernel.h>

extern "C" {
    NTKERNELAPI PSTR PsGetProcessImageFileName(_In_ PEPROCESS Process);
    NTKERNELAPI NTSTATUS ZwQueryInformationProcess(
        _In_ HANDLE ProcessHandle,
        _In_ PROCESSINFOCLASS ProcessInformationClass,
        _Out_ PVOID ProcessInformation,
        _In_ ULONG ProcessInformationLength,
        _Out_opt_ PULONG ReturnLength
    );
}

#define ProcessSignatureInformation ((PROCESSINFOCLASS)75)

typedef enum _SIGNATURE_LEVEL {
    SIG_LEVEL_UNSIGNED = 1,
    SIG_LEVEL_AUTHENTICODE = 4,
    SIG_LEVEL_MICROSOFT = 9,
    SIG_LEVEL_WINDOWS = 13,
    SIG_LEVEL_WINDOWS_TCB = 15
} SIGNATURE_LEVEL;

typedef struct _PS_PROTECTION {
    union {
        UCHAR Level;
        struct {
            UCHAR Type : 3;
            UCHAR Audit : 1;
            UCHAR Signer : 4;
        } s;
    } u;
} PS_PROTECTION;

typedef struct _PROCESS_SIGNATURE_INFORMATION {
    PS_PROTECTION Protection;
    UCHAR SignatureLevel;
    UCHAR SectionSignatureLevel;
    UCHAR Reserved;
} PROCESS_SIGNATURE_INFORMATION;

// Check if process is protected (Windows 10+)
BOOLEAN IsProcessProtected(PEPROCESS process) {
    if (!process) return FALSE;
    
    HANDLE hProcess = nullptr;
    NTSTATUS status = ObOpenObjectByPointer(
        process,
        OBJ_KERNEL_HANDLE,
        nullptr,
        PROCESS_QUERY_LIMITED_INFORMATION,
        *PsProcessType,
        KernelMode,
        &hProcess
    );
    
    if (!NT_SUCCESS(status)) return FALSE;
    
    PROCESS_SIGNATURE_INFORMATION sigInfo = {0};
    ULONG returnLength = 0;
    
    status = ZwQueryInformationProcess(
        hProcess,
        ProcessSignatureInformation,
        &sigInfo,
        sizeof(sigInfo),
        &returnLength
    );
    
    ZwClose(hProcess);
    
    if (!NT_SUCCESS(status)) return FALSE;
    
    // Check if signed by Microsoft or higher
    return (sigInfo.SignatureLevel >= SIG_LEVEL_MICROSOFT);
}

// Get process name
NTSTATUS GetProcessName(PEPROCESS process, PCHAR buffer, ULONG bufferSize) {
    if (!process || !buffer || bufferSize == 0) {
        return STATUS_INVALID_PARAMETER;
    }
    
    __try {
        const CHAR* imageName = PsGetProcessImageFileName(process);
        if (imageName && imageName[0] != '\0') {
            ULONG len = 0;
            while (imageName[len] != '\0' && len < bufferSize - 1) {
                buffer[len] = imageName[len];
                len++;
            }
            buffer[len] = '\0';
            return STATUS_SUCCESS;
        }
    } __except(EXCEPTION_EXECUTE_HANDLER) {
        return STATUS_UNSUCCESSFUL;
    }
    
    return STATUS_UNSUCCESSFUL;
}

// Check if process is system process
BOOLEAN IsSystemProcess(PEPROCESS process) {
    if (!process) return FALSE;
    
    // System process (PID 4)
    if (PsGetProcessId(process) == (HANDLE)4) return TRUE;
    
    CHAR procName[256] = {0};
    if (!NT_SUCCESS(GetProcessName(process, procName, sizeof(procName)))) {
        return FALSE;
    }
    
    // List of system processes
    const CHAR* systemProcesses[] = {
        "System",
        "smss.exe",
        "csrss.exe",
        "wininit.exe",
        "services.exe",
        "lsass.exe",
        "winlogon.exe"
    };
    
    for (ULONG i = 0; i < sizeof(systemProcesses) / sizeof(systemProcesses[0]); i++) {
        if (_stricmp(procName, systemProcesses[i]) == 0) {
            return TRUE;
        }
    }
    
    return FALSE;
}

// Main process verification function
BOOLEAN IsProcessAllowed(PEPROCESS process) {
    if (!process) return FALSE;
    
    // 1. Check if system process
    if (IsSystemProcess(process)) {
        return TRUE;
    }
    
    // 2. Check if protected process (Microsoft signed)
    if (IsProcessProtected(process)) {
        return TRUE;
    }
    
    // 3. For your anti-ransomware: Check if has valid token
    // This is where you'd integrate your token validation
    // BOOLEAN hasValidToken = CheckTokenForProcess(process);
    // if (hasValidToken) return TRUE;
    
    // 4. Default: deny
    return FALSE;
}

// Usage in callback
FLT_PREOP_CALLBACK_STATUS PreOperationWithProcessCheck(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    PEPROCESS currentProcess = PsGetCurrentProcess();
    
    if (!IsProcessAllowed(currentProcess)) {
        DbgPrint("[AntiRansomware] BLOCKED: Untrusted process\n");
        
        // Block the operation
        Data->IoStatus.Status = STATUS_ACCESS_DENIED;
        Data->IoStatus.Information = 0;
        return FLT_PREOP_COMPLETE;
    }
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}
